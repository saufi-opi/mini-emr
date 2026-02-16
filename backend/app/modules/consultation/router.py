import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.core.database import AsyncSessionDep
from app.modules.consultation import service
from app.modules.consultation.schemas import ConsultationCreate, ConsultationRead
from app.modules.user.models import User, Role
from app.modules.user.dependencies import get_current_active_user
from app.core.schemas import PaginationParams, SortParams, SearchParams
from app.core.query_builder import QueryResult
from app.core.rate_limiter import limiter

router = APIRouter(prefix="/consultation", tags=["consultation"])

@router.post("/", response_model=ConsultationRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("60/minute")
async def create_consultation(
    request: Request,
    consultation_in: ConsultationCreate,
    session: AsyncSessionDep,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new consultation record.
    """
    return await service.create_consultation(
        session=session, 
        consultation_in=consultation_in, 
        doctor_id=current_user.id
    )

@router.get("/", response_model=QueryResult[ConsultationRead])
@limiter.limit("60/minute")
async def list_consultations(
    request: Request,
    session: AsyncSessionDep,
    current_user: User = Depends(get_current_active_user),
    pagination: PaginationParams = Depends(),
    sort: SortParams = Depends(),
    search: SearchParams = Depends()
):
    """
    List consultations. Doctors only see their own, Admins see all.
    """
    doctor_id = current_user.id if current_user.role == Role.DOCTOR else None
    return await service.get_consultations(
        session=session,
        pagination=pagination,
        sort=sort,
        search=search,
        doctor_id=doctor_id
    )

@router.get("/{consultation_id}", response_model=ConsultationRead)
@limiter.limit("60/minute")
async def get_consultation(
    request: Request,
    consultation_id: uuid.UUID,
    session: AsyncSessionDep,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed consultation info. Doctors can only access their own records.
    """
    db_consultation = await service.get_consultation(session=session, consultation_id=consultation_id)
    
    if not db_consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
        
    # Permission check: Doctors only see their own
    if current_user.role == Role.DOCTOR and db_consultation.doctor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You do not have permission to view this consultation"
        )
        
    return db_consultation
