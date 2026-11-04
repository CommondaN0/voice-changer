"""
Audio DSP Processor chain coordinating all voice effects.
"""
import threading
import numpy as np

from src.dsp.pitch_shift import RealtimePitchShifter
from src.dsp.effects import NoiseGate, Equalizer, RingModulator, DelayEcho, Distortion
from src.dsp.presets import VoiceParams


class DSPProcessor:
    def __init__(self, sample_rate: int = 44100, chunk_size: int = 1024):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self._lock = threading.Lock()
        
        self.params = VoiceParams()
        self.enabled = False

        # Effect instances
        self.noise_gate = NoiseGate(sample_rate=sample_rate)
        self.pitch_shifter = RealtimePitchShifter(sample_rate=sample_rate, chunk_size=chunk_size)
        self.equalizer = Equalizer(sample_rate=sample_rate)
        self.robot = RingModulator(sample_rate=sample_rate)
        self.delay = DelayEcho(sample_rate=sample_rate)
        
        # Audio level metering (0.0 to 1.0)
        self.input_level = 0.0
        self.output_level = 0.0

    def set_params(self, params: VoiceParams):
        with self._lock:
            self.params = params

    def set_enabled(self, enabled: bool):
        with self._lock:
            self.enabled = enabled
            if not enabled:
                self.pitch_shifter.reset()

    def process_frame(self, input_chunk: np.ndarray) -> np.ndarray:
        """
        Processes a single mono audio frame (numpy float32 array).
        Returns the processed float32 audio array.
        """
        # Calculate input level
        raw_peak = float(np.max(np.abs(input_chunk))) if len(input_chunk) > 0 else 0.0
        self.input_level = 0.7 * self.input_level + 0.3 * raw_peak

        with self._lock:
            enabled = self.enabled
            p = self.params

        if not enabled:
            self.output_level = self.input_level
            return input_chunk

        # 1. Noise gate
        audio = self.noise_gate.process(input_chunk, enabled=p.gate_enabled, threshold_db=p.gate_threshold_db)

        # 2. Pitch & Formant shift
        audio = self.pitch_shifter.process(audio, semitones=p.pitch_semitones, formant_factor=p.formant_factor)

        # 3. 3-Band Equalizer
        audio = self.equalizer.process(audio, low_gain_db=p.eq_low, mid_gain_db=p.eq_mid, high_gain_db=p.eq_high)

        # 4. Robot / Ring modulation
        audio = self.robot.process(audio, frequency_hz=p.robot_freq, mix=p.robot_mix)

        # 5. Delay / Echo
        audio = self.delay.process(audio, delay_ms=p.delay_ms, feedback=p.delay_feedback, mix=p.delay_mix)

        # 6. Distortion / Overdrive
        audio = Distortion.process(audio, drive=p.drive, mix=p.distortion_mix)

        # 7. Master Output Gain
        audio = audio * p.output_gain

        # 8. Soft limiter to prevent harsh digital clipping
        audio = np.clip(audio, -1.0, 1.0)

        # Calculate output level
        out_peak = float(np.max(np.abs(audio))) if len(audio) > 0 else 0.0
        self.output_level = 0.7 * self.output_level + 0.3 * out_peak

        return audio.astype(np.float32)
