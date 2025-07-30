"""
Batch processing API endpoints for bulk operations.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from typing import List, Dict, Any, Optional
import pandas as pd
import json
import uuid
from datetime import datetime
from pathlib import Path
import asyncio
import os

router = APIRouter(prefix="/api/batch", tags=["batch-operations"])

# Path to store batch data
BATCH_DATA_PATH = Path(__file__).parent.parent.parent / "scripts" / "seed_data"
SAMPLE_DATA_PATH = BATCH_DATA_PATH / "sample_data.json"

# Batch job status tracking
_batch_jobs = {}

def load_sample_data() -> Dict[str, Any]:
    """Load existing sample data."""
    try:
        if SAMPLE_DATA_PATH.exists():
            with open(SAMPLE_DATA_PATH, 'r') as f:
                return json.load(f)
        else:
            return {"patients": [], "intakes": [], "ehr_records": [], "care_plans": []}
    except Exception as e:
        print(f"Error loading sample data: {e}")
        return {"patients": [], "intakes": [], "ehr_records": [], "care_plans": []}

def save_sample_data(data: Dict[str, Any]) -> bool:
    """Save sample data to file."""
    try:
        BATCH_DATA_PATH.mkdir(parents=True, exist_ok=True)
        with open(SAMPLE_DATA_PATH, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving sample data: {e}")
        return False

def transform_kaggle_patient_data(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Transform Kaggle healthcare dataset to our patient format."""
    patients = []
    intakes = []
    ehr_records = []
    
    for _, row in df.iterrows():
        patient_id = str(uuid.uuid4())
        
        # Transform patient data
        patient = {
            "patient_id": patient_id,
            "name": row.get('Name', f"Patient {len(patients) + 1}"),
            "age": int(row.get('Age', 0)) if pd.notna(row.get('Age')) else 30,
            "gender": row.get('Gender', 'Unknown'),
            "blood_type": row.get('Blood Type', 'O+'),
            "medical_condition": row.get('Medical Condition', 'General Health'),
            "doctor": row.get('Doctor', 'Dr. Smith'),
            "hospital": row.get('Hospital', 'General Hospital'),
            "insurance_provider": row.get('Insurance Provider', 'Health Insurance Co.')
        }
        patients.append(patient)
        
        # Create intake record
        intake = {
            "intake_id": str(uuid.uuid4()),
            "patient_id": patient_id,
            "chief_complaint": patient["medical_condition"],
            "symptoms": [row.get('Medical Condition', 'General symptoms')],
            "medical_history": f"Patient with {patient['medical_condition']}",
            "current_medications": row.get('Medication', '').split(',') if pd.notna(row.get('Medication')) else [],
            "allergies": [],
            "lifestyle_factors": {
                "smoking": False,
                "alcohol": False,
                "exercise": "moderate"
            },
            "created_date": datetime.now().isoformat(),
            "status": "completed"
        }
        intakes.append(intake)
        
        # Create EHR record
        ehr = {
            "ehr_id": str(uuid.uuid4()),
            "patient_id": patient_id,
            "admission_type": row.get('Admission Type', 'Emergency'),
            "test_results": row.get('Test Results', 'Normal'),
            "billing_amount": float(row.get('Billing Amount', 0)) if pd.notna(row.get('Billing Amount')) else 0.0,
            "room_number": int(row.get('Room Number', 101)) if pd.notna(row.get('Room Number')) else 101,
            "discharge_date": row.get('Discharge Date', datetime.now().strftime('%Y-%m-%d')),
            "created_date": datetime.now().isoformat()
        }
        ehr_records.append(ehr)
    
    return patients, intakes, ehr_records

async def generate_care_plan_for_patient(patient: Dict[str, Any], intake: Dict[str, Any]) -> Dict[str, Any]:
    """Generate an LLM-assisted care plan for a patient."""
    # Simulate LLM generation with realistic care plan data
    await asyncio.sleep(0.1)  # Simulate processing time
    
    care_plan = {
        "careplan_id": str(uuid.uuid4()),
        "patient_id": patient["patient_id"],
        "patient_name": patient["name"],
        "primary_diagnosis": patient["medical_condition"],
        "chief_complaint": intake.get("chief_complaint", patient["medical_condition"]),
        "clinical_summary": f"Patient {patient['name']} presents with {patient['medical_condition']}. "
                           f"Comprehensive care plan developed based on current symptoms and medical history.",
        "version": 1,
        "status": "under_review",  # AI-generated plans require clinician review before activation
        "confidence_score": 0.85,
        "llm_model_used": "gpt-4-healthcare",
        "created_date": datetime.now().isoformat(),
        "last_modified": datetime.now().isoformat(),
        
        # Generate actions based on condition
        "actions": generate_actions_for_condition(patient["medical_condition"]),
        
        # Generate goals
        "short_term_goals": [
            f"Stabilize {patient['medical_condition']} symptoms within 2 weeks",
            "Establish regular monitoring routine",
            "Patient education on condition management"
        ],
        "long_term_goals": [
            f"Achieve optimal management of {patient['medical_condition']}",
            "Prevent complications and improve quality of life",
            "Maintain treatment adherence"
        ],
        "success_metrics": [
            "Symptom improvement by 50% within 4 weeks",
            "Patient compliance rate > 90%",
            "No emergency visits related to condition"
        ],
        "educational_resources": [
            f"Understanding {patient['medical_condition']}",
            "Medication adherence guide",
            "Lifestyle modifications handbook"
        ],
        "patient_instructions": f"Follow prescribed treatment plan for {patient['medical_condition']}. "
                             "Monitor symptoms daily and report any changes to your healthcare provider."
    }
    
    return care_plan

def generate_actions_for_condition(condition: str) -> List[Dict[str, Any]]:
    """Generate appropriate actions based on medical condition."""
    base_actions = [
        {
            "action_id": str(uuid.uuid4()),
            "description": f"Initial assessment and diagnosis confirmation for {condition}",
            "action_type": "diagnostic",
            "priority": "high",
            "timeline": "immediate",
            "rationale": "Establish baseline and confirm diagnosis",
            "evidence_source": "Clinical guidelines",
            "contraindications": []
        },
        {
            "action_id": str(uuid.uuid4()),
            "description": f"Medication therapy for {condition}",
            "action_type": "medication",
            "priority": "high",
            "timeline": "ongoing",
            "rationale": "Control symptoms and prevent progression",
            "evidence_source": "Standard treatment protocols",
            "contraindications": []
        },
        {
            "action_id": str(uuid.uuid4()),
            "description": "Patient education and lifestyle counseling",
            "action_type": "lifestyle",
            "priority": "medium",
            "timeline": "within 1 week",
            "rationale": "Improve patient understanding and compliance",
            "evidence_source": "Patient education best practices",
            "contraindications": []
        }
    ]
    
    # Add condition-specific actions
    if "diabetes" in condition.lower():
        base_actions.append({
            "action_id": str(uuid.uuid4()),
            "description": "Blood glucose monitoring setup",
            "action_type": "monitoring",
            "priority": "high",
            "timeline": "within 24 hours",
            "rationale": "Essential for diabetes management",
            "evidence_source": "Diabetes care guidelines",
            "contraindications": []
        })
    
    if "hypertension" in condition.lower():
        base_actions.append({
            "action_id": str(uuid.uuid4()),
            "description": "Blood pressure monitoring protocol",
            "action_type": "monitoring",
            "priority": "high",
            "timeline": "daily",
            "rationale": "Monitor treatment effectiveness",
            "evidence_source": "Hypertension management guidelines",
            "contraindications": []
        })
    
    return base_actions

@router.post("/intake/upload")
async def batch_intake_upload(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
) -> Dict[str, Any]:
    """
    Upload and process Kaggle healthcare dataset for batch patient intake.
    """
    try:
        print(f"Received file upload: {file.filename}")
        
        # Validate file type
        if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")
        
        # Create batch job
        job_id = str(uuid.uuid4())
        _batch_jobs[job_id] = {
            "job_id": job_id,
            "type": "batch_intake",
            "status": "processing",
            "created_at": datetime.now().isoformat(),
            "total_records": 0,
            "processed_records": 0,
            "errors": []
        }
        
        print(f"Created batch job: {job_id}")
        
        # Read file content
        content = await file.read()
        print(f"Read {len(content)} bytes from file")
        
        # Schedule background processing
        background_tasks.add_task(process_batch_intake, job_id, content, file.filename)
        print(f"Scheduled background task for job: {job_id}")
        
        return {
            "job_id": job_id,
            "status": "accepted",
            "message": "Batch intake processing started"
        }
        
    except Exception as e:
        print(f"Error in batch_intake_upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing upload: {str(e)}")

async def process_batch_intake(job_id: str, content: bytes, filename: str):
    """Background task to process batch intake."""
    try:
        # Update job status
        _batch_jobs[job_id]["status"] = "processing"
        
        # Read data based on file type
        if filename.endswith('.csv'):
            df = pd.read_csv(pd.io.common.StringIO(content.decode('utf-8')))
        else:
            df = pd.read_excel(pd.io.common.BytesIO(content))
        
        _batch_jobs[job_id]["total_records"] = len(df)
        
        # Transform data
        patients, intakes, ehr_records = transform_kaggle_patient_data(df)
        
        # Load existing data
        existing_data = load_sample_data()
        
        # Append new data
        existing_data["patients"].extend(patients)
        existing_data["intakes"].extend(intakes)
        existing_data["ehr_records"].extend(ehr_records)
        
        # Save updated data
        if save_sample_data(existing_data):
            _batch_jobs[job_id]["status"] = "completed"
            _batch_jobs[job_id]["processed_records"] = len(patients)
        else:
            _batch_jobs[job_id]["status"] = "failed"
            _batch_jobs[job_id]["errors"].append("Failed to save data")
            
    except Exception as e:
        _batch_jobs[job_id]["status"] = "failed"
        _batch_jobs[job_id]["errors"].append(str(e))

@router.post("/care-plans/generate")
async def batch_generate_care_plans(
    background_tasks: BackgroundTasks,
    force_regenerate: bool = False
) -> Dict[str, Any]:
    """
    Generate care plans for all patients that don't have care plans yet.
    """
    try:
        # Create batch job
        job_id = str(uuid.uuid4())
        _batch_jobs[job_id] = {
            "job_id": job_id,
            "type": "batch_care_plan_generation",
            "status": "processing",
            "created_at": datetime.now().isoformat(),
            "total_patients": 0,
            "processed_patients": 0,
            "generated_plans": 0,
            "errors": []
        }
        
        # Schedule background processing
        background_tasks.add_task(process_batch_care_plan_generation, job_id, force_regenerate)
        
        return {
            "job_id": job_id,
            "status": "accepted",
            "message": "Batch care plan generation started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting batch generation: {str(e)}")

async def process_batch_care_plan_generation(job_id: str, force_regenerate: bool = False):
    """Background task to generate care plans for patients."""
    try:
        # Load existing data
        data = load_sample_data()
        patients = data.get("patients", [])
        intakes = data.get("intakes", [])
        existing_care_plans = data.get("care_plans", [])
        
        _batch_jobs[job_id]["total_patients"] = len(patients)
        
        # Find patients without care plans
        patients_with_plans = {cp["patient_id"] for cp in existing_care_plans}
        patients_needing_plans = []
        
        if force_regenerate:
            patients_needing_plans = patients
        else:
            patients_needing_plans = [p for p in patients if p["patient_id"] not in patients_with_plans]
        
        # Create intake lookup
        intake_lookup = {intake["patient_id"]: intake for intake in intakes}
        
        new_care_plans = []
        processed = 0
        
        for patient in patients_needing_plans:
            try:
                # Get patient's intake record
                patient_intake = intake_lookup.get(
                    patient["patient_id"], 
                    {
                        "chief_complaint": patient["medical_condition"],
                        "symptoms": [patient["medical_condition"]]
                    }
                )
                
                # Generate care plan
                care_plan = await generate_care_plan_for_patient(patient, patient_intake)
                new_care_plans.append(care_plan)
                
                processed += 1
                _batch_jobs[job_id]["processed_patients"] = processed
                
                # Add small delay to simulate realistic processing
                await asyncio.sleep(0.1)
                
            except Exception as e:
                _batch_jobs[job_id]["errors"].append(f"Error generating plan for {patient['name']}: {str(e)}")
        
        # Save new care plans
        if force_regenerate:
            data["care_plans"] = new_care_plans
        else:
            data["care_plans"].extend(new_care_plans)
        
        if save_sample_data(data):
            _batch_jobs[job_id]["status"] = "completed"
            _batch_jobs[job_id]["generated_plans"] = len(new_care_plans)
        else:
            _batch_jobs[job_id]["status"] = "failed"
            _batch_jobs[job_id]["errors"].append("Failed to save care plans")
            
    except Exception as e:
        _batch_jobs[job_id]["status"] = "failed"
        _batch_jobs[job_id]["errors"].append(str(e))

@router.get("/jobs/{job_id}")
async def get_batch_job_status(job_id: str) -> Dict[str, Any]:
    """Get the status of a batch job."""
    if job_id not in _batch_jobs:
        raise HTTPException(status_code=404, detail="Batch job not found")
    
    return _batch_jobs[job_id]

@router.get("/jobs")
async def list_batch_jobs() -> List[Dict[str, Any]]:
    """List all batch jobs."""
    return list(_batch_jobs.values())

@router.delete("/jobs/{job_id}")
async def cancel_batch_job(job_id: str) -> Dict[str, str]:
    """Cancel a batch job (if still processing)."""
    if job_id not in _batch_jobs:
        raise HTTPException(status_code=404, detail="Batch job not found")
    
    job = _batch_jobs[job_id]
    if job["status"] == "processing":
        job["status"] = "cancelled"
        return {"message": "Batch job cancelled"}
    else:
        return {"message": f"Cannot cancel job with status: {job['status']}"}

@router.get("/stats")
async def get_batch_stats() -> Dict[str, Any]:
    """Get statistics about the data in the system."""
    data = load_sample_data()
    
    return {
        "total_patients": len(data.get("patients", [])),
        "total_intakes": len(data.get("intakes", [])),
        "total_care_plans": len(data.get("care_plans", [])),
        "patients_without_care_plans": len(data.get("patients", [])) - len(data.get("care_plans", [])),
        "care_plan_statuses": {}
    }