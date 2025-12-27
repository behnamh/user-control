"""Serial port configuration constants."""

import platform

# Serial port settings - OS-specific defaults
if platform.system() == "Windows":
    SERIAL_PORT = "COM3"  # Common Windows USB serial port
else:
    SERIAL_PORT = "/dev/ttyUSB2"  # Linux USB serial port

BAUD_RATE = 57600
TIMEOUT = 2  # seconds

# Serial port parameters (8N1)
DATA_BITS = 8
PARITY = "N"  # None
STOP_BITS = 1

# Encoding
ENCODING = "iso-8859-1"

# Value constraints
MIN_VALUE = 0
MAX_VALUE = 100
DEFAULT_VALUE = 0
