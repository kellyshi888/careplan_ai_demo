from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class LabResult(BaseModel):
    test_name: str
    value: str
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    status: Optional[str] = None  # normal, abnormal, critical
    test_date: datetime


class VitalSigns(BaseModel):
    temperature_f: Optional[float] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    heart_rate: Optional[int] = None
    respiratory_rate: Optional[int] = None
    oxygen_saturation: Optional[float] = None
    recorded_date: datetime


class Diagnosis(BaseModel):
    icd_10_code: Optional[str] = None
    description: str
    diagnosis_date: datetime
    status: str = Field(description="primary, secondary, rule_out")
    provider: Optional[str] = None


class Procedure(BaseModel):
    cpt_code: Optional[str] = None
    description: str
    procedure_date: datetime
    provider: Optional[str] = None
    notes: Optional[str] = None


class EHRRecord(BaseModel):
    patient_id: str
    record_id: str
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    # Patient demographics from EHR
    mrn: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    
    # Clinical data
    diagnoses: List[Diagnosis] = []
    procedures: List[Procedure] = []
    lab_results: List[LabResult] = []
    vital_signs: List[VitalSigns] = []
    
    # Provider notes
    provider_notes: List[Dict[str, Any]] = []
    
    # Insurance and administrative
    insurance_info: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }