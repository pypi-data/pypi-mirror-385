class InvalidClientOptionsException(Exception):
    """Exception raised when invalid client options are provided."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

