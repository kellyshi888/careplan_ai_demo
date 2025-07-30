import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

from app.llm.client import LLMClient
from app.models.intake import PatientIntake, Symptom
from app.models.ehr import EHRRecord
from app.models.guideline import Guideline


class TestLLMClient:
    """Test suite for LLM client functionality."""
    
    @pytest.fixture
    def llm_client(self):
        """Create LLM client instance for testing."""
        return LLMClient(api_key="test-api-key", model="gpt-4-turbo-preview")
    
    @pytest.fixture
    def mock_openai_response(self):
        """Mock OpenAI API response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "primary_diagnosis": "Type 2 Diabetes Mellitus",
            "secondary_diagnoses": ["Hypertension"],
            "clinical_summary": "45-year-old female with elevated blood sugar and classic symptoms of T2DM",
            "actions": [
                {
                    "type": "medication",
                    "description": "Start Metformin 500mg twice daily with meals",
                    "priority": "high",
                    "timeline": "immediate",
                    "rationale": "First-line therapy for T2DM, helps reduce glucose production"
                },
                {
                    "type": "diagnostic",
                    "description": "Order HbA1c test",
                    "priority": "high",
                    "timeline": "within 1 week",
                    "rationale": "Establish baseline glycemic control"
                }
            ],
            "short_term_goals": ["Achieve fasting glucose < 130 mg/dL"],
            "long_term_goals": ["Maintain HbA1c < 7%", "Prevent diabetic complications"],
            "success_metrics": ["HbA1c every 3 months", "Daily glucose monitoring"],
            "patient_instructions": "Take Metformin with meals to reduce GI side effects",
            "educational_resources": ["ADA diabetes education materials", "Nutritionist referral"]
        })
        mock_response.usage.total_tokens = 1500
        return mock_response
    
    @pytest.fixture
    def sample_patient_intake(self):
        """Sample patient intake data."""
        return PatientIntake(
            patient_id="test_patient_123",
            age=45,
            gender="female",
            chief_complaint="Elevated blood sugar levels and frequent urination",
            symptoms=[
                Symptom(
                    description="Frequent urination",
                    severity=7,
                    duration_days=14
                ),
                Symptom(
                    description="Excessive thirst",
                    severity=6,
                    duration_days=10
                )
            ]
        )
    
    @pytest.fixture
    def sample_guidelines(self):
        """Sample clinical guidelines."""
        return [
            Guideline(
                id="ada_dm_2023",
                content="ADA Standards of Care for Diabetes 2023: Metformin is first-line therapy...",
                metadata={"specialty": "endocrinology", "condition_codes": ["E11"]}
            ),
            Guideline(
                id="aha_htn_2022",
                content="AHA Hypertension Guidelines: BP targets for diabetic patients...",
                metadata={"specialty": "cardiology", "condition_codes": ["I10"]}
            )
        ]
    
    @pytest.mark.asyncio
    async def test_generate_care_plan_success(
        self, 
        llm_client: LLMClient,
        sample_patient_intake: PatientIntake,
        sample_guidelines: list,
        mock_openai_response: MagicMock
    ):
        """Test successful care plan generation."""
        with patch.object(llm_client.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_openai_response
            
            result = await llm_client.generate_care_plan(
                sample_patient_intake,
                ehr_data=None,
                relevant_guidelines=sample_guidelines
            )
            
            assert "care_plan" in result
            assert "model_used" in result
            assert "tokens_used" in result
            assert "confidence_score" in result
            
            care_plan = result["care_plan"]
            assert care_plan["primary_diagnosis"] == "Type 2 Diabetes Mellitus"
            assert len(care_plan["actions"]) == 2
            assert care_plan["actions"][0]["type"] == "medication"
            assert result["model_used"] == "gpt-4-turbo-preview"
            assert result["tokens_used"] == 1500
            assert 0.0 <= result["confidence_score"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_generate_care_plan_with_ehr_data(
        self,
        llm_client: LLMClient,
        sample_patient_intake: PatientIntake,
        mock_openai_response: MagicMock
    ):
        """Test care plan generation with EHR data."""
        ehr_data = EHRRecord(
            patient_id="test_patient_123",
            record_id="ehr_123",
            diagnoses=[],
            lab_results=[],
            vital_signs=[],
            procedures=[]
        )
        
        with patch.object(llm_client.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_openai_response
            
            result = await llm_client.generate_care_plan(
                sample_patient_intake,
                ehr_data=ehr_data,
                relevant_guidelines=[]
            )
            
            assert "care_plan" in result
            
            # Verify that EHR data was included in the prompt
            call_args = mock_create.call_args
            messages = call_args[1]["messages"]
            user_message = messages[1]["content"]
            assert "EHR DATA:" in user_message
    
    @pytest.mark.asyncio
    async def test_regenerate_section_success(
        self,
        llm_client: LLMClient,
        mock_openai_response: MagicMock
    ):
        """Test successful section regeneration."""
        existing_plan = {
            "primary_diagnosis": "Type 2 Diabetes",
            "actions": [
                {"type": "medication", "description": "Old medication plan"}
            ]
        }
        
        mock_section_response = MagicMock()
        mock_section_response.choices = [MagicMock()]
        mock_section_response.choices[0].message.content = json.dumps({
            "actions": [
                {
                    "type": "medication",
                    "description": "Updated medication plan with better dosing"
                }
            ]
        })
        
        with patch.object(llm_client.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_section_response
            
            result = await llm_client.regenerate_section(
                "actions",
                existing_plan,
                "Consider patient's kidney function"
            )
            
            assert "actions" in result
            assert result["actions"][0]["description"] == "Updated medication plan with better dosing"
    
    @pytest.mark.asyncio
    async def test_validate_care_plan_success(
        self,
        llm_client: LLMClient
    ):
        """Test successful care plan validation."""
        care_plan = {
            "primary_diagnosis": "Type 2 Diabetes",
            "actions": [
                {
                    "type": "medication",
                    "description": "Metformin 500mg twice daily"
                }
            ]
        }
        
        mock_validation_response = MagicMock()
        mock_validation_response.choices = [MagicMock()]
        mock_validation_response.choices[0].message.content = json.dumps({
            "is_valid": True,
            "safety_concerns": [],
            "drug_interactions": [],
            "completeness_score": 0.9,
            "recommendations": ["Consider adding lifestyle counseling"]
        })
        
        with patch.object(llm_client.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_validation_response
            
            result = await llm_client.validate_care_plan(care_plan)
            
            assert result["is_valid"] is True
            assert result["safety_concerns"] == []
            assert result["completeness_score"] == 0.9
    
    @pytest.mark.asyncio
    async def test_generate_care_plan_api_error(
        self,
        llm_client: LLMClient,
        sample_patient_intake: PatientIntake
    ):
        """Test handling of OpenAI API errors."""
        with patch.object(llm_client.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = Exception("OpenAI API rate limit exceeded")
            
            with pytest.raises(Exception) as exc_info:
                await llm_client.generate_care_plan(sample_patient_intake)
            
            assert "LLM generation failed" in str(exc_info.value)
    
    def test_build_system_prompt(self, llm_client: LLMClient):
        """Test system prompt construction."""
        system_prompt = llm_client._build_system_prompt()
        
        assert "clinical AI assistant" in system_prompt.lower()
        assert "evidence-based" in system_prompt.lower()
        assert "json format" in system_prompt.lower()
        assert "clinician review" in system_prompt.lower()
    
    def test_build_care_plan_prompt(
        self,
        llm_client: LLMClient,
        sample_patient_intake: PatientIntake,
        sample_guidelines: list
    ):
        """Test care plan prompt construction."""
        prompt = llm_client._build_care_plan_prompt(
            sample_patient_intake,
            ehr_data=None,
            guidelines=sample_guidelines
        )
        
        assert sample_patient_intake.patient_id in prompt
        assert sample_patient_intake.chief_complaint in prompt
        assert str(sample_patient_intake.age) in prompt
        assert sample_patient_intake.gender in prompt
        
        # Check that symptoms are included
        assert "SYMPTOMS:" in prompt
        assert "Frequent urination" in prompt
        
        # Check that guidelines are included
        assert "RELEVANT CLINICAL GUIDELINES:" in prompt
        assert "ADA Standards of Care" in prompt
    
    def test_calculate_confidence_score(self, llm_client: LLMClient):
        """Test confidence score calculation."""
        # Complete care plan
        complete_plan = {
            "primary_diagnosis": "Type 2 Diabetes",
            "clinical_summary": "Patient summary",
            "actions": [{"type": "medication", "description": "Metformin"}],
            "short_term_goals": ["Goal 1"],
            "long_term_goals": ["Goal 2"],
            "success_metrics": ["Metric 1"],
            "patient_instructions": "Instructions",
            "educational_resources": ["Resource 1"]
        }
        
        score = llm_client._calculate_confidence_score(complete_plan)
        assert score == 1.0
        
        # Incomplete care plan
        incomplete_plan = {
            "primary_diagnosis": "Type 2 Diabetes",
            "clinical_summary": "Patient summary",
            "actions": []
        }
        
        score = llm_client._calculate_confidence_score(incomplete_plan)
        assert 0.0 <= score < 1.0
    
    @pytest.mark.asyncio
    async def test_json_parsing_error(
        self,
        llm_client: LLMClient,
        sample_patient_intake: PatientIntake
    ):
        """Test handling of invalid JSON response."""
        mock_bad_response = MagicMock()
        mock_bad_response.choices = [MagicMock()]
        mock_bad_response.choices[0].message.content = "Invalid JSON response"
        mock_bad_response.usage.total_tokens = 1000
        
        with patch.object(llm_client.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_bad_response
            
            with pytest.raises(Exception) as exc_info:
                await llm_client.generate_care_plan(sample_patient_intake)
            
            assert "LLM generation failed" in str(exc_info.value)
    
    def test_llm_client_initialization(self):
        """Test LLM client initialization with different parameters."""
        # Test with default parameters
        client1 = LLMClient(api_key="test-key")
        assert client1.model == "gpt-4-turbo-preview"
        assert client1.temperature == 0.3
        assert client1.max_tokens == 4000
        
        # Test with custom parameters
        client2 = LLMClient(api_key="test-key", model="gpt-3.5-turbo")
        assert client2.model == "gpt-3.5-turbo"