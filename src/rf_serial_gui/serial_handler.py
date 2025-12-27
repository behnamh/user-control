"""Serial port communication handler for RF transceiver."""

from enum import Enum
from typing import Callable

import serial
from serial import SerialException

try:
    from .config import SERIAL_PORT, BAUD_RATE, TIMEOUT, DATA_BITS, STOP_BITS, ENCODING
except ImportError:
    from config import SERIAL_PORT, BAUD_RATE, TIMEOUT, DATA_BITS, STOP_BITS, ENCODING


class ConnectionStatus(Enum):
    """Connection status states for the serial port."""
    DISCONNECTED = "Disconnected"
    CONNECTING = "Connecting..."
    CONNECTED = "Connected"
    ERROR = "Error"


class SerialHandler:
    """Handles serial port communication with the RF transceiver."""

    def __init__(self, port: str = SERIAL_PORT, baud_rate: int = BAUD_RATE,
                 status_callback: Callable[[ConnectionStatus, str], None] | None = None):
        """Initialize the serial handler.

        Args:
            port: Serial port address (default: /dev/ttyUSB2)
            baud_rate: Communication speed (default: 57600)
            status_callback: Optional callback for status updates (status, message).
        """
        self.port = port
        self.baud_rate = baud_rate
        self._serial: serial.Serial | None = None
        self._status = ConnectionStatus.DISCONNECTED
        self._error_message = ""
        self._status_callback = status_callback

    @property
    def status(self) -> ConnectionStatus:
        """Get the current connection status."""
        return self._status

    @property
    def error_message(self) -> str:
        """Get the last error message."""
        return self._error_message

    def _update_status(self, status: ConnectionStatus, message: str = "") -> None:
        """Update status and notify callback."""
        self._status = status
        self._error_message = message
        if self._status_callback:
            self._status_callback(status, message)

    def connect(self) -> bool:
        """Attempt to connect to the serial port.

        Returns:
            True if connection successful, False otherwise.
        """
        self._update_status(ConnectionStatus.CONNECTING)

        try:
            self._serial = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                bytesize=DATA_BITS,
                parity=serial.PARITY_NONE,
                stopbits=STOP_BITS,
                timeout=TIMEOUT
            )
            self._update_status(ConnectionStatus.CONNECTED)
            return True
        except SerialException as e:
            self._serial = None
            error_msg = self._get_error_message(e)
            self._update_status(ConnectionStatus.ERROR, error_msg)
            return False
        except Exception as e:
            self._serial = None
            self._update_status(ConnectionStatus.ERROR, str(e))
            return False

    def _get_error_message(self, exception: SerialException) -> str:
        """Convert SerialException to user-friendly message."""
        error_str = str(exception).lower()
        if "no such file" in error_str or "not found" in error_str:
            return f"Serial port {self.port} not found"
        elif "permission denied" in error_str:
            return "Permission denied. Check port access rights"
        elif "access is denied" in error_str:
            return "Port is in use by another application"
        else:
            return str(exception)

    def retry(self) -> bool:
        """Retry connection after an error.

        Returns:
            True if reconnection successful, False otherwise.
        """
        self.disconnect()
        return self.connect()

    def disconnect(self) -> None:
        """Close the serial port connection."""
        if self._serial and self._serial.is_open:
            self._serial.close()
        self._serial = None

    def is_connected(self) -> bool:
        """Check if serial port is connected.

        Returns:
            True if connected and port is open, False otherwise.
        """
        return self._serial is not None and self._serial.is_open

    def send(self, value: int) -> tuple[bool, str]:
        """Send a value to the RF transceiver.

        The value is converted to string, then encoded as ISO-8859-1
        before being written to the serial port.

        Args:
            value: Integer value to send (0-100).

        Returns:
            Tuple of (success: bool, message: str).
        """
        if not self.is_connected():
            return False, "Error: Not connected to serial port"

        try:
            # Convert integer to ASCII string and encode as ISO-8859-1
            ascii_string = str(value)
            encoded_data = ascii_string.encode(ENCODING)

            # Write to serial port
            bytes_written = self._serial.write(encoded_data)

            if bytes_written == len(encoded_data):
                return True, f"Sent: {value}"
            else:
                return False, "Error: Incomplete transmission"

        except SerialException as e:
            return False, f"Error: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"
