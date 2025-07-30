from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx

from ..models.ehr import EHRRecord, LabResult, VitalSigns, Diagnosis


class EHRClient:
    """Client for fetching data from EHR systems (Epic, Cerner, etc.)"""
    
    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def get_patient_record(self, patient_id: str, mrn: Optional[str] = None) -> EHRRecord:
        """Fetch comprehensive patient record from EHR"""
        try:
            # Fetch different data types in parallel
            patient_info = await self._fetch_patient_demographics(patient_id, mrn)
            diagnoses = await self._fetch_diagnoses(patient_id)
            lab_results = await self._fetch_lab_results(patient_id)
            vital_signs = await self._fetch_vital_signs(patient_id)
            procedures = await self._fetch_procedures(patient_id)
            
            return EHRRecord(
                patient_id=patient_id,
                record_id=f"ehr_{patient_id}_{int(datetime.utcnow().timestamp())}",
                mrn=patient_info.get("mrn"),
                date_of_birth=patient_info.get("date_of_birth"),
                gender=patient_info.get("gender"),
                diagnoses=diagnoses,
                lab_results=lab_results,
                vital_signs=vital_signs,
                procedures=procedures
            )
            
        except Exception as e:
            raise Exception(f"Failed to fetch EHR data: {str(e)}")
    
    async def get_recent_labs(self, patient_id: str, days: int = 30) -> List[LabResult]:
        """Fetch recent laboratory results"""
        return await self._fetch_lab_results(patient_id, days_back=days)
    
    async def get_recent_vitals(self, patient_id: str, days: int = 7) -> List[VitalSigns]:
        """Fetch recent vital signs"""
        return await self._fetch_vital_signs(patient_id, days_back=days)
    
    async def search_diagnoses(self, patient_id: str, icd_codes: List[str]) -> List[Diagnosis]:
        """Search for specific diagnoses by ICD codes"""
        all_diagnoses = await self._fetch_diagnoses(patient_id)
        filtered_diagnoses = [
            dx for dx in all_diagnoses 
            if dx.icd_10_code in icd_codes
        ]
        return filtered_diagnoses
    
    async def _fetch_patient_demographics(self, patient_id: str, mrn: Optional[str]) -> Dict[str, Any]:
        """Fetch patient demographic information"""
        # Placeholder for actual EHR API call
        params = {"patient_id": patient_id}
        if mrn:
            params["mrn"] = mrn
            
        # Example API call structure
        # response = await self.client.get(
        #     f"{self.base_url}/patients/{patient_id}",
        #     headers={"Authorization": f"Bearer {self.api_key}"},
        #     params=params
        # )
        
        # Mock response for now
        return {
            "mrn": f"MRN{patient_id}",
            "date_of_birth": datetime(1985, 5, 15),
            "gender": "F"
        }
    
    async def _fetch_diagnoses(self, patient_id: str) -> List[Diagnosis]:
        """Fetch patient diagnoses from EHR"""
        # Placeholder for EHR API call
        # Mock data
        return [
            Diagnosis(
                icd_10_code="E11.9",
                description="Type 2 diabetes mellitus without complications",
                diagnosis_date=datetime(2023, 1, 15),
                status="primary",
                provider="Dr. Smith"
            )
        ]
    
    async def _fetch_lab_results(self, patient_id: str, days_back: int = 30) -> List[LabResult]:
        """Fetch laboratory results"""
        # Placeholder for EHR API call
        return [
            LabResult(
                test_name="HbA1c",
                value="7.2",
                unit="%",
                reference_range="< 7.0",
                status="abnormal",
                test_date=datetime(2024, 1, 10)
            )
        ]
    
    async def _fetch_vital_signs(self, patient_id: str, days_back: int = 7) -> List[VitalSigns]:
        """Fetch vital signs"""
        # Placeholder for EHR API call
        return [
            VitalSigns(
                temperature_f=98.6,
                blood_pressure_systolic=145,
                blood_pressure_diastolic=92,
                heart_rate=78,
                respiratory_rate=16,
                oxygen_saturation=98.5,
                recorded_date=datetime(2024, 1, 15)
            )
        ]
    
    async def _fetch_procedures(self, patient_id: str) -> List[Dict[str, Any]]:
        """Fetch procedures from EHR"""
        # Placeholder for EHR API call
        return []
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()