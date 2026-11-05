"""
Simplified and clear Audio settings dialog.
"""
import threading
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QLabel, QComboBox, QPushButton, QGroupBox, QMessageBox
)
from PySide6.QtCore import QTimer
from src.audio.devices import (
    get_input_devices, get_output_devices, find_virtual_cable_output, refresh_devices
)
from src.utils.virtual_cable import is_virtual_cable_installed, install_driver_silent


class SettingsDialog(QDialog):
    def __init__(self, current_input_id: int | None, current_cable_id: int | None, 
                 current_headphone_id: int | None, buffer_size: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки аудиоустройств")
        self.resize(540, 480)
        
        self.input_id = current_input_id
        self.cable_id = current_cable_id
        self.headphone_id = current_headphone_id
        self.buffer_size = buffer_size

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        # 1. Physical Microphone
        mic_group = QGroupBox("1. Ваш физический микрофон")
        mic_layout = QVBoxLayout(mic_group)
        self.mic_combo = QComboBox()
        self.input_devices = get_input_devices()
        
        mic_select_idx = 0
        for i, dev in enumerate(self.input_devices):
            self.mic_combo.addItem(f"🎤 {dev.name}", dev.index)
            if dev.index == self.input_id:
                mic_select_idx = i
        if self.input_devices:
            self.mic_combo.setCurrentIndex(mic_select_idx)
        mic_layout.addWidget(self.mic_combo)
        layout.addWidget(mic_group)

        # 2. Virtual Cable Status & Setup
        cable_group = QGroupBox("2. Виртуальное устройство (для Discord и игр)")
        self.cable_group_layout = QVBoxLayout(cable_group)
        self.cable_group_layout.setSpacing(8)
        
        cable_dev = find_virtual_cable_output()
        if cable_dev is not None:
            self.cable_id = cable_dev.index
            lbl_status = QLabel("✅ Виртуальный кабель найден и активен!\nВ Discord или игре выберите микрофон: «CABLE Output».")
            lbl_status.setStyleSheet("color: #22c55e; font-weight: 600;")
            self.cable_group_layout.addWidget(lbl_status)
        else:
            self.lbl_cable_status = QLabel("❌ Виртуальный кабель не установлен.\nОн необходим, чтобы ваш измененный голос слышали другие игроки.")
            self.lbl_cable_status.setStyleSheet("color: #ef4444; font-weight: 500;")
            self.cable_group_layout.addWidget(self.lbl_cable_status)

            self.btn_install_cable = QPushButton("⚡ Активировать виртуальный кабель (1 клик)")
            self.btn_install_cable.setStyleSheet("background-color: #0284c7; color: white; font-weight: 700; padding: 7px;")
            self.btn_install_cable.clicked.connect(self._install_cable)
            self.cable_group_layout.addWidget(self.btn_install_cable)
        
        layout.addWidget(cable_group)

        # 3. Headphones for Testing
        hp_group = QGroupBox("3. Ваши наушники (для кнопки «Тест»)")
        hp_layout = QVBoxLayout(hp_group)
        self.hp_combo = QComboBox()
        self.output_devices = get_output_devices()

        hp_select_idx = 0
        for i, dev in enumerate(self.output_devices):
            if "cable" in dev.name.lower():
                continue
            self.hp_combo.addItem(f"🎧 {dev.name}", dev.index)
            if dev.index == self.headphone_id:
                hp_select_idx = self.hp_combo.count() - 1

        if self.hp_combo.count() > 0:
            self.hp_combo.setCurrentIndex(hp_select_idx)
        hp_layout.addWidget(self.hp_combo)
        layout.addWidget(hp_group)

        # 4. Latency / Buffer
        buf_group = QGroupBox("4. Задержка звука (Размер буфера)")
        buf_layout = QHBoxLayout(buf_group)
        self.buf_combo = QComboBox()
        self.buf_combo.addItem("512 сэмплов (~10.7 мс, ультра-низкая задержка)", 512)
        self.buf_combo.addItem("1024 сэмплов (~21.3 мс, сбалансировано)", 1024)
        self.buf_combo.addItem("2048 сэмплов (~42.7 мс, максимальная стабильность)", 2048)

        for idx in range(self.buf_combo.count()):
            if self.buf_combo.itemData(idx) == self.buffer_size:
                self.buf_combo.setCurrentIndex(idx)
                break
        buf_layout.addWidget(self.buf_combo)
        layout.addWidget(buf_group)

        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Отмена")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_save = QPushButton("Сохранить и применить")
        btn_save.setStyleSheet("background-color: #4f46e5; color: white;")
        btn_save.clicked.connect(self._save_and_apply)
        btn_layout.addWidget(btn_save)

        layout.addLayout(btn_layout)

    def _install_cable(self):
        self.btn_install_cable.setEnabled(False)
        self.btn_install_cable.setText("⏳ Идет активация...")
        self.lbl_cable_status.setText("⏳ Установка драйвера... Пожалуйста, подтвердите системный запрос Windows (UAC).")
        self.lbl_cable_status.setStyleSheet("color: #0284c7; font-weight: 500;")

        threading.Thread(target=install_driver_silent, daemon=True).start()

        self.poll_count = 0
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self._check_installed)
        self.poll_timer.start(1200)

    def _check_installed(self):
        self.poll_count += 1
        refresh_devices()
        cable_dev = find_virtual_cable_output()
        if cable_dev is not None:
            self.poll_timer.stop()
            self.btn_install_cable.hide()
            self.lbl_cable_status.setText("✅ Виртуальный кабель успешно активирован!\nВ Discord или игре выберите микрофон: «CABLE Output».")
            self.lbl_cable_status.setStyleSheet("color: #22c55e; font-weight: 600;")
            self.cable_id = cable_dev.index
            QMessageBox.information(
                self, 
                "Успех", 
                "Виртуальный аудиокабель готов к работе!"
            )
        elif self.poll_count > 30:
            self.poll_timer.stop()
            self.btn_install_cable.setEnabled(True)
            self.btn_install_cable.setText("⚡ Повторить активацию")
            self.lbl_cable_status.setText("⚠️ Установка не завершилась или запрос UAC был отклонен.")
            self.lbl_cable_status.setStyleSheet("color: #ef4444; font-weight: 500;")

    def _save_and_apply(self):
        self.input_id = self.mic_combo.currentData()
        self.headphone_id = self.hp_combo.currentData()
        self.buffer_size = self.buf_combo.currentData()
        self.accept()
