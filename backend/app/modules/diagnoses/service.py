from typing import List, Sequence, Optional
from sqlalchemy import or_
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.diagnoses.models import Diagnosis
from app.modules.diagnoses.schemas import DiagnosisCreate
from app.modules.diagnoses.exceptions import DiagnosisAlreadyExistsException, DiagnosisNotFoundException
from app.core.schemas import PaginationParams, SortParams, SearchParams
from app.core.query_builder import QueryBuilder, QueryResult

async def get_diagnoses(*,
    session: AsyncSession, 
    pagination: PaginationParams, 
    sort: SortParams,
    search: SearchParams
) -> QueryResult[Diagnosis]:
    query = QueryBuilder(Diagnosis, session)
    query.paginate(pagination).sort(sort).search(search, [Diagnosis.code, Diagnosis.description])
    return await query.execute()

async def get_diagnosis_by_code(*, session: AsyncSession, code: str) -> Optional[Diagnosis]:
    statement = select(Diagnosis).where(Diagnosis.code == code)
    result = await session.execute(statement)
    return result.scalar_one_or_none()

async def create_diagnosis(*, session: AsyncSession, diagnosis: DiagnosisCreate) -> Optional[Diagnosis]:
    db_diagnosis = Diagnosis.model_validate(diagnosis)

    existing_diagnosis = await get_diagnosis_by_code(session=session, code=db_diagnosis.code)
    if existing_diagnosis:
        raise DiagnosisAlreadyExistsException()

    session.add(db_diagnosis)
    await session.commit()
    await session.refresh(db_diagnosis)
    return db_diagnosis
