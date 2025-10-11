class DbOperationException(Exception):
    def __init__(self, original_exception: Exception):
        message = f"Error obtaining database connection: {original_exception}"
        super().__init__(message)
        self.original_exception = original_exception
