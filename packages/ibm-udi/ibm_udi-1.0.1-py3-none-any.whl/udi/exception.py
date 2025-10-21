

class ElyraGenerationException(Exception):
    """Exception raised when Elyra pipeline generation fails."""
    def __init__(self, message="Elyra pipeline generation failed.", traceback_info=None):
        self.message = message
        self.traceback_info = traceback_info or ""
        super().__init__(f"{self.message}\nTraceback:\n{self.traceback_info}")

class DatasiftSDKException(Exception):
    """Exception raised for runtime errors in the Datasift SDK."""
    def __init__(self, message="An error occurred in the Datasift SDK.", traceback_info=None):
        self.message = message
        self.traceback_info = traceback_info or ""
        super().__init__(f"{self.message}\nTraceback:\n{self.traceback_info}")