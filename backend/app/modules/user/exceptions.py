from fastapi import status, HTTPException
from pydantic import EmailStr

class CredentialException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Could not validate credentials", 
            headers={"WWW-Authenticate": "Bearer"}
        )

class UnauthorizedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to perform this action"
        )

class InactiveUserException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )

class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )

class UserAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="User with this email already exists"
        )
