from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class EvidenceLevel(BaseModel):
    level: str = Field(description="A, B, C evidence levels")
    description: str
    source: Optional[str] = None


class Recommendation(BaseModel):
    text: str
    evidence_level: EvidenceLevel
    category: str = Field(description="diagnostic, therapeutic, monitoring")
    contraindications: List[str] = []
    prerequisites: List[str] = []


class ClinicalGuideline(BaseModel):
    guideline_id: str
    title: str
    organization: str = Field(description="Publishing organization (AHA, ADA, etc.)")
    version: str
    publication_date: datetime
    last_updated: datetime
    
    # Clinical context
    condition_codes: List[str] = Field(description="ICD-10 codes this applies to")
    patient_population: str = Field(description="Adult, pediatric, geriatric, etc.")
    
    # Content
    summary: str
    recommendations: List[Recommendation] = []
    
    # Metadata for retrieval
    keywords: List[str] = []
    specialty: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Guideline(BaseModel):
    """Simplified guideline model for vector retrieval"""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding_vector: Optional[List[float]] = None
    
    class Config:
        arbitrary_types_allowed = True