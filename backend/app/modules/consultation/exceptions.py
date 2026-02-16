from fastapi import status
from fastapi.exceptions import HTTPException

class NotADoctorException(HTTPException):
    def __init__(self, message="User is not a doctor"):
        self.message = message
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=self.message)

class ConsultationNotFoundException(HTTPException):
    def __init__(self, message="Consultation not found"):
        self.message = message
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=self.message)

class ConsultationPermissionException(HTTPException):
    def __init__(self, message="You do not have permission to view this consultation"):
        self.message = message
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=self.message)