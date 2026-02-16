import uuid
from datetime import datetime, UTC
from typing import List, Optional, Sequence
from sqlalchemy import func, or_
from sqlalchemy.orm import selectinload, joinedload
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import col, desc, asc, select
from app.modules.consultation.models import Consultation
from app.modules.consultation.schemas import ConsultationCreate
from app.modules.diagnoses.models import Diagnosis
from app.modules.user.service import get_doctor_by_id
from app.modules.user.exceptions import UserNotFoundException, InactiveUserException
from app.core.schemas import PaginationParams, SortParams, SearchParams
from app.core.query_builder import QueryBuilder, QueryResult

async def create_consultation(*, 
    session: AsyncSession, 
    consultation_in: ConsultationCreate,
    doctor_id: uuid.UUID
) -> Consultation:
    """Creates a new consultation and links diagnoses."""
    doctor = await get_doctor_by_id(session=session, doctor_id=doctor_id)
    if not doctor:
        raise UserNotFoundException("Doctor not found")
    if not doctor.is_active:
        raise InactiveUserException("Doctor is inactive")
    
    # Create consultation object
    db_consultation = Consultation(
        patient_full_name=consultation_in.patient_full_name,
        doctor_id=doctor_id,
        notes=consultation_in.notes
    )
    
    # Link diagnoses
    if consultation_in.diagnosis_ids:
        # Using col() to satisfy the static analyzer for .in_
        statement = select(Diagnosis).where(col(Diagnosis.id).in_(consultation_in.diagnosis_ids))
        result = await session.exec(statement)
        diagnoses = result.all()
        db_consultation.diagnoses = list(diagnoses)
        
    session.add(db_consultation)
    await session.commit()
    
    # Re-fetch with all relationships for the response
    result = await get_consultation(session=session, consultation_id=db_consultation.id)
    if not result:
        raise RuntimeError("Consultation was not found after creation")
    return result

async def get_consultations(*,
    session: AsyncSession,
    pagination: PaginationParams,
    sort: SortParams,
    search: SearchParams,
    doctor_id: Optional[uuid.UUID] = None
) -> QueryResult[Consultation]:
    """Retrieves consultations with optional doctor filtering."""
    builder = QueryBuilder(Consultation, session, pagination, sort)
    
    # Add relationships
    builder.options(
        joinedload(Consultation.doctor), # type: ignore
        selectinload(Consultation.diagnoses) # type: ignore
    )
    
    # Add filters
    if doctor_id:
        builder.filter(col(Consultation.doctor_id) == doctor_id)
        
    # Search
    if search.search:
        builder.search(search, [Consultation.patient_full_name, Consultation.notes])
        
    # Sorting config
    sort_config = {
        "patient_name": Consultation.patient_full_name,
        "created_at": Consultation.created_at
    }
    builder.sort(sort, sort_config)
    
    return await builder.execute()

async def get_consultation(*, session: AsyncSession, consultation_id: uuid.UUID) -> Optional[Consultation]:
    """Retrieves a single consultation with all relationships."""
    statement = select(Consultation).where(col(Consultation.id) == consultation_id).options(
        joinedload(Consultation.doctor), # type: ignore
        selectinload(Consultation.diagnoses) # type: ignore
    )
    result = await session.exec(statement)
    return result.unique().first()
