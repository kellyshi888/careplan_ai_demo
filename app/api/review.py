from typing import List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks

from ..dependencies import ReviewServiceDep
from ..review.service import ReviewRequest, ApprovalRequest
from ..logging.audit import audit_log

router = APIRouter(prefix="/api/review", tags=["review"])


@router.get("/pending")
async def get_pending_reviews(
    review_service: ReviewServiceDep,
    reviewer_id: Optional[str] = None
):
    """Get all care plans pending review"""
    try:
        pending_plans = await review_service.get_pending_reviews(reviewer_id)
        return {
            "status": "success",
            "pending_count": len(pending_plans),
            "care_plans": pending_plans
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{careplan_id}/review")
async def submit_review(
    careplan_id: str,
    review_request: ReviewRequest,
    background_tasks: BackgroundTasks,
    review_service: ReviewServiceDep
):
    """Submit clinician review for a care plan draft"""
    try:
        review_result = await review_service.submit_review(
            careplan_id, review_request
        )
        
        background_tasks.add_task(
            audit_log,
            action="careplan_reviewed",
            careplan_id=careplan_id,
            reviewer_id=review_request.reviewer_id,
            details={
                "status": review_request.status,
                "has_modifications": len(review_request.modifications) > 0
            }
        )
        
        return {
            "status": "success",
            "careplan_id": careplan_id,
            "review_status": review_request.status,
            "message": "Review submitted successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{careplan_id}/approve")
async def approve_careplan(
    careplan_id: str,
    approval_request: ApprovalRequest,
    background_tasks: BackgroundTasks,
    review_service: ReviewServiceDep
):
    """Final approval of care plan for patient delivery"""
    try:
        approval_result = await review_service.approve_careplan(
            careplan_id, approval_request
        )
        
        background_tasks.add_task(
            audit_log,
            action="careplan_approved",
            careplan_id=careplan_id,
            approver_id=approval_request.approver_id,
            details={"final_comments": approval_request.final_comments}
        )
        
        return {
            "status": "success",
            "careplan_id": careplan_id,
            "approved_by": approval_request.approver_name,
            "message": "Care plan approved and ready for patient delivery"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{careplan_id}/history")
async def get_review_history(
    careplan_id: str,
    review_service: ReviewServiceDep
):
    """Get review history for a care plan"""
    try:
        history = await review_service.get_review_history(careplan_id)
        return {
            "careplan_id": careplan_id,
            "review_history": history
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail="Care plan not found")


@router.post("/{careplan_id}/send-to-patient")
async def send_to_patient(
    careplan_id: str,
    background_tasks: BackgroundTasks,
    review_service: ReviewServiceDep
):
    """Send approved care plan to patient"""
    try:
        send_result = await review_service.send_to_patient(careplan_id)
        
        background_tasks.add_task(
            audit_log,
            action="careplan_sent_to_patient",
            careplan_id=careplan_id,
            details={"delivery_method": send_result.get("delivery_method")}
        )
        
        return {
            "status": "success",
            "careplan_id": careplan_id,
            "message": "Care plan sent to patient successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))