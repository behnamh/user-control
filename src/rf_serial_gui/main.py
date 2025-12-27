"""Application entry point for RF Serial Controller."""

import platform

try:
    # When running as package
    from .serial_handler import SerialHandler
    from .gui import RFSerialGUI
except ImportError:
    # When running as standalone script or PyInstaller executable
    from serial_handler import SerialHandler
    from gui import RFSerialGUI


def main() -> None:
    """Initialize and run the RF Serial Controller application."""
    # Create serial handler with status callback
    serial_handler = SerialHandler()

    # Create GUI with serial handler
    gui = RFSerialGUI(serial_handler)

    # Set up status callback to update GUI
    serial_handler._status_callback = gui.on_status_change

    # On non-Windows systems, attempt initial connection automatically
    # On Windows, user will select port from dropdown and click Connect
    if platform.system() != "Windows":
        serial_handler.connect()

    # Update GUI with connection status
    gui._update_connection_display()

    # Start the application
    gui.run()


if __name__ == "__main__":
    main()
