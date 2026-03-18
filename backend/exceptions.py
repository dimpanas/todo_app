class AppBaseException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code


class UserAlreadyExist(AppBaseException):
    def __init__(self, details: str = "User already exists"):
        super().__init__(message=details, status_code=400)


class AuthenticationException(AppBaseException):
    def __init__(self, details: str = "Could not validate credentials"):
        super().__init__(message=details, status_code=401)


class UnauthorizedActionException(AppBaseException):
    def __init__(self, details="Unauthorized user"):
        super().__init__(message=details, status_code=403)


class ResourceNotFoundException(AppBaseException):
    def __init__(self, resource_name: str, resource_id: int):
        super().__init__(
            message=f"{resource_name} with ID = {resource_id} not found",
            status_code=404,
        )


class DatabaseConnectionException(AppBaseException):
    def __init__(self):
        super().__init__(message="Database connection error", status_code=500)
