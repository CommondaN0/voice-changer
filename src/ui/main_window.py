"""
Main Application Window for Voice Changer.
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QTabWidget, QFrame, QMessageBox, QApplication,
    QSystemTrayIcon
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCloseEvent

from src.audio.engine import AudioEngine
from src.audio.devices import find_default_device, find_virtual_cable_output
from src.dsp.presets import VoiceParams
from src.ui.tabs_presets import PresetsTab
from src.ui.tabs_advanced import AdvancedTab
from src.ui.dialog_settings import SettingsDialog
from src.ui.vu_meter import VUMeter
from src.ui.theme import apply_theme
from src.utils.admin import is_admin, restart_as_admin
from src.utils.virtual_cable import (
    is_virtual_cable_installed, open_download_page, 
    find_downloaded_setup, run_installer_from_path
)
from src.utils.tray import AppTrayIcon


class MainWindow(QMainWindow):
    def __init__(self, engine: AudioEngine, is_dark_theme: bool = True):
        super().__init__()
        self.engine = engine
        self.is_dark_theme = is_dark_theme
        self.is_voice_changing_active = False
        self.is_test_active = False

        self.setWindowTitle("Voice Changer Pro - Изменение голоса в реальном времени")
        self.resize(800, 700)

        # Tray Icon
        self.tray = AppTrayIcon(self)
        self.tray.toggle_requested.connect(self._toggle_voice_changing)
        self.tray.settings_requested.connect(self._open_settings)
        self.tray.show_window_requested.connect(self._show_window)
        self.tray.exit_requested.connect(self._force_exit)
        self.tray.show()

        self._init_ui()
        self._init_audio()

        # Timer for VU Meters
        self.vu_timer = QTimer(self)
        self.vu_timer.timeout.connect(self._update_vu_meters)
        self.vu_timer.start(35)

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(18, 14, 18, 14)
        root_layout.setSpacing(12)

        # 1. Admin Banner (if not admin)
        if not is_admin():
            self.admin_banner = QFrame()
            self.admin_banner.setObjectName("AdminBanner")
            banner_layout = QHBoxLayout(self.admin_banner)
            banner_layout.setContentsMargins(10, 6, 10, 6)
            
            warn_lbl = QLabel("⚠️ Запущено с обычными правами. Для надежного перехвата клавиш в играх рекомендуется запуск от имени администратора.")
            warn_lbl.setStyleSheet("color: #d97706; font-size: 12px; font-weight: 500;")
            banner_layout.addWidget(warn_lbl)
            
            btn_restart_admin = QPushButton("Перезапустить от Администратора")
            btn_restart_admin.setStyleSheet("background-color: #d97706; color: white; padding: 4px 10px; font-size: 11px;")
            btn_restart_admin.clicked.connect(self._restart_as_admin)
            banner_layout.addWidget(btn_restart_admin)
            
            root_layout.addWidget(self.admin_banner)

        # 2. Virtual Cable Notice (if cable not installed)
        if not is_virtual_cable_installed():
            self.cable_banner = QFrame()
            self.cable_banner.setObjectName("AdminBanner")
            c_layout = QHBoxLayout(self.cable_banner)
            c_layout.setContentsMargins(10, 6, 10, 6)
            
            c_lbl = QLabel("ℹ️ Виртуальный аудиокабель не обнаружен. Установите его, чтобы голос менялся в Discord и играх.")
            c_lbl.setStyleSheet("color: #0284c7; font-size: 12px; font-weight: 500;")
            c_layout.addWidget(c_lbl)

            btn_inst = QPushButton("Установить кабель в 1 клик")
            btn_inst.setStyleSheet("background-color: #0284c7; color: white; padding: 4px 10px; font-size: 11px;")
            btn_inst.clicked.connect(self._install_virtual_cable)
            c_layout.addWidget(btn_inst)

            root_layout.addWidget(self.cable_banner)

        # 3. Top Header Bar
        top_bar = QHBoxLayout()
        top_bar.setSpacing(12)

        # Master Toggle Button
        self.btn_master_toggle = QPushButton("ИЗМЕНИТЬ ГОЛОС: ВЫКЛ")
        self.btn_master_toggle.setObjectName("MasterToggleButton")
        self.btn_master_toggle.setProperty("active", "false")
        self.btn_master_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_master_toggle.setMinimumHeight(54)
        self.btn_master_toggle.clicked.connect(self._toggle_voice_changing)
        top_bar.addWidget(self.btn_master_toggle, stretch=2)

        # Theme Switcher Button
        self.btn_theme = QPushButton("☀️ Светлая" if self.is_dark_theme else "🌙 Тёмная")
        self.btn_theme.setMinimumHeight(54)
        self.btn_theme.clicked.connect(self._toggle_theme)
        top_bar.addWidget(self.btn_theme)

        # Settings Button
        btn_settings = QPushButton("⚙️ Настройки")
        btn_settings.setMinimumHeight(54)
        btn_settings.clicked.connect(self._open_settings)
        top_bar.addWidget(btn_settings)

        root_layout.addLayout(top_bar)

        # 4. Audio Level VU Meters
        vu_box = QHBoxLayout()
        vu_box.setSpacing(16)

        mic_layout = QVBoxLayout()
        mic_lbl = QLabel("Входной уровень (Микрофон):")
        mic_lbl.setStyleSheet("font-size: 11px; color: #94a3b8;")
        self.mic_vu = VUMeter(title="Вход")
        mic_layout.addWidget(mic_lbl)
        mic_layout.addWidget(self.mic_vu)

        out_layout = QVBoxLayout()
        out_lbl = QLabel("Выходной уровень (Измененный голос):")
        out_lbl.setStyleSheet("font-size: 11px; color: #94a3b8;")
        self.out_vu = VUMeter(title="Выход")
        out_layout.addWidget(out_lbl)
        out_layout.addWidget(self.out_vu)

        vu_box.addLayout(mic_layout)
        vu_box.addLayout(out_layout)
        root_layout.addLayout(vu_box)

        # 5. Central Tabs
        self.tabs = QTabWidget()
        
        self.presets_tab = PresetsTab()
        self.presets_tab.params_changed.connect(self._on_params_changed)
        self.tabs.addTab(self.presets_tab, " Готовые пресеты ")

        self.advanced_tab = AdvancedTab()
        self.advanced_tab.params_changed.connect(self._on_params_changed)
        self.tabs.addTab(self.advanced_tab, " Для продвинутых пользователей ")

        root_layout.addWidget(self.tabs, stretch=1)

        # 6. Bottom Test Bar ("Слышать себя")
        bottom_bar = QHBoxLayout()
        bottom_bar.setSpacing(12)

        self.btn_test = QPushButton("🎧 ТЕСТ: Слышать себя (ВЫКЛ)")
        self.btn_test.setObjectName("TestButton")
        self.btn_test.setProperty("active", "false")
        self.btn_test.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_test.setMinimumHeight(46)
        self.btn_test.clicked.connect(self._toggle_test_mode)
        bottom_bar.addWidget(self.btn_test, stretch=2)

        lbl_test_hint = QLabel("Нажмите «Тест», чтобы услышать свой измененный голос в наушниках для проверки.")
        lbl_test_hint.setStyleSheet("font-size: 11px; color: #94a3b8;")
        lbl_test_hint.setWordWrap(True)
        bottom_bar.addWidget(lbl_test_hint, stretch=3)

        root_layout.addLayout(bottom_bar)

    def _init_audio(self):
        """Initializes default devices and starts audio engine."""
        def_in = find_default_device(is_input=True)
        def_headphone = find_default_device(is_input=False)
        cable_out = find_virtual_cable_output()

        in_id = def_in.index if def_in else None
        cable_id = cable_out.index if cable_out else None
        headphone_id = def_headphone.index if def_headphone else None

        try:
            self.engine.start(
                input_device_id=in_id,
                cable_output_device_id=cable_id,
                headphone_device_id=headphone_id
            )
        except Exception as e:
            QMessageBox.warning(
                self, 
                "Аудиоустройства", 
                f"Не удалось подключиться к аудиоустройствам: {e}\nПожалуйста, выберите микрофон в Настройках."
            )

    def _toggle_voice_changing(self):
        self.is_voice_changing_active = not self.is_voice_changing_active
        self.engine.set_voice_changing_enabled(self.is_voice_changing_active)
        
        # Update Master button
        if self.is_voice_changing_active:
            self.btn_master_toggle.setText("🔊 ИЗМЕНИТЬ ГОЛОС: ВКЛЮЧЕНО")
            self.btn_master_toggle.setProperty("active", "true")
        else:
            self.btn_master_toggle.setText("ИЗМЕНИТЬ ГОЛОС: ВЫКЛ")
            self.btn_master_toggle.setProperty("active", "false")

        self.btn_master_toggle.style().unpolish(self.btn_master_toggle)
        self.btn_master_toggle.style().polish(self.btn_master_toggle)

        # Update tray
        self.tray.update_icon(self.is_voice_changing_active)

    def _toggle_test_mode(self):
        """Toggles headphone test monitoring."""
        self.is_test_active = not self.is_test_active
        self.engine.set_test_mode(self.is_test_active)

        if self.is_test_active:
            self.btn_test.setText("🔊 ТЕСТ: Слышите себя (ВКЛЮЧЕНО)")
            self.btn_test.setProperty("active", "true")
        else:
            self.btn_test.setText("🎧 ТЕСТ: Слышать себя (ВЫКЛ)")
            self.btn_test.setProperty("active", "false")

        self.btn_test.style().unpolish(self.btn_test)
        self.btn_test.style().polish(self.btn_test)

    def _on_params_changed(self, params: VoiceParams):
        self.engine.set_params(params)

    def _update_vu_meters(self):
        self.mic_vu.set_level(self.engine.processor.input_level)
        self.out_vu.set_level(self.engine.processor.output_level)

    def _toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        apply_theme(QApplication.instance(), self.is_dark_theme)
        self.btn_theme.setText("☀️ Светлая" if self.is_dark_theme else "🌙 Тёмная")

    def _open_settings(self):
        dlg = SettingsDialog(
            current_input_id=self.engine.input_device_id,
            current_cable_id=self.engine.cable_output_device_id,
            current_headphone_id=self.engine.headphone_device_id,
            buffer_size=self.engine.block_size,
            parent=self
        )
        if dlg.exec():
            # Apply changes
            self.engine.block_size = dlg.buffer_size
            try:
                self.engine.start(
                    input_device_id=dlg.input_id,
                    cable_output_device_id=dlg.cable_id,
                    headphone_device_id=dlg.headphone_id
                )
            except Exception as e:
                QMessageBox.critical(self, "Ошибка аудио", f"Не удалось применить устройства: {e}")

    def _install_virtual_cable(self):
        found = find_downloaded_setup()
        if found:
            try:
                run_installer_from_path(found)
                QMessageBox.information(
                    self, 
                    "Установка запущена", 
                    "В появившемся окне нажмите 'Install Driver'. После установки перезапустите приложение."
                )
                return
            except Exception as e:
                QMessageBox.critical(self, "Ошибка запуска", f"Не удалось запустить установщик: {e}")

        # If not found locally, open official website
        QMessageBox.information(
            self, 
            "Установка виртуального кабеля", 
            "Сейчас откроется официальная страница VB-CABLE.\n1. Скачайте архив 'VBCABLE_Driver_Pack43.zip' (или Pack45)\n2. Распакуйте архив и запустите от администратора VBCABLE_Setup_x64.exe\n(или нажмите кнопку 'Запустить установщик' в программе)."
        )
        open_download_page()

    def _restart_as_admin(self):
        try:
            restart_as_admin()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось перезапустить: {e}")

    def _show_window(self):
        self.showNormal()
        self.activateWindow()

    def _force_exit(self):
        self.engine.stop()
        QApplication.quit()

    def closeEvent(self, event: QCloseEvent):
        if self.tray.isVisible():
            self.hide()
            self.tray.showMessage(
                "Voice Changer",
                "Приложение свернуто в системный трей и продолжает работать.",
                QSystemTrayIcon.MessageIcon.Information,
                1500
            )
            event.ignore()
        else:
            self.engine.stop()
            event.accept()
