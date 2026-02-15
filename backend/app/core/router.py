from fastapi import APIRouter, Request
from app.core.rate_limiter import limiter

router = APIRouter(
    prefix="",
    tags=["root"],
)

@router.get("/")
@limiter.limit("60/minute")
async def root(request: Request):
    return {"message": "ClinicCare Backend is Running"}

@router.get("/health")
@limiter.limit("60/minute")
async def health_check(request: Request):
    return {"status": "ok"}
