"""
Database seeder for CarePlan AI system.
Seeds the database with synthetic healthcare data.
"""

import asyncio
import csv
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from app.models.intake import PatientIntake, Symptom, MedicalHistory, Medication
from app.models.ehr import EHRRecord, LabResult, VitalSigns, Diagnosis
from app.models.careplan import CarePlan, CarePlanAction, ActionType, Priority
from .healthcare_data_generator import HealthcareDataGenerator


class DatabaseSeeder:
    """Seed database with healthcare data."""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv(
            "DATABASE_URL", 
            "postgresql://postgres:password@localhost:5432/careplan_db"
        )
        self.data_dir = os.path.dirname(__file__)
    
    async def seed_from_csv(self, csv_file: str, model_type: str):
        """Seed database from CSV file."""
        csv_path = os.path.join(self.data_dir, csv_file)
        
        if not os.path.exists(csv_path):
            print(f"CSV file not found: {csv_path}")
            return
        
        records = []
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    if model_type == "intake":
                        record = self.create_intake_record(row)
                    elif model_type == "ehr":
                        record = self.create_ehr_record(row)
                    elif model_type == "patient":
                        record = row  # Keep patient data as dict for now
                    
                    if record:
                        records.append(record)
                except Exception as e:
                    print(f"Error processing row: {e}")
                    continue
        
        print(f"Processed {len(records)} {model_type} records from {csv_file}")
        return records
    
    def create_intake_record(self, row: Dict[str, Any]) -> PatientIntake:
        """Create PatientIntake from CSV row."""
        try:
            # Parse symptoms if they exist
            symptoms = []
            if 'symptoms' in row and row['symptoms']:
                symptoms_data = json.loads(row['symptoms'].replace("'", '"'))
                for symptom_data in symptoms_data:
                    symptoms.append(Symptom(
                        description=symptom_data['description'],
                        severity=symptom_data['severity'],
                        duration_days=symptom_data.get('duration_days')
                    ))
            
            # Parse medical history
            medical_history = []
            if 'medical_history' in row and row['medical_history']:
                history_data = json.loads(row['medical_history'].replace("'", '"'))
                for history_item in history_data:
                    medical_history.append(MedicalHistory(
                        condition=history_item['condition'],
                        status=history_item['status'],
                        diagnosis_date=datetime.fromisoformat(history_item['diagnosis_date']) if history_item.get('diagnosis_date') else None
                    ))
            
            # Parse medications
            medications = []
            if 'current_medications' in row and row['current_medications']:
                meds_data = json.loads(row['current_medications'].replace("'", '"'))
                for med_data in meds_data:
                    medications.append(Medication(
                        name=med_data['name'],
                        dosage=med_data['dosage'],
                        frequency=med_data['frequency'],
                        active=med_data.get('active', True)
                    ))
            
            # Parse family history and allergies
            family_history = json.loads(row.get('family_history', '[]').replace("'", '"')) if row.get('family_history') else []
            allergies = json.loads(row.get('allergies', '[]').replace("'", '"')) if row.get('allergies') else []
            
            return PatientIntake(
                patient_id=row['patient_id'],
                age=int(row['age']),
                gender=row['gender'],
                weight_kg=float(row.get('weight_kg', 70.0)),
                height_cm=float(row.get('height_cm', 170.0)),
                chief_complaint=row['chief_complaint'],
                symptoms=symptoms,
                medical_history=medical_history,
                family_history=family_history,
                allergies=allergies,
                current_medications=medications,
                smoking_status=row.get('smoking_status'),
                alcohol_consumption=row.get('alcohol_consumption'),
                exercise_frequency=row.get('exercise_frequency')
            )
        except Exception as e:
            print(f"Error creating intake record: {e}")
            return None
    
    def create_ehr_record(self, row: Dict[str, Any]) -> EHRRecord:
        """Create EHRRecord from CSV row."""
        try:
            # Parse diagnoses
            diagnoses = []
            if 'diagnoses' in row and row['diagnoses']:
                diagnoses_data = json.loads(row['diagnoses'].replace("'", '"'))
                for dx_data in diagnoses_data:
                    diagnoses.append(Diagnosis(
                        icd_10_code=dx_data.get('icd_10_code'),
                        description=dx_data['description'],
                        diagnosis_date=datetime.fromisoformat(dx_data['diagnosis_date']),
                        status=dx_data['status'],
                        provider=dx_data.get('provider')
                    ))
            
            # Parse lab results
            lab_results = []
            if 'lab_results' in row and row['lab_results']:
                labs_data = json.loads(row['lab_results'].replace("'", '"'))
                for lab_data in labs_data:
                    lab_results.append(LabResult(
                        test_name=lab_data['test_name'],
                        value=lab_data['value'],
                        unit=lab_data.get('unit'),
                        reference_range=lab_data.get('reference_range'),
                        status=lab_data.get('status'),
                        test_date=datetime.fromisoformat(lab_data['test_date'])
                    ))
            
            # Parse vital signs
            vital_signs = []
            if 'vital_signs' in row and row['vital_signs']:
                vitals_data = json.loads(row['vital_signs'].replace("'", '"'))
                for vital_data in vitals_data:
                    vital_signs.append(VitalSigns(
                        temperature_f=vital_data.get('temperature_f'),
                        blood_pressure_systolic=vital_data.get('blood_pressure_systolic'),
                        blood_pressure_diastolic=vital_data.get('blood_pressure_diastolic'),
                        heart_rate=vital_data.get('heart_rate'),
                        respiratory_rate=vital_data.get('respiratory_rate'),
                        oxygen_saturation=vital_data.get('oxygen_saturation'),
                        recorded_date=datetime.fromisoformat(vital_data['recorded_date'])
                    ))
            
            return EHRRecord(
                patient_id=row['patient_id'],
                record_id=row['record_id'],
                mrn=row.get('mrn'),
                date_of_birth=datetime.fromisoformat(row['date_of_birth']) if row.get('date_of_birth') else None,
                gender=row.get('gender'),
                diagnoses=diagnoses,
                lab_results=lab_results,
                vital_signs=vital_signs
            )
        except Exception as e:
            print(f"Error creating EHR record: {e}")
            return None
    
    async def generate_sample_care_plans(self, patient_records: List[Dict[str, Any]], num_plans: int = 50) -> List[CarePlan]:
        """Generate sample care plans for some patients."""
        care_plans = []
        
        for i, patient in enumerate(patient_records[:num_plans]):
            try:
                # Create sample care plan actions based on medical condition
                actions = self.create_care_plan_actions(patient['medical_condition'])
                
                care_plan = CarePlan(
                    careplan_id=f"cp_{patient['patient_id']}_{int(datetime.now().timestamp())}",
                    patient_id=patient['patient_id'],
                    primary_diagnosis=patient['medical_condition'],
                    chief_complaint=f"Management of {patient['medical_condition']}",
                    clinical_summary=f"Patient presents with {patient['medical_condition']} requiring comprehensive management.",
                    actions=actions,
                    short_term_goals=self.get_short_term_goals(patient['medical_condition']),
                    long_term_goals=self.get_long_term_goals(patient['medical_condition']),
                    success_metrics=self.get_success_metrics(patient['medical_condition']),
                    patient_instructions=f"Follow prescribed treatment plan for {patient['medical_condition']}",
                    educational_resources=self.get_educational_resources(patient['medical_condition'])
                )
                
                care_plans.append(care_plan)
            except Exception as e:
                print(f"Error creating care plan for patient {patient['patient_id']}: {e}")
                continue
        
        return care_plans
    
    def create_care_plan_actions(self, condition: str) -> List[CarePlanAction]:
        """Create care plan actions based on medical condition."""
        actions = []
        action_templates = {
            "Diabetes": [
                {
                    "type": ActionType.MEDICATION,
                    "description": "Continue Metformin 500mg twice daily with meals",
                    "priority": Priority.HIGH,
                    "timeline": "ongoing",
                    "rationale": "First-line therapy for Type 2 diabetes management"
                },
                {
                    "type": ActionType.DIAGNOSTIC,
                    "description": "HbA1c test every 3 months",
                    "priority": Priority.HIGH,
                    "timeline": "every 3 months",
                    "rationale": "Monitor glycemic control and treatment effectiveness"
                },
                {
                    "type": ActionType.LIFESTYLE,
                    "description": "Dietary consultation with nutritionist",
                    "priority": Priority.MEDIUM,
                    "timeline": "within 2 weeks",
                    "rationale": "Optimize nutrition for diabetes management"
                }
            ],
            "Hypertension": [
                {
                    "type": ActionType.MEDICATION,
                    "description": "Continue Lisinopril 10mg daily",
                    "priority": Priority.HIGH,
                    "timeline": "ongoing",
                    "rationale": "ACE inhibitor for blood pressure control"
                },
                {
                    "type": ActionType.MONITORING,
                    "description": "Home blood pressure monitoring twice daily",
                    "priority": Priority.HIGH,
                    "timeline": "daily",
                    "rationale": "Track blood pressure trends and medication effectiveness"
                }
            ]
        }
        
        templates = action_templates.get(condition, [])
        for i, template in enumerate(templates):
            action = CarePlanAction(
                action_id=f"action_{condition}_{i}",
                action_type=template["type"],
                description=template["description"],
                priority=template["priority"],
                timeline=template["timeline"],
                rationale=template["rationale"]
            )
            actions.append(action)
        
        return actions
    
    def get_short_term_goals(self, condition: str) -> List[str]:
        """Get short-term goals for condition."""
        goals_map = {
            "Diabetes": ["Achieve fasting glucose < 130 mg/dL", "Reduce HbA1c by 0.5%"],
            "Hypertension": ["Maintain BP < 130/80 mmHg", "Establish medication compliance"],
            "Arthritis": ["Reduce joint pain by 50%", "Improve mobility"],
            "Asthma": ["Achieve symptom control", "Reduce rescue inhaler use"],
            "Obesity": ["Lose 5-10% of body weight", "Establish exercise routine"],
            "Cancer": ["Complete treatment protocol", "Manage side effects"]
        }
        return goals_map.get(condition, ["Improve symptoms", "Optimize treatment"])
    
    def get_long_term_goals(self, condition: str) -> List[str]:
        """Get long-term goals for condition."""
        goals_map = {
            "Diabetes": ["Prevent diabetic complications", "Maintain HbA1c < 7%"],
            "Hypertension": ["Prevent cardiovascular events", "Maintain target BP"],
            "Arthritis": ["Preserve joint function", "Maintain quality of life"],
            "Asthma": ["Prevent exacerbations", "Maintain normal lung function"],
            "Obesity": ["Achieve healthy BMI", "Prevent obesity-related complications"],
            "Cancer": ["Achieve remission", "Prevent recurrence"]
        }
        return goals_map.get(condition, ["Manage condition effectively", "Improve quality of life"])
    
    def get_success_metrics(self, condition: str) -> List[str]:
        """Get success metrics for condition."""
        metrics_map = {
            "Diabetes": ["HbA1c < 7%", "Fasting glucose 80-130 mg/dL"],
            "Hypertension": ["BP < 130/80 mmHg", "Medication adherence > 90%"],
            "Arthritis": ["Pain score < 4/10", "Improved joint mobility"],
            "Asthma": ["Peak flow > 80% predicted", "Rescue inhaler use < 2x/week"],
            "Obesity": ["BMI reduction", "Waist circumference reduction"],
            "Cancer": ["Complete response to treatment", "No disease progression"]
        }
        return metrics_map.get(condition, ["Symptom improvement", "Treatment adherence"])
    
    def get_educational_resources(self, condition: str) -> List[str]:
        """Get educational resources for condition."""
        resources_map = {
            "Diabetes": ["ADA diabetes education materials", "Diabetic diet guidelines"],
            "Hypertension": ["AHA blood pressure resources", "DASH diet information"],
            "Arthritis": ["Arthritis Foundation resources", "Joint protection techniques"],
            "Asthma": ["Asthma Action Plan", "Peak flow monitoring guide"],
            "Obesity": ["Weight management programs", "Healthy eating guidelines"],
            "Cancer": ["Cancer support resources", "Treatment information packets"]
        }
        return resources_map.get(condition, ["General health education", "Disease management guides"])
    
    async def run_seeding(self, num_patients: int = 100):
        """Run the complete seeding process."""
        print("Starting database seeding process...")
        
        # Generate data if CSV files don't exist
        if not all(os.path.exists(os.path.join(self.data_dir, f)) 
                  for f in ["patients.csv", "patient_intakes.csv", "ehr_records.csv"]):
            print("Generating healthcare data...")
            generator = HealthcareDataGenerator(num_patients=num_patients)
            data = generator.generate_all_data()
            
            # Save to CSV files
            generator.save_to_csv(os.path.join(self.data_dir, "patients.csv"), data["patients"])
            generator.save_to_csv(os.path.join(self.data_dir, "patient_intakes.csv"), data["intakes"])
            generator.save_to_csv(os.path.join(self.data_dir, "ehr_records.csv"), data["ehr_records"])
        
        # Load data from CSV files
        print("Loading data from CSV files...")
        patient_records = await self.seed_from_csv("patients.csv", "patient")
        intake_records = await self.seed_from_csv("patient_intakes.csv", "intake")
        ehr_records = await self.seed_from_csv("ehr_records.csv", "ehr")
        
        # Generate sample care plans
        print("Generating sample care plans...")
        care_plans = await self.generate_sample_care_plans(patient_records, num_plans=min(50, len(patient_records)))
        
        print(f"Seeding completed:")
        print(f"- {len(patient_records)} patient records")
        print(f"- {len(intake_records)} intake records")
        print(f"- {len(ehr_records)} EHR records")
        print(f"- {len(care_plans)} care plans")
        
        # In a real implementation, you would save these to the database
        # For now, we'll save sample JSON files for the web UI
        sample_data = {
            "patients": patient_records[:10],  # First 10 patients
            "intakes": [intake.dict() if hasattr(intake, 'dict') else intake for intake in intake_records[:10]],
            "ehr_records": [ehr.dict() if hasattr(ehr, 'dict') else ehr for ehr in ehr_records[:10]],
            "care_plans": [cp.dict() if hasattr(cp, 'dict') else cp for cp in care_plans[:10]]
        }
        
        # Save sample data for web UI
        sample_file = os.path.join(self.data_dir, "sample_data.json")
        with open(sample_file, 'w') as f:
            json.dump(sample_data, f, indent=2, default=str)
        
        print(f"Sample data saved to: {sample_file}")
        return sample_data


async def main():
    """Main seeding function."""
    seeder = DatabaseSeeder()
    await seeder.run_seeding(num_patients=100)


if __name__ == "__main__":
    asyncio.run(main())