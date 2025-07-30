import pytest
import asyncio
from typing import AsyncGenerator, Generator
import httpx
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock

from app.main import app
from app.models.intake import PatientIntake
from app.models.ehr import EHRRecord
from app.models.careplan import CarePlan
from app.llm.client import LLMClient
from app.ehr.client import EHRClient
from app.retrieval.vector_store import VectorStore


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Create an async test client for the FastAPI app."""
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_llm_client() -> MagicMock:
    """Create a mock LLM client."""
    mock_client = MagicMock(spec=LLMClient)
    mock_client.generate_care_plan = AsyncMock(return_value={
        "care_plan": {
            "primary_diagnosis": "Type 2 Diabetes Mellitus",
            "clinical_summary": "Patient presents with elevated blood glucose levels...",
            "actions": [
                {
                    "type": "medication",
                    "description": "Start Metformin 500mg twice daily",
                    "priority": "high",
                    "timeline": "immediate",
                    "rationale": "First-line therapy for T2DM"
                }
            ],
            "short_term_goals": ["Achieve HbA1c < 7%"],
            "long_term_goals": ["Prevent diabetic complications"],
            "success_metrics": ["HbA1c monitoring every 3 months"],
            "patient_instructions": "Take medication with meals",
            "educational_resources": ["ADA patient education materials"]
        },
        "model_used": "gpt-4-turbo-preview",
        "tokens_used": 1500,
        "confidence_score": 0.85
    })
    
    mock_client.validate_care_plan = AsyncMock(return_value={
        "is_valid": True,
        "safety_concerns": [],
        "completeness_score": 0.9
    })
    
    return mock_client


@pytest.fixture
def mock_ehr_client() -> MagicMock:
    """Create a mock EHR client."""
    mock_client = MagicMock(spec=EHRClient)
    mock_client.get_patient_record = AsyncMock(return_value=EHRRecord(
        patient_id="test_patient_123",
        record_id="ehr_test_patient_123_1234567890",
        mrn="MRN123456",
        diagnoses=[],
        lab_results=[],
        vital_signs=[],
        procedures=[]
    ))
    
    return mock_client


@pytest.fixture
def mock_vector_store() -> MagicMock:
    """Create a mock vector store."""
    mock_store = MagicMock(spec=VectorStore)
    mock_store.search = AsyncMock(return_value=[])
    mock_store.add_guidelines = AsyncMock()
    
    return mock_store


@pytest.fixture
def sample_patient_intake() -> PatientIntake:
    """Create a sample patient intake for testing."""
    return PatientIntake(
        patient_id="test_patient_123",
        age=45,
        gender="female",
        weight_kg=70.0,
        height_cm=165.0,
        chief_complaint="Elevated blood sugar levels and frequent urination",
        symptoms=[],
        medical_history=[],
        family_history=["diabetes", "hypertension"],
        allergies=["penicillin"],
        current_medications=[],
        smoking_status="never",
        alcohol_consumption="occasional",
        exercise_frequency="2-3 times per week"
    )


@pytest.fixture
def sample_care_plan() -> CarePlan:
    """Create a sample care plan for testing."""
    return CarePlan(
        careplan_id="cp_test_patient_123_1234567890",
        patient_id="test_patient_123",
        primary_diagnosis="Type 2 Diabetes Mellitus",
        chief_complaint="Elevated blood sugar levels",
        clinical_summary="Patient presents with classic symptoms of T2DM...",
        actions=[],
        short_term_goals=["Achieve glycemic control"],
        long_term_goals=["Prevent complications"],
        success_metrics=["HbA1c < 7%"],
        patient_instructions="Follow medication regimen and dietary recommendations",
        educational_resources=["Diabetes education materials"]
    )


@pytest.fixture
def mock_database():
    """Create a mock database for testing."""
    database = {
        "patient_intakes": {},
        "care_plans": {},
        "ehr_records": {},
        "reviews": {}
    }
    return database


@pytest.fixture(autouse=True)
def override_dependencies(
    mock_llm_client: MagicMock,
    mock_ehr_client: MagicMock,
    mock_vector_store: MagicMock
):
    """Override FastAPI dependencies with mocks for all tests."""
    from app.dependencies import get_llm_client, get_ehr_client, get_vector_store
    
    app.dependency_overrides[get_llm_client] = lambda: mock_llm_client
    app.dependency_overrides[get_ehr_client] = lambda: mock_ehr_client
    app.dependency_overrides[get_vector_store] = lambda: mock_vector_store
    
    yield
    
    # Clean up after tests
    app.dependency_overrides.clear()


# Test data fixtures
@pytest.fixture
def valid_intake_data():
    """Valid intake data for API testing."""
    return {
        "patient_id": "test_patient_123",
        "age": 45,
        "gender": "female",
        "chief_complaint": "Elevated blood sugar levels",
        "symptoms": [
            {
                "description": "Frequent urination",
                "severity": 7,
                "duration_days": 14
            }
        ],
        "medical_history": [
            {
                "condition": "Hypertension",
                "status": "active"
            }
        ],
        "allergies": ["penicillin"],
        "current_medications": [
            {
                "name": "Lisinopril",
                "dosage": "10mg",
                "frequency": "once daily",
                "active": True
            }
        ]
    }


@pytest.fixture
def invalid_intake_data():
    """Invalid intake data for testing validation."""
    return {
        "patient_id": "",  # Invalid: empty patient_id
        "age": -5,  # Invalid: negative age
        "gender": "female",
        "chief_complaint": ""  # Invalid: empty complaint
    }


# Mock environment variables
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("EHR_API_URL", "http://mock-ehr.test")
    monkeypatch.setenv("EHR_API_KEY", "test-ehr-key")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")


# Async test utilities
@pytest.fixture
async def cleanup_tasks():
    """Cleanup any remaining asyncio tasks after tests."""
    yield
    
    # Cancel any remaining tasks
    tasks = [task for task in asyncio.all_tasks() if not task.done()]
    for task in tasks:
        task.cancel()
    
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)