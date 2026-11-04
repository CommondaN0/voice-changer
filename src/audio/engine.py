"""
Low-latency real-time audio streaming engine using sounddevice.
Decoupled architecture:
- Mic input stream
- Virtual Cable output stream (for Discord / Games)
- Test Monitor output stream (for Headphones - only active when Test button is ON)
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
        self.cable_output_device_id: int | None = None
        self.headphone_device_id: int | None = None
        
        # Test mode flag: user only hears themselves when this is True
        self.test_mode_active: bool = False

        self.input_stream: sd.InputStream | None = None
        self.cable_stream: sd.OutputStream | None = None
        self.monitor_stream: sd.OutputStream | None = None
        
        self.cable_queue = queue.Queue(maxsize=10)
        self.monitor_queue = queue.Queue(maxsize=10)
        
        self.is_running = False
        self._lock = threading.Lock()

    def set_voice_changing_enabled(self, enabled: bool):
        self.processor.set_enabled(enabled)

    def set_params(self, params: VoiceParams):
        self.processor.set_params(params)

    def set_test_mode(self, enabled: bool):
        """Toggles headphone monitoring (hearing yourself for testing)."""
        with self._lock:
            self.test_mode_active = enabled
        self._restart_monitor_stream()

    def _input_callback(self, indata, frames, time_info, status):
        """Captures microphone audio and passes through DSP processor."""
        if indata.shape[1] > 1:
            mono_in = np.mean(indata, axis=1, dtype=np.float32)
        else:
            mono_in = indata[:, 0].astype(np.float32)

        # Process through DSP
        processed = self.processor.process_frame(mono_in)

        # 1. Send to Virtual Cable (if active)
        if self.cable_stream is not None:
            try:
                self.cable_queue.put_nowait(processed.copy())
            except queue.Full:
                pass

        # 2. Send to Headphones Test Monitor ONLY if test mode is active
        if self.test_mode_active and self.monitor_stream is not None:
            try:
                self.monitor_queue.put_nowait(processed.copy())
            except queue.Full:
                pass

    def _cable_callback(self, outdata, frames, time_info, status):
        """Sends audio to Virtual Cable (Discord / Games)."""
        try:
            data = self.cable_queue.get_nowait()
            if outdata.shape[1] == 1:
                outdata[:] = data[:, np.newaxis]
            else:
                outdata[:, 0] = data
                outdata[:, 1] = data
        except queue.Empty:
            outdata.fill(0)

    def _monitor_callback(self, outdata, frames, time_info, status):
        """Sends audio to Headphones for user testing."""
        if not self.test_mode_active:
            outdata.fill(0)
            return

        try:
            data = self.monitor_queue.get_nowait()
            if outdata.shape[1] == 1:
                outdata[:] = data[:, np.newaxis]
            else:
                outdata[:, 0] = data
                outdata[:, 1] = data
        except queue.Empty:
            outdata.fill(0)

    def start(self, input_device_id: int | None = None, cable_output_device_id: int | None = None, headphone_device_id: int | None = None):
        """Starts audio engine streaming."""
        self.stop()
        with self._lock:
            if input_device_id is not None:
                self.input_device_id = input_device_id
            if cable_output_device_id is not None:
                self.cable_output_device_id = cable_output_device_id
            if headphone_device_id is not None:
                self.headphone_device_id = headphone_device_id

            try:
                # 1. Start Input Stream (Microphone)
                self.input_stream = sd.InputStream(
                    device=self.input_device_id,
                    samplerate=self.sample_rate,
                    blocksize=self.block_size,
                    channels=1,
                    dtype='float32',
                    callback=self._input_callback,
                    latency='low'
                )
                self.input_stream.start()
                self.is_running = True
            except Exception as e:
                self.is_running = False
                print(f"[AudioEngine] Failed to start input stream: {e}")
                raise e

            # 2. Start Virtual Cable Stream (if device configured)
            if self.cable_output_device_id is not None:
                try:
                    self.cable_stream = sd.OutputStream(
                        device=self.cable_output_device_id,
                        samplerate=self.sample_rate,
                        blocksize=self.block_size,
                        channels=2,
                        dtype='float32',
                        callback=self._cable_callback,
                        latency='low'
                    )
                    self.cable_stream.start()
                except Exception as e:
                    print(f"[AudioEngine] Cable output stream failed: {e}")
                    self.cable_stream = None

        # 3. Start Monitor Stream if test mode was active
        self._restart_monitor_stream()

    def _restart_monitor_stream(self):
        """Manages the headphone monitoring stream."""
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

        if self.is_running and self.test_mode_active and self.headphone_device_id is not None:
            try:
                self.monitor_stream = sd.OutputStream(
                    device=self.headphone_device_id,
                    samplerate=self.sample_rate,
                    blocksize=self.block_size,
                    channels=2,
                    dtype='float32',
                    callback=self._monitor_callback,
                    latency='low'
                )
                self.monitor_stream.start()
            except Exception as e:
                print(f"[AudioEngine] Failed to start test monitor: {e}")

    def stop(self):
        """Stops all streams."""
        with self._lock:
            self.is_running = False
            for s in (self.input_stream, self.cable_stream, self.monitor_stream):
                if s is not None:
                    try:
                        s.stop()
                        s.close()
                    except Exception:
                        pass
            self.input_stream = None
            self.cable_stream = None
            self.monitor_stream = None
