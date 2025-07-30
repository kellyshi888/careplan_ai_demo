from functools import lru_cache
from typing import Optional, Annotated
import os
from pydantic_settings import BaseSettings
from fastapi import Depends

from app.llm.client import LLMClient
from app.ehr.client import EHRClient
from app.retrieval.vector_store import VectorStore
from app.intake.service import IntakeService
from app.review.service import ReviewService
from app.llm.orchestrator import CarePlanOrchestrator


class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    app_name: str = "CarePlan AI"
    environment: str = "development"
    debug: bool = True
    
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4-turbo-preview"
    
    # EHR Integration
    ehr_api_url: str = "http://localhost:8080"
    ehr_api_key: str = ""
    
    # Database Configuration
    database_url: str = "postgresql://postgres:password@localhost:5432/careplan_db"
    
    # Vector Store Configuration
    vector_store_path: str = "/app/data/vector_store"
    vector_dimension: int = 1536
    
    # Logging Configuration
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        extra = "allow"  # Allow extra fields from environment


# Global instances to avoid recreating services on each request
_llm_client: Optional[LLMClient] = None
_ehr_client: Optional[EHRClient] = None
_vector_store: Optional[VectorStore] = None
_intake_service: Optional[IntakeService] = None
_review_service: Optional[ReviewService] = None
_orchestrator: Optional[CarePlanOrchestrator] = None


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


def get_llm_client() -> LLMClient:
    """Get LLM client dependency."""
    global _llm_client
    if _llm_client is None:
        settings = get_settings()
        _llm_client = LLMClient(
            api_key=settings.openai_api_key,
            model=settings.openai_model
        )
    return _llm_client


def get_ehr_client() -> EHRClient:
    """Get EHR client dependency."""
    global _ehr_client
    if _ehr_client is None:
        settings = get_settings()
        _ehr_client = EHRClient(
            base_url=settings.ehr_api_url,
            api_key=settings.ehr_api_key
        )
    return _ehr_client


def get_vector_store() -> VectorStore:
    """Get vector store dependency."""
    global _vector_store
    if _vector_store is None:
        settings = get_settings()
        _vector_store = VectorStore(dimension=settings.vector_dimension)
    return _vector_store


def get_intake_service() -> IntakeService:
    """Get intake service dependency."""
    global _intake_service
    if _intake_service is None:
        _intake_service = IntakeService()
    return _intake_service


def get_review_service() -> ReviewService:
    """Get review service dependency.""" 
    global _review_service
    if _review_service is None:
        _review_service = ReviewService()
    return _review_service


def get_careplan_orchestrator() -> CarePlanOrchestrator:
    """Get care plan orchestrator dependency."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = CarePlanOrchestrator(
            llm_client=get_llm_client(),
            ehr_client=get_ehr_client(),
            vector_store=get_vector_store()
        )
    return _orchestrator


# Type aliases for dependency injection
SettingsDep = Annotated[Settings, Depends(get_settings)]
LLMClientDep = Annotated[LLMClient, Depends(get_llm_client)]
EHRClientDep = Annotated[EHRClient, Depends(get_ehr_client)]
VectorStoreDep = Annotated[VectorStore, Depends(get_vector_store)]
IntakeServiceDep = Annotated[IntakeService, Depends(get_intake_service)]
ReviewServiceDep = Annotated[ReviewService, Depends(get_review_service)]
OrchestratorDep = Annotated[CarePlanOrchestrator, Depends(get_careplan_orchestrator)]