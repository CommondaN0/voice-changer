"""
System tray integration using QSystemTrayIcon.
"""
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtCore import Qt, Signal, QObject

from src.utils.admin import restart_app


def create_tray_icon_pixmap(active: bool = False) -> QPixmap:
    """Generates a clean programmatic icon for system tray."""
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Circle background
    bg_color = QColor(99, 102, 241) if active else QColor(71, 85, 105)
    painter.setBrush(bg_color)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(2, 2, 28, 28)

    # Microphone shape
    painter.setBrush(QColor(255, 255, 255))
    painter.drawRoundedRect(12, 7, 8, 12, 4, 4)

    # Base arc
    painter.setPen(QColor(255, 255, 255))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawArc(9, 11, 14, 12, 0, -180 * 16)
    painter.drawLine(16, 23, 16, 26)
    painter.drawLine(12, 26, 20, 26)
    
    painter.end()
    return pixmap


class AppTrayIcon(QSystemTrayIcon):
    toggle_requested = Signal()
    settings_requested = Signal()
    show_window_requested = Signal()
    exit_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_active = False

        self.update_icon(False)
        self._build_menu()

        self.activated.connect(self._on_tray_activated)

    def update_icon(self, is_active: bool):
        self.is_active = is_active
        pixmap = create_tray_icon_pixmap(is_active)
        self.setIcon(QIcon(pixmap))
        self.setToolTip(f"Voice Changer ({'ВКЛЮЧЕН' if is_active else 'ВЫКЛЮЧЕН'})")
        if hasattr(self, 'toggle_action'):
            self.toggle_action.setText("Выключить изменение голоса" if is_active else "Включить изменение голоса")

    def _build_menu(self):
        menu = QMenu()
        
        self.status_action = menu.addAction("Voice Changer")
        self.status_action.setEnabled(False)
        menu.addSeparator()

        self.toggle_action = menu.addAction("Включить изменение голоса")
        self.toggle_action.triggered.connect(lambda: self.toggle_requested.emit())

        show_act = menu.addAction("Открыть окно")
        show_act.triggered.connect(lambda: self.show_window_requested.emit())

        settings_act = menu.addAction("Настройки")
        settings_act.triggered.connect(lambda: self.settings_requested.emit())

        menu.addSeparator()

        restart_act = menu.addAction("Перезапустить программу")
        restart_act.triggered.connect(restart_app)

        exit_act = menu.addAction("Выход")
        exit_act.triggered.connect(lambda: self.exit_requested.emit())

        self.setContextMenu(menu)

    def _on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self.show_window_requested.emit()
