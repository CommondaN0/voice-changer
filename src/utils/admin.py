"""
Utilities for checking Windows administrator privileges and application elevation/restart.
"""
import ctypes
import os
import sys


def is_admin() -> bool:
    """Returns True if current process has Administrator privileges."""
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def restart_as_admin():
    """
    Relaunches the current application requesting Administrator privileges via Windows UAC.
    """
    if is_admin():
        return

    # ShellExecuteW runas command
    executable = sys.executable
    params = " ".join([f'"{arg}"' for arg in sys.argv])
    cwd = os.getcwd()

    ret = ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        executable,
        params,
        cwd,
        1  # SW_SHOWNORMAL
    )
    if ret > 32:
        # Success, exit this process
        sys.exit(0)
    else:
        raise RuntimeError(f"Elevation request declined or failed with code {ret}")


def restart_app():
    """Restarts the application normally without changing privileges."""
    executable = sys.executable
    params = [executable] + sys.argv
    os.execv(executable, params)
