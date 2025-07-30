from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class Symptom(BaseModel):
    description: str
    severity: int = Field(ge=1, le=10, description="Severity scale 1-10")
    duration_days: Optional[int] = None
    onset_date: Optional[datetime] = None


class MedicalHistory(BaseModel):
    condition: str
    diagnosis_date: Optional[datetime] = None
    status: str = Field(description="active, resolved, chronic")
    notes: Optional[str] = None


class Medication(BaseModel):
    name: str
    dosage: str
    frequency: str
    start_date: Optional[datetime] = None
    prescribing_physician: Optional[str] = None
    active: bool = True


class PatientIntake(BaseModel):
    patient_id: str
    intake_date: datetime = Field(default_factory=datetime.utcnow)
    
    # Demographics
    age: int
    gender: str
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    
    # Chief complaint and symptoms
    chief_complaint: str
    symptoms: List[Symptom] = []
    
    # Medical history
    medical_history: List[MedicalHistory] = []
    family_history: List[str] = []
    allergies: List[str] = []
    
    # Current medications
    current_medications: List[Medication] = []
    
    # Lifestyle factors
    smoking_status: Optional[str] = None
    alcohol_consumption: Optional[str] = None
    exercise_frequency: Optional[str] = None
    
    # Additional notes
    additional_notes: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }