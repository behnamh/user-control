"""Input validation for RF Serial Controller."""

try:
    from .config import MIN_VALUE, MAX_VALUE
except ImportError:
    from config import MIN_VALUE, MAX_VALUE


class Validator:
    """Validates user input for RF transceiver values."""

    @staticmethod
    def validate(input_str: str) -> tuple[bool, str]:
        """Validate user input.

        Args:
            input_str: The input string to validate.

        Returns:
            Tuple of (is_valid: bool, error_message: str).
            If valid, error_message is empty string.
        """
        # Handle empty input
        if not input_str or input_str.strip() == "":
            return True, ""  # Empty treated as valid (will use default)

        # Check for non-numeric characters
        stripped = input_str.strip()
        
        # Allow negative sign only at the beginning for error messaging
        if stripped.startswith("-"):
            if not stripped[1:].isdigit():
                return False, "Invalid: Numbers only"
        elif not stripped.isdigit():
            return False, "Invalid: Numbers only"

        # Parse the value
        try:
            value = int(stripped)
        except ValueError:
            return False, "Invalid: Numbers only"

        # Check range
        if value < MIN_VALUE:
            return False, f"Invalid: Min value is {MIN_VALUE}"
        if value > MAX_VALUE:
            return False, f"Invalid: Max value is {MAX_VALUE}"

        return True, ""

    @staticmethod
    def is_valid_char(char: str) -> bool:
        """Check if a character is valid for input.

        Args:
            char: Single character to validate.

        Returns:
            True if character is a digit, False otherwise.
        """
        return char.isdigit()
