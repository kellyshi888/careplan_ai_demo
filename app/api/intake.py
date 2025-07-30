from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from ..models.intake import PatientIntake
from ..dependencies import IntakeServiceDep
from ..logging.audit import audit_log

router = APIRouter(prefix="/api/intake", tags=["intake"])


@router.post("/submit", response_model=dict)
async def submit_intake(
    intake_data: PatientIntake,
    background_tasks: BackgroundTasks,
    intake_service: IntakeServiceDep
):
    """Submit patient intake data for processing"""
    try:
        result = await intake_service.process_intake(intake_data)
        
        background_tasks.add_task(
            audit_log,
            action="intake_submitted",
            patient_id=intake_data.patient_id,
            details={"intake_id": result["intake_id"]}
        )
        
        return {
            "status": "success",
            "intake_id": result["intake_id"],
            "message": "Intake data submitted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/validate/{patient_id}")
async def validate_intake(patient_id: str, intake_service: IntakeServiceDep):
    """Validate intake data completeness for care plan generation"""
    try:
        validation_result = await intake_service.validate_intake_completeness(patient_id)
        return validation_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{patient_id}/history")
async def get_intake_history(patient_id: str, intake_service: IntakeServiceDep):
    """Retrieve intake history for a patient"""
    try:
        history = await intake_service.get_intake_history(patient_id)
        return {"patient_id": patient_id, "intake_history": history}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Patient intake history not found")