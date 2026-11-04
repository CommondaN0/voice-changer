"""
Low-latency real-time audio streaming engine using sounddevice.
Supports main output (e.g. Virtual Cable) and parallel headphone monitoring.
"""
import threading
import queue
import sounddevice as sd
import numpy as np

from src.dsp.processor import DSPProcessor
from src.dsp.presets import VoiceParams


class AudioEngine:
    def __init__(self, sample_rate: int = 44100, block_size: int = 1024):
        self.sample_rate = sample_rate
        self.block_size = block_size
        
        self.processor = DSPProcessor(sample_rate=sample_rate, chunk_size=block_size)
        
        self.input_device_id: int | None = None
        self.output_device_id: int | None = None
        self.monitor_device_id: int | None = None
        self.monitor_enabled: bool = False

        self.stream: sd.Stream | None = None
        self.monitor_stream: sd.OutputStream | None = None
        
        self.monitor_queue = queue.Queue(maxsize=10)
        self.is_running = False
        self._lock = threading.Lock()

    def set_voice_changing_enabled(self, enabled: bool):
        self.processor.set_enabled(enabled)

    def set_params(self, params: VoiceParams):
        self.processor.set_params(params)

    def set_monitor(self, enabled: bool, monitor_device_id: int | None = None):
        with self._lock:
            self.monitor_enabled = enabled
            if monitor_device_id is not None:
                self.monitor_device_id = monitor_device_id
        
        if self.is_running:
            self._restart_monitor_stream()

    def _audio_callback(self, indata, outdata, frames, time_info, status):
        """Main audio callback for duplex stream (Mic -> Process -> Output)."""
        if status:
            pass  # Buffer overflow / underflow handling if needed

        # Convert input to mono float32
        if indata.shape[1] > 1:
            mono_in = np.mean(indata, axis=1, dtype=np.float32)
        else:
            mono_in = indata[:, 0].astype(np.float32)

        # DSP Processing
        processed = self.processor.process_frame(mono_in)

        # Output to primary output device (mono or stereo)
        if outdata.shape[1] == 1:
            outdata[:] = processed[:, np.newaxis]
        else:
            outdata[:, 0] = processed
            outdata[:, 1] = processed

        # Pass to monitor queue if monitoring is on
        if self.monitor_enabled:
            try:
                self.monitor_queue.put_nowait(processed.copy())
            except queue.Full:
                pass

    def _monitor_callback(self, outdata, frames, time_info, status):
        """Secondary callback for headphones monitoring."""
        try:
            data = self.monitor_queue.get_nowait()
            if outdata.shape[1] == 1:
                outdata[:] = data[:, np.newaxis]
            else:
                outdata[:, 0] = data
                outdata[:, 1] = data
        except queue.Empty:
            outdata.fill(0)

    def _restart_monitor_stream(self):
        """Starts or stops the monitor stream depending on configuration."""
        if self.monitor_stream is not None:
            try:
                self.monitor_stream.stop()
                self.monitor_stream.close()
            except Exception:
                pass
            self.monitor_stream = None

        while not self.monitor_queue.empty():
            try:
                self.monitor_queue.get_nowait()
            except queue.Empty:
                break

        if self.is_running and self.monitor_enabled and self.monitor_device_id is not None:
            try:
                self.monitor_stream = sd.OutputStream(
                    device=self.monitor_device_id,
                    samplerate=self.sample_rate,
                    blocksize=self.block_size,
                    channels=2,
                    dtype='float32',
                    callback=self._monitor_callback,
                    latency='low'
                )
                self.monitor_stream.start()
            except Exception as e:
                print(f"[AudioEngine] Failed to start monitor stream: {e}")

    def start(self, input_device_id: int | None = None, output_device_id: int | None = None):
        """Starts audio engine streaming."""
        self.stop()
        with self._lock:
            if input_device_id is not None:
                self.input_device_id = input_device_id
            if output_device_id is not None:
                self.output_device_id = output_device_id

            try:
                # Primary stream (Mic -> Output)
                self.stream = sd.Stream(
                    device=(self.input_device_id, self.output_device_id),
                    samplerate=self.sample_rate,
                    blocksize=self.block_size,
                    channels=(1, 2),
                    dtype='float32',
                    callback=self._audio_callback,
                    latency='low'
                )
                self.stream.start()
                self.is_running = True
            except Exception as e:
                self.is_running = False
                print(f"[AudioEngine] Failed to start primary stream: {e}")
                raise e

        self._restart_monitor_stream()

    def stop(self):
        """Stops all streams."""
        with self._lock:
            self.is_running = False
            if self.stream is not None:
                try:
                    self.stream.stop()
                    self.stream.close()
                except Exception:
                    pass
                self.stream = None

            if self.monitor_stream is not None:
                try:
                    self.monitor_stream.stop()
                    self.monitor_stream.close()
                except Exception:
                    pass
                self.monitor_stream = None
