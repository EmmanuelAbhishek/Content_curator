import csv

class ContentCuratorException(Exception):
    """Base exception for Content Curator errors."""
    pass


class APIRequestError(ContentCuratorException):
    """Exception for API request errors."""
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class VideoFetchError(ContentCuratorException):
    """Exception for video fetch errors."""
    def __init__(self, message, video_id):
        self.message = message
        self.video_id = video_id
        super().__init__(message)


class ExportError(ContentCuratorException):
    """Exception for export errors."""
    def __init__(self, message, export_type):
        self.message = message
        self.export_type = export_type
        super().__init__(message)
