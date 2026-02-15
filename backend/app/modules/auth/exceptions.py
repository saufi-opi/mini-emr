from fastapi import status, HTTPException

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