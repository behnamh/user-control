"""Tkinter GUI for RF Serial Controller."""

import platform
import tkinter as tk
from tkinter import ttk

import serial.tools.list_ports

try:
    from .config import DEFAULT_VALUE, SERIAL_PORT
    from .serial_handler import SerialHandler, ConnectionStatus
    from .validator import Validator
except ImportError:
    from config import DEFAULT_VALUE, SERIAL_PORT
    from serial_handler import SerialHandler, ConnectionStatus
    from validator import Validator


def get_available_ports() -> list[str]:
    """Get list of available serial ports."""
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]


class RFSerialGUI:
    """Main GUI window for RF Serial Controller."""

    def __init__(self, serial_handler: SerialHandler):
        """Initialize the GUI.

        Args:
            serial_handler: SerialHandler instance for communication.
        """
        self.serial_handler = serial_handler
        self.validator = Validator()
        self._is_sending = False
        self._input_valid = True
        self._is_windows = platform.system() == "Windows"

        # Create main window
        self.root = tk.Tk()
        self.root.title("RF Serial Controller")
        self.root.geometry("350x280" if self._is_windows else "320x250")
        self.root.resizable(False, False)

        # Create widgets
        self._create_widgets()

        # Update connection status display
        self._update_connection_display()

    def _create_widgets(self) -> None:
        """Create and layout GUI widgets."""
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        current_row = 0

        # Port selection (Windows only)
        if self._is_windows:
            port_frame = ttk.LabelFrame(main_frame, text="Serial Port", padding="5")
            port_frame.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=5)

            # Port dropdown
            self.port_var = tk.StringVar(value=self.serial_handler.port)
            self.port_combo = ttk.Combobox(port_frame, textvariable=self.port_var, width=15, state="readonly")
            self._refresh_ports()
            self.port_combo.grid(row=0, column=0, sticky="w", padx=5)

            # Refresh button
            refresh_btn = ttk.Button(port_frame, text="Refresh", command=self._refresh_ports, width=8)
            refresh_btn.grid(row=0, column=1, sticky="w", padx=5)

            # Connect button
            self.connect_button = ttk.Button(port_frame, text="Connect", command=self._on_connect_click, width=8)
            self.connect_button.grid(row=0, column=2, sticky="e", padx=5)

            current_row += 1

        # Connection status frame
        status_frame = ttk.LabelFrame(main_frame, text="Connection", padding="5")
        status_frame.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=5)

        # Connection status label
        self.status_var = tk.StringVar(value="Disconnected")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
        self.status_label.grid(row=0, column=0, sticky="w", padx=5)

        # Retry button (hidden by default, shown on non-Windows or as fallback)
        self.retry_button = ttk.Button(status_frame, text="Retry", command=self._on_retry_click)
        self.retry_button.grid(row=0, column=1, sticky="e", padx=5)
        self.retry_button.grid_remove()  # Hidden initially

        current_row += 1

        # Input label
        input_label = ttk.Label(main_frame, text="Value (0-100):")
        input_label.grid(row=current_row, column=0, sticky="w", pady=5)

        # Input field with default value and validation
        self.input_var = tk.StringVar(value=str(DEFAULT_VALUE))
        self.input_var.trace_add("write", self._on_input_change)
        self.input_field = ttk.Entry(main_frame, textvariable=self.input_var, width=10)
        self.input_field.grid(row=current_row, column=1, sticky="w", pady=5, padx=5)

        current_row += 1

        # Validation error label
        self.validation_var = tk.StringVar(value="")
        self.validation_label = ttk.Label(main_frame, textvariable=self.validation_var, foreground="red")
        self.validation_label.grid(row=current_row, column=0, columnspan=2, pady=2)

        current_row += 1

        # Send button
        self.send_button = ttk.Button(main_frame, text="Send", command=self._on_send_click)
        self.send_button.grid(row=current_row, column=0, columnspan=2, pady=10)

        current_row += 1

        # Feedback label
        self.feedback_var = tk.StringVar(value="")
        self.feedback_label = ttk.Label(main_frame, textvariable=self.feedback_var)
        self.feedback_label.grid(row=current_row, column=0, columnspan=2, pady=5)

    def _refresh_ports(self) -> None:
        """Refresh the list of available serial ports."""
        ports = get_available_ports()
        if not ports:
            ports = ["No ports found"]
        self.port_combo['values'] = ports

        # Keep current selection if still available, otherwise select first
        current = self.port_var.get()
        if current not in ports:
            self.port_var.set(ports[0] if ports else "")

    def _on_connect_click(self) -> None:
        """Handle Connect button click (Windows port selection)."""
        selected_port = self.port_var.get()
        if selected_port and selected_port != "No ports found":
            # Update serial handler with new port
            self.serial_handler.disconnect()
            self.serial_handler.port = selected_port

            self.status_var.set("Connecting...")
            self.root.update()

            success = self.serial_handler.connect()
            self._update_connection_display()

            if success:
                self.feedback_var.set(f"Connected to {selected_port}")
            else:
                self.feedback_var.set("Connection failed")

    def _update_connection_display(self) -> None:
        """Update the connection status display based on SerialHandler state."""
        status = self.serial_handler.status
        error_msg = self.serial_handler.error_message

        if status == ConnectionStatus.CONNECTED:
            self.status_var.set(f"Connected ({self.serial_handler.port})")
            self.retry_button.grid_remove()
            if self._is_windows:
                self.connect_button.config(text="Disconnect")
        elif status == ConnectionStatus.CONNECTING:
            self.status_var.set("Connecting...")
            self.retry_button.grid_remove()
        elif status == ConnectionStatus.ERROR:
            self.status_var.set(f"Error: {error_msg}" if error_msg else "Error")
            if not self._is_windows:
                self.retry_button.grid()  # Show retry button on non-Windows
            if self._is_windows:
                self.connect_button.config(text="Connect")
        else:  # DISCONNECTED
            self.status_var.set("Disconnected")
            if not self._is_windows:
                self.retry_button.grid()  # Show retry button on non-Windows
            if self._is_windows:
                self.connect_button.config(text="Connect")

        # Update send button state
        self._update_send_button_state()

    def on_status_change(self, status: ConnectionStatus, message: str) -> None:
        """Callback for connection status changes.

        Args:
            status: New connection status.
            message: Associated message (usually error message).
        """
        self._update_connection_display()

    def _on_retry_click(self) -> None:
        """Handle Retry button click."""
        self.status_var.set("Connecting...")
        self.retry_button.grid_remove()
        self.root.update()  # Force UI update

        success = self.serial_handler.retry()
        self._update_connection_display()

        if success:
            self.feedback_var.set("Reconnected successfully")
        else:
            self.feedback_var.set("Reconnection failed")

    def _on_input_change(self, *args) -> None:
        """Handle input field changes for validation."""
        input_text = self.input_var.get()
        is_valid, error_msg = self.validator.validate(input_text)

        self._input_valid = is_valid
        self.validation_var.set(error_msg)

        # Update send button state based on validation
        self._update_send_button_state()

    def _update_send_button_state(self) -> None:
        """Update Send button enabled/disabled state."""
        is_connected = self.serial_handler.status == ConnectionStatus.CONNECTED
        if self._is_sending or not self._input_valid or not is_connected:
            self.send_button.config(state="disabled")
        else:
            self.send_button.config(state="normal")

    def _on_send_click(self) -> None:
        """Handle Send button click."""
        if self._is_sending or not self._input_valid:
            return

        # Disable button during transmission
        self._is_sending = True
        self._update_send_button_state()
        self.feedback_var.set("Sending...")
        self.root.update()  # Force UI update

        # Get value and send
        try:
            value = int(self.input_var.get())
            success, message = self.serial_handler.send(value)
            self.feedback_var.set(message)
        except ValueError:
            self.feedback_var.set("Error: Invalid input")
        except Exception as e:
            self.feedback_var.set(f"Error: {str(e)}")
        finally:
            # Re-enable button after transmission
            self._is_sending = False
            self._update_send_button_state()

    def run(self) -> None:
        """Start the GUI main loop."""
        self.root.mainloop()
