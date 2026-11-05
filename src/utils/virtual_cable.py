"""
Helper to check and silently install VB-Audio Virtual Cable driver.
Uses bundled signed driver files and silent installation via Windows UAC.
"""
import os
import sys
import ctypes
from ctypes import wintypes

from src.audio.devices import find_virtual_cable_output


class _SHELLEXECUTEINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("fMask", wintypes.ULONG),
        ("hwnd", wintypes.HWND),
        ("lpVerb", wintypes.LPCWSTR),
        ("lpFile", wintypes.LPCWSTR),
        ("lpParameters", wintypes.LPCWSTR),
        ("lpDirectory", wintypes.LPCWSTR),
        ("nShow", ctypes.c_int),
        ("hInstApp", wintypes.HINSTANCE),
        ("lpIDList", wintypes.LPVOID),
        ("lpClass", wintypes.LPCWSTR),
        ("hkeyClass", wintypes.HKEY),
        ("dwHotKey", wintypes.DWORD),
        ("hIconOrMonitor", wintypes.HANDLE),
        ("hProcess", wintypes.HANDLE)
    ]


SEE_MASK_NOCLOSEPROCESS = 0x00000040


def get_driver_dir() -> str:
    """Returns absolute path to local drivers/vbcable directory."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "drivers", "vbcable"))


def is_driver_package_available() -> bool:
    """Checks if bundled driver files are present in drivers/vbcable."""
    d = get_driver_dir()
    if not os.path.isdir(d):
        return False
    inf = get_driver_inf_path()
    setup = get_driver_setup_exe()
    return (inf is not None and os.path.exists(inf)) or (setup is not None and os.path.exists(setup))


def get_driver_inf_path() -> str | None:
    """Returns path to .inf file matching current system architecture."""
    d = get_driver_dir()
    is_64bit = sys.maxsize > 2**32
    inf_name = "vbMmeCable64_win7.inf" if is_64bit else "vbMmeCable_win7.inf"
    path = os.path.join(d, inf_name)
    return path if os.path.exists(path) else None


def get_driver_setup_exe() -> str | None:
    """Returns path to setup executable matching current system architecture."""
    d = get_driver_dir()
    is_64bit = sys.maxsize > 2**32
    exe_name = "VBCABLE_Setup_x64.exe" if is_64bit else "VBCABLE_Setup.exe"
    path = os.path.join(d, exe_name)
    return path if os.path.exists(path) else None


def is_virtual_cable_installed() -> bool:
    """Checks if VB-Audio Virtual Cable is already available in Windows."""
    return find_virtual_cable_output() is not None


def _run_elevated_wait(executable: str, params: str, working_dir: str, timeout_ms: int = 30000) -> bool:
    """
    Executes a program with elevated privileges (UAC) and waits for completion.
    Returns True if completed successfully, False if cancelled by user or timed out.
    """
    sei = _SHELLEXECUTEINFO()
    sei.cbSize = ctypes.sizeof(_SHELLEXECUTEINFO)
    sei.fMask = SEE_MASK_NOCLOSEPROCESS
    sei.hwnd = None
    sei.lpVerb = "runas"
    sei.lpFile = executable
    sei.lpParameters = params
    sei.lpDirectory = working_dir
    sei.nShow = 0  # SW_HIDE

    if not ctypes.windll.shell32.ShellExecuteExW(ctypes.byref(sei)):
        return False

    if sei.hProcess:
        try:
            res = ctypes.windll.kernel32.WaitForSingleObject(sei.hProcess, timeout_ms)
            ctypes.windll.kernel32.CloseHandle(sei.hProcess)
            return res == 0  # WAIT_OBJECT_0
        except Exception:
            return True
    return True


def install_driver_silent() -> tuple[bool, str]:
    """
    Installs the Virtual Cable driver silently without any GUI windows.
    Prompts standard Windows UAC confirmation once.
    Returns (success, message).
    """
    if is_virtual_cable_installed():
        return True, "Виртуальный аудиокабель уже установлен в системе."

    driver_dir = get_driver_dir()
    setup_exe = get_driver_setup_exe()
    inf_path = get_driver_inf_path()

    # 1. Primary: Silent installation via bundled official driver installer (-i -h)
    if setup_exe and os.path.exists(setup_exe):
        try:
            ok = _run_elevated_wait(setup_exe, "-i -h", driver_dir, timeout_ms=35000)
            if ok:
                return True, "Установка драйвера выполнена."
            else:
                return False, "Установка была отменена пользователем (отклонен запрос UAC)."
        except Exception as e:
            pass

    # 2. Fallback: via Windows pnputil.exe
    if inf_path and os.path.exists(inf_path):
        try:
            cmd = f'pnputil.exe /add-driver "{inf_path}" /install'
            ok = _run_elevated_wait("cmd.exe", f"/c {cmd}", driver_dir, timeout_ms=30000)
            if ok:
                return True, "Драйвер добавлен в систему через pnputil."
            else:
                return False, "Установка через pnputil отменена пользователем."
        except Exception as e:
            return False, f"Ошибка при установке через pnputil: {e}"

    return False, "Файлы драйвера не найдены в каталоге drivers/vbcable."


def uninstall_driver_silent() -> tuple[bool, str]:
    """Silently uninstalls the driver."""
    driver_dir = get_driver_dir()
    setup_exe = get_driver_setup_exe()
    if setup_exe and os.path.exists(setup_exe):
        try:
            ok = _run_elevated_wait(setup_exe, "-u -h", driver_dir, timeout_ms=30000)
            if ok:
                return True, "Удаление драйвера завершено."
            return False, "Отклонен запрос администратора."
        except Exception as e:
            return False, str(e)
    return False, "Установщик драйвера не найден."
