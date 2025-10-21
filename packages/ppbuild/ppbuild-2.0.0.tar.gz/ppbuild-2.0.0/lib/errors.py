"""Unified error handling."""


class PPError(Exception):
    """
    Main pp error class.

    Wraps other exceptions with a simple error_context for compatibility.
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
        # Create simple error_context for test compatibility
        self.error_context = SimpleErrorContext(message)


class SimpleErrorContext:
    """Simple error context for test compatibility."""

    def __init__(self, message: str):
        self.message = message
        self.details = {}

    def format_user_message(self) -> str:
        """Format error message for user display."""
        return self.message
