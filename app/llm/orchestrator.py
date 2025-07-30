from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from pathlib import Path

from .client import LLMClient
from ..models.careplan import CarePlan, CarePlanAction, Priority, ActionType
from ..models.intake import PatientIntake
from ..models.ehr import EHRRecord
from ..models.guideline import Guideline
from ..ehr.client import EHRClient
from ..retrieval.vector_store import VectorStore


class CarePlanOrchestrator:
    """Orchestrates care plan generation using LLM, EHR, and guidelines"""
    
    def __init__(
        self,
        llm_client: LLMClient,
        ehr_client: EHRClient,
        vector_store: VectorStore
    ):
        self.llm_client = llm_client
        self.ehr_client = ehr_client
        self.vector_store = vector_store
        self.sample_data_path = Path(__file__).parent.parent.parent / "scripts" / "seed_data" / "sample_data.json"
        self._careplan_storage = {}  # In-memory storage for development
    
    def _load_sample_data(self) -> Dict[str, Any]:
        """Load sample data from JSON file."""
        try:
            if self.sample_data_path.exists():
                with open(self.sample_data_path, 'r') as f:
                    return json.load(f)
            return {"intakes": [], "patients": [], "care_plans": []}
        except Exception:
            return {"intakes": [], "patients": [], "care_plans": []}
    
    async def generate_careplan_draft(self, patient_id: str) -> Dict[str, Any]:
        """Generate complete care plan draft from patient intake data"""
        
        # 1. Retrieve patient intake data from sample data
        sample_data = self._load_sample_data()
        intake_data = None
        
        for intake in sample_data.get("intakes", []):
            if intake.get("patient_id") == patient_id:
                # Convert dict to PatientIntake model
                try:
                    intake_data = PatientIntake(**intake)
                    break
                except Exception as e:
                    print(f"Error converting intake data: {e}")
                    continue
        
        if not intake_data:
            raise ValueError(f"No intake data found for patient {patient_id}")
        
        # 2. Try to fetch EHR data (may not exist for sample data)
        ehr_data = None
        try:
            for ehr in sample_data.get("ehr_records", []):
                if ehr.get("patient_id") == patient_id:
                    ehr_data = EHRRecord(**ehr)
                    break
        except Exception as e:
            print(f"Warning: Could not load EHR data: {e}")
        
        # 3. Get mock clinical guidelines (simplified for now)
        guidelines = []
        
        # 4. Generate care plan using mock LLM (since we may not have API key)
        try:
            llm_result = await self.llm_client.generate_care_plan(
                intake_data, ehr_data, guidelines
            )
        except Exception as e:
            # Fallback to mock generation if LLM fails
            print(f"LLM generation failed, using mock: {e}")
            llm_result = self._generate_mock_care_plan(intake_data)
        
        # 5. Convert LLM output to structured CarePlan model
        care_plan = await self._convert_to_careplan_model(
            patient_id, llm_result["care_plan"], llm_result
        )
        
        # 6. Store the draft
        self._careplan_storage[care_plan.careplan_id] = care_plan
        
        return {
            "careplan_id": care_plan.careplan_id,
            "model_used": llm_result.get("model_used", "mock"),
            "tokens_used": llm_result.get("tokens_used", 0),
            "confidence_score": llm_result.get("confidence_score", 0.8),
            "created_at": care_plan.created_date.isoformat()
        }
    
    async def get_existing_draft(self, patient_id: str) -> Optional[CarePlan]:
        """Check for existing draft care plan"""
        # Check in-memory storage first
        for careplan_id, care_plan in self._careplan_storage.items():
            if care_plan.patient_id == patient_id:
                return care_plan
        
        # Check sample data for existing care plans
        sample_data = self._load_sample_data()
        for care_plan_data in sample_data.get("care_plans", []):
            if care_plan_data.get("patient_id") == patient_id:
                try:
                    return CarePlan(**care_plan_data)
                except Exception as e:
                    print(f"Error converting care plan data: {e}")
                    continue
        
        return None
    
    async def get_careplan_draft(self, careplan_id: str) -> Optional[CarePlan]:
        """Retrieve care plan draft by ID"""
        # Check in-memory storage first
        if careplan_id in self._careplan_storage:
            return self._careplan_storage[careplan_id]
        
        # Check sample data
        sample_data = self._load_sample_data()
        for care_plan_data in sample_data.get("care_plans", []):
            if care_plan_data.get("careplan_id") == careplan_id:
                try:
                    return CarePlan(**care_plan_data)
                except Exception as e:
                    print(f"Error converting care plan data: {e}")
                    continue
        
        return None
    
    async def regenerate_section(
        self,
        careplan_id: str,
        section: str,
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Regenerate a specific section of the care plan"""
        
        # 1. Retrieve existing care plan
        existing_plan = await self.get_careplan_draft(careplan_id)
        if not existing_plan:
            raise ValueError(f"Care plan {careplan_id} not found")
        
        # 2. Convert to dict for LLM processing
        existing_plan_dict = existing_plan.dict()
        
        # 3. Regenerate section using LLM
        updated_section = await self.llm_client.regenerate_section(
            section, existing_plan_dict, additional_context
        )
        
        # 4. Update the care plan
        updated_plan = await self._update_careplan_section(
            existing_plan, section, updated_section
        )
        
        # 5. Store updated plan
        await self._store_careplan_draft(updated_plan)
        
        return {
            "careplan_id": careplan_id,
            "updated_section": section,
            "updated_at": datetime.utcnow().isoformat()
        }
    
    async def _get_patient_intake(self, patient_id: str) -> Optional[PatientIntake]:
        """Retrieve patient intake data"""
        # Placeholder for database query
        # In real implementation, would query intake database
        return None
    
    async def _get_relevant_guidelines(
        self,
        intake_data: PatientIntake,
        ehr_data: Optional[EHRRecord]
    ) -> List[Guideline]:
        """Retrieve relevant clinical guidelines using vector search"""
        
        # Create search query from patient data
        search_text = self._build_guideline_search_query(intake_data, ehr_data)
        
        # Get query embedding (would use actual embedding service)
        query_embedding = await self._get_text_embedding(search_text)
        
        # Search vector store for relevant guidelines
        search_results = await self.vector_store.search(
            query_embedding, k=5
        )
        
        # Extract guidelines from results
        return [guideline for guideline, score in search_results if score > 0.7]
    
    def _build_guideline_search_query(
        self,
        intake_data: PatientIntake,
        ehr_data: Optional[EHRRecord]
    ) -> str:
        """Build search query for guideline retrieval"""
        query_parts = [
            f"chief complaint: {intake_data.chief_complaint}"
        ]
        
        # Add symptoms
        if intake_data.symptoms:
            symptoms_text = ", ".join([s.description for s in intake_data.symptoms])
            query_parts.append(f"symptoms: {symptoms_text}")
        
        # Add medical history
        if intake_data.medical_history:
            history_text = ", ".join([h.condition for h in intake_data.medical_history])
            query_parts.append(f"medical history: {history_text}")
        
        # Add EHR diagnoses if available
        if ehr_data and ehr_data.diagnoses:
            dx_text = ", ".join([dx.description for dx in ehr_data.diagnoses[-3:]])
            query_parts.append(f"recent diagnoses: {dx_text}")
        
        return " | ".join(query_parts)
    
    async def _get_text_embedding(self, text: str) -> List[float]:
        """Get text embedding for vector search"""
        # Placeholder - would use actual embedding service (OpenAI, etc.)
        # For now, return dummy embedding
        return [0.1] * 1536
    
    async def _convert_to_careplan_model(
        self,
        patient_id: str,
        llm_output: Dict[str, Any],
        llm_metadata: Dict[str, Any]
    ) -> CarePlan:
        """Convert LLM output to structured CarePlan model"""
        
        careplan_id = f"cp_{patient_id}_{int(datetime.utcnow().timestamp())}"
        
        # Convert actions
        actions = []
        for i, action_data in enumerate(llm_output.get("actions", [])):
            action = CarePlanAction(
                action_id=f"{careplan_id}_action_{i}",
                action_type=ActionType(action_data.get("type", "medication")),
                description=action_data.get("description", ""),
                priority=Priority(action_data.get("priority", "medium")),
                timeline=action_data.get("timeline", "within 1 week"),
                rationale=action_data.get("rationale", ""),
                evidence_source=action_data.get("evidence_source")
            )
            actions.append(action)
        
        return CarePlan(
            careplan_id=careplan_id,
            patient_id=patient_id,
            primary_diagnosis=llm_output.get("primary_diagnosis", ""),
            secondary_diagnoses=llm_output.get("secondary_diagnoses", []),
            chief_complaint=llm_output.get("chief_complaint", ""),
            clinical_summary=llm_output.get("clinical_summary", ""),
            actions=actions,
            short_term_goals=llm_output.get("short_term_goals", []),
            long_term_goals=llm_output.get("long_term_goals", []),
            success_metrics=llm_output.get("success_metrics", []),
            patient_instructions=llm_output.get("patient_instructions"),
            educational_resources=llm_output.get("educational_resources", []),
            llm_model_used=llm_metadata.get("model_used"),
            generation_timestamp=datetime.utcnow(),
            confidence_score=llm_metadata.get("confidence_score")
        )
    
    async def _store_careplan_draft(self, care_plan: CarePlan) -> Dict[str, Any]:
        """Store care plan draft in database"""
        # Placeholder for database storage
        return {"stored": True, "careplan_id": care_plan.careplan_id}
    
    async def _update_careplan_section(
        self,
        care_plan: CarePlan,
        section: str,
        updated_data: Dict[str, Any]
    ) -> CarePlan:
        """Update specific section of care plan"""
        
        # Create a copy of the care plan
        updated_plan = care_plan.copy(deep=True)
        updated_plan.last_modified = datetime.utcnow()
        updated_plan.version += 1
        
        # Update the specified section
        if hasattr(updated_plan, section):
            setattr(updated_plan, section, updated_data.get(section))
        
        return updated_plan
    
    def _generate_mock_care_plan(self, intake_data: PatientIntake) -> Dict[str, Any]:
        """Generate mock care plan when LLM is unavailable"""
        
        # Extract key information from intake
        chief_complaint = intake_data.chief_complaint
        age = intake_data.age
        gender = intake_data.gender
        
        # Generate realistic mock response based on chief complaint
        mock_actions = []
        mock_goals = []
        
        # Common conditions and their typical care plans
        if "diabetes" in chief_complaint.lower():
            mock_actions = [
                {
                    "type": "medication",
                    "description": "Continue Metformin 500mg twice daily",
                    "priority": "high",
                    "timeline": "ongoing",
                    "rationale": "Blood glucose management"
                },
                {
                    "type": "lifestyle",
                    "description": "Low-carb diet consultation with nutritionist",
                    "priority": "high",
                    "timeline": "within 2 weeks",
                    "rationale": "Dietary management essential for diabetes control"
                },
                {
                    "type": "monitoring",
                    "description": "HbA1c testing every 3 months",
                    "priority": "medium",
                    "timeline": "quarterly",
                    "rationale": "Monitor long-term glucose control"
                }
            ]
            mock_goals = [
                "Achieve HbA1c < 7%",
                "Maintain stable blood glucose levels",
                "Prevent diabetic complications"
            ]
            
        elif "hypertension" in chief_complaint.lower() or "blood pressure" in chief_complaint.lower():
            mock_actions = [
                {
                    "type": "medication",
                    "description": "Start ACE inhibitor (Lisinopril 10mg daily)",
                    "priority": "high",
                    "timeline": "immediately",
                    "rationale": "First-line treatment for hypertension"
                },
                {
                    "type": "lifestyle",
                    "description": "Reduce sodium intake to <2g/day",
                    "priority": "high",
                    "timeline": "ongoing",
                    "rationale": "Dietary sodium reduction improves BP control"
                },
                {
                    "type": "monitoring",
                    "description": "Home blood pressure monitoring twice daily",
                    "priority": "medium",
                    "timeline": "daily",
                    "rationale": "Track treatment response"
                }
            ]
            mock_goals = [
                "Achieve blood pressure <130/80 mmHg",
                "Reduce cardiovascular risk",
                "Maintain medication adherence"
            ]
            
        else:
            # Generic care plan for other conditions
            mock_actions = [
                {
                    "type": "diagnostic",
                    "description": f"Further evaluation of {chief_complaint}",
                    "priority": "high",
                    "timeline": "within 1 week",
                    "rationale": "Need additional information for proper diagnosis"
                },
                {
                    "type": "lifestyle",
                    "description": "General wellness consultation",
                    "priority": "medium",
                    "timeline": "within 2 weeks",
                    "rationale": "Address overall health optimization"
                }
            ]
            mock_goals = [
                "Establish accurate diagnosis",
                "Address patient concerns",
                "Develop comprehensive treatment plan"
            ]
        
        return {
            "care_plan": {
                "primary_diagnosis": chief_complaint,
                "secondary_diagnoses": [],
                "chief_complaint": chief_complaint,
                "clinical_summary": f"Patient presents with {chief_complaint}. Comprehensive evaluation and management plan developed.",
                "actions": mock_actions,
                "short_term_goals": mock_goals[:2],
                "long_term_goals": mock_goals[2:] if len(mock_goals) > 2 else ["Maintain optimal health"],
                "success_metrics": [
                    "Patient reports symptom improvement",
                    "Clinical markers within target range",
                    "Treatment adherence >80%"
                ],
                "patient_instructions": f"Follow prescribed treatment plan for {chief_complaint}. Contact provider with concerns.",
                "educational_resources": [
                    f"Patient education materials for {chief_complaint}",
                    "General wellness resources"
                ]
            },
            "model_used": "mock_generator",
            "tokens_used": 0,
            "confidence_score": 0.7
        }