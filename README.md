# RF Serial GUI

A Python GUI application for sending integer values to an RF transceiver via USB serial port.

## Quick Start

### Run the Executable (Windows)

Double-click `rf_serial_gui.exe` in the project root.

### Run from Source

```bash
# Install dependencies
uv sync

# Run the application
uv run python src/rf_serial_gui/main.py
```

## Features

- Send integer values (0-100) to RF transceiver via serial port
- Real-time input validation with error messages
- Cross-platform support (Windows and Linux)
- Windows: COM port selection dropdown with refresh capability
- Linux: Auto-connects to configured port (/dev/ttyUSB2)
- Connection status display with retry functionality
- Send button disabled during transmission to prevent duplicate sends

## Requirements

- Python 3.8+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Installation

### Using uv (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd user_control

# Create virtual environment and install dependencies
uv sync

# Install development dependencies (for testing)
uv sync --extra dev
```

### Using pip

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install pyserial

# Install dev dependencies (optional)
pip install pytest pytest-mock
```

## Usage

### Windows

1. Launch the application
2. Select a COM port from the dropdown
3. Click **Refresh** to rescan available ports if needed
4. Click **Connect** to establish connection
5. Enter a value between 0 and 100
6. Click **Send** to transmit

### Linux

1. Launch the application (auto-connects to /dev/ttyUSB2)
2. If connection fails, click **Retry**
3. Enter a value between 0 and 100
4. Click **Send** to transmit

## Configuration

Serial port settings can be modified in `src/rf_serial_gui/config.py`:

| Parameter | Default (Windows) | Default (Linux) |
|-----------|-------------------|-----------------|
| Port | COM3 | /dev/ttyUSB2 |
| Baud Rate | 57600 | 57600 |
| Data Bits | 8 | 8 |
| Parity | None | None |
| Stop Bits | 1 | 1 |
| Encoding | ISO-8859-1 | ISO-8859-1 |

## Development

### Running Tests

```bash
uv run pytest tests/ -v
```

### Building Executable

Executables must be built on the target platform (PyInstaller does not support cross-compilation).

#### Windows

```bash
uv run pyinstaller --onefile --windowed --name rf_serial_gui ^
    --paths src/rf_serial_gui ^
    --hidden-import config ^
    --hidden-import gui ^
    --hidden-import serial_handler ^
    --hidden-import validator ^
    src/rf_serial_gui/main.py

# Copy to project root
copy dist\rf_serial_gui.exe .
```

#### Linux

```bash
uv run pyinstaller --onefile --name rf_serial_gui \
    --paths src/rf_serial_gui \
    --hidden-import config \
    --hidden-import gui \
    --hidden-import serial_handler \
    --hidden-import validator \
    src/rf_serial_gui/main.py

# Copy to project root
cp dist/rf_serial_gui .

# Make executable (if needed)
chmod +x rf_serial_gui
```

#### Linux via Docker (from Windows)

```bash
docker run --rm -v "$(pwd):/app" -w /app python:3.11 bash -c "
    pip install pyinstaller pyserial &&
    pyinstaller --onefile --name rf_serial_gui_linux \
        --paths src/rf_serial_gui \
        --hidden-import config \
        --hidden-import gui \
        --hidden-import serial_handler \
        --hidden-import validator \
        src/rf_serial_gui/main.py
"
cp dist/rf_serial_gui_linux .
```

## Project Structure

```
user_control/
├── src/
│   └── rf_serial_gui/
│       ├── __init__.py
│       ├── main.py           # Application entry point
│       ├── gui.py            # Tkinter GUI implementation
│       ├── serial_handler.py # Serial port communication
│       ├── validator.py      # Input validation
│       └── config.py         # Configuration constants
├── tests/
│   └── unit/
│       ├── test_validator.py
│       └── test_serial_handler.py
├── pyproject.toml            # Project configuration
├── rf_serial_gui.exe         # Windows executable
└── README.md
```

## License

MIT
