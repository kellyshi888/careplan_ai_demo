"""
Healthcare data generator based on Kaggle healthcare dataset structure.
Creates synthetic healthcare data for seeding the CarePlan AI system.
"""

import csv
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from faker import Faker
import uuid

fake = Faker()

# Medical conditions and their associated data
MEDICAL_CONDITIONS = {
    "Diabetes": {
        "medications": ["Metformin", "Insulin", "Glipizide", "Jardiance", "Ozempic"],
        "test_results": {"Normal": 0.3, "Abnormal": 0.6, "Inconclusive": 0.1},
        "avg_billing": 5500,
        "symptoms": ["Frequent urination", "Excessive thirst", "Fatigue", "Blurred vision"]
    },
    "Hypertension": {
        "medications": ["Lisinopril", "Amlodipine", "Losartan", "Hydrochlorothiazide", "Atenolol"],
        "test_results": {"Normal": 0.4, "Abnormal": 0.5, "Inconclusive": 0.1},
        "avg_billing": 3200,
        "symptoms": ["Headache", "Dizziness", "Chest pain", "Shortness of breath"]
    },
    "Arthritis": {
        "medications": ["Ibuprofen", "Naproxen", "Prednisone", "Methotrexate", "Humira"],
        "test_results": {"Normal": 0.2, "Abnormal": 0.7, "Inconclusive": 0.1},
        "avg_billing": 4100,
        "symptoms": ["Joint pain", "Stiffness", "Swelling", "Reduced range of motion"]
    },
    "Asthma": {
        "medications": ["Albuterol", "Fluticasone", "Singulair", "Symbicort", "Advair"],
        "test_results": {"Normal": 0.5, "Abnormal": 0.4, "Inconclusive": 0.1},
        "avg_billing": 2800,
        "symptoms": ["Wheezing", "Shortness of breath", "Chest tightness", "Coughing"]
    },
    "Obesity": {
        "medications": ["Orlistat", "Phentermine", "Liraglutide", "Naltrexone-Bupropion"],
        "test_results": {"Normal": 0.3, "Abnormal": 0.6, "Inconclusive": 0.1},
        "avg_billing": 6200,
        "symptoms": ["Fatigue", "Sleep apnea", "Joint pain", "High blood pressure"]
    },
    "Cancer": {
        "medications": ["Chemotherapy", "Radiation", "Immunotherapy", "Targeted therapy"],
        "test_results": {"Normal": 0.2, "Abnormal": 0.7, "Inconclusive": 0.1},
        "avg_billing": 25000,
        "symptoms": ["Fatigue", "Weight loss", "Pain", "Nausea"]
    }
}

BLOOD_TYPES = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
ADMISSION_TYPES = ["Emergency", "Elective", "Urgent"]
INSURANCE_PROVIDERS = [
    "Blue Cross Blue Shield", "Aetna", "Cigna", "UnitedHealth", "Humana",
    "Kaiser Permanente", "Medicare", "Medicaid", "Anthem", "Molina Healthcare"
]

DOCTORS = [
    "Dr. Sarah Johnson", "Dr. Michael Chen", "Dr. Emily Rodriguez", "Dr. David Smith",
    "Dr. Lisa Thompson", "Dr. James Wilson", "Dr. Maria Garcia", "Dr. Robert Brown",
    "Dr. Jennifer Davis", "Dr. Christopher Lee", "Dr. Amanda Taylor", "Dr. Kevin Martinez"
]

HOSPITALS = [
    "City General Hospital", "St. Mary's Medical Center", "Memorial Hospital",
    "University Hospital", "Regional Medical Center", "Community General Hospital",
    "Sacred Heart Hospital", "Mercy Medical Center", "Central Hospital",
    "Metropolitan Medical Center"
]


class HealthcareDataGenerator:
    """Generate synthetic healthcare data for seeding."""
    
    def __init__(self, num_patients: int = 1000):
        self.num_patients = num_patients
        self.fake = Faker()
        
    def generate_patient_record(self) -> Dict[str, Any]:
        """Generate a single patient record."""
        # Basic demographics
        gender = random.choice(["Male", "Female"])
        age = random.randint(18, 90)
        blood_type = random.choice(BLOOD_TYPES)
        
        # Medical condition and related data
        condition = random.choice(list(MEDICAL_CONDITIONS.keys()))
        condition_data = MEDICAL_CONDITIONS[condition]
        
        medication = random.choice(condition_data["medications"])
        
        # Test result based on condition probabilities
        test_result = random.choices(
            list(condition_data["test_results"].keys()),
            weights=list(condition_data["test_results"].values())
        )[0]
        
        # Billing amount with some variation
        base_billing = condition_data["avg_billing"]
        billing_amount = base_billing * random.uniform(0.7, 1.3)
        
        # Dates
        admission_date = self.fake.date_between(start_date='-2y', end_date='today')
        discharge_date = admission_date + timedelta(days=random.randint(1, 14))
        
        return {
            "patient_id": str(uuid.uuid4()),
            "name": self.fake.name(),
            "age": age,
            "gender": gender,
            "blood_type": blood_type,
            "medical_condition": condition,
            "date_of_admission": admission_date.strftime("%Y-%m-%d"),
            "doctor": random.choice(DOCTORS),
            "hospital": random.choice(HOSPITALS),
            "insurance_provider": random.choice(INSURANCE_PROVIDERS),
            "billing_amount": round(billing_amount, 2),
            "room_number": random.randint(100, 999),
            "admission_type": random.choice(ADMISSION_TYPES),
            "discharge_date": discharge_date.strftime("%Y-%m-%d"),
            "medication": medication,
            "test_results": test_result,
            "symptoms": condition_data["symptoms"]
        }
    
    def generate_patient_intake(self, patient_record: Dict[str, Any]) -> Dict[str, Any]:
        """Convert patient record to intake format."""
        condition_data = MEDICAL_CONDITIONS[patient_record["medical_condition"]]
        
        # Generate symptoms with severity
        symptoms = []
        for symptom_desc in random.sample(condition_data["symptoms"], 
                                        random.randint(1, len(condition_data["symptoms"]))):
            symptoms.append({
                "description": symptom_desc,
                "severity": random.randint(4, 9),
                "duration_days": random.randint(7, 60)
            })
        
        # Generate medical history
        medical_history = [
            {
                "condition": patient_record["medical_condition"],
                "status": "active",
                "diagnosis_date": patient_record["date_of_admission"]
            }
        ]
        
        # Add some past conditions for older patients
        if patient_record["age"] > 50:
            past_conditions = random.sample([c for c in MEDICAL_CONDITIONS.keys() 
                                          if c != patient_record["medical_condition"]], 
                                         random.randint(0, 2))
            for condition in past_conditions:
                medical_history.append({
                    "condition": condition,
                    "status": "resolved",
                    "diagnosis_date": (datetime.strptime(patient_record["date_of_admission"], "%Y-%m-%d") 
                                     - timedelta(days=random.randint(365, 1825))).strftime("%Y-%m-%d")
                })
        
        return {
            "patient_id": patient_record["patient_id"],
            "age": patient_record["age"],
            "gender": patient_record["gender"].lower(),
            "weight_kg": random.uniform(50, 120) if patient_record["gender"] == "Female" else random.uniform(60, 140),
            "height_cm": random.uniform(150, 180) if patient_record["gender"] == "Female" else random.uniform(160, 200),
            "chief_complaint": f"Symptoms related to {patient_record['medical_condition'].lower()}",
            "symptoms": symptoms,
            "medical_history": medical_history,
            "family_history": random.sample(list(MEDICAL_CONDITIONS.keys()), random.randint(0, 3)),
            "allergies": random.sample(["Penicillin", "Peanuts", "Shellfish", "Latex", "Pollen"], 
                                     random.randint(0, 2)),
            "current_medications": [
                {
                    "name": patient_record["medication"],
                    "dosage": "As prescribed",
                    "frequency": random.choice(["Once daily", "Twice daily", "Three times daily"]),
                    "active": True
                }
            ],
            "smoking_status": random.choice(["never", "former", "current"]),
            "alcohol_consumption": random.choice(["none", "occasional", "moderate", "heavy"]),
            "exercise_frequency": random.choice(["never", "rarely", "1-2 times/week", "3-4 times/week", "daily"])
        }
    
    def generate_ehr_record(self, patient_record: Dict[str, Any]) -> Dict[str, Any]:
        """Generate EHR record from patient data."""
        return {
            "patient_id": patient_record["patient_id"],
            "record_id": f"ehr_{patient_record['patient_id']}_{int(datetime.now().timestamp())}",
            "mrn": f"MRN{random.randint(100000, 999999)}",
            "date_of_birth": (datetime.now() - timedelta(days=patient_record["age"] * 365)).strftime("%Y-%m-%d"),
            "gender": patient_record["gender"],
            "diagnoses": [
                {
                    "icd_10_code": self.get_icd_code(patient_record["medical_condition"]),
                    "description": patient_record["medical_condition"],
                    "diagnosis_date": patient_record["date_of_admission"],
                    "status": "primary",
                    "provider": patient_record["doctor"]
                }
            ],
            "lab_results": self.generate_lab_results(patient_record["medical_condition"], 
                                                   patient_record["test_results"]),
            "vital_signs": [
                {
                    "temperature_f": round(random.uniform(97.0, 101.0), 1),
                    "blood_pressure_systolic": random.randint(110, 180),
                    "blood_pressure_diastolic": random.randint(70, 120),
                    "heart_rate": random.randint(60, 100),
                    "respiratory_rate": random.randint(12, 20),
                    "oxygen_saturation": round(random.uniform(95.0, 100.0), 1),
                    "recorded_date": patient_record["date_of_admission"]
                }
            ]
        }
    
    def get_icd_code(self, condition: str) -> str:
        """Get ICD-10 code for medical condition."""
        icd_codes = {
            "Diabetes": "E11.9",
            "Hypertension": "I10",
            "Arthritis": "M19.9",
            "Asthma": "J45.9",
            "Obesity": "E66.9",
            "Cancer": "C80.1"
        }
        return icd_codes.get(condition, "Z00.00")
    
    def generate_lab_results(self, condition: str, test_result: str) -> List[Dict[str, Any]]:
        """Generate relevant lab results for condition."""
        labs = []
        
        if condition == "Diabetes":
            hba1c_value = "6.8" if test_result == "Normal" else random.choice(["8.2", "9.1", "10.5"])
            labs.append({
                "test_name": "HbA1c",
                "value": hba1c_value,
                "unit": "%",
                "reference_range": "< 7.0",
                "status": "normal" if test_result == "Normal" else "abnormal",
                "test_date": datetime.now().strftime("%Y-%m-%d")
            })
        
        elif condition == "Hypertension":
            bp_value = "125/80" if test_result == "Normal" else random.choice(["150/95", "160/100", "145/92"])
            labs.append({
                "test_name": "Blood Pressure",
                "value": bp_value,
                "unit": "mmHg",
                "reference_range": "< 130/80",
                "status": "normal" if test_result == "Normal" else "abnormal",
                "test_date": datetime.now().strftime("%Y-%m-%d")
            })
        
        return labs
    
    def save_to_csv(self, filename: str, data: List[Dict[str, Any]]):
        """Save data to CSV file."""
        if not data:
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
    
    def generate_all_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generate all types of healthcare data."""
        print(f"Generating {self.num_patients} patient records...")
        
        patient_records = []
        intake_records = []
        ehr_records = []
        
        for i in range(self.num_patients):
            if i % 100 == 0:
                print(f"Progress: {i}/{self.num_patients}")
            
            # Generate base patient record
            patient_record = self.generate_patient_record()
            patient_records.append(patient_record)
            
            # Generate intake data
            intake_record = self.generate_patient_intake(patient_record)
            intake_records.append(intake_record)
            
            # Generate EHR data
            ehr_record = self.generate_ehr_record(patient_record)
            ehr_records.append(ehr_record)
        
        return {
            "patients": patient_records,
            "intakes": intake_records,
            "ehr_records": ehr_records
        }


if __name__ == "__main__":
    generator = HealthcareDataGenerator(num_patients=500)
    data = generator.generate_all_data()
    
    # Save to CSV files
    generator.save_to_csv("patients.csv", data["patients"])
    generator.save_to_csv("patient_intakes.csv", data["intakes"])
    generator.save_to_csv("ehr_records.csv", data["ehr_records"])
    
    print("Healthcare data generation completed!")
    print(f"Generated {len(data['patients'])} patient records")
    print("Files saved: patients.csv, patient_intakes.csv, ehr_records.csv")