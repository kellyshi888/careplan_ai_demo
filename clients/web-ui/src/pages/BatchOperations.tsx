import React, { useState, useEffect, useCallback } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  LinearProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField
} from '@mui/material';
import {
  Upload,
  AutoAwesome,
  Refresh,
  CheckCircle,
  Error,
  Schedule,
  Cancel,
  CloudUpload,
  Assessment,
  Group,
  Assignment
} from '@mui/icons-material';
import Layout from '../components/Layout/Layout';
import ApiService from '../services/api';

interface BatchJob {
  job_id: string;
  type: string;
  status: string;
  created_at: string;
  total_records?: number;
  processed_records?: number;
  total_patients?: number;
  processed_patients?: number;
  generated_plans?: number;
  errors: string[];
}

interface BatchStats {
  total_patients: number;
  total_intakes: number;
  total_care_plans: number;
  patients_without_care_plans: number;
}

const BatchOperations: React.FC = () => {
  const [jobs, setJobs] = useState<BatchJob[]>([]);
  const [stats, setStats] = useState<BatchStats | null>(null);
  const [uploadDialogOpen, setUploadDialogOpen] = useState<boolean>(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [generatingPlans, setGeneratingPlans] = useState<boolean>(false);

  const loadJobs = useCallback(async () => {
    try {
      const jobsData = await ApiService.getBatchJobs();
      setJobs(jobsData);
    } catch (error) {
      console.error('Error loading batch jobs:', error);
    }
  }, []);

  const loadStats = useCallback(async () => {
    try {
      const statsData = await ApiService.getBatchStats();
      setStats(statsData);
    } catch (error) {
      console.error('Error loading batch stats:', error);
    }
  }, []);

  const loadData = useCallback(async () => {
    await Promise.all([loadJobs(), loadStats()]);
  }, [loadJobs, loadStats]);

  useEffect(() => {
    loadData();
    // Set up polling for job status updates
    const interval = setInterval(loadJobs, 3000);
    return () => clearInterval(interval);
  }, [loadData, loadJobs]);

  const handleFileUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    try {
      await ApiService.uploadPatientBatch(selectedFile);
      
      setUploadDialogOpen(false);
      setSelectedFile(null);
      
      // Show success message and refresh data
      setTimeout(() => {
        loadData();
      }, 1000);
    } catch (error: any) {
      console.error('Error uploading file:', error);
      alert(`Error uploading file: ${error?.response?.data?.detail || error?.message || 'Unknown error'}`);
    } finally {
      setUploading(false);
    }
  };

  const handleGenerateCarePlans = async (forceRegenerate: boolean = false) => {
    setGeneratingPlans(true);
    try {
      await ApiService.batchGenerateCarePlans(forceRegenerate);
      
      // Refresh data after starting the job
      setTimeout(() => {
        loadData();
      }, 1000);
    } catch (error) {
      console.error('Error generating care plans:', error);
    } finally {
      setGeneratingPlans(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'processing': return 'warning';
      case 'failed': return 'error';
      case 'cancelled': return 'default';
      default: return 'info';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle />;
      case 'processing': return <Schedule />;
      case 'failed': return <Error />;
      case 'cancelled': return <Cancel />;
      default: return <Schedule />;
    }
  };

  const formatJobType = (type: string) => {
    switch (type) {
      case 'batch_intake': return 'Patient Intake';
      case 'batch_care_plan_generation': return 'Care Plan Generation';
      default: return type;
    }
  };

  const getProgress = (job: BatchJob) => {
    if (job.type === 'batch_intake' && job.total_records && job.processed_records) {
      return (job.processed_records / job.total_records) * 100;
    }
    if (job.type === 'batch_care_plan_generation' && job.total_patients && job.processed_patients) {
      return (job.processed_patients / job.total_patients) * 100;
    }
    return job.status === 'completed' ? 100 : 0;
  };

  return (
    <Layout title="Batch Operations">
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'primary.main', mb: 1 }}>
          Batch Operations
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Perform bulk operations on patient data and care plans. AI-generated care plans require clinician review before activation.
        </Typography>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Group color="primary" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h6">{stats?.total_patients || 0}</Typography>
              <Typography variant="body2" color="text.secondary">
                Total Patients
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Assignment color="success" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h6">{stats?.total_care_plans || 0}</Typography>
              <Typography variant="body2" color="text.secondary">
                Care Plans
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Assessment color="warning" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h6">{stats?.patients_without_care_plans || 0}</Typography>
              <Typography variant="body2" color="text.secondary">
                Missing Care Plans
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <CloudUpload color="info" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h6">{stats?.total_intakes || 0}</Typography>
              <Typography variant="body2" color="text.secondary">
                Intake Records
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Action Buttons */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Batch Patient Intake
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Upload patient data from Kaggle Healthcare Dataset (CSV/Excel format)
              </Typography>
              <Button
                variant="contained"
                startIcon={<Upload />}
                onClick={() => setUploadDialogOpen(true)}
                disabled={uploading}
                fullWidth
              >
                Upload Patient Data
              </Button>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Generate Care Plans
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Generate AI-assisted care plans for patients. Generated plans will be marked "under review" and require clinician approval.
              </Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  variant="contained"
                  startIcon={<AutoAwesome />}
                  onClick={() => handleGenerateCarePlans(false)}
                  disabled={generatingPlans || (stats?.patients_without_care_plans || 0) === 0}
                  sx={{ flex: 1 }}
                >
                  Generate Missing Plans
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<AutoAwesome />}
                  onClick={() => handleGenerateCarePlans(true)}
                  disabled={generatingPlans}
                  sx={{ flex: 1 }}
                >
                  Regenerate All
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Job Status Table */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              Batch Job Status
            </Typography>
            <Button
              variant="outlined"
              startIcon={<Refresh />}
              onClick={loadData}
              size="small"
            >
              Refresh
            </Button>
          </Box>

          {jobs.length === 0 ? (
            <Alert severity="info">
              No batch jobs have been run yet. Start by uploading patient data or generating care plans.
            </Alert>
          ) : (
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Job ID</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Progress</TableCell>
                    <TableCell>Created</TableCell>
                    <TableCell>Details</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {jobs.map((job) => (
                    <TableRow key={job.job_id}>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                          {job.job_id.slice(-8)}
                        </Typography>
                      </TableCell>
                      <TableCell>{formatJobType(job.type)}</TableCell>
                      <TableCell>
                        <Chip
                          icon={getStatusIcon(job.status)}
                          label={job.status}
                          color={getStatusColor(job.status) as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell sx={{ minWidth: 150 }}>
                        <Box>
                          <LinearProgress
                            variant="determinate"
                            value={getProgress(job)}
                            sx={{ mb: 0.5 }}
                          />
                          <Typography variant="caption">
                            {job.type === 'batch_intake' 
                              ? `${job.processed_records || 0}/${job.total_records || 0} records`
                              : `${job.processed_patients || 0}/${job.total_patients || 0} patients`
                            }
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {new Date(job.created_at).toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        {job.type === 'batch_care_plan_generation' && job.generated_plans && (
                          <Typography variant="body2" color="success.main">
                            {job.generated_plans} plans generated
                          </Typography>
                        )}
                        {job.errors.length > 0 && (
                          <Typography variant="body2" color="error">
                            {job.errors.length} errors
                          </Typography>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* Upload Dialog */}
      <Dialog open={uploadDialogOpen} onClose={() => !uploading && setUploadDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Upload Patient Data</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Upload a CSV or Excel file containing patient data from the Kaggle Healthcare Dataset.
            The file should contain columns like: Name, Age, Gender, Medical Condition, etc.
          </Typography>
          
          <TextField
            type="file"
            fullWidth
            onChange={(e) => {
              const files = (e.target as HTMLInputElement).files;
              setSelectedFile(files ? files[0] : null);
            }}
            inputProps={{
              accept: '.csv,.xlsx,.xls'
            }}
            disabled={uploading}
            sx={{ mb: 2 }}
          />
          
          {selectedFile && (
            <Alert severity="info" sx={{ mb: 2 }}>
              Selected file: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
            </Alert>
          )}
          
          {uploading && (
            <Box sx={{ mb: 2 }}>
              <LinearProgress />
              <Typography variant="body2" sx={{ mt: 1 }}>
                Processing upload...
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadDialogOpen(false)} disabled={uploading}>
            Cancel
          </Button>
          <Button
            onClick={handleFileUpload}
            variant="contained"
            disabled={!selectedFile || uploading}
            startIcon={<CloudUpload />}
          >
            {uploading ? 'Uploading...' : 'Upload'}
          </Button>
        </DialogActions>
      </Dialog>
    </Layout>
  );
};

export default BatchOperations;