import React, { useState, useEffect, useCallback } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Avatar,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Alert,
  Button,
  IconButton
} from '@mui/material';
import {
  Person,
  LocalHospital,
  Assignment,
  TrendingUp,
  Warning,
  CheckCircle,
  Schedule,
  Refresh,
  Visibility
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import ApiService from '../../services/api';
import { Patient, CarePlan, HealthMetric } from '../../types';
import { useAuth } from '../../contexts/AuthContext';

const PatientDashboard: React.FC = () => {
  const { user } = useAuth();
  const [patient, setPatient] = useState<Patient | null>(null);
  const [carePlans, setCarePlans] = useState<CarePlan[]>([]);
  const [healthMetrics, setHealthMetrics] = useState<HealthMetric[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  const patientId = user?.patient_id;

  const loadPatientDashboard = useCallback(async () => {
    if (!patientId) return;
    
    setLoading(true);
    try {
      // Load patient profile, care plans, and health metrics
      const [patientData, carePlansData, healthMetricsData] = await Promise.all([
        ApiService.getPatientProfile(patientId),
        ApiService.getPatientCarePlans(patientId),
        ApiService.getHealthMetrics(patientId)
      ]);

      setPatient(patientData);
      setCarePlans(carePlansData);
      setHealthMetrics(healthMetricsData);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Error loading patient dashboard data:', error);
    } finally {
      setLoading(false);
    }
  }, [patientId]);

  useEffect(() => {
    if (patientId) {
      loadPatientDashboard();
    } else {
      setLoading(false);
    }
  }, [user, patientId, loadPatientDashboard]);

  // Mock chart data
  const chartData = [
    { date: '2024-01-01', glucose: 140, bp_systolic: 135 },
    { date: '2024-01-05', glucose: 155, bp_systolic: 145 },
    { date: '2024-01-10', glucose: 142, bp_systolic: 140 },
    { date: '2024-01-15', glucose: 138, bp_systolic: 145 },
    { date: '2024-01-16', glucose: 135, bp_systolic: 142 }
  ];

  const upcomingAppointments = [
    { date: '2024-01-20', time: '10:00 AM', provider: 'Dr. Sarah Johnson', type: 'Follow-up' },
    { date: '2024-01-25', time: '2:30 PM', provider: 'Nutritionist', type: 'Consultation' },
    { date: '2024-02-01', time: '9:00 AM', provider: 'Lab Work', type: 'Blood Test' }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'normal': return 'success';
      case 'abnormal': return 'warning';
      case 'critical': return 'error';
      default: return 'default';
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return <TrendingUp color="error" />;
      case 'down': return <TrendingUp sx={{ transform: 'rotate(180deg)', color: 'success.main' }} />;
      default: return <TrendingUp sx={{ transform: 'rotate(90deg)', color: 'grey.500' }} />;
    }
  };

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 4 }}>
        <LinearProgress />
        <Typography sx={{ mt: 2, textAlign: 'center' }}>
          Loading your health dashboard...
        </Typography>
      </Box>
    );
  }

  return (
    <>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
            Health Dashboard
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Welcome {user?.first_name || 'Patient'}
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="caption" color="text.secondary">
            Last updated: {lastUpdated.toLocaleTimeString()}
          </Typography>
          <IconButton onClick={loadPatientDashboard} size="small">
            <Refresh />
          </IconButton>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Patient Summary Card */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                  <Person />
                </Avatar>
                <Box>
                  <Typography variant="h6">
                    {patient?.name || `${user?.first_name} ${user?.last_name}`}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {`${patient?.age || 'N/A'} years old • ${patient?.gender || 'N/A'}`}
                  </Typography>
                </Box>
              </Box>
              
              <Divider sx={{ my: 2 }} />
              
              <Box sx={{ mb: 1 }}>
                <Typography variant="body2" color="text.secondary">Primary Condition</Typography>
                <Typography variant="body1">{patient?.medical_condition || 'N/A'}</Typography>
              </Box>
              
              <Box sx={{ mb: 1 }}>
                <Typography variant="body2" color="text.secondary">Care Provider</Typography>
                <Typography variant="body1">{patient?.doctor || 'N/A'}</Typography>
              </Box>
              
              <Box sx={{ mb: 1 }}>
                <Typography variant="body2" color="text.secondary">Blood Type</Typography>
                <Chip label={patient?.blood_type || 'N/A'} size="small" variant="outlined" />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Stats */}
        <Grid item xs={12} md={8}>
          <Grid container spacing={2}>
            <Grid item xs={6} sm={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Assignment color="primary" sx={{ fontSize: 40, mb: 1 }} />
                  <Typography variant="h6">{carePlans.length}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Active Plans
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Schedule color="warning" sx={{ fontSize: 40, mb: 1 }} />
                  <Typography variant="h6">{upcomingAppointments.length}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Appointments
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <LocalHospital color="success" sx={{ fontSize: 40, mb: 1 }} />
                  <Typography variant="h6">
                    {healthMetrics.filter(m => m.status === 'normal').length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Normal Metrics
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Warning color="error" sx={{ fontSize: 40, mb: 1 }} />
                  <Typography variant="h6">
                    {healthMetrics.filter(m => m.status !== 'normal').length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Needs Attention
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Grid>

        {/* Health Metrics */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Health Metrics
              </Typography>
              <List>
                {healthMetrics.map((metric, index) => (
                  <React.Fragment key={metric.name}>
                    <ListItem>
                      <ListItemIcon>
                        {getTrendIcon(metric.trend || 'stable')}
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Typography>{metric.name}</Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Typography variant="body2">
                                {metric.value} {metric.unit}
                              </Typography>
                              <Chip 
                                size="small" 
                                label={metric.status}
                                color={getStatusColor(metric.status) as any}
                                variant="outlined"
                              />
                            </Box>
                          </Box>
                        }
                        secondary={`Last updated: ${metric.lastUpdated}`}
                      />
                    </ListItem>
                    {index < healthMetrics.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Upcoming Appointments */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Upcoming Appointments
              </Typography>
              <List>
                {upcomingAppointments.map((appointment, index) => (
                  <React.Fragment key={index}>
                    <ListItem>
                      <ListItemIcon>
                        <Schedule color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Typography>{appointment.provider}</Typography>
                            <Typography variant="body2" color="text.secondary">
                              {appointment.type}
                            </Typography>
                          </Box>
                        }
                        secondary={`${appointment.date} at ${appointment.time}`}
                      />
                    </ListItem>
                    {index < upcomingAppointments.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Health Trends Chart */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Health Trends (Last 30 Days)
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Line 
                    type="monotone" 
                    dataKey="glucose" 
                    stroke="#8884d8" 
                    name="Blood Glucose (mg/dL)"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="bp_systolic" 
                    stroke="#82ca9d" 
                    name="Blood Pressure Systolic"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Active Care Plan Summary */}
        {carePlans.length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">Current Care Plan</Typography>
                  <Button 
                    variant="outlined" 
                    startIcon={<Visibility />}
                    onClick={() => window.location.href = '/care-plans'}
                  >
                    View Details
                  </Button>
                </Box>
                
                <Alert severity="info" sx={{ mb: 2 }}>
                  Your care plan was last updated on {new Date(carePlans[0].last_modified).toLocaleDateString()}
                </Alert>

                <Typography variant="subtitle1" sx={{ mb: 1 }}>
                  Primary Focus: {carePlans[0].primary_diagnosis}
                </Typography>
                
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {carePlans[0].clinical_summary}
                </Typography>

                <Typography variant="subtitle2" sx={{ mb: 1 }}>
                  Current Actions ({carePlans[0].actions.length}):</Typography>
                
                <List dense>
                  {carePlans[0].actions.slice(0, 3).map((action, index) => (
                    <ListItem key={action.action_id}>
                      <ListItemIcon>
                        <CheckCircle color={action.priority === 'high' ? 'error' : 'success'} />
                      </ListItemIcon>
                      <ListItemText
                        primary={action.description}
                        secondary={`Priority: ${action.priority} • ${action.timeline}`}
                      />
                    </ListItem>
                  ))}
                  {carePlans[0].actions.length > 3 && (
                    <ListItem>
                      <ListItemText
                        primary={
                          <Typography variant="body2" color="primary">
                            +{carePlans[0].actions.length - 3} more actions
                          </Typography>
                        }
                      />
                    </ListItem>
                  )}
                </List>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </>
  );
};

export default PatientDashboard;