import pytest
from datetime import datetime
from pydantic import ValidationError

from app.models.careplan import (
    CarePlan, CarePlanAction, ClinicianReview, 
    Priority, ActionType, CarePlanStatus
)


class TestCarePlanModels:
    """Test suite for care plan data models."""
    
    def test_care_plan_creation_minimal(self):
        """Test creating a care plan with minimal required fields."""
        care_plan = CarePlan(
            careplan_id="cp_test_123",
            patient_id="patient_123",
            primary_diagnosis="Type 2 Diabetes",
            chief_complaint="Elevated blood sugar",
            clinical_summary="Patient presents with symptoms of diabetes"
        )
        
        assert care_plan.careplan_id == "cp_test_123"
        assert care_plan.patient_id == "patient_123"
        assert care_plan.status == CarePlanStatus.DRAFT
        assert care_plan.version == 1
        assert isinstance(care_plan.created_date, datetime)
        assert len(care_plan.actions) == 0
        assert len(care_plan.clinician_reviews) == 0
    
    def test_care_plan_action_creation(self):
        """Test creating care plan actions."""
        action = CarePlanAction(
            action_id="action_1",
            action_type=ActionType.MEDICATION,
            description="Start Metformin 500mg twice daily",
            priority=Priority.HIGH,
            timeline="immediate",
            rationale="First-line therapy for T2DM"
        )
        
        assert action.action_type == ActionType.MEDICATION
        assert action.priority == Priority.HIGH
        assert action.description == "Start Metformin 500mg twice daily"
        assert action.contraindications == []
    
    def test_care_plan_with_actions(self):
        """Test care plan with multiple actions."""
        actions = [
            CarePlanAction(
                action_id="action_1",
                action_type=ActionType.MEDICATION,
                description="Start Metformin",
                priority=Priority.HIGH,
                timeline="immediate",
                rationale="First-line therapy"
            ),
            CarePlanAction(
                action_id="action_2",
                action_type=ActionType.DIAGNOSTIC,
                description="HbA1c test in 3 months",
                priority=Priority.MEDIUM,
                timeline="within 3 months",
                rationale="Monitor glycemic control"
            )
        ]
        
        care_plan = CarePlan(
            careplan_id="cp_test_123",
            patient_id="patient_123",
            primary_diagnosis="Type 2 Diabetes",
            chief_complaint="Elevated blood sugar",
            clinical_summary="Patient presents with diabetes",
            actions=actions
        )
        
        assert len(care_plan.actions) == 2
        assert care_plan.actions[0].action_type == ActionType.MEDICATION
        assert care_plan.actions[1].action_type == ActionType.DIAGNOSTIC
    
    def test_clinician_review_creation(self):
        """Test creating clinician reviews."""
        review = ClinicianReview(
            reviewer_id="dr_smith_123",
            reviewer_name="Dr. Sarah Smith",
            review_date=datetime.utcnow(),
            status="approved",
            comments="Care plan looks comprehensive and appropriate"
        )
        
        assert review.reviewer_id == "dr_smith_123"
        assert review.status == "approved"
        assert review.modifications == []
    
    def test_care_plan_with_reviews(self):
        """Test care plan with clinician reviews."""
        review1 = ClinicianReview(
            reviewer_id="dr_smith_123",
            reviewer_name="Dr. Sarah Smith",
            review_date=datetime.utcnow(),
            status="needs_revision",
            comments="Consider adding lifestyle modifications",
            modifications=[
                {"field": "actions", "operation": "append", "new_value": "lifestyle_action"}
            ]
        )
        
        review2 = ClinicianReview(
            reviewer_id="dr_jones_456",
            reviewer_name="Dr. John Jones",
            review_date=datetime.utcnow(),
            status="approved",
            comments="Revised plan looks good"
        )
        
        care_plan = CarePlan(
            careplan_id="cp_test_123",
            patient_id="patient_123",
            primary_diagnosis="Type 2 Diabetes",
            chief_complaint="Elevated blood sugar",
            clinical_summary="Patient presents with diabetes",
            clinician_reviews=[review1, review2]
        )
        
        assert len(care_plan.clinician_reviews) == 2
        assert care_plan.clinician_reviews[0].status == "needs_revision"
        assert care_plan.clinician_reviews[1].status == "approved"
        assert len(care_plan.clinician_reviews[0].modifications) == 1
    
    def test_care_plan_status_enum(self):
        """Test care plan status enumeration."""
        care_plan = CarePlan(
            careplan_id="cp_test_123",
            patient_id="patient_123",
            primary_diagnosis="Type 2 Diabetes",
            chief_complaint="Elevated blood sugar",
            clinical_summary="Patient presents with diabetes"
        )
        
        # Test default status
        assert care_plan.status == CarePlanStatus.DRAFT
        
        # Test status changes
        care_plan.status = CarePlanStatus.UNDER_REVIEW
        assert care_plan.status == CarePlanStatus.UNDER_REVIEW
        
        care_plan.status = CarePlanStatus.APPROVED
        assert care_plan.status == CarePlanStatus.APPROVED
    
    def test_action_type_enum(self):
        """Test action type enumeration."""
        action_types = [
            ActionType.MEDICATION,
            ActionType.DIAGNOSTIC,
            ActionType.LIFESTYLE,
            ActionType.FOLLOWUP,
            ActionType.MONITORING,
            ActionType.REFERRAL
        ]
        
        for action_type in action_types:
            action = CarePlanAction(
                action_id=f"action_{action_type.value}",
                action_type=action_type,
                description=f"Test {action_type.value} action",
                priority=Priority.MEDIUM,
                timeline="within 1 week",
                rationale="Test rationale"
            )
            assert action.action_type == action_type
    
    def test_priority_enum(self):
        """Test priority enumeration."""
        priorities = [Priority.HIGH, Priority.MEDIUM, Priority.LOW]
        
        for priority in priorities:
            action = CarePlanAction(
                action_id=f"action_{priority.value}",
                action_type=ActionType.MEDICATION,
                description="Test action",
                priority=priority,
                timeline="within 1 week",
                rationale="Test rationale"
            )
            assert action.priority == priority
    
    def test_care_plan_validation_required_fields(self):
        """Test validation of required fields."""
        with pytest.raises(ValidationError) as exc_info:
            CarePlan(
                # Missing required fields
                patient_id="patient_123"
            )
        
        errors = exc_info.value.errors()
        error_fields = [error["loc"][0] for error in errors]
        
        assert "careplan_id" in error_fields
        assert "primary_diagnosis" in error_fields
        assert "chief_complaint" in error_fields
        assert "clinical_summary" in error_fields
    
    def test_care_plan_json_serialization(self):
        """Test JSON serialization of care plan."""
        care_plan = CarePlan(
            careplan_id="cp_test_123",
            patient_id="patient_123",
            primary_diagnosis="Type 2 Diabetes",
            chief_complaint="Elevated blood sugar",
            clinical_summary="Patient presents with diabetes",
            short_term_goals=["Achieve HbA1c < 7%"],
            long_term_goals=["Prevent complications"],
            success_metrics=["HbA1c monitoring"],
            patient_instructions="Take medication as prescribed",
            educational_resources=["Diabetes education materials"]
        )
        
        # Test that the model can be serialized to JSON
        json_data = care_plan.model_dump()
        
        assert json_data["careplan_id"] == "cp_test_123"
        assert json_data["patient_id"] == "patient_123"
        assert json_data["status"] == "draft"
        assert isinstance(json_data["created_date"], str)  # Should be ISO format
        assert json_data["short_term_goals"] == ["Achieve HbA1c < 7%"]
    
    def test_care_plan_confidence_score_validation(self):
        """Test confidence score validation (0.0 to 1.0)."""
        # Valid confidence score
        care_plan = CarePlan(
            careplan_id="cp_test_123",
            patient_id="patient_123",
            primary_diagnosis="Type 2 Diabetes",
            chief_complaint="Elevated blood sugar",
            clinical_summary="Patient presents with diabetes",
            confidence_score=0.85
        )
        assert care_plan.confidence_score == 0.85
        
        # Invalid confidence score (too high)
        with pytest.raises(ValidationError):
            CarePlan(
                careplan_id="cp_test_123",
                patient_id="patient_123",
                primary_diagnosis="Type 2 Diabetes",
                chief_complaint="Elevated blood sugar",
                clinical_summary="Patient presents with diabetes",
                confidence_score=1.5
            )
        
        # Invalid confidence score (negative)
        with pytest.raises(ValidationError):
            CarePlan(
                careplan_id="cp_test_123",
                patient_id="patient_123",
                primary_diagnosis="Type 2 Diabetes",
                chief_complaint="Elevated blood sugar",
                clinical_summary="Patient presents with diabetes",
                confidence_score=-0.1
            )
    
    def test_care_plan_timestamps(self):
        """Test automatic timestamp generation."""
        care_plan = CarePlan(
            careplan_id="cp_test_123",
            patient_id="patient_123",
            primary_diagnosis="Type 2 Diabetes",
            chief_complaint="Elevated blood sugar",
            clinical_summary="Patient presents with diabetes"
        )
        
        assert isinstance(care_plan.created_date, datetime)
        assert isinstance(care_plan.last_modified, datetime)
        assert care_plan.created_date <= care_plan.last_modified
        
        # Test that generation_timestamp is set when provided
        generation_time = datetime.utcnow()
        care_plan.generation_timestamp = generation_time
        assert care_plan.generation_timestamp == generation_time