import React, { useState, useEffect, useCallback } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Avatar,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  TextField,
  InputAdornment,
  LinearProgress
} from '@mui/material';
import {
  Person,
  Visibility,
  Assignment,
  Search,
  Refresh,
  Email
} from '@mui/icons-material';
import Layout from '../components/Layout/Layout';
import ApiService from '../services/api';

interface Patient {
  patient_id: string;
  name: string;
  age: number;
  gender: string;
  medical_condition: string;
  doctor: string;
  blood_type: string;
  last_visit?: string;
  next_appointment?: string;
  care_plan_status?: string;
  risk_level?: string;
  treatment_status?: string;
}

const PatientDirectory: React.FC = () => {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [filteredPatients, setFilteredPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  const getTreatmentStatus = (careplanStatus?: string, riskLevel?: string): string => {
    if (careplanStatus === 'needs_review' || careplanStatus === 'under_review') return 'Care Plan Under Review';
    if (careplanStatus === 'approved' && riskLevel === 'high') return 'Actively Treated - High Priority';
    if (careplanStatus === 'approved') return 'Treatment Approved';
    if (careplanStatus === 'active' && riskLevel === 'high') return 'Actively Treated - High Priority';
    if (careplanStatus === 'active') return 'Actively Treated';
    if (careplanStatus === 'completed') return 'Treatment Completed';
    if (careplanStatus === 'no_plan') return 'No Care Plan';
    return 'Status Unknown';
  };

  const loadPatients = useCallback(async () => {
    setLoading(true);
    try {
      // Load patients from API - using the clinician patients endpoint
      const patientsData = await ApiService.getClinicianPatients();
      
      // Enhance patient data with treatment status
      const enhancedPatients = patientsData.map(patient => ({
        ...patient,
        treatment_status: getTreatmentStatus(patient.care_plan_status, patient.risk_level)
      }));
      
      setPatients(enhancedPatients);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Error loading patients:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadPatients();
  }, [loadPatients]);

  useEffect(() => {
    // Filter patients based on search term
    if (searchTerm) {
      const filtered = patients.filter(patient =>
        patient.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        patient.medical_condition.toLowerCase().includes(searchTerm.toLowerCase()) ||
        patient.patient_id.includes(searchTerm)
      );
      setFilteredPatients(filtered);
    } else {
      setFilteredPatients(patients);
    }
  }, [searchTerm, patients]);

  const getTreatmentStatusColor = (treatmentStatus?: string) => {
    switch (treatmentStatus) {
      case 'Care Plan Under Review': return 'warning';
      case 'Actively Treated - High Priority': return 'error';
      case 'Actively Treated': return 'success';
      case 'Treatment Approved': return 'primary';
      case 'Treatment Completed': return 'info';
      case 'No Care Plan': return 'default';
      default: return 'default';
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk?.toLowerCase()) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Layout title="Patient Directory">
        <Box sx={{ width: '100%', mt: 4 }}>
          <LinearProgress />
          <Typography sx={{ mt: 2, textAlign: 'center' }}>
            Loading patient directory...
          </Typography>
        </Box>
      </Layout>
    );
  }

  return (
    <Layout title="Patient Directory">
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
            Patient Directory
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            View all patients under your care with their current treatment status
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="caption" color="text.secondary">
            Last updated: {lastUpdated.toLocaleTimeString()}
          </Typography>
          <IconButton onClick={loadPatients} size="small">
            <Refresh />
          </IconButton>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Patient Summary Stats */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Person color="primary" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h6">{patients.length}</Typography>
              <Typography variant="body2" color="text.secondary">
                Total Patients
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Assignment color="warning" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h6">
                {patients.filter(p => p.treatment_status === 'Care Plan Under Review').length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Under Review
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Assignment color="success" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h6">
                {patients.filter(p => p.treatment_status?.includes('Actively Treated')).length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Actively Treated
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Search and Filter */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Patients ({filteredPatients.length})
                </Typography>
                <TextField
                  size="small"
                  placeholder="Search patients..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Search />
                      </InputAdornment>
                    ),
                  }}
                  sx={{ width: 300 }}
                />
              </Box>

              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Patient</TableCell>
                      <TableCell>Age/Gender</TableCell>
                      <TableCell>Condition</TableCell>
                      <TableCell>Treatment Status</TableCell>
                      <TableCell>Risk Level</TableCell>
                      <TableCell>Last Visit</TableCell>
                      <TableCell>Next Appointment</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filteredPatients.map((patient) => (
                      <TableRow key={patient.patient_id}>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Avatar sx={{ mr: 2, bgcolor: 'primary.main' }}>
                              <Person />
                            </Avatar>
                            <Box>
                              <Typography variant="subtitle2">{patient.name}</Typography>
                              <Typography variant="caption" color="text.secondary">
                                ID: {patient.patient_id.slice(-8)}
                              </Typography>
                            </Box>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {patient.age} years old
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {patient.gender}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">{patient.medical_condition}</Typography>
                          <Chip 
                            label={patient.blood_type} 
                            size="small" 
                            variant="outlined"
                            sx={{ mt: 0.5 }}
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={patient.treatment_status || 'Status Unknown'}
                            size="small"
                            color={getTreatmentStatusColor(patient.treatment_status) as any}
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={patient.risk_level || 'medium'}
                            size="small"
                            color={getRiskColor(patient.risk_level || 'medium') as any}
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {patient.last_visit || 'N/A'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {patient.next_appointment || 'Not scheduled'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 0.5 }}>
                            <IconButton size="small" title="View Patient">
                              <Visibility />
                            </IconButton>
                            <IconButton 
                              size="small" 
                              title="View Care Plans"
                              onClick={() => window.location.href = `/care-plans?patient_id=${patient.patient_id}`}
                            >
                              <Assignment />
                            </IconButton>
                            <IconButton size="small" title="Contact">
                              <Email />
                            </IconButton>
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>

              {filteredPatients.length === 0 && (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="h6" color="text.secondary">
                    No patients found
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {searchTerm ? 'Try adjusting your search criteria' : 'No patients assigned to you yet'}
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Layout>
  );
};

export default PatientDirectory;