"""
Preset configurations and definitions for Voice Changer.
"""
from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class VoiceParams:
    # Pitch & Formants
    pitch_semitones: float = 0.0     # -12.0 to +12.0
    formant_factor: float = 1.0      # 0.6 to 1.5

    # Equalizer (dB)
    eq_low: float = 0.0              # -12.0 to +12.0 dB
    eq_mid: float = 0.0              # -12.0 to +12.0 dB
    eq_high: float = 0.0             # -12.0 to +12.0 dB

    # Robot / Modulation
    robot_mix: float = 0.0           # 0.0 to 1.0
    robot_freq: float = 65.0         # 20.0 to 200.0 Hz

    # Echo / Delay
    delay_mix: float = 0.0           # 0.0 to 1.0
    delay_ms: float = 120.0          # 20.0 to 500.0 ms
    delay_feedback: float = 0.3      # 0.0 to 0.8

    # Distortion / Drive
    drive: float = 1.0               # 1.0 to 5.0
    distortion_mix: float = 0.0      # 0.0 to 1.0

    # Noise gate
    gate_enabled: bool = True
    gate_threshold_db: float = -45.0 # -70.0 to -20.0 dB

    # Master Output Gain
    output_gain: float = 1.0         # 0.0 to 2.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VoiceParams":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


PRESETS: Dict[str, VoiceParams] = {
    "Оригинал (Без изменений)": VoiceParams(
        pitch_semitones=0.0,
        formant_factor=1.0,
    ),
    "Женский (Естественный)": VoiceParams(
        pitch_semitones=3.8,
        formant_factor=1.18,
        eq_low=-2.0,
        eq_mid=1.5,
        eq_high=2.0,
    ),
    "Женский (Высокий / Аниме)": VoiceParams(
        pitch_semitones=6.5,
        formant_factor=1.30,
        eq_low=-4.0,
        eq_mid=2.0,
        eq_high=3.0,
    ),
    "Мужской (Баритон)": VoiceParams(
        pitch_semitones=-3.5,
        formant_factor=0.88,
        eq_low=3.5,
        eq_mid=-1.0,
        eq_high=0.5,
    ),
    "Мужской (Глубокий бас)": VoiceParams(
        pitch_semitones=-6.0,
        formant_factor=0.80,
        eq_low=5.0,
        eq_mid=-2.0,
        eq_high=-1.0,
    ),
    "Робот": VoiceParams(
        pitch_semitones=-1.5,
        formant_factor=1.0,
        robot_mix=0.65,
        robot_freq=70.0,
        eq_mid=4.0,
    ),
    "Рация / Walkie-Talkie": VoiceParams(
        pitch_semitones=0.0,
        formant_factor=1.0,
        eq_low=-12.0,
        eq_mid=6.0,
        eq_high=-8.0,
        drive=2.8,
        distortion_mix=0.5,
    ),
    "Космическое Эхо": VoiceParams(
        pitch_semitones=1.0,
        formant_factor=1.05,
        delay_mix=0.4,
        delay_ms=220.0,
        delay_feedback=0.5,
    ),
}
