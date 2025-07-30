from typing import List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

router = APIRouter(prefix="/api/review", tags=["review"])


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


@router.get("/pending")
async def get_pending_reviews(reviewer_id: Optional[str] = None):
    """Get all care plans pending review (Mock)"""
    return {
        "status": "success",
        "pending_count": 0,
        "care_plans": []
    }


@router.post("/{careplan_id}/review")
async def submit_review(
    careplan_id: str,
    review_request: ReviewRequest,
    background_tasks: BackgroundTasks
):
    """Submit clinician review for a care plan draft (Mock)"""
    return {
        "status": "success",
        "careplan_id": careplan_id,
        "review_status": review_request.status,
        "message": "Review submitted successfully (mock)"
    }


@router.post("/{careplan_id}/approve")
async def approve_careplan(
    careplan_id: str,
    approval_request: ApprovalRequest,
    background_tasks: BackgroundTasks
):
    """Final approval of care plan for patient delivery (Mock)"""
    return {
        "status": "success",
        "careplan_id": careplan_id,
        "approved_by": approval_request.approver_name,
        "message": "Care plan approved and ready for patient delivery (mock)"
    }


@router.get("/{careplan_id}/history")
async def get_review_history(careplan_id: str):
    """Get review history for a care plan (Mock)"""
    return {
        "careplan_id": careplan_id,
        "review_history": []
    }


@router.post("/{careplan_id}/send-to-patient")
async def send_to_patient(careplan_id: str, background_tasks: BackgroundTasks):
    """Send approved care plan to patient (Mock)"""
    return {
        "status": "success",
        "careplan_id": careplan_id,
        "message": "Care plan sent to patient successfully (mock)"
    }