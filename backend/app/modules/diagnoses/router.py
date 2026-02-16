from fastapi import APIRouter, Query, Depends, Request
from app.core.database import AsyncSessionDep
from app.modules.diagnoses import service
from app.modules.diagnoses.schemas import DiagnosisRead
from app.core.schemas import PaginationParams, SortParams, SearchParams
from app.core.query_builder import QueryResult
from app.core.rate_limiter import limiter
from app.modules.user.dependencies import get_current_active_user

router = APIRouter(prefix="/diagnosis", tags=["diagnosis"])

@router.get("/", 
    # dependencies=[Depends(get_current_active_user)], 
    response_model=QueryResult[DiagnosisRead]
)
@limiter.limit("60/minute")
async def search_diagnoses(
    request: Request,
    session: AsyncSessionDep,
    pagination: PaginationParams = Depends(),
    sort: SortParams = Depends(),
    search: SearchParams = Depends(),
):
    """
    Search for diagnosis codes by code.
    """
    return await service.get_diagnoses(
        session=session, 
        search=search, 
        pagination=pagination, 
        sort=sort
    )
