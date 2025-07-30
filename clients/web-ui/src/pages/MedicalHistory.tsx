import React, { useState, useEffect, useCallback } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tab,
  Tabs,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Alert,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  LocalHospital,
  Medication,
  Science,
  Assignment,
  Warning,
  Download,
  Visibility
} from '@mui/icons-material';
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot
} from '@mui/lab';
import Layout from '../components/Layout/Layout';
import ApiService from '../services/api';
import { Patient, EHRRecord, PatientIntake } from '../types';
import { useAuth } from '../contexts/AuthContext';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`medical-history-tabpanel-${index}`}
      aria-labelledby={`medical-history-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const MedicalHistory: React.FC = () => {
  const { user } = useAuth();
  const [, setPatient] = useState<Patient | null>(null);
  const [ehrRecord, setEhrRecord] = useState<EHRRecord | null>(null);
  const [intakeHistory, setIntakeHistory] = useState<PatientIntake[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<number>(0);

  // Get patient ID from authenticated user
  const patientId = user?.patient_id;

  const loadMedicalHistory = useCallback(async () => {
    if (!patientId) return;
    
    setLoading(true);
    try {
      const [patientData, ehrData] = await Promise.all([
        ApiService.getPatientProfile(patientId),
        ApiService.getPatientEHR(patientId)
      ]);

      setPatient(patientData);
      setEhrRecord(ehrData);

      // Mock intake history
      setIntakeHistory([
        {
          patient_id: patientId,
          intake_date: '2024-01-15T10:30:00Z',
          age: 45,
          gender: 'male',
          weight_kg: 85.5,
          height_cm: 175,
          chief_complaint: 'Elevated blood sugar levels and frequent urination',
          symptoms: [
            { description: 'Frequent urination', severity: 7, duration_days: 14 },
            { description: 'Excessive thirst', severity: 6, duration_days: 10 }
          ],
          medical_history: [
            { condition: 'Type 2 Diabetes', status: 'active', diagnosis_date: '2023-01-15' },
            { condition: 'Hypertension', status: 'active', diagnosis_date: '2022-06-10' }
          ],
          family_history: ['Diabetes', 'Heart Disease'],
          allergies: ['Penicillin'],
          current_medications: [
            { name: 'Metformin', dosage: '500mg', frequency: 'twice daily', active: true },
            { name: 'Lisinopril', dosage: '10mg', frequency: 'once daily', active: true }
          ],
          smoking_status: 'never',
          alcohol_consumption: 'occasional',
          exercise_frequency: '2-3 times per week',
          additional_notes: 'Patient reports improved glucose control with current regimen'
        }
      ]);
    } catch (error) {
      console.error('Error loading medical history:', error);
    } finally {
      setLoading(false);
    }
  }, [patientId]);

  useEffect(() => {
    if (patientId) {
      loadMedicalHistory();
    }
  }, [patientId, loadMedicalHistory]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'normal': return 'success';
      case 'abnormal': return 'warning';
      case 'critical': return 'error';
      case 'active': return 'primary';
      case 'resolved': return 'default';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Layout title="Medical History">
        <Box sx={{ textAlign: 'center', mt: 4 }}>
          <Typography>Loading medical history...</Typography>
        </Box>
      </Layout>
    );
  }

  return (
    <Layout title="Medical History">
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'primary.main', mb: 1 }}>
          Medical History
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Complete medical record and treatment history
        </Typography>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange} aria-label="medical history tabs">
          <Tab label="Timeline" />
          <Tab label="Diagnoses" />
          <Tab label="Medications" />
          <Tab label="Lab Results" />
          <Tab label="Vital Signs" />
        </Tabs>
      </Box>

      {/* Timeline Tab */}
      <TabPanel value={activeTab} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 3 }}>
                  Medical Timeline
                </Typography>
                <Timeline>
                  {/* Recent Intake */}
                  <TimelineItem>
                    <TimelineSeparator>
                      <TimelineDot color="primary">
                        <Assignment />
                      </TimelineDot>
                      <TimelineConnector />
                    </TimelineSeparator>
                    <TimelineContent>
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="h6">
                          Patient Intake - Follow-up Visit
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          January 15, 2024
                        </Typography>
                        <Typography variant="body1" sx={{ mt: 1 }}>
                          Chief Complaint: {intakeHistory[0]?.chief_complaint}
                        </Typography>
                        <Box sx={{ mt: 1 }}>
                          {intakeHistory[0]?.symptoms.map((symptom, index) => (
                            <Chip
                              key={index}
                              label={`${symptom.description} (${symptom.severity}/10)`}
                              size="small"
                              color={symptom.severity > 6 ? 'error' : 'warning'}
                              sx={{ mr: 1, mb: 1 }}
                            />
                          ))}
                        </Box>
                      </Box>
                    </TimelineContent>
                  </TimelineItem>

                  {/* Lab Results */}
                  {ehrRecord?.lab_results.map((lab, index) => (
                    <TimelineItem key={index}>
                      <TimelineSeparator>
                        <TimelineDot color={getStatusColor(lab.status || '') as any}>
                          <Science />
                        </TimelineDot>
                        <TimelineConnector />
                      </TimelineSeparator>
                      <TimelineContent>
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="h6">
                            {lab.test_name} Results
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {new Date(lab.test_date).toLocaleDateString()}
                          </Typography>
                          <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body1">
                              {lab.value} {lab.unit}
                            </Typography>
                            <Chip
                              label={lab.status}
                              size="small"
                              color={getStatusColor(lab.status || '') as any}
                            />
                          </Box>
                          {lab.reference_range && (
                            <Typography variant="body2" color="text.secondary">
                              Reference: {lab.reference_range}
                            </Typography>
                          )}
                        </Box>
                      </TimelineContent>
                    </TimelineItem>
                  ))}

                  {/* Diagnoses */}
                  {ehrRecord?.diagnoses.map((diagnosis, index) => (
                    <TimelineItem key={index}>
                      <TimelineSeparator>
                        <TimelineDot color="secondary">
                          <LocalHospital />
                        </TimelineDot>
                        {index < ehrRecord.diagnoses.length - 1 && <TimelineConnector />}
                      </TimelineSeparator>
                      <TimelineContent>
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="h6">
                            Diagnosis: {diagnosis.description}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {new Date(diagnosis.diagnosis_date).toLocaleDateString()}
                          </Typography>
                          <Box sx={{ mt: 1 }}>
                            <Chip
                              label={diagnosis.status}
                              size="small"
                              color={getStatusColor(diagnosis.status) as any}
                            />
                            {diagnosis.icd_10_code && (
                              <Chip
                                label={`ICD-10: ${diagnosis.icd_10_code}`}
                                size="small"
                                variant="outlined"
                                sx={{ ml: 1 }}
                              />
                            )}
                          </Box>
                          {diagnosis.provider && (
                            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                              Provider: {diagnosis.provider}
                            </Typography>
                          )}
                        </Box>
                      </TimelineContent>
                    </TimelineItem>
                  ))}
                </Timeline>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Diagnoses Tab */}
      <TabPanel value={activeTab} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 3 }}>
                  Current and Past Diagnoses
                </Typography>
                
                {ehrRecord?.diagnoses.length === 0 ? (
                  <Alert severity="info">No diagnoses on record</Alert>
                ) : (
                  <List>
                    {ehrRecord?.diagnoses.map((diagnosis, index) => (
                      <React.Fragment key={index}>
                        <ListItem>
                          <ListItemIcon>
                            <LocalHospital color={getStatusColor(diagnosis.status) as any} />
                          </ListItemIcon>
                          <ListItemText
                            primary={
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Typography variant="subtitle1">
                                  {diagnosis.description}
                                </Typography>
                                <Chip
                                  label={diagnosis.status}
                                  size="small"
                                  color={getStatusColor(diagnosis.status) as any}
                                />
                              </Box>
                            }
                            secondary={
                              <Box>
                                <Typography variant="body2" color="text.secondary">
                                  Diagnosed: {new Date(diagnosis.diagnosis_date).toLocaleDateString()}
                                </Typography>
                                {diagnosis.icd_10_code && (
                                  <Typography variant="body2" color="text.secondary">
                                    ICD-10 Code: {diagnosis.icd_10_code}
                                  </Typography>
                                )}
                                {diagnosis.provider && (
                                  <Typography variant="body2" color="text.secondary">
                                    Provider: {diagnosis.provider}
                                  </Typography>
                                )}
                              </Box>
                            }
                          />
                        </ListItem>
                        {index < ehrRecord.diagnoses.length - 1 && <Divider />}
                      </React.Fragment>
                    ))}
                  </List>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Medications Tab */}
      <TabPanel value={activeTab} index={2}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 3 }}>
                  Current Medications
                </Typography>
                
                {intakeHistory[0]?.current_medications.length === 0 ? (
                  <Alert severity="info">No current medications on record</Alert>
                ) : (
                  <List>
                    {intakeHistory[0]?.current_medications.map((medication, index) => (
                      <React.Fragment key={index}>
                        <ListItem>
                          <ListItemIcon>
                            <Medication color={medication.active ? 'primary' : 'disabled'} />
                          </ListItemIcon>
                          <ListItemText
                            primary={
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Typography variant="subtitle1">
                                  {medication.name}
                                </Typography>
                                <Chip
                                  label={medication.active ? 'Active' : 'Inactive'}
                                  size="small"
                                  color={medication.active ? 'success' : 'default'}
                                />
                              </Box>
                            }
                            secondary={
                              <Box>
                                <Typography variant="body2" color="text.secondary">
                                  Dosage: {medication.dosage} • Frequency: {medication.frequency}
                                </Typography>
                                {medication.prescribing_physician && (
                                  <Typography variant="body2" color="text.secondary">
                                    Prescribed by: {medication.prescribing_physician}
                                  </Typography>
                                )}
                              </Box>
                            }
                          />
                        </ListItem>
                        {index < intakeHistory[0].current_medications.length - 1 && <Divider />}
                      </React.Fragment>
                    ))}
                  </List>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Allergies */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  Known Allergies
                </Typography>
                
                {intakeHistory[0]?.allergies.length === 0 ? (
                  <Alert severity="success">No known allergies</Alert>
                ) : (
                  <Box>
                    <Alert severity="warning" sx={{ mb: 2 }}>
                      <Warning sx={{ mr: 1 }} />
                      Patient has known allergies
                    </Alert>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {intakeHistory[0]?.allergies.map((allergy, index) => (
                        <Chip
                          key={index}
                          label={allergy}
                          color="error"
                          variant="outlined"
                          icon={<Warning />}
                        />
                      ))}
                    </Box>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Lab Results Tab */}
      <TabPanel value={activeTab} index={3}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 3 }}>
                  Laboratory Results
                </Typography>
                
                <TableContainer component={Paper} variant="outlined">
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Test Name</TableCell>
                        <TableCell>Result</TableCell>
                        <TableCell>Reference Range</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Date</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {ehrRecord?.lab_results.map((lab, index) => (
                        <TableRow key={index}>
                          <TableCell>{lab.test_name}</TableCell>
                          <TableCell>
                            <strong>{lab.value} {lab.unit}</strong>
                          </TableCell>
                          <TableCell>{lab.reference_range || 'N/A'}</TableCell>
                          <TableCell>
                            <Chip
                              label={lab.status}
                              size="small"
                              color={getStatusColor(lab.status || '') as any}
                            />
                          </TableCell>
                          <TableCell>
                            {new Date(lab.test_date).toLocaleDateString()}
                          </TableCell>
                          <TableCell>
                            <Tooltip title="View Details">
                              <IconButton size="small">
                                <Visibility />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Download Report">
                              <IconButton size="small">
                                <Download />
                              </IconButton>
                            </Tooltip>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Vital Signs Tab */}
      <TabPanel value={activeTab} index={4}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 3 }}>
                  Recent Vital Signs
                </Typography>
                
                <TableContainer component={Paper} variant="outlined">
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Date</TableCell>
                        <TableCell>Temperature</TableCell>
                        <TableCell>Blood Pressure</TableCell>
                        <TableCell>Heart Rate</TableCell>
                        <TableCell>Respiratory Rate</TableCell>
                        <TableCell>O2 Saturation</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {ehrRecord?.vital_signs.map((vitals, index) => (
                        <TableRow key={index}>
                          <TableCell>
                            {new Date(vitals.recorded_date).toLocaleDateString()}
                          </TableCell>
                          <TableCell>
                            {vitals.temperature_f ? `${vitals.temperature_f}°F` : 'N/A'}
                          </TableCell>
                          <TableCell>
                            {vitals.blood_pressure_systolic && vitals.blood_pressure_diastolic
                              ? `${vitals.blood_pressure_systolic}/${vitals.blood_pressure_diastolic} mmHg`
                              : 'N/A'}
                          </TableCell>
                          <TableCell>
                            {vitals.heart_rate ? `${vitals.heart_rate} bpm` : 'N/A'}
                          </TableCell>
                          <TableCell>
                            {vitals.respiratory_rate ? `${vitals.respiratory_rate} /min` : 'N/A'}
                          </TableCell>
                          <TableCell>
                            {vitals.oxygen_saturation ? `${vitals.oxygen_saturation}%` : 'N/A'}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>
    </Layout>
  );
};

export default MedicalHistory;