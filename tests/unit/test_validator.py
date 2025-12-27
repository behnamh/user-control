"""Unit tests for Validator class."""

import pytest
from src.rf_serial_gui.validator import Validator


class TestValidator:
    """Tests for the Validator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = Validator()

    # Valid input tests
    def test_validate_zero(self):
        """Test that 0 is valid."""
        is_valid, error = self.validator.validate("0")
        assert is_valid is True
        assert error == ""

    def test_validate_hundred(self):
        """Test that 100 is valid."""
        is_valid, error = self.validator.validate("100")
        assert is_valid is True
        assert error == ""

    def test_validate_mid_range(self):
        """Test that 50 is valid."""
        is_valid, error = self.validator.validate("50")
        assert is_valid is True
        assert error == ""

    def test_validate_empty_string(self):
        """Test that empty string is valid (uses default)."""
        is_valid, error = self.validator.validate("")
        assert is_valid is True
        assert error == ""

    def test_validate_whitespace_only(self):
        """Test that whitespace-only is valid (uses default)."""
        is_valid, error = self.validator.validate("   ")
        assert is_valid is True
        assert error == ""

    # Invalid input tests - out of range
    def test_validate_negative(self):
        """Test that negative numbers are invalid."""
        is_valid, error = self.validator.validate("-1")
        assert is_valid is False
        assert "Min value" in error

    def test_validate_over_hundred(self):
        """Test that values over 100 are invalid."""
        is_valid, error = self.validator.validate("101")
        assert is_valid is False
        assert "Max value" in error

    def test_validate_large_number(self):
        """Test that large numbers are invalid."""
        is_valid, error = self.validator.validate("999")
        assert is_valid is False
        assert "Max value" in error

    # Invalid input tests - non-numeric
    def test_validate_letters(self):
        """Test that letters are invalid."""
        is_valid, error = self.validator.validate("abc")
        assert is_valid is False
        assert "Numbers only" in error

    def test_validate_mixed_letters_numbers(self):
        """Test that mixed input is invalid."""
        is_valid, error = self.validator.validate("12a")
        assert is_valid is False
        assert "Numbers only" in error

    def test_validate_special_characters(self):
        """Test that special characters are invalid."""
        is_valid, error = self.validator.validate("50!")
        assert is_valid is False
        assert "Numbers only" in error

    def test_validate_decimal(self):
        """Test that decimal numbers are invalid."""
        is_valid, error = self.validator.validate("50.5")
        assert is_valid is False
        assert "Numbers only" in error

    # Edge cases
    def test_validate_leading_zeros(self):
        """Test that leading zeros are valid."""
        is_valid, error = self.validator.validate("007")
        assert is_valid is True
        assert error == ""

    def test_validate_with_spaces(self):
        """Test that value with surrounding spaces is valid."""
        is_valid, error = self.validator.validate("  50  ")
        assert is_valid is True
        assert error == ""

    # is_valid_char tests
    def test_is_valid_char_digit(self):
        """Test that digits are valid characters."""
        assert Validator.is_valid_char("0") is True
        assert Validator.is_valid_char("5") is True
        assert Validator.is_valid_char("9") is True

    def test_is_valid_char_letter(self):
        """Test that letters are invalid characters."""
        assert Validator.is_valid_char("a") is False
        assert Validator.is_valid_char("Z") is False

    def test_is_valid_char_special(self):
        """Test that special characters are invalid."""
        assert Validator.is_valid_char("-") is False
        assert Validator.is_valid_char(".") is False
