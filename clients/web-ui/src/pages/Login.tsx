import React, { useState } from 'react';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  Link,
  Checkbox,
  FormControlLabel,
  CircularProgress
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate, Link as RouterLink } from 'react-router-dom';

interface LoginForm {
  email: string;
  password: string;
  remember_me: boolean;
}

const Login: React.FC = () => {
  const [form, setForm] = useState<LoginForm>({
    email: '',
    password: '',
    remember_me: false
  });
  const [error, setError] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, checked, type } = event.target;
    setForm(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError('');
    setIsLoading(true);

    if (!form.email || !form.password) {
      setError('Please enter both email and password');
      setIsLoading(false);
      return;
    }

    try {
      const success = await login({
        email: form.email,
        password: form.password,
        remember_me: form.remember_me
      });

      if (success) {
        navigate('/dashboard');
      } else {
        setError('Invalid email or password. Please try again.');
      }
    } catch (error) {
      setError('Login failed. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    setForm({
      email: 'jerry.clark@email.com',
      password: 'password123',
      remember_me: false
    });
    
    setError('');
    setIsLoading(true);

    try {
      const success = await login({
        email: 'jerry.clark@email.com',
        password: 'password123',
        remember_me: false
      });

      if (success) {
        navigate('/dashboard');
      } else {
        setError('Demo login failed. Please try again.');
      }
    } catch (error) {
      setError('Demo login failed. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container component="main" maxWidth="sm">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper elevation={3} sx={{ padding: 4, width: '100%' }}>
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            <Typography component="h1" variant="h4" color="primary">
              CarePlan AI
            </Typography>
            <Typography variant="subtitle1" color="textSecondary">
              Patient Portal Login
            </Typography>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="email"
              label="Email Address"
              name="email"
              autoComplete="email"
              autoFocus
              value={form.email}
              onChange={handleChange}
              disabled={isLoading}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type="password"
              id="password"
              autoComplete="current-password"
              value={form.password}
              onChange={handleChange}
              disabled={isLoading}
            />
            
            <FormControlLabel
              control={
                <Checkbox
                  value="remember"
                  name="remember_me"
                  color="primary"
                  checked={form.remember_me}
                  onChange={handleChange}
                  disabled={isLoading}
                />
              }
              label="Remember me"
            />
            
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={isLoading}
            >
              {isLoading ? <CircularProgress size={24} /> : 'Sign In'}
            </Button>

            <Button
              fullWidth
              variant="outlined"
              onClick={handleDemoLogin}
              sx={{ mb: 2 }}
              disabled={isLoading}
            >
              Try Demo Account
            </Button>

            <Box sx={{ textAlign: 'center' }}>
              <Link component={RouterLink} to="/register" variant="body2">
                Don't have an account? Sign Up
              </Link>
            </Box>
          </Box>

          <Box sx={{ mt: 4, p: 2, backgroundColor: 'grey.100', borderRadius: 1 }}>
            <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
              <strong>Demo Accounts:</strong>
            </Typography>
            <Typography variant="body2" color="textSecondary">
              • Patient: jerry.clark@email.com / password123
            </Typography>
            <Typography variant="body2" color="textSecondary">
              • Patient: tina.hall@email.com / password123
            </Typography>
            <Typography variant="body2" color="textSecondary">
              • Clinician: dr.garcia@hospital.com / doctor123
            </Typography>
            <Typography variant="body2" color="textSecondary">
              • Admin: admin@hospital.com / admin123
            </Typography>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default Login;