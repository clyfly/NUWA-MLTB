class DirectDownloadLinkException(Exception):
    """Not method found for extracting direct download link from the http link"""

    pass


class NotSupportedExtractionArchive(Exception):
    """The archive format being used for extraction is not supported"""

    pass


class RssShutdownException(Exception):
    """This exception should be raised when shutdown is called to stop the monitor"""

    pass


class TgLinkException(Exception):
    """No Access granted for this chat"""

    pass


class InvalidConfigError(Exception):
    """Raised when a configuration value is invalid or missing."""

    pass


class UploadFailedException(Exception):
    """Raised when an upload operation fails after retries."""

    pass


class RateLimitExceededException(Exception):
    """Raised when a user exceeds the rate limit for bot commands."""

    pass
