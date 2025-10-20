from json import load
import os
import sys
import platform
import atexit
import signal

# Qt platform plugin detection (fixes #59)
try:
    from PyQt5.QtCore import QLibraryInfo
    plugins = QLibraryInfo.location(QLibraryInfo.PluginsPath)
    # Normalize path to use the OS-native separators and absolute path
    platform_dir = os.path.normpath(os.path.join(plugins, "platforms"))
    # Ensure we work with an absolute path for clarity
    platform_dir = os.path.abspath(platform_dir)
    if os.path.isdir(platform_dir):
        os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = platform_dir
        print("QT_QPA_PLATFORM_PLUGIN_PATH set to:", platform_dir)
    else:
        print("PyQt5 platform plugins not found at", platform_dir)
except ImportError:
    print("PyQt5 not installed.")

# Set application ID for Windows taskbar icon
if platform.system() == "Windows":
    try:
        from abogen.constants import PROGRAM_NAME, VERSION
        import ctypes
        app_id = f"{PROGRAM_NAME}.{VERSION}"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except Exception as e:
        print("Warning: failed to set AppUserModelID:", e)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import qInstallMessageHandler, QtMsgType

# Add the directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from abogen.utils import get_resource_path, load_config, prevent_sleep_end

# Set Hugging Face Hub environment variables
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"  # Disable Hugging Face telemetry
os.environ["HF_HUB_ETAG_TIMEOUT"] = "10"  # Metadata request timeout (seconds)
os.environ["HF_HUB_DOWNLOAD_TIMEOUT"] = "10"  # File download timeout (seconds)
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"  # Disable symlinks warning
if load_config().get("disable_kokoro_internet", False):
    print("INFO: Kokoro's internet access is disabled.")
    os.environ["HF_HUB_OFFLINE"] = "1"  # Disable Hugging Face Hub internet access

from abogen.gui import abogen
from abogen.constants import PROGRAM_NAME, VERSION

# Set environment variables for AMD ROCm
os.environ["MIOPEN_FIND_MODE"] = "FAST"
os.environ["MIOPEN_CONV_PRECISE_ROCM_TUNING"] = "0"

# Reset sleep states
atexit.register(prevent_sleep_end)


# Also handle signals (Ctrl+C, kill, etc.)
def _cleanup_sleep(signum, frame):
    prevent_sleep_end()
    sys.exit(0)


signal.signal(signal.SIGINT, _cleanup_sleep)
signal.signal(signal.SIGTERM, _cleanup_sleep)

# Ensure sys.stdout and sys.stderr are valid in GUI mode
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

# Enable MPS GPU acceleration on Mac Apple Silicon
if platform.system() == "Darwin" and platform.processor() == "arm":
    os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"


# Custom message handler to filter out specific Qt warnings
def qt_message_handler(mode, context, message):
    if "Wayland does not support QWindow::requestActivate()" in message:
        return  # Suppress this specific message
    if "setGrabPopup called with a parent, QtWaylandClient" in message:
        return
    if mode == QtMsgType.QtWarningMsg:
        print(f"Qt Warning: {message}")
    elif mode == QtMsgType.QtCriticalMsg:
        print(f"Qt Critical: {message}")
    elif mode == QtMsgType.QtFatalMsg:
        print(f"Qt Fatal: {message}")
    elif mode == QtMsgType.QtInfoMsg:
        print(f"Qt Info: {message}")


# Install the custom message handler
qInstallMessageHandler(qt_message_handler)

# Handle Wayland on Linux GNOME
if platform.system() == "Linux":
    xdg_session = os.environ.get("XDG_SESSION_TYPE", "").lower()
    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    if (
        "gnome" in desktop
        and xdg_session == "wayland"
        and "QT_QPA_PLATFORM" not in os.environ
    ):
        os.environ["QT_QPA_PLATFORM"] = "wayland"


def main():
    """Main entry point for console usage."""
    app = QApplication(sys.argv)

    # Set application icon using get_resource_path from utils
    icon_path = get_resource_path("abogen.assets", "icon.ico")
    if icon_path:
        app.setWindowIcon(QIcon(icon_path))

    # Set the .desktop name on Linux
    if platform.system() == "Linux":
        try:
            app.setDesktopFileName("abogen.desktop")
        except AttributeError:
            pass

    ex = abogen()
    ex.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
