"""
Mock data API endpoints for development and demo purposes.
Serves sample healthcare data for the web UI.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
import json
import os
from pathlib import Path

router = APIRouter(prefix="/api/mock", tags=["mock-data"])

# Path to sample data
SAMPLE_DATA_PATH = Path(__file__).parent.parent.parent / "scripts" / "seed_data" / "sample_data.json"

# In-memory storage for care plan status changes (for demo purposes)
_care_plan_status_cache = {}


def load_sample_data() -> Dict[str, Any]:
    """Load sample data from JSON file."""
    try:
        if SAMPLE_DATA_PATH.exists():
            with open(SAMPLE_DATA_PATH, 'r') as f:
                return json.load(f)
        else:
            # Return empty data if file doesn't exist
            return {
                "patients": [],
                "intakes": [],
                "ehr_records": [],
                "care_plans": []
            }
    except Exception as e:
        print(f"Error loading sample data: {e}")
        return {"patients": [], "intakes": [], "ehr_records": [], "care_plans": []}


@router.get("/patients")
async def get_patients() -> List[Dict[str, Any]]:
    """Get list of sample patients."""
    data = load_sample_data()
    return data.get("patients", [])


@router.get("/patients/{patient_id}")
async def get_patient(patient_id: str) -> Dict[str, Any]:
    """Get specific patient by ID."""
    data = load_sample_data()
    patients = data.get("patients", [])
    
    for patient in patients:
        if patient.get("patient_id") == patient_id:
            return patient
    
    raise HTTPException(status_code=404, detail="Patient not found")


@router.get("/patients/{patient_id}/intake")
async def get_patient_intake(patient_id: str) -> Dict[str, Any]:
    """Get patient intake data."""
    data = load_sample_data()
    intakes = data.get("intakes", [])
    
    for intake in intakes:
        if intake.get("patient_id") == patient_id:
            return intake
    
    raise HTTPException(status_code=404, detail="Patient intake not found")


@router.get("/patients/{patient_id}/ehr")
async def get_patient_ehr(patient_id: str) -> Dict[str, Any]:
    """Get patient EHR data."""
    data = load_sample_data()
    ehr_records = data.get("ehr_records", [])
    
    for ehr in ehr_records:
        if ehr.get("patient_id") == patient_id:
            return ehr
    
    raise HTTPException(status_code=404, detail="EHR record not found")


@router.get("/patients/{patient_id}/care-plans")
async def get_patient_care_plans(patient_id: str) -> List[Dict[str, Any]]:
    """Get patient care plans from actual data."""
    data = load_sample_data()
    care_plans = data.get("care_plans", [])
    
    # Filter care plans for the specific patient
    patient_plans = [cp for cp in care_plans if cp.get("patient_id") == patient_id]
    
    # Apply any status updates from the cache
    for plan in patient_plans:
        careplan_id = plan.get("careplan_id")
        if careplan_id in _care_plan_status_cache:
            cached_data = _care_plan_status_cache[careplan_id]
            plan["status"] = cached_data["status"]
            plan["reviewer_comments"] = cached_data.get("comments")
            plan["last_review_date"] = cached_data.get("reviewed_at")
    
    return patient_plans


@router.get("/care-plans/{careplan_id}")
async def get_care_plan(careplan_id: str) -> Dict[str, Any]:
    """Get specific care plan by ID from actual data."""
    data = load_sample_data()
    care_plans = data.get("care_plans", [])
    
    for plan in care_plans:
        if plan.get("careplan_id") == careplan_id:
            # Apply any status updates from the cache
            if careplan_id in _care_plan_status_cache:
                cached_data = _care_plan_status_cache[careplan_id]
                plan["status"] = cached_data["status"]
                plan["reviewer_comments"] = cached_data.get("comments")
                plan["last_review_date"] = cached_data.get("reviewed_at")
            return plan
    
    raise HTTPException(status_code=404, detail="Care plan not found")


@router.get("/clinician/care-plans")
async def get_all_care_plans_for_clinician(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all care plans for clinician review from actual data."""
    data = load_sample_data()
    care_plans = data.get("care_plans", [])
    patients = data.get("patients", [])
    
    # Create a lookup for patient names
    patient_lookup = {p.get("patient_id"): p.get("name") for p in patients}
    
    # Enhance care plans with patient names and apply cached status updates
    enhanced_care_plans = []
    for plan in care_plans:
        enhanced_plan = plan.copy()
        
        # Add patient name
        patient_id = plan.get("patient_id")
        enhanced_plan["patient_name"] = patient_lookup.get(patient_id, "Unknown Patient")
        
        # Apply any status updates from the cache
        careplan_id = plan.get("careplan_id")
        if careplan_id in _care_plan_status_cache:
            cached_data = _care_plan_status_cache[careplan_id]
            enhanced_plan["status"] = cached_data["status"]
            enhanced_plan["reviewer_comments"] = cached_data.get("comments")
            enhanced_plan["last_review_date"] = cached_data.get("reviewed_at")
        
        # Add clinician-specific fields if missing
        enhanced_plan.setdefault("assigned_clinician", "Dr. Maria Garcia")
        enhanced_plan.setdefault("priority", "medium")
        
        enhanced_care_plans.append(enhanced_plan)
    
    # Filter by status if provided
    if status:
        enhanced_care_plans = [cp for cp in enhanced_care_plans if cp.get("status") == status]
    
    return enhanced_care_plans


@router.put("/care-plans/{careplan_id}/review")
async def submit_care_plan_review(careplan_id: str, review_data: Dict[str, Any]) -> Dict[str, Any]:
    """Submit clinician review for a care plan."""
    action = review_data.get("action")  # "approve" or "deny"
    comments = review_data.get("comments", "")
    modifications = review_data.get("modifications", {})
    
    if action not in ["approve", "deny", "edit"]:
        raise HTTPException(status_code=400, detail="Action must be 'approve', 'deny', or 'edit'")
    
    # Store the review result in our cache
    if action == "edit":
        # For edit action, keep the current status but apply modifications
        new_status = None  # Don't change status for edits
        reviewed_at = "2024-01-15T15:30:00Z"
    else:
        new_status = "approved" if action == "approve" else "denied"
        reviewed_at = "2024-01-15T15:30:00Z"
    
    # For edit actions, only store modifications and comments, not status changes
    if action == "edit":
        _care_plan_status_cache[careplan_id] = {
            "comments": comments,
            "reviewed_at": reviewed_at,
            "modifications": modifications,
            "reviewer": "Dr. Maria Garcia"
        }
        
        return {
            "careplan_id": careplan_id,
            "status": "modified",  # Indicate it was modified but keep original status
            "reviewer_comments": comments,
            "modifications_applied": len(modifications) > 0,
            "reviewed_at": reviewed_at,
            "reviewer": "Dr. Maria Garcia"
        }
    else:
        _care_plan_status_cache[careplan_id] = {
            "status": new_status,
            "comments": comments,
            "reviewed_at": reviewed_at,
            "modifications": modifications,
            "reviewer": "Dr. Maria Garcia"
        }
        
        return {
            "careplan_id": careplan_id,
            "status": new_status,
            "reviewer_comments": comments,
            "modifications_applied": len(modifications) > 0,
            "reviewed_at": reviewed_at,
            "reviewer": "Dr. Maria Garcia"
        }


@router.get("/clinician/patients")
async def get_clinician_patients() -> List[Dict[str, Any]]:
    """Get all patients assigned to the clinician with real care plan data."""
    data = load_sample_data()
    patients = data.get("patients", [])
    care_plans = data.get("care_plans", [])
    intakes = data.get("intakes", [])
    
    # Create lookup dictionaries for efficient matching
    care_plan_lookup = {}
    intake_lookup = {}
    
    for plan in care_plans:
        patient_id = plan.get("patient_id")
        if patient_id:
            if patient_id not in care_plan_lookup:
                care_plan_lookup[patient_id] = []
            care_plan_lookup[patient_id].append(plan)
    
    for intake in intakes:
        patient_id = intake.get("patient_id")
        if patient_id:
            intake_lookup[patient_id] = intake
    
    # Enhance patients with real data
    enhanced_patients = []
    for patient in patients:
        patient_id = patient.get("patient_id")
        
        # Get patient's care plans
        patient_care_plans = care_plan_lookup.get(patient_id, [])
        patient_intake = intake_lookup.get(patient_id)
        
        # Determine care plan status from actual care plans
        if patient_care_plans:
            # Get the most recent care plan
            latest_plan = max(patient_care_plans, key=lambda p: p.get("last_modified", ""))
            care_plan_status = latest_plan.get("status", "unknown")
        else:
            care_plan_status = "no_plan"
        
        # Determine risk level based on medical condition and care plan data
        medical_condition = patient.get("medical_condition", "").lower()
        if "cancer" in medical_condition or "diabetes" in medical_condition or "heart" in medical_condition:
            risk_level = "high"
        elif "hypertension" in medical_condition or "asthma" in medical_condition:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Generate realistic visit dates based on care plan activity
        last_visit = "2024-01-15"  # Default
        next_appointment = "Not scheduled"  # Default
        
        if patient_care_plans:
            # If patient has care plans, generate more recent dates
            from datetime import datetime, timedelta
            import random
            
            base_date = datetime.now()
            last_visit_date = base_date - timedelta(days=random.randint(1, 30))
            last_visit = last_visit_date.strftime("%Y-%m-%d")
            
            if care_plan_status in ["approved", "under_review"]:
                next_appointment_date = base_date + timedelta(days=random.randint(1, 14))
                next_appointment = next_appointment_date.strftime("%Y-%m-%d")
        
        enhanced_patient = {
            **patient,
            "last_visit": last_visit,
            "next_appointment": next_appointment,
            "care_plan_status": care_plan_status,
            "risk_level": risk_level,
            "care_plans_count": len(patient_care_plans),
            "has_intake": patient_intake is not None
        }
        
        enhanced_patients.append(enhanced_patient)
    
    return enhanced_patients


@router.get("/dashboard-stats")
async def get_dashboard_stats(patient_id: Optional[str] = None) -> Dict[str, Any]:
    """Get dashboard statistics."""
    data = load_sample_data()
    
    # Calculate stats from loaded data
    total_patients = len(data.get("patients", []))
    total_care_plans = len(data.get("care_plans", []))
    
    # Mock some additional stats
    return {
        "totalPatients": total_patients,
        "activeCarePlans": total_care_plans,
        "pendingReviews": max(0, total_care_plans - 2),
        "completedTreatments": min(total_care_plans, 5)
    }


@router.get("/health-metrics/{patient_id}")
async def get_health_metrics(patient_id: str) -> List[Dict[str, Any]]:
    """Get health metrics for a patient."""
    # Mock health metrics data
    return [
        {
            "name": "Blood Pressure",
            "value": "145/92",
            "unit": "mmHg",
            "status": "abnormal",
            "lastUpdated": "2024-01-15",
            "trend": "up"
        },
        {
            "name": "HbA1c",
            "value": 7.2,
            "unit": "%",
            "status": "abnormal", 
            "lastUpdated": "2024-01-10",
            "trend": "stable"
        },
        {
            "name": "Weight",
            "value": 185,
            "unit": "lbs",
            "status": "normal",
            "lastUpdated": "2024-01-16",
            "trend": "down"
        },
        {
            "name": "Heart Rate",
            "value": 78,
            "unit": "bpm",
            "status": "normal",
            "lastUpdated": "2024-01-15",
            "trend": "stable"
        }
    ]


@router.get("/appointments/{patient_id}")
async def get_upcoming_appointments(patient_id: str) -> List[Dict[str, Any]]:
    """Get upcoming appointments for a patient."""
    # Mock appointments data
    return [
        {
            "date": "2024-01-20",
            "time": "10:00 AM",
            "provider": "Dr. Sarah Johnson",
            "type": "Follow-up"
        },
        {
            "date": "2024-01-25",
            "time": "2:30 PM", 
            "provider": "Nutritionist",
            "type": "Consultation"
        },
        {
            "date": "2024-02-01",
            "time": "9:00 AM",
            "provider": "Lab Work",
            "type": "Blood Test"
        }
    ]


@router.get("/chart-data/{patient_id}")
async def get_chart_data(patient_id: str) -> List[Dict[str, Any]]:
    """Get chart data for health trends."""
    # Mock chart data
    return [
        {"date": "2024-01-01", "glucose": 140, "bp_systolic": 135},
        {"date": "2024-01-05", "glucose": 155, "bp_systolic": 145},
        {"date": "2024-01-10", "glucose": 142, "bp_systolic": 140},
        {"date": "2024-01-15", "glucose": 138, "bp_systolic": 145},
        {"date": "2024-01-16", "glucose": 135, "bp_systolic": 142}
    ]


@router.post("/generate-sample-data")
async def generate_sample_data(num_patients: int = 50) -> Dict[str, Any]:
    """Generate new sample data."""
    try:
        from scripts.seed_data.database_seeder import DatabaseSeeder
        
        seeder = DatabaseSeeder()
        sample_data = await seeder.run_seeding(num_patients=num_patients)
        
        return {
            "status": "success",
            "message": f"Generated sample data for {num_patients} patients",
            "data_summary": {
                "patients": len(sample_data.get("patients", [])),
                "intakes": len(sample_data.get("intakes", [])),
                "ehr_records": len(sample_data.get("ehr_records", [])),
                "care_plans": len(sample_data.get("care_plans", []))
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating sample data: {str(e)}")


@router.get("/data-info")
async def get_data_info() -> Dict[str, Any]:
    """Get information about the loaded sample data."""
    data = load_sample_data()
    
    return {
        "sample_data_available": SAMPLE_DATA_PATH.exists(),
        "sample_data_path": str(SAMPLE_DATA_PATH),
        "counts": {
            "patients": len(data.get("patients", [])),
            "intakes": len(data.get("intakes", [])),
            "ehr_records": len(data.get("ehr_records", [])),
            "care_plans": len(data.get("care_plans", []))
        },
        "instructions": {
            "generate_data": "POST /api/mock/generate-sample-data",
            "generate_care_plans": "POST /api/mock/generate-care-plans",
            "web_ui": "Start React app with: cd clients/web-ui && npm start"
        }
    }


@router.post("/generate-care-plans")
async def generate_care_plans() -> Dict[str, Any]:
    """Generate care plans for existing patients."""
    import json
    from datetime import datetime, timedelta
    
    data = load_sample_data()
    patients = data.get("patients", [])
    
    if not patients:
        raise HTTPException(status_code=400, detail="No patients found. Please generate patients first.")
    
    care_plans = []
    statuses = ["under_review", "approved", "completed"]
    
    for i, patient in enumerate(patients):
        patient_id = patient.get("patient_id")
        medical_condition = patient.get("medical_condition", "General Health")
        
        # Create 1-2 care plans per patient
        num_plans = 1 if i % 2 == 0 else 2
        
        for plan_idx in range(num_plans):
            status = statuses[i % len(statuses)]
            careplan_id = f"cp_{patient_id}_{plan_idx}_{status}"
            
            created_date = datetime.now() - timedelta(days=30 - i)
            
            care_plan = {
                "careplan_id": careplan_id,
                "patient_id": patient_id,
                "created_date": created_date.isoformat(),
                "last_modified": created_date.isoformat(),
                "status": status,
                "version": 1,
                "primary_diagnosis": medical_condition,
                "secondary_diagnoses": [],
                "chief_complaint": f"Management and treatment of {medical_condition.lower()}",
                "clinical_summary": f"Patient presents with {medical_condition.lower()} requiring comprehensive care coordination and evidence-based treatment approach. Current clinical status shows good response to therapy with continued monitoring needed.",
                "actions": [
                    {
                        "action_id": f"action_{careplan_id}_1",
                        "action_type": "medication",
                        "description": f"Continue current {medical_condition.lower()} medication regimen as prescribed",
                        "priority": "high",
                        "timeline": "ongoing",
                        "rationale": f"Medication compliance is essential for effective {medical_condition.lower()} management",
                        "evidence_source": "Clinical guidelines",
                        "contraindications": []
                    },
                    {
                        "action_id": f"action_{careplan_id}_2",
                        "action_type": "lifestyle",
                        "description": f"Implement lifestyle modifications to support {medical_condition.lower()} treatment",
                        "priority": "medium",
                        "timeline": "within 2 weeks",
                        "rationale": "Lifestyle interventions complement medical therapy",
                        "evidence_source": "Evidence-based practice guidelines",
                        "contraindications": []
                    },
                    {
                        "action_id": f"action_{careplan_id}_3",
                        "action_type": "monitoring",
                        "description": "Regular monitoring and follow-up appointments",
                        "priority": "high",
                        "timeline": "monthly",
                        "rationale": "Ongoing monitoring ensures treatment effectiveness",
                        "evidence_source": "Standard of care",
                        "contraindications": []
                    }
                ],
                "short_term_goals": [
                    f"Stabilize {medical_condition.lower()} symptoms within 4 weeks",
                    "Improve quality of life and daily functioning",
                    "Achieve medication compliance > 90%"
                ],
                "long_term_goals": [
                    f"Prevent {medical_condition.lower()} complications",
                    "Maintain independent living",
                    "Optimize overall health status"
                ],
                "success_metrics": [
                    "Symptom severity score improvement",
                    "Functional status assessment",
                    "Patient-reported outcomes"
                ],
                "clinician_reviews": [],
                "patient_instructions": f"Continue taking prescribed medications for {medical_condition.lower()} as directed. Follow lifestyle recommendations provided. Attend all scheduled follow-up appointments.",
                "educational_resources": [
                    f"Understanding {medical_condition}",
                    "Medication adherence guide",
                    "Lifestyle modification tips"
                ],
                "confidence_score": 0.85 if status in ["approved", "completed"] else 0.75
            }
            
            care_plans.append(care_plan)
    
    # Update the sample data file
    data["care_plans"] = care_plans
    
    try:
        with open(SAMPLE_DATA_PATH, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving care plans: {str(e)}")
    
    return {
        "status": "success",
        "message": f"Generated {len(care_plans)} care plans for {len(patients)} patients",
        "care_plans_created": len(care_plans)
    }