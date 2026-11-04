"""
Audio and Application settings dialog.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QLabel, QComboBox, QCheckBox, QPushButton, QGroupBox, QMessageBox
)
from src.audio.devices import get_input_devices, get_output_devices
from src.utils.admin import is_admin, restart_as_admin


class SettingsDialog(QDialog):
    def __init__(self, current_input_id: int | None, current_output_id: int | None, 
                 current_monitor_id: int | None, monitor_enabled: bool, 
                 buffer_size: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки аудио и устройств")
        self.resize(500, 420)
        
        self.input_id = current_input_id
        self.output_id = current_output_id
        self.monitor_id = current_monitor_id
        self.monitor_enabled = monitor_enabled
        self.buffer_size = buffer_size

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # Device selection group
        group = QGroupBox("Устройства ввода и вывода звука")
        grid = QGridLayout(group)
        grid.setSpacing(12)

        # 1. Microphone Input
        grid.addWidget(QLabel("Микрофон (Вход):"), 0, 0)
        self.in_combo = QComboBox()
        self.input_devices = get_input_devices()
        in_idx_to_select = 0
        for i, dev in enumerate(self.input_devices):
            self.in_combo.addItem(dev.display_name, dev.index)
            if dev.index == self.input_id:
                in_idx_to_select = i
        if self.input_devices:
            self.in_combo.setCurrentIndex(in_idx_to_select)
        grid.addWidget(self.in_combo, 0, 1)

        # 2. Main Output (Virtual Cable / Game / Discord)
        grid.addWidget(QLabel("Вывод (Virtual Cable / Discord):"), 1, 0)
        self.out_combo = QComboBox()
        self.output_devices = get_output_devices()
        out_idx_to_select = 0
        for i, dev in enumerate(self.output_devices):
            self.out_combo.addItem(dev.display_name, dev.index)
            if dev.index == self.output_id:
                out_idx_to_select = i
        if self.output_devices:
            self.out_combo.setCurrentIndex(out_idx_to_select)
        grid.addWidget(self.out_combo, 1, 1)

        # 3. Monitor Output (Headphones)
        grid.addWidget(QLabel("Мониторинг (Наушники):"), 2, 0)
        self.mon_combo = QComboBox()
        mon_idx_to_select = 0
        for i, dev in enumerate(self.output_devices):
            self.mon_combo.addItem(dev.display_name, dev.index)
            if dev.index == self.monitor_id:
                mon_idx_to_select = i
        if self.output_devices:
            self.mon_combo.setCurrentIndex(mon_idx_to_select)
        grid.addWidget(self.mon_combo, 2, 1)

        # 4. Hear myself check
        self.hear_myself_check = QCheckBox("Слышать свой голос в реальном времени (Мониторинг)")
        self.hear_myself_check.setChecked(self.monitor_enabled)
        grid.addWidget(self.hear_myself_check, 3, 0, 1, 2)

        # 5. Buffer Size / Latency
        grid.addWidget(QLabel("Буфер (Задержка):"), 4, 0)
        self.buf_combo = QComboBox()
        self.buf_combo.addItem("512 сэмплов (~11.6 мс, ультра-низкая задержка)", 512)
        self.buf_combo.addItem("1024 сэмплов (~23.2 мс, сбалансировано)", 1024)
        self.buf_combo.addItem("2048 сэмплов (~46.4 мс, макс. стабильность)", 2048)
        
        for idx in range(self.buf_combo.count()):
            if self.buf_combo.itemData(idx) == self.buffer_size:
                self.buf_combo.setCurrentIndex(idx)
                break
        grid.addWidget(self.buf_combo, 4, 1)

        layout.addWidget(group)

        # Admin status section
        admin_group = QGroupBox("Права администратора")
        admin_layout = QHBoxLayout(admin_group)
        
        has_admin = is_admin()
        status_text = "Приложение запущено с правами Администратора." if has_admin else "Приложение запущено с обычными правами."
        admin_lbl = QLabel(status_text)
        admin_layout.addWidget(admin_lbl)

        if not has_admin:
            btn_elevate = QPushButton("Перезапустить от имени Администратора")
            btn_elevate.clicked.connect(self._restart_admin)
            admin_layout.addWidget(btn_elevate)

        layout.addWidget(admin_group)

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

    def _restart_admin(self):
        try:
            restart_as_admin()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось повысить права: {e}")

    def _save_and_apply(self):
        self.input_id = self.in_combo.currentData()
        self.output_id = self.out_combo.currentData()
        self.monitor_id = self.mon_combo.currentData()
        self.monitor_enabled = self.hear_myself_check.isChecked()
        self.buffer_size = self.buf_combo.currentData()
        self.accept()
