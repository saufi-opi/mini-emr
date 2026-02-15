from fastapi import APIRouter

router = APIRouter(
    prefix="",
    tags=["root"],
)

@router.get("/")
async def root():
    return {"message": "ClinicCare Backend is Running"}

@router.get("/health")
async def health_check():
    return {"status": "ok"}
