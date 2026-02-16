from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings, AppEnv
from app.core.rate_limiter import limiter

# routers
from app.core.router import router as root_router
from app.modules.user.router import router as user_router
from app.modules.auth.router import router as auth_router
from app.modules.diagnoses.router import router as diagnoses_router
from app.modules.consultation.router import router as consultation_router

def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"

app = FastAPI(
    title="ClinicCare Mini EMR", 
    generate_unique_id_function=custom_generate_unique_id
)
app.state.limiter = limiter

# Add rate limiter middleware except in tests due to RuntimeError in BaseHTTPMiddleware
if settings.APP_ENV != AppEnv.TEST:
    app.add_middleware(SlowAPIMiddleware) # type: ignore

@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."},
    )

# middleware
app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=settings.CORS_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(root_router)
app.include_router(auth_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(diagnoses_router, prefix="/api/v1")
app.include_router(consultation_router, prefix="/api/v1")
