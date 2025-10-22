from importlib import import_module


def get_pyside_availability() -> bool:
    try:
        import_module("PySide6")
        return True
    except ImportError:
        print("[ERROR] PySide6 aka QT for Python is not available.")
        return False


def start_qt_gui():
    if not get_pyside_availability():
        return
