"""
Preset selection and quick tuning tab for Voice Changer.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QPushButton, QLabel, QSlider, QGroupBox
)
from PySide6.QtCore import Qt, Signal
from src.dsp.presets import PRESETS, VoiceParams


class PresetsTab(QWidget):
    params_changed = Signal(VoiceParams)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_preset_name = "Оригинал (Без изменений)"
        self.base_params = VoiceParams()
        self.current_params = VoiceParams()
        
        self.cards: dict[str, QPushButton] = {}
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Title / Description
        header = QLabel("Выберите готовый профиль голоса:")
        header.setStyleSheet("font-size: 15px; font-weight: 700; color: #818cf8;")
        layout.addWidget(header)

        # Presets Grid
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        
        row, col = 0, 0
        for name in PRESETS.keys():
            btn = QPushButton(name)
            btn.setProperty("class", "PresetCard")
            btn.setCheckable(True)
            btn.setMinimumHeight(48)
            btn.clicked.connect(lambda checked, n=name: self._on_preset_clicked(n))
            self.cards[name] = btn
            
            grid_layout.addWidget(btn, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1

        layout.addLayout(grid_layout)

        # Quick Adjustments Group
        tweak_group = QGroupBox("Быстрая подстройка выбранного пресета")
        tweak_layout = QVBoxLayout(tweak_group)
        tweak_layout.setSpacing(12)

        # 1. Pitch fine-tuning
        self.pitch_label = QLabel("Сдвиг тональности: 0.0 полутонов")
        self.pitch_slider = QSlider(Qt.Orientation.Horizontal)
        self.pitch_slider.setRange(-60, 60) # -6.0 to +6.0
        self.pitch_slider.setValue(0)
        self.pitch_slider.valueChanged.connect(self._on_tweak_changed)
        tweak_layout.addWidget(self.pitch_label)
        tweak_layout.addWidget(self.pitch_slider)

        # 2. Formant / Timbre fine-tuning
        self.formant_label = QLabel("Окрас голоса (Форманта): Норма")
        self.formant_slider = QSlider(Qt.Orientation.Horizontal)
        self.formant_slider.setRange(-30, 30) # -0.30 to +0.30
        self.formant_slider.setValue(0)
        self.formant_slider.valueChanged.connect(self._on_tweak_changed)
        tweak_layout.addWidget(self.formant_label)
        tweak_layout.addWidget(self.formant_slider)

        # 3. Volume / Gain
        self.gain_label = QLabel("Громкость голоса: 100%")
        self.gain_slider = QSlider(Qt.Orientation.Horizontal)
        self.gain_slider.setRange(20, 180)
        self.gain_slider.setValue(100)
        self.gain_slider.valueChanged.connect(self._on_tweak_changed)
        tweak_layout.addWidget(self.gain_label)
        tweak_layout.addWidget(self.gain_slider)

        layout.addWidget(tweak_group)
        layout.addStretch()

        # Select default
        self._on_preset_clicked("Оригинал (Без изменений)")

    def _on_preset_clicked(self, name: str):
        self.current_preset_name = name
        self.base_params = PRESETS[name]

        # Reset fine-tuning sliders without re-triggering signal
        self.pitch_slider.blockSignals(True)
        self.formant_slider.blockSignals(True)
        self.gain_slider.blockSignals(True)

        self.pitch_slider.setValue(0)
        self.formant_slider.setValue(0)
        self.gain_slider.setValue(int(self.base_params.output_gain * 100))

        self.pitch_slider.blockSignals(False)
        self.formant_slider.blockSignals(False)
        self.gain_slider.blockSignals(False)

        self._update_card_styles()
        self._apply_and_emit()

    def _on_tweak_changed(self):
        pitch_offset = self.pitch_slider.value() / 10.0
        formant_offset = self.formant_slider.value() / 100.0
        gain_pct = self.gain_slider.value()

        self.pitch_label.setText(f"Сдвиг тональности: {pitch_offset:+.1f} полутонов")
        self.formant_label.setText(f"Окрас голоса (Форманта): {formant_offset:+.2f}")
        self.gain_label.setText(f"Громкость голоса: {gain_pct}%")

        self._apply_and_emit()

    def _apply_and_emit(self):
        pitch_offset = self.pitch_slider.value() / 10.0
        formant_offset = self.formant_slider.value() / 100.0
        gain_pct = self.gain_slider.value()

        p = VoiceParams.from_dict(self.base_params.to_dict())
        p.pitch_semitones = max(-12.0, min(12.0, p.pitch_semitones + pitch_offset))
        p.formant_factor = max(0.5, min(1.8, p.formant_factor + formant_offset))
        p.output_gain = gain_pct / 100.0

        self.current_params = p
        self.params_changed.emit(p)

    def _update_card_styles(self):
        for name, btn in self.cards.items():
            is_active = (name == self.current_preset_name)
            btn.setChecked(is_active)
            btn.setProperty("selected", "true" if is_active else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
