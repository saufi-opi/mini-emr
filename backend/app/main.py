from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# routers
from app.core.router import router as root_router

app = FastAPI(title="ClinicCare Mini EMR")

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
