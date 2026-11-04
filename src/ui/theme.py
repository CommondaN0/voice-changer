"""
Dark and Light themes for PySide6 application with modern sleek styling.
"""

DARK_THEME_QSS = """
QMainWindow, QDialog {
    background-color: #0f1117;
    color: #e2e8f0;
    font-family: 'Segoe UI', Arial, sans-serif;
}

QWidget {
    color: #e2e8f0;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #1e2230;
    background-color: #161922;
    border-radius: 8px;
    top: -1px;
}

QTabBar::tab {
    background-color: #0f1117;
    color: #94a3b8;
    padding: 10px 22px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    border: 1px solid #1e2230;
    border-bottom: none;
    font-weight: 600;
}

QTabBar::tab:selected {
    background-color: #161922;
    color: #818cf8;
    border-top: 2px solid #6366f1;
}

QTabBar::tab:hover:!selected {
    background-color: #1a1e2b;
    color: #cbd5e1;
}

/* Buttons */
QPushButton {
    background-color: #1e2230;
    color: #e2e8f0;
    border: 1px solid #2d3348;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #272d40;
    border-color: #6366f1;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #1b1f2e;
}

/* Master Voice Toggle Button */
QPushButton#MasterToggleButton {
    background-color: #1e293b;
    color: #94a3b8;
    border: 2px solid #334155;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 700;
    padding: 14px;
}

QPushButton#MasterToggleButton:hover {
    border-color: #6366f1;
    color: #e2e8f0;
}

QPushButton#MasterToggleButton[active="true"] {
    background-color: #4f46e5;
    color: #ffffff;
    border: 2px solid #818cf8;
}

/* Test Button */
QPushButton#TestButton {
    background-color: #1e2230;
    color: #94a3b8;
    border: 2px solid #2d3348;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 700;
    padding: 10px;
}

QPushButton#TestButton:hover {
    border-color: #10b981;
    color: #e2e8f0;
}

QPushButton#TestButton[active="true"] {
    background-color: #065f46;
    color: #ffffff;
    border: 2px solid #10b981;
}

/* Group Boxes and Panels */
QGroupBox {
    background-color: #161922;
    border: 1px solid #1e2230;
    border-radius: 8px;
    margin-top: 24px;
    padding-top: 16px;
    font-weight: 600;
    color: #818cf8;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    padding: 0 6px;
    color: #818cf8;
}

/* Sliders */
QSlider::groove:horizontal {
    height: 6px;
    background: #1e2230;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #6366f1;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #ffffff;
    border: 2px solid #6366f1;
    width: 16px;
    margin-top: -6px;
    margin-bottom: -6px;
    border-radius: 9px;
}

QSlider::handle:horizontal:hover {
    background: #818cf8;
    border-color: #ffffff;
}

/* ComboBox */
QComboBox {
    background-color: #161922;
    border: 1px solid #2d3348;
    border-radius: 6px;
    padding: 6px 12px;
    color: #e2e8f0;
}

QComboBox:hover {
    border-color: #6366f1;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid #2d3348;
}

QComboBox QAbstractItemView {
    background-color: #161922;
    color: #e2e8f0;
    selection-background-color: #4f46e5;
    selection-color: #ffffff;
    border: 1px solid #2d3348;
}

/* Preset Cards */
QPushButton.PresetCard {
    background-color: #161922;
    border: 2px solid #1e2230;
    border-radius: 10px;
    padding: 14px;
    text-align: center;
    font-weight: 600;
    color: #cbd5e1;
}

QPushButton.PresetCard:hover {
    border-color: #4f46e5;
    background-color: #1b1f2e;
}

QPushButton.PresetCard[selected="true"] {
    border: 2px solid #6366f1;
    background-color: #1e1b4b;
    color: #ffffff;
}

/* Admin Banner */
QFrame#AdminBanner {
    background-color: #2e1d0f;
    border: 1px solid #d97706;
    border-radius: 6px;
    padding: 6px 12px;
}
"""

LIGHT_THEME_QSS = """
QMainWindow, QDialog {
    background-color: #f1f5f9;
    color: #0f172a;
    font-family: 'Segoe UI', Arial, sans-serif;
}

QWidget {
    color: #0f172a;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #cbd5e1;
    background-color: #ffffff;
    border-radius: 8px;
    top: -1px;
}

QTabBar::tab {
    background-color: #f1f5f9;
    color: #64748b;
    padding: 10px 22px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    border: 1px solid #cbd5e1;
    border-bottom: none;
    font-weight: 600;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #4f46e5;
    border-top: 2px solid #4f46e5;
}

QTabBar::tab:hover:!selected {
    background-color: #e2e8f0;
    color: #334155;
}

/* Buttons */
QPushButton {
    background-color: #e2e8f0;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #cbd5e1;
    border-color: #4f46e5;
    color: #0f172a;
}

QPushButton:pressed {
    background-color: #94a3b8;
}

/* Master Voice Toggle Button */
QPushButton#MasterToggleButton {
    background-color: #e2e8f0;
    color: #475569;
    border: 2px solid #cbd5e1;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 700;
    padding: 14px;
}

QPushButton#MasterToggleButton:hover {
    border-color: #4f46e5;
    color: #0f172a;
}

QPushButton#MasterToggleButton[active="true"] {
    background-color: #4f46e5;
    color: #ffffff;
    border: 2px solid #3730a3;
}

/* Test Button */
QPushButton#TestButton {
    background-color: #1e2230;
    color: #94a3b8;
    border: 2px solid #2d3348;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 700;
    padding: 10px;
}

QPushButton#TestButton:hover {
    border-color: #10b981;
    color: #e2e8f0;
}

QPushButton#TestButton[active="true"] {
    background-color: #065f46;
    color: #ffffff;
    border: 2px solid #10b981;
}

/* Group Boxes and Panels */
QGroupBox {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    margin-top: 24px;
    padding-top: 16px;
    font-weight: 600;
    color: #4f46e5;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    padding: 0 6px;
    color: #4f46e5;
}

/* Sliders */
QSlider::groove:horizontal {
    height: 6px;
    background: #e2e8f0;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #4f46e5;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #ffffff;
    border: 2px solid #4f46e5;
    width: 16px;
    margin-top: -6px;
    margin-bottom: -6px;
    border-radius: 9px;
}

QSlider::handle:horizontal:hover {
    background: #6366f1;
    border-color: #3730a3;
}

/* ComboBox */
QComboBox {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 6px 12px;
    color: #0f172a;
}

QComboBox:hover {
    border-color: #4f46e5;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid #cbd5e1;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #0f172a;
    selection-background-color: #4f46e5;
    selection-color: #ffffff;
    border: 1px solid #cbd5e1;
}

/* Preset Cards */
QPushButton.PresetCard {
    background-color: #ffffff;
    border: 2px solid #e2e8f0;
    border-radius: 10px;
    padding: 14px;
    text-align: center;
    font-weight: 600;
    color: #334155;
}

QPushButton.PresetCard:hover {
    border-color: #4f46e5;
    background-color: #f8fafc;
}

QPushButton.PresetCard[selected="true"] {
    border: 2px solid #4f46e5;
    background-color: #e0e7ff;
    color: #312e81;
}

/* Admin Banner */
QFrame#AdminBanner {
    background-color: #fef3c7;
    border: 1px solid #f59e0b;
    border-radius: 6px;
    padding: 6px 12px;
}
"""


def apply_theme(app, is_dark: bool = True):
    """Applies either dark or light QSS style sheet to the QApplication."""
    qss = DARK_THEME_QSS if is_dark else LIGHT_THEME_QSS
    app.setStyleSheet(qss)
