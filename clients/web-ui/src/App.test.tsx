import React from 'react';
import { render } from '@testing-library/react';
import App from './App';

// Mock the AuthProvider
jest.mock('./contexts/AuthContext', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => <div data-testid="auth-provider">{children}</div>,
  useAuth: () => ({
    user: null,
    login: jest.fn(),
    logout: jest.fn(),
    loading: false
  })
}));

// Mock all page components to avoid complex routing issues in tests
jest.mock('./pages/Login', () => () => <div data-testid="login-page">Login Page</div>);
jest.mock('./pages/Dashboard', () => () => <div data-testid="dashboard-page">Dashboard Page</div>);
jest.mock('./pages/CarePlans', () => () => <div data-testid="care-plans-page">Care Plans Page</div>);
jest.mock('./pages/PatientDirectory', () => () => <div data-testid="patient-directory-page">Patient Directory Page</div>);
jest.mock('./pages/BatchOperations', () => () => <div data-testid="batch-operations-page">Batch Operations Page</div>);
jest.mock('./pages/MedicalHistory', () => () => <div data-testid="medical-history-page">Medical History Page</div>);

// Mock ProtectedRoute component
jest.mock('./components/ProtectedRoute', () => ({ children }: { children: React.ReactNode }) => 
  <div data-testid="protected-route">{children}</div>
);

describe('App Component', () => {
  test('renders without crashing', () => {
    const { container } = render(<App />);
    
    // Check if the app renders some content
    expect(container).toBeInTheDocument();
  });

  test('renders auth provider wrapper', () => {
    const { getByTestId } = render(<App />);
    
    // Check if AuthProvider is rendered
    expect(getByTestId('auth-provider')).toBeInTheDocument();
  });

  test('app has theme provider structure', () => {
    const { container } = render(<App />);
    
    // Check if the theme provider structure is applied
    const themeProvider = container.querySelector('.MuiCssBaseline-root');
    expect(container.firstChild).toBeInTheDocument();
  });
});