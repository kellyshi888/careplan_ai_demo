from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel
import json
from pathlib import Path

from ..models.careplan import CarePlan, ClinicianReview, CarePlanStatus


class ReviewRequest(BaseModel):
    reviewer_id: str
    reviewer_name: str
    status: str
    comments: Optional[str] = None
    modifications: List[dict] = []


class ApprovalRequest(BaseModel):
    approver_id: str
    approver_name: str
    final_comments: Optional[str] = None


class ReviewService:
    """Service for managing clinician review and approval workflow"""
    
    def __init__(self):
        self.sample_data_path = Path(__file__).parent.parent.parent / "scripts" / "seed_data" / "sample_data.json"
        self._review_storage = {}  # In-memory storage for development
    
    async def get_pending_reviews(self, reviewer_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all care plans pending review"""
        # Placeholder for database query
        # Would filter by reviewer_id if provided for assigned reviews
        
        # Mock data for demonstration
        pending_plans = [
            {
                "careplan_id": "cp_patient123_1234567890",
                "patient_id": "patient123",
                "created_date": "2024-01-15T10:30:00Z",
                "primary_diagnosis": "Type 2 Diabetes Mellitus",
                "chief_complaint": "Elevated blood sugar levels",
                "status": "draft",
                "confidence_score": 0.85,
                "assigned_reviewer": reviewer_id if reviewer_id else None
            }
        ]
        
        return pending_plans
    
    async def submit_review(
        self,
        careplan_id: str,
        review_request: ReviewRequest
    ) -> Dict[str, Any]:
        """Submit clinician review for a care plan"""
        
        # 1. Retrieve the care plan
        care_plan = await self._get_careplan(careplan_id)
        if not care_plan:
            raise ValueError(f"Care plan {careplan_id} not found")
        
        # 2. Create review record
        review = ClinicianReview(
            reviewer_id=review_request.reviewer_id,
            reviewer_name=review_request.reviewer_name,
            review_date=datetime.utcnow(),
            status=review_request.status,
            comments=review_request.comments,
            modifications=review_request.modifications
        )
        
        # 3. Update care plan with review
        updated_plan = await self._add_review_to_careplan(care_plan, review)
        
        # 4. Update care plan status based on review
        if review_request.status == "approved":
            updated_plan.status = CarePlanStatus.APPROVED
        elif review_request.status == "needs_revision":
            updated_plan.status = CarePlanStatus.UNDER_REVIEW
        elif review_request.status == "rejected":
            updated_plan.status = CarePlanStatus.DRAFT
        
        # 5. Apply modifications if any
        if review_request.modifications:
            updated_plan = await self._apply_modifications(
                updated_plan, review_request.modifications
            )
        
        # 6. Store updated care plan
        await self._store_careplan(updated_plan)
        
        return {
            "careplan_id": careplan_id,
            "review_status": review_request.status,
            "reviewer": review_request.reviewer_name,
            "reviewed_at": review.review_date.isoformat(),
            "modifications_applied": len(review_request.modifications)
        }
    
    async def approve_careplan(
        self,
        careplan_id: str,
        approval_request: ApprovalRequest
    ) -> Dict[str, Any]:
        """Final approval of care plan for patient delivery"""
        
        # 1. Retrieve the care plan
        care_plan = await self._get_careplan(careplan_id)
        if not care_plan:
            raise ValueError(f"Care plan {careplan_id} not found")
        
        # 2. Verify care plan is ready for approval
        if care_plan.status not in [CarePlanStatus.APPROVED, CarePlanStatus.UNDER_REVIEW]:
            raise ValueError(f"Care plan {careplan_id} is not ready for final approval")
        
        # 3. Update care plan with final approval
        care_plan.final_approver = approval_request.approver_id
        care_plan.approval_date = datetime.utcnow()
        care_plan.status = CarePlanStatus.APPROVED
        
        # 4. Add final approval comments if provided
        if approval_request.final_comments:
            final_review = ClinicianReview(
                reviewer_id=approval_request.approver_id,
                reviewer_name=approval_request.approver_name,
                review_date=datetime.utcnow(),
                status="approved",
                comments=approval_request.final_comments
            )
            care_plan.clinician_reviews.append(final_review)
        
        # 5. Store updated care plan
        await self._store_careplan(care_plan)
        
        return {
            "careplan_id": careplan_id,
            "approved_by": approval_request.approver_name,
            "approved_at": care_plan.approval_date.isoformat(),
            "status": "approved_for_patient_delivery"
        }
    
    async def get_review_history(self, careplan_id: str) -> List[Dict[str, Any]]:
        """Get complete review history for a care plan"""
        
        care_plan = await self._get_careplan(careplan_id)
        if not care_plan:
            raise ValueError(f"Care plan {careplan_id} not found")
        
        history = []
        for review in care_plan.clinician_reviews:
            history.append({
                "reviewer_id": review.reviewer_id,
                "reviewer_name": review.reviewer_name,
                "review_date": review.review_date.isoformat(),
                "status": review.status,
                "comments": review.comments,
                "modifications_count": len(review.modifications)
            })
        
        return sorted(history, key=lambda x: x["review_date"])
    
    async def send_to_patient(self, careplan_id: str) -> Dict[str, Any]:
        """Send approved care plan to patient"""
        
        # 1. Retrieve and validate care plan
        care_plan = await self._get_careplan(careplan_id)
        if not care_plan:
            raise ValueError(f"Care plan {careplan_id} not found")
        
        if care_plan.status != CarePlanStatus.APPROVED:
            raise ValueError(f"Care plan {careplan_id} is not approved for patient delivery")
        
        # 2. Format care plan for patient consumption
        patient_care_plan = await self._format_for_patient(care_plan)
        
        # 3. Send via patient portal/communication system
        delivery_result = await self._deliver_to_patient(
            care_plan.patient_id, patient_care_plan
        )
        
        # 4. Update care plan status
        care_plan.status = CarePlanStatus.SENT_TO_PATIENT
        await self._store_careplan(care_plan)
        
        return {
            "careplan_id": careplan_id,
            "patient_id": care_plan.patient_id,
            "delivered_at": datetime.utcnow().isoformat(),
            "delivery_method": delivery_result.get("method", "patient_portal"),
            "status": "delivered_to_patient"
        }
    
    def _load_sample_data(self) -> Dict[str, Any]:
        """Load sample data from JSON file."""
        try:
            if self.sample_data_path.exists():
                with open(self.sample_data_path, 'r') as f:
                    return json.load(f)
            return {"intakes": [], "patients": [], "care_plans": []}
        except Exception:
            return {"intakes": [], "patients": [], "care_plans": []}
    
    async def _get_careplan(self, careplan_id: str) -> Optional[CarePlan]:
        """Retrieve care plan from database"""
        # Check in-memory storage first (from orchestrator)
        if careplan_id in self._review_storage:
            return self._review_storage[careplan_id]
        
        # Check sample data
        sample_data = self._load_sample_data()
        for care_plan_data in sample_data.get("care_plans", []):
            if care_plan_data.get("careplan_id") == careplan_id:
                try:
                    return CarePlan(**care_plan_data)
                except Exception as e:
                    print(f"Error converting care plan data: {e}")
                    continue
        
        # Try to get from orchestrator (shared storage would be better in production)
        # For now, create a mock care plan if not found
        if careplan_id.startswith("cp_"):
            return self._create_mock_careplan(careplan_id)
        
        return None
    
    def _create_mock_careplan(self, careplan_id: str) -> CarePlan:
        """Create a mock care plan for development/testing"""
        from ..models.careplan import CarePlanAction, Priority, ActionType
        
        # Extract patient_id from careplan_id if possible
        parts = careplan_id.split("_")
        patient_id = parts[1] if len(parts) > 1 else "unknown_patient"
        
        mock_actions = [
            CarePlanAction(
                action_id=f"{careplan_id}_action_0",
                action_type=ActionType.MEDICATION,
                description="Continue current medication regimen",
                priority=Priority.HIGH,
                timeline="ongoing",
                rationale="Maintain therapeutic levels"
            )
        ]
        
        return CarePlan(
            careplan_id=careplan_id,
            patient_id=patient_id,
            primary_diagnosis="General Care Plan", 
            secondary_diagnoses=[],
            chief_complaint="Routine care management",
            clinical_summary="Mock care plan for testing purposes",
            actions=mock_actions,
            short_term_goals=["Maintain current health status"],
            long_term_goals=["Optimize overall wellness"],
            success_metrics=["Patient compliance with recommendations"],
            patient_instructions="Follow care plan as outlined",
            educational_resources=["General health education materials"],
            llm_model_used="mock_model",
            generation_timestamp=datetime.utcnow(),
            confidence_score=0.8
        )
    
    async def _add_review_to_careplan(
        self, care_plan: CarePlan, review: ClinicianReview
    ) -> CarePlan:
        """Add review to care plan"""
        care_plan.clinician_reviews.append(review)
        care_plan.last_modified = datetime.utcnow()
        return care_plan
    
    async def _apply_modifications(
        self, care_plan: CarePlan, modifications: List[Dict[str, Any]]
    ) -> CarePlan:
        """Apply clinician modifications to care plan"""
        
        for modification in modifications:
            field = modification.get("field")
            new_value = modification.get("new_value")
            operation = modification.get("operation", "replace")
            
            if hasattr(care_plan, field):
                if operation == "replace":
                    setattr(care_plan, field, new_value)
                elif operation == "append" and isinstance(getattr(care_plan, field), list):
                    getattr(care_plan, field).append(new_value)
                elif operation == "remove" and isinstance(getattr(care_plan, field), list):
                    current_list = getattr(care_plan, field)
                    if new_value in current_list:
                        current_list.remove(new_value)
        
        care_plan.version += 1
        care_plan.last_modified = datetime.utcnow()
        return care_plan
    
    async def _store_careplan(self, care_plan: CarePlan) -> Dict[str, Any]:
        """Store care plan in database"""
        # Store in memory for development
        self._review_storage[care_plan.careplan_id] = care_plan
        
        # In production, would store in actual database
        return {
            "stored": True,
            "careplan_id": care_plan.careplan_id,
            "stored_at": datetime.utcnow().isoformat()
        }
    
    async def _format_for_patient(self, care_plan: CarePlan) -> Dict[str, Any]:
        """Format care plan for patient consumption"""
        
        # Simplify medical terminology and focus on actionable items
        patient_format = {
            "summary": care_plan.clinical_summary,
            "your_care_plan": {
                "primary_condition": care_plan.primary_diagnosis,
                "what_you_need_to_do": [
                    {
                        "action": action.description,
                        "priority": action.priority.value,
                        "when": action.timeline,
                        "why": action.rationale
                    }
                    for action in care_plan.actions
                ],
                "your_goals": {
                    "short_term": care_plan.short_term_goals,
                    "long_term": care_plan.long_term_goals
                },
                "how_we_measure_success": care_plan.success_metrics
            },
            "instructions": care_plan.patient_instructions,
            "helpful_resources": care_plan.educational_resources,
            "care_plan_date": care_plan.created_date.strftime("%B %d, %Y")
        }
        
        return patient_format
    
    async def _deliver_to_patient(
        self, patient_id: str, patient_care_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deliver care plan to patient via portal/email/SMS"""
        
        # Placeholder for actual delivery mechanism
        # Could integrate with patient portal API, email service, etc.
        
        return {
            "method": "patient_portal",
            "delivered_at": datetime.utcnow().isoformat(),
            "confirmation_id": f"delivery_{patient_id}_{int(datetime.utcnow().timestamp())}"
        }