from fastapi import status, HTTPException
from pydantic import EmailStr

class InactiveUserException(HTTPException):
    def __init__(self, message: str = "Inactive user"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=message
        )

class UserNotFoundException(HTTPException):
    def __init__(self, message: str = "User not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=message
        )

class UserAlreadyExistsException(HTTPException):
    def __init__(self, message: str = "User with this email already exists"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=message
        )
