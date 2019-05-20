"""Test suite errors."""


class BeaconTestError(Exception):
    """Class for all exceptions that are expected."""

    def __init__(self):
        """Nothing special, use standard exception."""
        Exception.__init__(self)


class ResponseError(Exception):
    """Class for exceptions in comparisons of the expected responses to the real ones."""

    def __init__(self, messages):
        """A standard exception, but with a list of messages."""
        Exception.__init__(self)
        # Keep a list of messages to log later
        self.messages = messages
