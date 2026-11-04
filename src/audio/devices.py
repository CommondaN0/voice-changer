"""
Clean Audio device enumeration and management using sounddevice.
Filters out low-level WDM-KS driver paths and duplicates, preferring WASAPI.
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
        return self.name


def get_all_raw_devices():
    return sd.query_devices()


def get_clean_devices(is_input: bool = True) -> List[AudioDeviceInfo]:
    """
    Returns clean, deduplicated audio devices prioritizing modern Windows WASAPI.
    Eliminates messy driver internal paths and generic remappers.
    """
    devices = sd.query_devices()
    hostapis = sd.query_hostapis()
    default_input, default_output = sd.default.device
    ch_key = 'max_input_channels' if is_input else 'max_output_channels'

    clean_list: List[AudioDeviceInfo] = []
    seen_names = set()

    # Pass 1: WASAPI devices (highest quality, lowest latency, clean names)
    for idx, dev in enumerate(devices):
        if dev[ch_key] <= 0:
            continue
        raw_name = dev.get("name", "")
        # Filter driver paths and system remappers
        if "@System32" in raw_name or "Переназначение" in raw_name or "Первичный" in raw_name:
            continue
        
        hostapi_idx = dev.get("hostapi", 0)
        api_name = hostapis[hostapi_idx].get("name", "") if hostapi_idx < len(hostapis) else ""

        if "WASAPI" in api_name:
            clean_name = raw_name.strip()
            # Normalize truncated names
            norm_key = clean_name.lower()[:15]
            if norm_key not in seen_names:
                seen_names.add(norm_key)
                clean_list.append(AudioDeviceInfo(
                    index=idx,
                    name=clean_name,
                    hostapi_name=api_name,
                    max_input_channels=dev.get("max_input_channels", 0),
                    max_output_channels=dev.get("max_output_channels", 0),
                    default_samplerate=dev.get("default_samplerate", 44100.0),
                    is_default_input=(idx == default_input),
                    is_default_output=(idx == default_output),
                ))

    # Pass 2: Fallback for any devices not available in WASAPI (excluding WDM-KS raw paths)
    for idx, dev in enumerate(devices):
        if dev[ch_key] <= 0:
            continue
        raw_name = dev.get("name", "")
        if "@System32" in raw_name or "Переназначение" in raw_name or "Первичный" in raw_name:
            continue

        hostapi_idx = dev.get("hostapi", 0)
        api_name = hostapis[hostapi_idx].get("name", "") if hostapi_idx < len(hostapis) else ""

        if "WDM-KS" not in api_name:
            clean_name = raw_name.strip()
            norm_key = clean_name.lower()[:15]
            if norm_key not in seen_names:
                seen_names.add(norm_key)
                clean_list.append(AudioDeviceInfo(
                    index=idx,
                    name=clean_name,
                    hostapi_name=api_name,
                    max_input_channels=dev.get("max_input_channels", 0),
                    max_output_channels=dev.get("max_output_channels", 0),
                    default_samplerate=dev.get("default_samplerate", 44100.0),
                    is_default_input=(idx == default_input),
                    is_default_output=(idx == default_output),
                ))

    return clean_list


def get_input_devices() -> List[AudioDeviceInfo]:
    """Returns human-friendly microphone devices."""
    return get_clean_devices(is_input=True)


def get_output_devices() -> List[AudioDeviceInfo]:
    """Returns human-friendly playback devices."""
    return get_clean_devices(is_input=False)


def find_default_device(is_input: bool = True) -> Optional[AudioDeviceInfo]:
    devices = get_clean_devices(is_input=is_input)
    if not devices:
        return None
    for dev in devices:
        if (is_input and dev.is_default_input) or (not is_input and dev.is_default_output):
            return dev
    return devices[0]


def find_virtual_cable_output() -> Optional[AudioDeviceInfo]:
    """Finds VB-Audio Cable Input (which our app outputs to)."""
    for dev in get_clean_devices(is_input=False):
        name_lower = dev.name.lower()
        if "cable input" in name_lower or "vb-audio" in name_lower:
            return dev
    return None


def find_virtual_cable_input() -> Optional[AudioDeviceInfo]:
    """Finds VB-Audio Cable Output (which games/discord read from)."""
    for dev in get_clean_devices(is_input=True):
        name_lower = dev.name.lower()
        if "cable output" in name_lower or "vb-audio" in name_lower:
            return dev
    return None
