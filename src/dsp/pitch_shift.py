"""
Real-time Pitch and Formant Shifter based on Phase Vocoder.
Optimized for streaming chunk-by-chunk audio with state preservation.
"""
import numpy as np


class RealtimePitchShifter:
    """
    Phase Vocoder real-time pitch shifter with overlap-add (OLA).
    Maintains phase history between consecutive audio chunks.
    """
    def __init__(self, sample_rate: int = 44100, chunk_size: int = 1024, hop_size: int = 256):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.hop_size = hop_size
        self.window_size = chunk_size
        
        # Hann window
        self.window = np.hanning(self.window_size).astype(np.float32)
        
        # State buffers
        self.last_phase = np.zeros(self.window_size // 2 + 1, dtype=np.float32)
        self.sum_phase = np.zeros(self.window_size // 2 + 1, dtype=np.float32)
        self.input_fifo = np.zeros(self.window_size, dtype=np.float32)
        self.output_fifo = np.zeros(self.window_size, dtype=np.float32)
        
        # Expected phase advance per hop
        self.omega = 2.0 * np.pi * self.hop_size * np.arange(self.window_size // 2 + 1) / self.window_size

    def reset(self):
        self.last_phase.fill(0)
        self.sum_phase.fill(0)
        self.input_fifo.fill(0)
        self.output_fifo.fill(0)

    def process(self, audio_chunk: np.ndarray, semitones: float, formant_factor: float = 1.0) -> np.ndarray:
        """
        Process an input chunk of mono float32 audio.
        semitones: pitch shift in semitones (-12 to +12)
        formant_factor: formant scaling factor (0.5 to 2.0, 1.0 = neutral)
        """
        if abs(semitones) < 0.05 and abs(formant_factor - 1.0) < 0.05:
            return audio_chunk

        pitch_factor = 2.0 ** (semitones / 12.0)
        n_samples = len(audio_chunk)
        output = np.zeros(n_samples, dtype=np.float32)

        # Append new audio to input fifo
        self.input_fifo = np.concatenate((self.input_fifo[n_samples:], audio_chunk))

        # Perform STFT analysis & synthesis over hops
        # To avoid high CPU, we process with synthesis hop
        syn_hop = self.hop_size
        ana_hop = int(round(syn_hop / pitch_factor))
        if ana_hop <= 0:
            ana_hop = 1

        # Phase vocoder processing
        windowed = self.input_fifo[-self.window_size:] * self.window
        spec = np.fft.rfft(windowed)
        mag = np.abs(spec).astype(np.float32)
        phase = np.angle(spec).astype(np.float32)

        # Formant correction if requested
        if abs(formant_factor - 1.0) >= 0.05:
            # Rescale spectral envelope
            indices = np.arange(len(mag), dtype=np.float32)
            rescaled_indices = np.clip(indices / formant_factor, 0, len(mag) - 1)
            envelope = np.interp(rescaled_indices, indices, mag)
            mag = envelope

        # Phase difference and phase accumulation
        delta_phase = phase - self.last_phase
        self.last_phase = phase

        # Subtract expected advance
        delta_phase -= 2.0 * np.pi * ana_hop * np.arange(len(delta_phase)) / self.window_size
        # Map to [-pi, pi]
        delta_phase = (delta_phase + np.pi) % (2.0 * np.pi) - np.pi
        
        # Compute true frequency and accumulate synthesis phase
        true_freq = 2.0 * np.pi * np.arange(len(delta_phase)) / self.window_size + delta_phase / ana_hop
        self.sum_phase += syn_hop * true_freq

        # Reconstruct complex spectrum
        synth_spec = mag * np.exp(1j * self.sum_phase)
        synth_windowed = np.fft.irfft(synth_spec).astype(np.float32) * self.window

        # Overlap add to output fifo
        self.output_fifo += synth_windowed
        output = self.output_fifo[:n_samples].copy()
        
        # Shift output fifo
        self.output_fifo = np.concatenate((self.output_fifo[n_samples:], np.zeros(n_samples, dtype=np.float32)))

        return output
