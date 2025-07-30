from typing import List, Dict, Any, Optional, AsyncGenerator
import openai
from openai import AsyncOpenAI
import json
import asyncio

from ..models.intake import PatientIntake
from ..models.ehr import EHRRecord
from ..models.guideline import Guideline


class LLMClient:
    """OpenAI GPT-4 client for care plan generation"""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.max_tokens = 4000
        self.temperature = 0.3  # Lower temperature for more consistent medical advice
    
    async def generate_care_plan(
        self,
        patient_intake: PatientIntake,
        ehr_data: Optional[EHRRecord] = None,
        relevant_guidelines: List[Guideline] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive care plan from patient data"""
        
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_care_plan_prompt(
            patient_intake, ehr_data, relevant_guidelines
        )
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                "care_plan": result,
                "model_used": self.model,
                "tokens_used": response.usage.total_tokens,
                "confidence_score": self._calculate_confidence_score(result)
            }
            
        except Exception as e:
            raise Exception(f"LLM generation failed: {str(e)}")
    
    async def regenerate_section(
        self,
        section_name: str,
        existing_plan: Dict[str, Any],
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Regenerate a specific section of the care plan"""
        
        system_prompt = f"""You are a clinical AI assistant helping to refine a care plan.
        You need to regenerate the '{section_name}' section while maintaining consistency 
        with the rest of the plan."""
        
        user_prompt = f"""
        Current care plan: {json.dumps(existing_plan, indent=2)}
        
        Please regenerate only the '{section_name}' section.
        {f'Additional context: {additional_context}' if additional_context else ''}
        
        Return the updated section in JSON format.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1500,
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            raise Exception(f"Section regeneration failed: {str(e)}")
    
    async def validate_care_plan(self, care_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Validate care plan for safety and completeness"""
        
        system_prompt = """You are a medical safety validator. Review the care plan for:
        1. Drug interactions and contraindications
        2. Dosage appropriateness
        3. Missing critical assessments
        4. Safety concerns
        
        Return a validation report in JSON format."""
        
        user_prompt = f"Care plan to validate: {json.dumps(care_plan, indent=2)}"
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            raise Exception(f"Care plan validation failed: {str(e)}")
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for care plan generation"""
        return """You are an expert clinical AI assistant specializing in personalized care plan generation.
        
        Your role is to:
        1. Analyze patient intake data and medical history
        2. Consider relevant clinical guidelines and evidence
        3. Generate comprehensive, personalized care plans
        4. Ensure all recommendations are evidence-based and safe
        5. Include appropriate monitoring and follow-up instructions
        
        Always provide your response in structured JSON format with the following sections:
        - primary_diagnosis
        - secondary_diagnoses
        - clinical_summary
        - actions (with priority, timeline, and rationale)
        - short_term_goals
        - long_term_goals
        - success_metrics
        - patient_instructions
        - educational_resources
        
        Remember: This is a draft for clinician review, not final medical advice."""
    
    def _build_care_plan_prompt(
        self,
        patient_intake: PatientIntake,
        ehr_data: Optional[EHRRecord],
        guidelines: Optional[List[Guideline]]
    ) -> str:
        """Build the user prompt with patient data"""
        
        prompt_parts = [
            "Generate a personalized care plan based on the following patient information:",
            "",
            "PATIENT INTAKE DATA:",
            f"Patient ID: {patient_intake.patient_id}",
            f"Age: {patient_intake.age}, Gender: {patient_intake.gender}",
            f"Chief Complaint: {patient_intake.chief_complaint}",
            ""
        ]
        
        # Add symptoms
        if patient_intake.symptoms:
            prompt_parts.append("SYMPTOMS:")
            for symptom in patient_intake.symptoms:
                prompt_parts.append(f"- {symptom.description} (severity: {symptom.severity}/10)")
            prompt_parts.append("")
        
        # Add medical history
        if patient_intake.medical_history:
            prompt_parts.append("MEDICAL HISTORY:")
            for history in patient_intake.medical_history:
                prompt_parts.append(f"- {history.condition} ({history.status})")
            prompt_parts.append("")
        
        # Add current medications
        if patient_intake.current_medications:
            prompt_parts.append("CURRENT MEDICATIONS:")
            for med in patient_intake.current_medications:
                prompt_parts.append(f"- {med.name} {med.dosage} {med.frequency}")
            prompt_parts.append("")
        
        # Add EHR data if available
        if ehr_data:
            prompt_parts.append("EHR DATA:")
            if ehr_data.diagnoses:
                prompt_parts.append("Recent Diagnoses:")
                for dx in ehr_data.diagnoses[-5:]:  # Last 5 diagnoses
                    prompt_parts.append(f"- {dx.description} ({dx.diagnosis_date.strftime('%Y-%m-%d')})")
            
            if ehr_data.lab_results:
                prompt_parts.append("Recent Lab Results:")
                for lab in ehr_data.lab_results[-5:]:  # Last 5 results
                    prompt_parts.append(f"- {lab.test_name}: {lab.value} {lab.unit or ''} ({lab.status})")
            prompt_parts.append("")
        
        # Add relevant guidelines
        if guidelines:
            prompt_parts.append("RELEVANT CLINICAL GUIDELINES:")
            for guideline in guidelines[:3]:  # Top 3 most relevant
                prompt_parts.append(f"- {guideline.content[:200]}...")
            prompt_parts.append("")
        
        prompt_parts.append("Please generate a comprehensive care plan in JSON format.")
        
        return "\n".join(prompt_parts)
    
    def _calculate_confidence_score(self, care_plan: Dict[str, Any]) -> float:
        """Calculate confidence score based on plan completeness"""
        score = 0.0
        total_components = 8
        
        required_sections = [
            "primary_diagnosis", "clinical_summary", "actions",
            "short_term_goals", "long_term_goals", "success_metrics",
            "patient_instructions", "educational_resources"
        ]
        
        for section in required_sections:
            if section in care_plan and care_plan[section]:
                score += 1.0
        
        return score / total_components