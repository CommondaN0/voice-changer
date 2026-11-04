"""
Advanced DSP controls tab with full fine-grained sliders.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QSlider, QLabel, QPushButton, QCheckBox, QGroupBox, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from src.dsp.presets import VoiceParams


class AdvancedTab(QWidget):
    params_changed = Signal(VoiceParams)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.params = VoiceParams()
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)

        # Scroll area for many sliders
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(14)

        # 1. Pitch & Formant Group
        pitch_group = QGroupBox("Тональность и Форманта")
        pitch_grid = QGridLayout(pitch_group)

        self.pitch_lbl = QLabel("Высота тона (Pitch): 0.0 полутонов")
        self.pitch_sld = self._make_slider(-120, 120, 0, self._on_value_changed)
        pitch_grid.addWidget(self.pitch_lbl, 0, 0)
        pitch_grid.addWidget(self.pitch_sld, 0, 1)

        self.formant_lbl = QLabel("Форманта (Окрас): 1.00x")
        self.formant_sld = self._make_slider(60, 150, 100, self._on_value_changed)
        pitch_grid.addWidget(self.formant_lbl, 1, 0)
        pitch_grid.addWidget(self.formant_sld, 1, 1)
        layout.addWidget(pitch_group)

        # 2. Equalizer Group
        eq_group = QGroupBox("3-Полосный Эквалайзер")
        eq_grid = QGridLayout(eq_group)

        self.eq_low_lbl = QLabel("Низкие частоты (Low): 0.0 dB")
        self.eq_low_sld = self._make_slider(-12, 12, 0, self._on_value_changed)
        eq_grid.addWidget(self.eq_low_lbl, 0, 0)
        eq_grid.addWidget(self.eq_low_sld, 0, 1)

        self.eq_mid_lbl = QLabel("Средние частоты (Mid): 0.0 dB")
        self.eq_mid_sld = self._make_slider(-12, 12, 0, self._on_value_changed)
        eq_grid.addWidget(self.eq_mid_lbl, 1, 0)
        eq_grid.addWidget(self.eq_mid_sld, 1, 1)

        self.eq_high_lbl = QLabel("Высокие частоты (High): 0.0 dB")
        self.eq_high_sld = self._make_slider(-12, 12, 0, self._on_value_changed)
        eq_grid.addWidget(self.eq_high_lbl, 2, 0)
        eq_grid.addWidget(self.eq_high_sld, 2, 1)
        layout.addWidget(eq_group)

        # 3. Robot & Ring Modulation
        robot_group = QGroupBox("Эффект Робота (Ring Modulation)")
        robot_grid = QGridLayout(robot_group)

        self.robot_mix_lbl = QLabel("Интенсивность: 0%")
        self.robot_mix_sld = self._make_slider(0, 100, 0, self._on_value_changed)
        robot_grid.addWidget(self.robot_mix_lbl, 0, 0)
        robot_grid.addWidget(self.robot_mix_sld, 0, 1)

        self.robot_freq_lbl = QLabel("Частота модуляции: 65 Hz")
        self.robot_freq_sld = self._make_slider(20, 200, 65, self._on_value_changed)
        robot_grid.addWidget(self.robot_freq_lbl, 1, 0)
        robot_grid.addWidget(self.robot_freq_sld, 1, 1)
        layout.addWidget(robot_group)

        # 4. Delay & Echo
        delay_group = QGroupBox("Эхо / Задержка")
        delay_grid = QGridLayout(delay_group)

        self.delay_mix_lbl = QLabel("Интенсивность эхо: 0%")
        self.delay_mix_sld = self._make_slider(0, 100, 0, self._on_value_changed)
        delay_grid.addWidget(self.delay_mix_lbl, 0, 0)
        delay_grid.addWidget(self.delay_mix_sld, 0, 1)

        self.delay_time_lbl = QLabel("Время задержки: 120 ms")
        self.delay_time_sld = self._make_slider(20, 500, 120, self._on_value_changed)
        delay_grid.addWidget(self.delay_time_lbl, 1, 0)
        delay_grid.addWidget(self.delay_time_sld, 1, 1)

        self.delay_fb_lbl = QLabel("Обратная связь (Feedback): 30%")
        self.delay_fb_sld = self._make_slider(0, 80, 30, self._on_value_changed)
        delay_grid.addWidget(self.delay_fb_lbl, 2, 0)
        delay_grid.addWidget(self.delay_fb_sld, 2, 1)
        layout.addWidget(delay_group)

        # 5. Distortion & Gate
        extra_group = QGroupBox("Перегруз и Шумоподавление")
        extra_grid = QGridLayout(extra_group)

        self.dist_mix_lbl = QLabel("Дисторшн / Перегруз: 0%")
        self.dist_mix_sld = self._make_slider(0, 100, 0, self._on_value_changed)
        extra_grid.addWidget(self.dist_mix_lbl, 0, 0)
        extra_grid.addWidget(self.dist_mix_sld, 0, 1)

        self.gate_check = QCheckBox("Включить шумоподавление (Noise Gate)")
        self.gate_check.setChecked(True)
        self.gate_check.toggled.connect(self._on_value_changed)
        extra_grid.addWidget(self.gate_check, 1, 0)

        self.gate_lbl = QLabel("Порог отсечки шума: -45 dB")
        self.gate_sld = self._make_slider(-70, -20, -45, self._on_value_changed)
        extra_grid.addWidget(self.gate_lbl, 2, 0)
        extra_grid.addWidget(self.gate_sld, 2, 1)
        layout.addWidget(extra_group)

        # Reset button
        btn_reset = QPushButton("Сбросить все параметры в ноль")
        btn_reset.clicked.connect(self.reset_to_defaults)
        layout.addWidget(btn_reset)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def _make_slider(self, min_val, max_val, default_val, callback):
        sld = QSlider(Qt.Orientation.Horizontal)
        sld.setRange(min_val, max_val)
        sld.setValue(default_val)
        sld.valueChanged.connect(callback)
        return sld

    def set_params(self, params: VoiceParams):
        self.params = params
        self.blockSignals(True)

        self.pitch_sld.setValue(int(params.pitch_semitones * 10))
        self.formant_sld.setValue(int(params.formant_factor * 100))
        self.eq_low_sld.setValue(int(params.eq_low))
        self.eq_mid_sld.setValue(int(params.eq_mid))
        self.eq_high_sld.setValue(int(params.eq_high))
        self.robot_mix_sld.setValue(int(params.robot_mix * 100))
        self.robot_freq_sld.setValue(int(params.robot_freq))
        self.delay_mix_sld.setValue(int(params.delay_mix * 100))
        self.delay_time_sld.setValue(int(params.delay_ms))
        self.delay_fb_sld.setValue(int(params.delay_feedback * 100))
        self.dist_mix_sld.setValue(int(params.distortion_mix * 100))
        self.gate_check.setChecked(params.gate_enabled)
        self.gate_sld.setValue(int(params.gate_threshold_db))

        self.blockSignals(False)
        self._update_labels()

    def reset_to_defaults(self):
        self.set_params(VoiceParams())
        self._on_value_changed()

    def _update_labels(self):
        pitch = self.pitch_sld.value() / 10.0
        formant = self.formant_sld.value() / 100.0
        low = self.eq_low_sld.value()
        mid = self.eq_mid_sld.value()
        high = self.eq_high_sld.value()
        robot_mix = self.robot_mix_sld.value()
        robot_freq = self.robot_freq_sld.value()
        delay_mix = self.delay_mix_sld.value()
        delay_ms = self.delay_time_sld.value()
        delay_fb = self.delay_fb_sld.value()
        dist_mix = self.dist_mix_sld.value()
        gate_db = self.gate_sld.value()

        self.pitch_lbl.setText(f"Высота тона (Pitch): {pitch:+.1f} полутонов")
        self.formant_lbl.setText(f"Форманта (Окрас): {formant:.2f}x")
        self.eq_low_lbl.setText(f"Низкие частоты (Low): {low:+d} dB")
        self.eq_mid_lbl.setText(f"Средние частоты (Mid): {mid:+d} dB")
        self.eq_high_lbl.setText(f"Высокие частоты (High): {high:+d} dB")
        self.robot_mix_lbl.setText(f"Интенсивность: {robot_mix}%")
        self.robot_freq_lbl.setText(f"Частота модуляции: {robot_freq} Hz")
        self.delay_mix_lbl.setText(f"Интенсивность эхо: {delay_mix}%")
        self.delay_time_lbl.setText(f"Время задержки: {delay_ms} ms")
        self.delay_fb_lbl.setText(f"Обратная связь (Feedback): {delay_fb}%")
        self.dist_mix_lbl.setText(f"Дисторшн / Перегруз: {dist_mix}%")
        self.gate_lbl.setText(f"Порог отсечки шума: {gate_db} dB")

    def _on_value_changed(self):
        self._update_labels()
        p = VoiceParams(
            pitch_semitones=self.pitch_sld.value() / 10.0,
            formant_factor=self.formant_sld.value() / 100.0,
            eq_low=float(self.eq_low_sld.value()),
            eq_mid=float(self.eq_mid_sld.value()),
            eq_high=float(self.eq_high_sld.value()),
            robot_mix=self.robot_mix_sld.value() / 100.0,
            robot_freq=float(self.robot_freq_sld.value()),
            delay_mix=self.delay_mix_sld.value() / 100.0,
            delay_ms=float(self.delay_time_sld.value()),
            delay_feedback=self.delay_fb_sld.value() / 100.0,
            drive=1.0 + (self.dist_mix_sld.value() / 100.0) * 3.0,
            distortion_mix=self.dist_mix_sld.value() / 100.0,
            gate_enabled=self.gate_check.isChecked(),
            gate_threshold_db=float(self.gate_sld.value()),
            output_gain=1.0
        )
        self.params = p
        self.params_changed.emit(p)
