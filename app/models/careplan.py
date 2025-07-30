from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ActionType(str, Enum):
    MEDICATION = "medication"
    DIAGNOSTIC = "diagnostic"
    LIFESTYLE = "lifestyle"
    FOLLOWUP = "followup"
    MONITORING = "monitoring"
    REFERRAL = "referral"


class CarePlanAction(BaseModel):
    action_id: str
    action_type: ActionType
    description: str
    priority: Priority
    timeline: str = Field(description="immediate, within 1 week, within 1 month, etc.")
    rationale: str
    evidence_source: Optional[str] = None
    contraindications: List[str] = []
    
    # Action-specific details
    medication_details: Optional[Dict[str, Any]] = None
    diagnostic_details: Optional[Dict[str, Any]] = None
    referral_details: Optional[Dict[str, Any]] = None


class ClinicianReview(BaseModel):
    reviewer_id: str
    reviewer_name: str
    review_date: datetime
    status: str = Field(description="approved, needs_revision, rejected")
    comments: Optional[str] = None
    modifications: List[Dict[str, Any]] = []


class CarePlanStatus(str, Enum):
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    SENT_TO_PATIENT = "sent_to_patient"
    ACTIVE = "active"
    COMPLETED = "completed"


class CarePlan(BaseModel):
    careplan_id: str
    patient_id: str
    created_date: datetime = Field(default_factory=datetime.utcnow)
    last_modified: datetime = Field(default_factory=datetime.utcnow)
    
    # Plan metadata
    status: CarePlanStatus = CarePlanStatus.DRAFT
    version: int = 1
    
    # Clinical summary
    primary_diagnosis: str
    secondary_diagnoses: List[str] = []
    chief_complaint: str
    clinical_summary: str
    
    # Care plan actions
    actions: List[CarePlanAction] = []
    
    # Goals and outcomes
    short_term_goals: List[str] = []
    long_term_goals: List[str] = []
    success_metrics: List[str] = []
    
    # Review and approval
    clinician_reviews: List[ClinicianReview] = []
    final_approver: Optional[str] = None
    approval_date: Optional[datetime] = None
    
    # Patient communication
    patient_instructions: Optional[str] = None
    educational_resources: List[str] = []
    
    # AI generation metadata
    llm_model_used: Optional[str] = None
    generation_timestamp: Optional[datetime] = None
    confidence_score: Optional[float] = Field(ge=0.0, le=1.0)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }