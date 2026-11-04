"""
Audio device enumeration and management using sounddevice.
"""
from dataclasses import dataclass
from typing import List, Optional
import sounddevice as sd


@dataclass
class AudioDeviceInfo:
    index: int
    name: str
    hostapi_name: str
    max_input_channels: int
    max_output_channels: int
    default_samplerate: float
    is_default_input: bool = False
    is_default_output: bool = False

    @property
    def display_name(self) -> str:
        return f"{self.name} ({self.hostapi_name})"


def get_audio_devices() -> List[AudioDeviceInfo]:
    """Returns a list of all available audio devices."""
    devices = sd.query_devices()
    hostapis = sd.query_hostapis()
    default_input, default_output = sd.default.device

    device_list: List[AudioDeviceInfo] = []
    for idx, dev in enumerate(devices):
        hostapi_idx = dev.get("hostapi", 0)
        hostapi_name = hostapis[hostapi_idx].get("name", "Unknown") if hostapi_idx < len(hostapis) else "Unknown"
        
        info = AudioDeviceInfo(
            index=idx,
            name=dev.get("name", f"Device #{idx}"),
            hostapi_name=hostapi_name,
            max_input_channels=dev.get("max_input_channels", 0),
            max_output_channels=dev.get("max_output_channels", 0),
            default_samplerate=dev.get("default_samplerate", 44100.0),
            is_default_input=(idx == default_input),
            is_default_output=(idx == default_output),
        )
        device_list.append(info)
    return device_list


def get_input_devices() -> List[AudioDeviceInfo]:
    """Returns input devices (microphones)."""
    return [d for d in get_audio_devices() if d.max_input_channels > 0]


def get_output_devices() -> List[AudioDeviceInfo]:
    """Returns output devices (speakers, virtual cables, headphones)."""
    return [d for d in get_audio_devices() if d.max_output_channels > 0]


def find_default_device(is_input: bool = True) -> Optional[AudioDeviceInfo]:
    """Finds default system audio device."""
    devices = get_input_devices() if is_input else get_output_devices()
    for dev in devices:
        if (is_input and dev.is_default_input) or (not is_input and dev.is_default_output):
            return dev
    return devices[0] if devices else None
