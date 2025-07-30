import ApiService from './api';

// Mock axios
jest.mock('axios', () => ({
  create: jest.fn(() => ({
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
    interceptors: {
      request: { use: jest.fn() },
      response: { use: jest.fn() }
    }
  }))
}));

describe('ApiService', () => {
  test('should have health check method', () => {
    expect(typeof ApiService.healthCheck).toBe('function');
  });

  test('should have batch operations methods', () => {
    expect(typeof ApiService.uploadPatientBatch).toBe('function');
    expect(typeof ApiService.batchGenerateCarePlans).toBe('function');
    expect(typeof ApiService.getBatchJobs).toBe('function');
  });

  test('should have patient data methods', () => {
    expect(typeof ApiService.getPatientProfile).toBe('function');
    expect(typeof ApiService.getPatientCarePlans).toBe('function');
    expect(typeof ApiService.getClinicianPatients).toBe('function');
  });

  test('should have care plan methods', () => {
    expect(typeof ApiService.getClinicianCarePlans).toBe('function');
    expect(typeof ApiService.submitCarePlanReview).toBe('function');
  });
});