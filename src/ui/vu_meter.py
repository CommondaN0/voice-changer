"""
Custom VU Meter Widget for real-time audio level monitoring.
"""
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QLinearGradient
from PySide6.QtCore import Qt, QTimer


class VUMeter(QWidget):
    def __init__(self, parent=None, title: str = "MIC"):
        super().__init__(parent)
        self.title = title
        self.level: float = 0.0
        self.peak: float = 0.0
        self.setMinimumHeight(16)
        self.setMinimumWidth(80)

        # Decay timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._decay)
        self.timer.start(30)

    def set_level(self, level: float):
        self.level = max(0.0, min(1.0, level))
        if self.level > self.peak:
            self.peak = self.level
        self.update()

    def _decay(self):
        self.level *= 0.88
        self.peak *= 0.96
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        # Background track
        painter.setBrush(QColor(30, 34, 48, 180))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, w, h, 4, 4)

        # Active Level Bar
        fill_width = int(w * self.level)
        if fill_width > 0:
            gradient = QLinearGradient(0, 0, w, 0)
            gradient.setColorAt(0.0, QColor(34, 197, 94))   # Green
            gradient.setColorAt(0.7, QColor(234, 179, 8))   # Yellow
            gradient.setColorAt(1.0, QColor(239, 68, 68))   # Red

            painter.setBrush(gradient)
            painter.drawRoundedRect(0, 0, fill_width, h, 4, 4)

        # Peak indicator line
        peak_x = int(w * self.peak)
        if peak_x > 0 and peak_x < w:
            painter.setPen(QColor(255, 255, 255, 220))
            painter.drawLine(peak_x, 1, peak_x, h - 2)
