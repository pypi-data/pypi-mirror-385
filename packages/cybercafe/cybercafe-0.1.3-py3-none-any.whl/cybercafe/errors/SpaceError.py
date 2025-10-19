class SpaceError(Exception):
    """
    Custom error for Space SDK.

    Raised when an HTTP request or SDK operation fails.
    """

    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    def __str__(self):
        if self.status_code:
            return f"SpaceError ({self.status_code}): {self.message}"
        return f"SpaceError: {self.message}"
