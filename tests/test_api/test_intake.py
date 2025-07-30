import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.models.intake import PatientIntake


class TestIntakeAPI:
    """Test suite for intake API endpoints."""
    
    def test_submit_intake_success(self, client: TestClient, valid_intake_data: dict):
        """Test successful intake submission."""
        with patch('app.intake.service.IntakeService.process_intake') as mock_process:
            mock_process.return_value = {
                "intake_id": "intake_test_patient_123_1234567890",
                "patient_id": "test_patient_123",
                "processed_at": "2024-01-15T10:30:00Z",
                "validation_status": "passed"
            }
            
            response = client.post("/api/intake/submit", json=valid_intake_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "intake_id" in data
            assert data["message"] == "Intake data submitted successfully"
    
    def test_submit_intake_validation_error(self, client: TestClient, invalid_intake_data: dict):
        """Test intake submission with validation errors."""
        response = client.post("/api/intake/submit", json=invalid_intake_data)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data
    
    def test_submit_intake_missing_required_fields(self, client: TestClient):
        """Test intake submission with missing required fields."""
        incomplete_data = {
            "patient_id": "test_patient_123"
            # Missing required fields like age, gender, chief_complaint
        }
        
        response = client.post("/api/intake/submit", json=incomplete_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        
        # Check that validation errors mention missing fields
        error_fields = [error["loc"][-1] for error in data["detail"]]
        assert "age" in error_fields
        assert "gender" in error_fields
        assert "chief_complaint" in error_fields
    
    def test_validate_intake_success(self, client: TestClient):
        """Test successful intake validation."""
        patient_id = "test_patient_123"
        
        with patch('app.intake.service.IntakeService.validate_intake_completeness') as mock_validate:
            mock_validate.return_value = {
                "is_complete": True,
                "missing_fields": [],
                "completeness_score": 0.9,
                "recommendations": []
            }
            
            response = client.get(f"/api/intake/validate/{patient_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["is_complete"] is True
            assert data["completeness_score"] == 0.9
    
    def test_validate_intake_incomplete(self, client: TestClient):
        """Test intake validation with incomplete data."""
        patient_id = "test_patient_123"
        
        with patch('app.intake.service.IntakeService.validate_intake_completeness') as mock_validate:
            mock_validate.return_value = {
                "is_complete": False,
                "missing_fields": ["symptoms", "medical_history"],
                "completeness_score": 0.4,
                "recommendations": [
                    "Please provide detailed symptom information",
                    "Medical history is crucial for accurate care planning"
                ]
            }
            
            response = client.get(f"/api/intake/validate/{patient_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["is_complete"] is False
            assert len(data["missing_fields"]) == 2
            assert data["completeness_score"] == 0.4
            assert len(data["recommendations"]) == 2
    
    def test_get_intake_history_success(self, client: TestClient):
        """Test successful retrieval of intake history."""
        patient_id = "test_patient_123"
        
        with patch('app.intake.service.IntakeService.get_intake_history') as mock_history:
            mock_history.return_value = [
                {
                    "intake_id": "intake_1",
                    "intake_date": "2024-01-15T10:30:00Z",
                    "chief_complaint": "Elevated blood sugar",
                    "completeness_score": 0.9
                },
                {
                    "intake_id": "intake_2",
                    "intake_date": "2024-01-10T14:20:00Z",
                    "chief_complaint": "Follow-up consultation",
                    "completeness_score": 0.8
                }
            ]
            
            response = client.get(f"/api/intake/{patient_id}/history")
            
            assert response.status_code == 200
            data = response.json()
            assert data["patient_id"] == patient_id
            assert len(data["intake_history"]) == 2
            assert data["intake_history"][0]["intake_id"] == "intake_1"
    
    def test_get_intake_history_not_found(self, client: TestClient):
        """Test intake history retrieval for non-existent patient."""
        patient_id = "non_existent_patient"
        
        with patch('app.intake.service.IntakeService.get_intake_history') as mock_history:
            mock_history.side_effect = Exception("Patient intake history not found")
            
            response = client.get(f"/api/intake/{patient_id}/history")
            
            assert response.status_code == 404
            data = response.json()
            assert "not found" in data["detail"].lower()
    
    def test_intake_data_types_validation(self, client: TestClient):
        """Test data type validation for intake fields."""
        invalid_type_data = {
            "patient_id": "test_patient_123",
            "age": "forty-five",  # Should be integer
            "gender": "female",
            "weight_kg": "seventy",  # Should be float
            "chief_complaint": "Elevated blood sugar levels",
            "symptoms": [
                {
                    "description": "Frequent urination",
                    "severity": "high",  # Should be integer 1-10
                    "duration_days": "two weeks"  # Should be integer
                }
            ]
        }
        
        response = client.post("/api/intake/submit", json=invalid_type_data)
        
        assert response.status_code == 422
        data = response.json()
        error_fields = [error["loc"][-1] for error in data["detail"]]
        assert "age" in error_fields
        assert "weight_kg" in error_fields
    
    def test_intake_boundary_values(self, client: TestClient):
        """Test boundary value validation."""
        boundary_data = {
            "patient_id": "test_patient_123",
            "age": 0,  # Edge case: minimum age
            "gender": "male",
            "chief_complaint": "Test complaint",
            "symptoms": [
                {
                    "description": "Test symptom",
                    "severity": 11,  # Invalid: severity should be 1-10
                    "duration_days": -5  # Invalid: negative duration
                }
            ]
        }
        
        response = client.post("/api/intake/submit", json=boundary_data)
        
        assert response.status_code == 422
        data = response.json()
        
        # Check validation error for severity
        severity_errors = [
            error for error in data["detail"] 
            if "severity" in str(error["loc"])
        ]
        assert len(severity_errors) > 0
    
    @pytest.mark.asyncio
    async def test_intake_service_integration(self, sample_patient_intake: PatientIntake):
        """Test integration with intake service."""
        from app.intake.service import IntakeService
        
        service = IntakeService()
        
        # Mock the internal methods
        with patch.object(service, '_validate_intake_data') as mock_validate, \
             patch.object(service, '_store_intake') as mock_store:
            
            mock_validate.return_value = {"is_valid": True, "errors": []}
            mock_store.return_value = {"stored": True, "intake_id": "test_intake_id"}
            
            result = await service.process_intake(sample_patient_intake)
            
            assert "intake_id" in result
            assert result["patient_id"] == sample_patient_intake.patient_id
            assert result["validation_status"] == "passed"