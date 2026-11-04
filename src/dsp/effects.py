"""
Audio DSP effects for real-time voice processing.
All effects maintain internal state for seamless chunk-by-chunk streaming.
"""
import numpy as np
from scipy import signal


class NoiseGate:
    """Noise gate to eliminate background microphone hiss and quiet room noise."""
    def __init__(self, threshold_db: float = -45.0, attack_ms: float = 10.0, release_ms: float = 80.0, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.threshold = 10.0 ** (threshold_db / 20.0)
        self.envelope = 0.0
        self.gain = 1.0
        
        self.attack_coef = np.exp(-1.0 / (sample_rate * (attack_ms / 1000.0)))
        self.release_coef = np.exp(-1.0 / (sample_rate * (release_ms / 1000.0)))

    def process(self, chunk: np.ndarray, enabled: bool = True, threshold_db: float = -45.0) -> np.ndarray:
        if not enabled:
            return chunk
        
        threshold = 10.0 ** (threshold_db / 20.0)
        rms = np.sqrt(np.mean(chunk ** 2) + 1e-12)
        
        target_gain = 1.0 if rms >= threshold else 0.0
        coef = self.attack_coef if target_gain > self.gain else self.release_coef
        self.gain = coef * self.gain + (1.0 - coef) * target_gain
        
        return chunk * self.gain


class Equalizer:
    """3-band shelving/peaking equalizer with filter state preservation."""
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        # Low shelf at 250 Hz, High shelf at 4000 Hz, Mid peak at 1500 Hz
        nyq = sample_rate / 2.0
        self.low_b, self.low_a = signal.butter(2, min(0.99, 250.0 / nyq), btype='low')
        self.high_b, self.high_a = signal.butter(2, min(0.99, 4000.0 / nyq), btype='high')
        
        # State filters
        self.low_zi = signal.lfilter_zi(self.low_b, self.low_a) * 0.0
        self.high_zi = signal.lfilter_zi(self.high_b, self.high_a) * 0.0

    def process(self, chunk: np.ndarray, low_gain_db: float = 0.0, mid_gain_db: float = 0.0, high_gain_db: float = 0.0) -> np.ndarray:
        if abs(low_gain_db) < 0.2 and abs(mid_gain_db) < 0.2 and abs(high_gain_db) < 0.2:
            return chunk

        low_linear = 10.0 ** (low_gain_db / 20.0)
        mid_linear = 10.0 ** (mid_gain_db / 20.0)
        high_linear = 10.0 ** (high_gain_db / 20.0)

        low_band, self.low_zi = signal.lfilter(self.low_b, self.low_a, chunk, zi=self.low_zi)
        high_band, self.high_zi = signal.lfilter(self.high_b, self.high_a, chunk, zi=self.high_zi)
        mid_band = chunk - (low_band + high_band)

        out = (low_band * low_linear) + (mid_band * mid_linear) + (high_band * high_linear)
        return out


class RingModulator:
    """Robot / Ring Modulator effect."""
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.phase = 0.0

    def process(self, chunk: np.ndarray, frequency_hz: float = 60.0, mix: float = 0.0) -> np.ndarray:
        if mix <= 0.01:
            return chunk

        n_samples = len(chunk)
        t = np.arange(n_samples) / self.sample_rate
        omega = 2.0 * np.pi * frequency_hz
        carrier = np.sin(self.phase + omega * t).astype(np.float32)
        
        # Advance phase
        self.phase = (self.phase + omega * (n_samples / self.sample_rate)) % (2.0 * np.pi)

        modulated = chunk * carrier
        return (1.0 - mix) * chunk + mix * modulated


class DelayEcho:
    """Delay / Echo effect with feedback and delay line."""
    def __init__(self, max_delay_sec: float = 1.0, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.buffer_len = int(max_delay_sec * sample_rate)
        self.buffer = np.zeros(self.buffer_len, dtype=np.float32)
        self.write_pos = 0

    def process(self, chunk: np.ndarray, delay_ms: float = 150.0, feedback: float = 0.35, mix: float = 0.0) -> np.ndarray:
        if mix <= 0.01:
            return chunk

        delay_samples = int((delay_ms / 1000.0) * self.sample_rate)
        delay_samples = max(1, min(self.buffer_len - 1, delay_samples))
        n_samples = len(chunk)
        output = np.empty_like(chunk)

        for i in range(n_samples):
            read_pos = (self.write_pos - delay_samples) % self.buffer_len
            delayed_sample = self.buffer[read_pos]
            input_sample = chunk[i]
            
            output[i] = (1.0 - mix) * input_sample + mix * delayed_sample
            self.buffer[self.write_pos] = input_sample + delayed_sample * feedback
            self.write_pos = (self.write_pos + 1) % self.buffer_len

        return output


class Distortion:
    """Drive / Distortion / Walkie-talkie overdrive effect."""
    @staticmethod
    def process(chunk: np.ndarray, drive: float = 1.0, mix: float = 0.0) -> np.ndarray:
        if mix <= 0.01 or drive <= 1.01:
            return chunk
        
        # Soft-clipping with tanh
        boosted = chunk * drive
        distorted = np.tanh(boosted)
        return (1.0 - mix) * chunk + mix * distorted
