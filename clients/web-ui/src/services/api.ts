// API service for CarePlan AI backend communication

import axios from 'axios';
import { 
  Patient, 
  PatientIntake, 
  EHRRecord, 
  CarePlan, 
  ApiResponse,
  DashboardStats 
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8002';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token');
      localStorage.removeItem('auth_user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API service class
export class ApiService {
  // Health check
  static async healthCheck(): Promise<any> {
    const response = await apiClient.get('/health');
    return response.data;
  }

  // Patient Intake APIs
  static async submitIntake(intakeData: Partial<PatientIntake>): Promise<ApiResponse<any>> {
    const response = await apiClient.post('/api/intake/submit', intakeData);
    return response.data;
  }

  static async validateIntake(patientId: string): Promise<ApiResponse<any>> {
    const response = await apiClient.get(`/api/intake/validate/${patientId}`);
    return response.data;
  }

  static async getIntakeHistory(patientId: string): Promise<ApiResponse<PatientIntake[]>> {
    const response = await apiClient.get(`/api/intake/${patientId}/history`);
    return response.data;
  }

  // Care Plan APIs
  static async generateCarePlan(patientId: string, overrideExisting = false): Promise<ApiResponse<any>> {
    const response = await apiClient.post(`/api/draft/generate/${patientId}`, {
      override_existing: overrideExisting
    });
    return response.data;
  }

  static async getCarePlanDraft(careplanId: string): Promise<ApiResponse<CarePlan>> {
    const response = await apiClient.get(`/api/draft/${careplanId}`);
    return response.data;
  }

  static async regenerateCarePlanSection(
    careplanId: string, 
    section: string, 
    additionalContext?: string
  ): Promise<ApiResponse<any>> {
    const response = await apiClient.put(`/api/draft/${careplanId}/regenerate`, {
      section,
      additional_context: additionalContext
    });
    return response.data;
  }

  // Review APIs
  static async getPendingReviews(reviewerId?: string): Promise<ApiResponse<CarePlan[]>> {
    const params = reviewerId ? { reviewer_id: reviewerId } : {};
    const response = await apiClient.get('/api/review/pending', { params });
    return response.data;
  }

  static async submitReview(
    careplanId: string, 
    reviewData: {
      reviewer_id: string;
      reviewer_name: string;
      status: string;
      comments?: string;
      modifications?: any[];
    }
  ): Promise<ApiResponse<any>> {
    const response = await apiClient.post(`/api/review/${careplanId}/review`, reviewData);
    return response.data;
  }

  static async approveCarePlan(
    careplanId: string,
    approvalData: {
      approver_id: string;
      approver_name: string;
      final_comments?: string;
    }
  ): Promise<ApiResponse<any>> {
    const response = await apiClient.post(`/api/review/${careplanId}/approve`, approvalData);
    return response.data;
  }

  static async getReviewHistory(careplanId: string): Promise<ApiResponse<any[]>> {
    const response = await apiClient.get(`/api/review/${careplanId}/history`);
    return response.data;
  }

  static async sendCarePlanToPatient(careplanId: string): Promise<ApiResponse<any>> {
    const response = await apiClient.post(`/api/review/${careplanId}/send-to-patient`);
    return response.data;
  }

  // Patient data APIs
  static async getPatientProfile(patientId: string): Promise<Patient> {
    try {
      const response = await apiClient.get(`/api/mock/patients/${patientId}`);
      const data = response.data;
      
      // Transform backend data to frontend Patient type
      return {
        patient_id: data.patient_id,
        name: data.name,
        age: parseInt(data.age) || 0,
        gender: data.gender,
        blood_type: data.blood_type,
        medical_condition: data.medical_condition,
        doctor: data.doctor,
        hospital: data.hospital,
        insurance_provider: data.insurance_provider
      };
    } catch (error: any) {
      console.error('Error fetching patient profile:', error);
      throw error;
    }
  }

  static async getPatientEHR(patientId: string): Promise<EHRRecord> {
    try {
      const response = await apiClient.get(`/api/mock/patients/${patientId}/ehr`);
      return response.data;
    } catch (error: any) {
      console.error('Error fetching patient EHR:', error);
      throw error;
    }
  }

  static async getPatientCarePlans(patientId: string): Promise<CarePlan[]> {
    try {
      const response = await apiClient.get(`/api/mock/patients/${patientId}/care-plans`);
      return response.data;
    } catch (error: any) {
      console.error('Error fetching patient care plans:', error);
      // Return empty array if no care plans found
      if (error.response?.status === 404) {
        return [];
      }
      throw error;
    }
  }

  static async getDashboardStats(patientId?: string): Promise<DashboardStats> {
    try {
      const response = await apiClient.get('/api/mock/dashboard-stats', {
        params: patientId ? { patient_id: patientId } : {}
      });
      return response.data;
    } catch (error: any) {
      console.error('Error fetching dashboard stats:', error);
      throw error;
    }
  }

  // Add new methods for health metrics and other dashboard data
  static async getHealthMetrics(patientId: string): Promise<any[]> {
    try {
      const response = await apiClient.get(`/api/mock/health-metrics/${patientId}`);
      return response.data;
    } catch (error: any) {
      console.error('Error fetching health metrics:', error);
      return [];
    }
  }

  static async getUpcomingAppointments(patientId: string): Promise<any[]> {
    try {
      const response = await apiClient.get(`/api/mock/appointments/${patientId}`);
      return response.data;
    } catch (error: any) {
      console.error('Error fetching appointments:', error);
      return [];
    }
  }

  static async getChartData(patientId: string): Promise<any[]> {
    try {
      const response = await apiClient.get(`/api/mock/chart-data/${patientId}`);
      return response.data;
    } catch (error: any) {
      console.error('Error fetching chart data:', error);
      return [];
    }
  }

  // Clinician-specific APIs
  static async getClinicianCarePlans(status?: string): Promise<any[]> {
    try {
      const response = await apiClient.get('/api/mock/clinician/care-plans', {
        params: status ? { status } : {}
      });
      return response.data;
    } catch (error: any) {
      console.error('Error fetching clinician care plans:', error);
      return [];
    }
  }

  static async getClinicianPatients(): Promise<any[]> {
    try {
      const response = await apiClient.get('/api/mock/clinician/patients');
      return response.data;
    } catch (error: any) {
      console.error('Error fetching clinician patients:', error);
      return [];
    }
  }

  static async submitCarePlanReview(careplanId: string, reviewData: {
    action: 'approve' | 'deny' | 'edit';
    comments?: string;
    modifications?: any;
  }): Promise<any> {
    try {
      const response = await apiClient.put(`/api/mock/care-plans/${careplanId}/review`, reviewData);
      return response.data;
    } catch (error: any) {
      console.error('Error submitting care plan review:', error);
      throw error;
    }
  }

  static async getCarePlanById(careplanId: string): Promise<any> {
    try {
      const response = await apiClient.get(`/api/mock/care-plans/${careplanId}`);
      return response.data;
    } catch (error: any) {
      console.error('Error fetching care plan:', error);
      throw error;
    }
  }

  // Batch Operations APIs
  static async uploadPatientBatch(file: File): Promise<any> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await apiClient.post('/api/batch/intake/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      return response.data;
    } catch (error: any) {
      console.error('Error uploading patient batch:', error);
      console.error('Error details:', error.response?.data, error.response?.status);
      throw error;
    }
  }

  static async batchGenerateCarePlans(forceRegenerate: boolean = false): Promise<any> {
    try {
      const response = await apiClient.post('/api/batch/care-plans/generate', null, {
        params: { force_regenerate: forceRegenerate }
      });
      return response.data;
    } catch (error: any) {
      console.error('Error generating care plans batch:', error);
      throw error;
    }
  }

  static async getBatchJobs(): Promise<any[]> {
    try {
      const response = await apiClient.get('/api/batch/jobs');
      return response.data;
    } catch (error: any) {
      console.error('Error fetching batch jobs:', error);
      return [];
    }
  }

  static async getBatchJobStatus(jobId: string): Promise<any> {
    try {
      const response = await apiClient.get(`/api/batch/jobs/${jobId}`);
      return response.data;
    } catch (error: any) {
      console.error('Error fetching batch job status:', error);
      throw error;
    }
  }

  static async getBatchStats(): Promise<any> {
    try {
      const response = await apiClient.get('/api/batch/stats');
      return response.data;
    } catch (error: any) {
      console.error('Error fetching batch stats:', error);
      throw error;
    }
  }

  static async cancelBatchJob(jobId: string): Promise<any> {
    try {
      const response = await apiClient.delete(`/api/batch/jobs/${jobId}`);
      return response.data;
    } catch (error: any) {
      console.error('Error cancelling batch job:', error);
      throw error;
    }
  }

  // Utility methods
  static async uploadFile(file: File, endpoint: string): Promise<ApiResponse<any>> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post(endpoint, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  }

  static async downloadFile(url: string, filename: string): Promise<void> {
    const response = await apiClient.get(url, {
      responseType: 'blob',
    });
    
    const blob = new Blob([response.data]);
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    link.click();
    window.URL.revokeObjectURL(downloadUrl);
  }
}

export default ApiService;