from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import os
from pathlib import Path

from ..models.intake import PatientIntake


class IntakeService:
    """Service for processing patient intake data"""
    
    def __init__(self):
        # Path to sample data
        self.sample_data_path = Path(__file__).parent.parent.parent / "scripts" / "seed_data" / "sample_data.json"
        self._intake_storage = {}  # In-memory storage for development
    
    def _load_sample_data(self) -> Dict[str, Any]:
        """Load sample data from JSON file."""
        try:
            if self.sample_data_path.exists():
                with open(self.sample_data_path, 'r') as f:
                    return json.load(f)
            return {"intakes": [], "patients": []}
        except Exception:
            return {"intakes": [], "patients": []}
    
    async def process_intake(self, intake_data: PatientIntake) -> Dict[str, Any]:
        """Process and validate patient intake data"""
        intake_id = f"intake_{intake_data.patient_id}_{int(datetime.utcnow().timestamp())}"
        
        # Validate required fields
        validation_result = await self._validate_intake_data(intake_data)
        if not validation_result["is_valid"]:
            raise ValueError(f"Invalid intake data: {validation_result['errors']}")
        
        # Store intake data in memory for development
        self._intake_storage[intake_id] = {
            "intake_id": intake_id,
            "patient_id": intake_data.patient_id,
            "intake_data": intake_data.dict(),
            "processed_at": datetime.utcnow().isoformat(),
            "validation_status": "passed"
        }
        
        return {
            "intake_id": intake_id,
            "patient_id": intake_data.patient_id,
            "processed_at": datetime.utcnow().isoformat(),
            "validation_status": "passed"
        }
    
    async def validate_intake_completeness(self, patient_id: str) -> Dict[str, Any]:
        """Validate if intake data is complete enough for care plan generation"""
        # First check in-memory storage
        intake_data = None
        for stored_intake in self._intake_storage.values():
            if stored_intake["patient_id"] == patient_id:
                intake_data = stored_intake["intake_data"]
                break
        
        # If not found in memory, check sample data
        if not intake_data:
            sample_data = self._load_sample_data()
            for intake in sample_data.get("intakes", []):
                if intake.get("patient_id") == patient_id:
                    intake_data = intake
                    break
        
        if not intake_data:
            return {
                "is_complete": False,
                "missing_fields": ["No intake data found"],
                "completeness_score": 0.0
            }
        
        missing_fields = []
        score = 0.0
        total_fields = 8  # Updated count
        
        # Check essential fields
        if not intake_data.get("chief_complaint"):
            missing_fields.append("chief_complaint")
        else:
            score += 1
            
        if not intake_data.get("symptoms") or len(intake_data.get("symptoms", [])) == 0:
            missing_fields.append("symptoms")
        else:
            score += 1
            
        if not intake_data.get("medical_history") or len(intake_data.get("medical_history", [])) == 0:
            missing_fields.append("medical_history")
        else:
            score += 1
            
        if not intake_data.get("current_medications"):
            missing_fields.append("current_medications")
        else:
            score += 1
            
        if not intake_data.get("allergies"):
            missing_fields.append("allergies")
        else:
            score += 1
            
        if not intake_data.get("age") or intake_data.get("age", 0) <= 0:
            missing_fields.append("age")
        else:
            score += 1
            
        if not intake_data.get("gender"):
            missing_fields.append("gender")
        else:
            score += 1
            
        if not intake_data.get("family_history"):
            missing_fields.append("family_history")
        else:
            score += 1
            
        completeness_score = score / total_fields
        
        return {
            "is_complete": completeness_score >= 0.7,
            "missing_fields": missing_fields,
            "completeness_score": completeness_score,
            "recommendations": self._get_completion_recommendations(missing_fields)
        }
    
    async def get_intake_history(self, patient_id: str) -> List[Dict[str, Any]]:
        """Retrieve intake history for a patient"""
        history = []
        
        # Get from in-memory storage
        for stored_intake in self._intake_storage.values():
            if stored_intake["patient_id"] == patient_id:
                history.append({
                    "intake_id": stored_intake["intake_id"],
                    "intake_date": stored_intake["processed_at"],
                    "chief_complaint": stored_intake["intake_data"].get("chief_complaint"),
                    "completeness_score": 1.0  # Stored intakes are assumed complete
                })
        
        # Also get from sample data
        sample_data = self._load_sample_data()
        for intake in sample_data.get("intakes", []):
            if intake.get("patient_id") == patient_id:
                history.append({
                    "intake_id": f"sample_{patient_id}",
                    "intake_date": intake.get("intake_date", datetime.utcnow().isoformat()),
                    "chief_complaint": intake.get("chief_complaint"),
                    "completeness_score": 0.9
                })
        
        return sorted(history, key=lambda x: x["intake_date"], reverse=True)
    
    async def _validate_intake_data(self, intake_data: PatientIntake) -> Dict[str, Any]:
        """Internal validation of intake data"""
        errors = []
        
        if not intake_data.chief_complaint.strip():
            errors.append("Chief complaint cannot be empty")
        
        if intake_data.age < 0 or intake_data.age > 150:
            errors.append("Age must be between 0 and 150")
        
        # Add more validation rules...
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
    
    async def _store_intake(self, intake_id: str, intake_data: PatientIntake) -> Dict[str, Any]:
        """Store intake data in database"""
        # Placeholder for database storage
        return {"stored": True, "intake_id": intake_id}
    
    async def _get_latest_intake(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve latest intake data for patient"""
        # Placeholder for database query
        return None
    
    def _get_completion_recommendations(self, missing_fields: List[str]) -> List[str]:
        """Get recommendations for completing intake"""
        recommendations = []
        
        if "symptoms" in missing_fields:
            recommendations.append("Please provide detailed symptom information")
        
        if "medical_history" in missing_fields:
            recommendations.append("Medical history is crucial for accurate care planning")
        
        return recommendations