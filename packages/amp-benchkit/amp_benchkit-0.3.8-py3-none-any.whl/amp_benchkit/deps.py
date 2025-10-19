"""Dependency detection and lightweight helper utilities.

This isolates environment probing logic from the main GUI script so that
further refactors can import these symbols without re-running detection
in multiple places.
"""

from __future__ import annotations

import io
import os
import sys
from contextlib import contextmanager

PYVISA_ERR = SERIAL_ERR = QT_ERR = U3_ERR = None  # populated on import
QT_BINDING = None

# Optional dependency placeholders
_pyvisa = None
_serial = None
_lp = None
_u3 = None
HAVE_U3 = False


@contextmanager
def _suppress_libusb_import_noise():
    """Silence noisy libusb messages when LabJackPython probes for devices."""

    saved_err_fd = None
    err_fd = None
    if os.name == "posix":
        try:
            err_fd = sys.stderr.fileno()
            saved_err_fd = os.dup(err_fd)
            with open(os.devnull, "w") as devnull:
                os.dup2(devnull.fileno(), err_fd)
        except (AttributeError, OSError, ValueError):
            err_fd = None
            saved_err_fd = None

    original_stdout = sys.stdout
    original_stderr = sys.stderr
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()
    try:
        yield
    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        if saved_err_fd is not None and err_fd is not None:
            os.dup2(saved_err_fd, err_fd)
            os.close(saved_err_fd)


# ------------------ pyvisa ------------------
try:  # pragma: no cover - environment dependent
    import pyvisa as _pyvisa  # type: ignore
except Exception as e:  # pragma: no cover
    PYVISA_ERR = e

# ------------------ pyserial ------------------
try:  # pragma: no cover
    import serial as _serial  # type: ignore
    import serial.tools.list_ports as _lp  # type: ignore
except Exception as e:  # pragma: no cover
    SERIAL_ERR = e

# ------------------ LabJack u3 ------------------
try:  # pragma: no cover
    with _suppress_libusb_import_noise():
        import u3 as _u3  # type: ignore[import-untyped,no-redef]

    HAVE_U3 = True
except Exception as e:  # pragma: no cover
    _u3 = None
    U3_ERR = e
    HAVE_U3 = False

# ------------------ Qt bindings ------------------
HAVE_QT = False
try:  # pragma: no cover
    from PySide6.QtCore import QLibraryInfo, Qt, QTimer
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import (
        QApplication,
        QCheckBox,
        QComboBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QProgressBar,
        QPushButton,
        QSpinBox,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    QT_BINDING = "PySide6"
    HAVE_QT = True
    try:
        try:
            # Qt 6.5+ prefers path()
            plugin_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.PluginsPath)  # type: ignore[attr-defined,union-attr]
        except AttributeError:  # pragma: no cover - backward compatibility
            plugin_path = QLibraryInfo.location(QLibraryInfo.LibraryPath.PluginsPath)  # type: ignore[attr-defined]
        if plugin_path:
            os.environ.setdefault(
                "QT_QPA_PLATFORM_PLUGIN_PATH", os.path.join(plugin_path, "platforms")
            )
    except Exception:
        pass
except Exception as e1:  # pragma: no cover
    try:
        from PyQt5.QtCore import QLibraryInfo, Qt, QTimer
        from PyQt5.QtGui import QFont
        from PyQt5.QtWidgets import (
            QApplication,
            QCheckBox,
            QComboBox,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QMainWindow,
            QProgressBar,
            QPushButton,
            QSpinBox,
            QTabWidget,
            QTextEdit,
            QVBoxLayout,
            QWidget,
        )

        QT_BINDING = "PyQt5"
        HAVE_QT = True
        try:
            plugin_path = QLibraryInfo.location(QLibraryInfo.PluginsPath)  # type: ignore[attr-defined]
            if plugin_path:
                os.environ.setdefault(
                    "QT_QPA_PLATFORM_PLUGIN_PATH", os.path.join(plugin_path, "platforms")
                )
        except Exception:
            pass
    except Exception as e2:  # pragma: no cover
        QT_ERR = (e1, e2)
        # wipe widget symbols so importing * from here can't accidentally use them
        (
            QApplication,  # type: ignore[assignment,misc]
            QMainWindow,  # type: ignore[assignment,misc]
            QWidget,  # type: ignore[assignment,misc]
            QTabWidget,  # type: ignore[assignment,misc]
            QVBoxLayout,  # type: ignore[assignment,misc]
            QHBoxLayout,  # type: ignore[assignment,misc]
            QLabel,  # type: ignore[assignment,misc]
            QLineEdit,  # type: ignore[assignment,misc]
            QComboBox,  # type: ignore[assignment,misc]
            QPushButton,  # type: ignore[assignment,misc]
            QTextEdit,  # type: ignore[assignment,misc]
            QProgressBar,  # type: ignore[assignment,misc]
            QCheckBox,  # type: ignore[assignment,misc]
            QSpinBox,  # type: ignore[assignment,misc]
            Qt,  # type: ignore[assignment,misc]
        ) = (None,) * 15

HAVE_PYVISA = _pyvisa is not None
HAVE_SERIAL = _serial is not None and _lp is not None

INSTALL_HINTS = {
    "pyvisa": "pip install pyvisa",
    "pyserial": "pip install pyserial",
    "pyside6": "pip install PySide6",
    "pyqt5": "pip install PyQt5",
    "u3": "pip install LabJackPython",
}


def fixed_font():  # pragma: no cover - trivial helper
    """Return a monospaced QFont if Qt is available.

    Extracted GUI tabs previously referenced a helper in the monolith; we provide
    a minimal version here to keep imports lightweight and tests headless-safe.
    """
    try:
        if HAVE_QT and "QFont" in globals():
            f = QFont("Courier New")  # type: ignore[misc]
            f.setStyleHint(QFont.TypeWriter)  # type: ignore[misc,attr-defined]
            return f
    except Exception:
        pass
    return None


def dep_msg() -> str:
    qt_str = f"Qt({QT_BINDING or 'none'})"
    return " | ".join(
        [
            f"pyvisa: {'OK' if HAVE_PYVISA else 'MISSING'}",
            f"pyserial: {'OK' if HAVE_SERIAL else 'MISSING'}",
            f"{qt_str}: {'OK' if HAVE_QT else 'MISSING'}",
            f"LabJack u3: {'OK' if HAVE_U3 else 'MISSING'}",
        ]
    )


def list_ports():  # pragma: no cover (depends on host hardware)
    return list(_lp.comports()) if HAVE_SERIAL else []


def find_fy_port():  # pragma: no cover (depends on host hardware)
    ps = list_ports()
    for p in ps:
        d = (p.device or "").lower()
        if any(k in d for k in ["usbserial", "tty.usb", "wchusb", "ftdi"]):
            return p.device
    return ps[0].device if ps else None


# Re-export Qt symbols so legacy code can transition gradually
__all__ = [
    "HAVE_PYVISA",
    "HAVE_SERIAL",
    "HAVE_QT",
    "HAVE_U3",
    "QT_BINDING",
    "QT_ERR",
    "PYVISA_ERR",
    "SERIAL_ERR",
    "U3_ERR",
    "dep_msg",
    "list_ports",
    "find_fy_port",
    "INSTALL_HINTS",
    "fixed_font",
    # Backwards compatibility exports (internal modules)
    "_pyvisa",
    "_serial",
    "_u3",
    # Qt symbols (may be None if unavailable)
    "QApplication",
    "QMainWindow",
    "QWidget",
    "QTabWidget",
    "QVBoxLayout",
    "QHBoxLayout",
    "QLabel",
    "QLineEdit",
    "QComboBox",
    "QPushButton",
    "QTextEdit",
    "QProgressBar",
    "QCheckBox",
    "QSpinBox",
    "Qt",
    "QTimer",
    "QFont",
]
