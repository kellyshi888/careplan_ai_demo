// Type definitions for CarePlan AI application

export interface Patient {
  patient_id: string;
  name: string;
  age: number;
  gender: string;
  blood_type: string;
  medical_condition: string;
  doctor: string;
  hospital: string;
  insurance_provider: string;
}

export interface Symptom {
  description: string;
  severity: number;
  duration_days?: number;
  onset_date?: string;
}

export interface MedicalHistory {
  condition: string;
  diagnosis_date?: string;
  status: string;
  notes?: string;
}

export interface Medication {
  name: string;
  dosage: string;
  frequency: string;
  start_date?: string;
  prescribing_physician?: string;
  active: boolean;
}

export interface PatientIntake {
  patient_id: string;
  intake_date: string;
  age: number;
  gender: string;
  weight_kg?: number;
  height_cm?: number;
  chief_complaint: string;
  symptoms: Symptom[];
  medical_history: MedicalHistory[];
  family_history: string[];
  allergies: string[];
  current_medications: Medication[];
  smoking_status?: string;
  alcohol_consumption?: string;
  exercise_frequency?: string;
  additional_notes?: string;
}

export interface LabResult {
  test_name: string;
  value: string;
  unit?: string;
  reference_range?: string;
  status?: string;
  test_date: string;
}

export interface VitalSigns {
  temperature_f?: number;
  blood_pressure_systolic?: number;
  blood_pressure_diastolic?: number;
  heart_rate?: number;
  respiratory_rate?: number;
  oxygen_saturation?: number;
  recorded_date: string;
}

export interface Diagnosis {
  icd_10_code?: string;
  description: string;
  diagnosis_date: string;
  status: string;
  provider?: string;
}

export interface EHRRecord {
  patient_id: string;
  record_id: string;
  last_updated: string;
  mrn?: string;
  date_of_birth?: string;
  gender?: string;
  diagnoses: Diagnosis[];
  lab_results: LabResult[];
  vital_signs: VitalSigns[];
}

export interface CarePlanAction {
  action_id: string;
  action_type: 'medication' | 'diagnostic' | 'lifestyle' | 'followup' | 'monitoring' | 'referral';
  description: string;
  priority: 'high' | 'medium' | 'low';
  timeline: string;
  rationale: string;
  evidence_source?: string;
  contraindications: string[];
}

export interface ClinicianReview {
  reviewer_id: string;
  reviewer_name: string;
  review_date: string;
  status: string;
  comments?: string;
  modifications: any[];
}

export interface CarePlan {
  careplan_id: string;
  patient_id: string;
  patient_name?: string;
  created_date: string;
  last_modified: string;
  status: 'draft' | 'under_review' | 'approved' | 'denied' | 'sent_to_patient' | 'active' | 'completed';
  version: number;
  primary_diagnosis: string;
  secondary_diagnoses: string[];
  chief_complaint: string;
  clinical_summary: string;
  actions: CarePlanAction[];
  short_term_goals: string[];
  long_term_goals: string[];
  success_metrics: string[];
  clinician_reviews: ClinicianReview[];
  final_approver?: string;
  approval_date?: string;
  patient_instructions?: string;
  educational_resources: string[];
  llm_model_used?: string;
  generation_timestamp?: string;
  confidence_score?: number;
  assigned_clinician?: string;
  priority?: 'high' | 'medium' | 'low';
  last_review_date?: string;
  reviewer_comments?: string;
  clinician_notes?: string;
}

export interface ApiResponse<T> {
  status: string;
  data?: T;
  message?: string;
  error?: string;
}

export interface DashboardStats {
  totalPatients: number;
  activeCarePlans: number;
  pendingReviews: number;
  completedTreatments: number;
}

export interface AuthUser {
  id: string;
  name: string;
  email: string;
  role: 'patient' | 'clinician' | 'admin';
}

// Navigation and UI types
export interface NavItem {
  label: string;
  path: string;
  icon: string;
  requiresAuth?: boolean;
  roles?: string[];
}

export interface TableColumn {
  field: string;
  headerName: string;
  width?: number;
  type?: 'string' | 'number' | 'date' | 'boolean';
  renderCell?: (params: any) => React.ReactNode;
}

export interface ChartDataPoint {
  date: string;
  value: number;
  label?: string;
}

export interface HealthMetric {
  name: string;
  value: string | number;
  unit?: string;
  status: 'normal' | 'abnormal' | 'critical';
  lastUpdated: string;
  trend?: 'up' | 'down' | 'stable';
}