from typing import Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse

from ..dependencies import OrchestratorDep
from ..logging.audit import audit_log
from ..auth.middleware import get_current_active_user, require_patient_access
from ..models.auth import User

router = APIRouter(prefix="/api/draft", tags=["draft"])


@router.post("/generate/{patient_id}", response_model=dict)
async def generate_careplan_draft(
    patient_id: str,
    background_tasks: BackgroundTasks,
    orchestrator: OrchestratorDep,
    override_existing: bool = False,
    current_user: User = Depends(get_current_active_user)
):
    """Generate AI-powered care plan draft from patient intake data"""
    try:
        # Check patient access permissions
        from ..models.auth import UserRole
        if current_user.role == UserRole.PATIENT and current_user.patient_id != patient_id:
            raise HTTPException(
                status_code=403,
                detail="Access denied to patient data"
            )
        
        # Check for existing draft
        if not override_existing:
            existing_draft = await orchestrator.get_existing_draft(patient_id)
            if existing_draft:
                return {
                    "status": "exists",
                    "careplan_id": existing_draft.careplan_id,
                    "message": "Draft already exists. Use override_existing=true to regenerate."
                }
        
        # Generate new draft
        draft_result = await orchestrator.generate_careplan_draft(patient_id)
        
        # Log the generation
        background_tasks.add_task(
            audit_log,
            action="careplan_draft_generated",
            patient_id=patient_id,
            details={
                "careplan_id": draft_result["careplan_id"],
                "model_used": draft_result.get("model_used"),
                "confidence_score": draft_result.get("confidence_score")
            }
        )
        
        return {
            "status": "success",
            "careplan_id": draft_result["careplan_id"],
            "confidence_score": draft_result.get("confidence_score"),
            "message": "Care plan draft generated successfully"
        }
        
    except Exception as e:
        background_tasks.add_task(
            audit_log,
            action="careplan_generation_failed",
            patient_id=patient_id,
            details={"error": str(e)}
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{careplan_id}")
async def get_careplan_draft(careplan_id: str, orchestrator: OrchestratorDep):
    """Retrieve care plan draft by ID"""
    try:
        draft = await orchestrator.get_careplan_draft(careplan_id)
        if not draft:
            raise HTTPException(status_code=404, detail="Care plan draft not found")
        return draft
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{careplan_id}/regenerate")
async def regenerate_careplan_section(
    careplan_id: str,
    section: str,
    background_tasks: BackgroundTasks,
    orchestrator: OrchestratorDep,
    additional_context: Optional[str] = None
):
    """Regenerate a specific section of the care plan"""
    try:
        updated_draft = await orchestrator.regenerate_section(
            careplan_id, section, additional_context
        )
        
        background_tasks.add_task(
            audit_log,
            action="careplan_section_regenerated",
            careplan_id=careplan_id,
            details={"section": section, "additional_context": additional_context}
        )
        
        return {
            "status": "success",
            "careplan_id": careplan_id,
            "updated_section": section,
            "message": f"Section '{section}' regenerated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))