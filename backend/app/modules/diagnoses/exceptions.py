from fastapi import status, HTTPException

class DiagnosisAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Diagnosis already exists"
        )

class DiagnosisNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Diagnosis not found"
        )