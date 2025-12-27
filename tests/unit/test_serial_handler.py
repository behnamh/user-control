"""Unit tests for SerialHandler class."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from serial import SerialException

from src.rf_serial_gui.serial_handler import SerialHandler, ConnectionStatus


class TestSerialHandlerConnection:
    """Tests for SerialHandler connection methods."""

    def test_initial_state(self):
        """Test that handler starts disconnected."""
        handler = SerialHandler()
        assert handler.status == ConnectionStatus.DISCONNECTED
        assert handler.is_connected() is False

    @patch('src.rf_serial_gui.serial_handler.serial.Serial')
    def test_connect_success(self, mock_serial_class):
        """Test successful connection."""
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial_class.return_value = mock_serial

        handler = SerialHandler()
        result = handler.connect()

        assert result is True
        assert handler.status == ConnectionStatus.CONNECTED
        assert handler.is_connected() is True
        mock_serial_class.assert_called_once()

    @patch('src.rf_serial_gui.serial_handler.serial.Serial')
    def test_connect_failure_port_not_found(self, mock_serial_class):
        """Test connection failure when port not found."""
        mock_serial_class.side_effect = SerialException("could not open port: No such file")

        handler = SerialHandler()
        result = handler.connect()

        assert result is False
        assert handler.status == ConnectionStatus.ERROR
        assert "not found" in handler.error_message

    @patch('src.rf_serial_gui.serial_handler.serial.Serial')
    def test_connect_failure_permission_denied(self, mock_serial_class):
        """Test connection failure when permission denied."""
        mock_serial_class.side_effect = SerialException("Permission denied")

        handler = SerialHandler()
        result = handler.connect()

        assert result is False
        assert handler.status == ConnectionStatus.ERROR
        assert "Permission denied" in handler.error_message

    @patch('src.rf_serial_gui.serial_handler.serial.Serial')
    def test_disconnect(self, mock_serial_class):
        """Test disconnection."""
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial_class.return_value = mock_serial

        handler = SerialHandler()
        handler.connect()
        handler.disconnect()

        mock_serial.close.assert_called_once()
        assert handler.is_connected() is False

    @patch('src.rf_serial_gui.serial_handler.serial.Serial')
    def test_retry_after_failure(self, mock_serial_class):
        """Test retry reconnects after failure."""
        # First call fails, second succeeds
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial_class.side_effect = [
            SerialException("Port not found"),
            mock_serial
        ]

        handler = SerialHandler()
        handler.connect()  # Fails
        assert handler.status == ConnectionStatus.ERROR

        result = handler.retry()  # Should succeed
        assert result is True
        assert handler.status == ConnectionStatus.CONNECTED

    def test_status_callback(self):
        """Test that status callback is called on status changes."""
        callback = Mock()
        handler = SerialHandler(status_callback=callback)

        with patch('src.rf_serial_gui.serial_handler.serial.Serial') as mock_serial_class:
            mock_serial_class.side_effect = SerialException("Port not found")
            handler.connect()

        # Should have been called with CONNECTING and then ERROR
        assert callback.call_count >= 2


class TestSerialHandlerSend:
    """Tests for SerialHandler send method."""

    @patch('src.rf_serial_gui.serial_handler.serial.Serial')
    def test_send_success(self, mock_serial_class):
        """Test successful send."""
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial.write.return_value = 2  # "50" = 2 bytes
        mock_serial_class.return_value = mock_serial

        handler = SerialHandler()
        handler.connect()
        success, message = handler.send(50)

        assert success is True
        assert "Sent: 50" in message
        mock_serial.write.assert_called_once_with(b'50')

    @patch('src.rf_serial_gui.serial_handler.serial.Serial')
    def test_send_encodes_iso_8859_1(self, mock_serial_class):
        """Test that values are encoded as ISO-8859-1."""
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial.write.return_value = 3  # "100" = 3 bytes
        mock_serial_class.return_value = mock_serial

        handler = SerialHandler()
        handler.connect()
        handler.send(100)

        # Verify the exact bytes sent
        mock_serial.write.assert_called_once()
        sent_data = mock_serial.write.call_args[0][0]
        assert sent_data == "100".encode('iso-8859-1')

    def test_send_not_connected(self):
        """Test send fails when not connected."""
        handler = SerialHandler()
        success, message = handler.send(50)

        assert success is False
        assert "Not connected" in message

    @patch('src.rf_serial_gui.serial_handler.serial.Serial')
    def test_send_incomplete_transmission(self, mock_serial_class):
        """Test send handles incomplete transmission."""
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial.write.return_value = 1  # Only 1 byte written instead of 2
        mock_serial_class.return_value = mock_serial

        handler = SerialHandler()
        handler.connect()
        success, message = handler.send(50)

        assert success is False
        assert "Incomplete" in message

    @patch('src.rf_serial_gui.serial_handler.serial.Serial')
    def test_send_serial_exception(self, mock_serial_class):
        """Test send handles serial exceptions."""
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial.write.side_effect = SerialException("Write timeout")
        mock_serial_class.return_value = mock_serial

        handler = SerialHandler()
        handler.connect()
        success, message = handler.send(50)

        assert success is False
        assert "Error" in message

    @patch('src.rf_serial_gui.serial_handler.serial.Serial')
    def test_send_zero(self, mock_serial_class):
        """Test sending value 0."""
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial.write.return_value = 1
        mock_serial_class.return_value = mock_serial

        handler = SerialHandler()
        handler.connect()
        success, message = handler.send(0)

        assert success is True
        mock_serial.write.assert_called_once_with(b'0')

    @patch('src.rf_serial_gui.serial_handler.serial.Serial')
    def test_send_hundred(self, mock_serial_class):
        """Test sending value 100."""
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial.write.return_value = 3
        mock_serial_class.return_value = mock_serial

        handler = SerialHandler()
        handler.connect()
        success, message = handler.send(100)

        assert success is True
        mock_serial.write.assert_called_once_with(b'100')


class TestConnectionStatus:
    """Tests for ConnectionStatus enum."""

    def test_status_values(self):
        """Test ConnectionStatus enum values."""
        assert ConnectionStatus.DISCONNECTED.value == "Disconnected"
        assert ConnectionStatus.CONNECTING.value == "Connecting..."
        assert ConnectionStatus.CONNECTED.value == "Connected"
        assert ConnectionStatus.ERROR.value == "Error"
