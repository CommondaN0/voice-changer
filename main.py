"""
Voice Changer Application Entry Point.
"""
import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from PySide6.QtWidgets import QApplication

from src.audio.engine import AudioEngine
from src.ui.main_window import MainWindow
from src.ui.theme import apply_theme


def main():
    # Setup QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Voice Changer Pro")
    app.setQuitOnLastWindowClosed(False)  # Allows running in tray

    # Apply initial modern Dark theme
    apply_theme(app, is_dark=True)

    # Initialize low-latency audio engine (48 kHz standard for modern Windows WASAPI)
    engine = AudioEngine(sample_rate=48000, block_size=1024)

    # Launch GUI
    window = MainWindow(engine=engine, is_dark_theme=True)
    window.show()

    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
