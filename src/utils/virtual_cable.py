"""
Helper to check, locate and install VB-Audio Virtual Cable driver.
"""
import os
import sys
import glob
import tempfile
import zipfile
import ctypes
import webbrowser

from src.audio.devices import find_virtual_cable_output


VB_CABLE_PAGE = "https://vb-audio.com/Cable/"


def is_virtual_cable_installed() -> bool:
    """Checks if VB-Audio Virtual Cable is already available in Windows."""
    return find_virtual_cable_output() is not None


def open_download_page():
    """Opens official VB-CABLE download page in user's default browser."""
    webbrowser.open(VB_CABLE_PAGE)


def find_downloaded_setup() -> str | None:
    """
    Looks for downloaded VBCABLE archive or setup executable in Downloads folder or Temp.
    Returns path to setup.exe or zip if found.
    """
    user_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
    temp_dir = tempfile.gettempdir()
    
    search_dirs = [user_downloads, temp_dir]
    for d in search_dirs:
        if not os.path.exists(d):
            continue
        
        # Check for extracted setup exe
        exe_matches = glob.glob(os.path.join(d, "**", "VBCABLE_Setup_x64.exe"), recursive=True)
        if exe_matches:
            return exe_matches[0]
        
        # Check for zip archive
        zip_matches = glob.glob(os.path.join(d, "*VBCABLE*.zip"))
        if zip_matches:
            return zip_matches[0]

    return None


def run_installer_from_path(path: str):
    """
    Runs installer from given .exe or extracts from .zip and launches as Admin.
    """
    if path.lower().endswith(".zip"):
        extract_dir = os.path.join(tempfile.gettempdir(), "VBCABLE_Setup")
        os.makedirs(extract_dir, exist_ok=True)
        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        is_64bit = sys.maxsize > 2**32
        exe_name = "VBCABLE_Setup_x64.exe" if is_64bit else "VBCABLE_Setup.exe"
        setup_exe = os.path.join(extract_dir, exe_name)
    else:
        setup_exe = path
        extract_dir = os.path.dirname(path)

    if not os.path.exists(setup_exe):
        raise FileNotFoundError(f"Исполняемый файл установщика не найден: {setup_exe}")

    ret = ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        setup_exe,
        "",
        extract_dir,
        1
    )
    if ret <= 32:
        raise RuntimeError("Установка была отменена пользователем или отклонена UAC.")
