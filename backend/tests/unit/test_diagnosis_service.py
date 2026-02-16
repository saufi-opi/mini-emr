import pytest
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.diagnoses import service as diagnosis_service
from app.modules.diagnoses.models import Diagnosis
from app.modules.diagnoses.schemas import DiagnosisCreate
from app.modules.diagnoses.exceptions import DiagnosisAlreadyExistsException
from app.core.schemas import PaginationParams, SortParams, SearchParams

@pytest.mark.asyncio
async def test_get_diagnosis_by_code_success(async_session: AsyncSession):
    """Test retrieving a diagnosis by code successfully."""
    # Create a test diagnosis
    diagnosis = Diagnosis(code="A00", description="Cholera")
    async_session.add(diagnosis)
    await async_session.commit()
    await async_session.refresh(diagnosis)
    
    result = await diagnosis_service.get_diagnosis_by_code(session=async_session, code="A00")
    
    assert result is not None
    assert result.code == "A00"
    assert result.description == "Cholera"

@pytest.mark.asyncio
async def test_get_diagnosis_by_code_not_found(async_session: AsyncSession):
    """Test retrieving a non-existent diagnosis by code returns None."""
    result = await diagnosis_service.get_diagnosis_by_code(session=async_session, code="NONEXISTENT")
    assert result is None

@pytest.mark.asyncio
async def test_create_diagnosis_success(async_session: AsyncSession):
    """Test creating a new diagnosis successfully."""
    diagnosis_create = DiagnosisCreate(code="B00", description="Herpesviral infection")
    
    result = await diagnosis_service.create_diagnosis(session=async_session, diagnosis=diagnosis_create)
    
    assert result is not None
    assert result.code == "B00"
    assert result.description == "Herpesviral infection"
    assert result.id is not None

@pytest.mark.asyncio
async def test_create_diagnosis_duplicate(async_session: AsyncSession):
    """Test creating a diagnosis with a duplicate code raises exception."""
    # Create an initial diagnosis
    diagnosis_create = DiagnosisCreate(code="C00", description="Malignant neoplasm of lip")
    await diagnosis_service.create_diagnosis(session=async_session, diagnosis=diagnosis_create)
    
    # Try to create another one with the same code
    duplicate_create = DiagnosisCreate(code="C00", description="Duplicate Code")
    
    with pytest.raises(DiagnosisAlreadyExistsException):
        await diagnosis_service.create_diagnosis(session=async_session, diagnosis=duplicate_create)

@pytest.mark.asyncio
async def test_get_diagnoses_pagination(async_session: AsyncSession):
    """Test retrieving diagnoses with pagination."""
    # Create 5 diagnoses
    for i in range(5):
        diag = Diagnosis(code=f"D0{i}", description=f"Description {i}")
        async_session.add(diag)
    await async_session.commit()
    
    pagination = PaginationParams(skip=0, limit=3)
    sort = SortParams(sort="code")
    search = SearchParams(search=None)
    
    result = await diagnosis_service.get_diagnoses(
        session=async_session,
        pagination=pagination,
        sort=sort,
        search=search
    )
    
    assert len(result.data) == 3
    assert result.count == 5

@pytest.mark.asyncio
async def test_get_diagnoses_search(async_session: AsyncSession):
    """Test searching for diagnoses."""
    # Create diagnoses
    diagnoses = [
        Diagnosis(code="E00", description="Hypothyroidism"),
        Diagnosis(code="E01", description="Iodine-deficiency related thyroid disorders"),
        Diagnosis(code="F00", description="Dementia in Alzheimer disease"),
    ]
    for diag in diagnoses:
        async_session.add(diag)
    await async_session.commit()
    
    pagination = PaginationParams(skip=0, limit=10)
    sort = SortParams(sort="code")
    
    # Search for "thyroid"
    search = SearchParams(search="thyroid")
    result = await diagnosis_service.get_diagnoses(
        session=async_session,
        pagination=pagination,
        sort=sort,
        search=search
    )
    
    assert result.count == 2
    assert all("thyroid" in d.description.lower() for d in result.data)

@pytest.mark.asyncio
async def test_get_diagnoses_sort(async_session: AsyncSession):
    """Test sorting diagnoses."""
    diagnoses = [
        Diagnosis(code="G02", description="B"),
        Diagnosis(code="G01", description="C"),
        Diagnosis(code="G03", description="A"),
    ]
    for diag in diagnoses:
        async_session.add(diag)
    await async_session.commit()
    
    pagination = PaginationParams(skip=0, limit=10)
    search = SearchParams(search=None)
    
    # Sort by code ascending
    result = await diagnosis_service.get_diagnoses(
        session=async_session,
        pagination=pagination,
        sort=SortParams(sort="code"),
        search=search
    )
    assert result.data[0].code == "G01"
    assert result.data[1].code == "G02"
    assert result.data[2].code == "G03"
    
    # Sort by description descending
    result = await diagnosis_service.get_diagnoses(
        session=async_session,
        pagination=pagination,
        sort=SortParams(sort="-description"),
        search=search
    )
    assert result.data[0].description == "C"
    assert result.data[1].description == "B"
    assert result.data[2].description == "A"
