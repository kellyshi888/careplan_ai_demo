import React, { useState, useEffect, useCallback } from 'react';
import {
  Grid,
  Card,
  CardContent,
  CardActions,
  Typography,
  Box,
  Chip,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
  Alert,
  IconButton,
  Tooltip,
  Divider,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Paper,
  TextField
} from '@mui/material';
import {
  Assignment,
  CheckCircle,
  Info,
  Download,
  Refresh,
  Print,
  Share,
  Visibility,
  Timeline as TimelineIcon,
  LocalHospital,
  Medication,
  FitnessCenter,
  MonitorHeart,
  PersonAdd,
  Warning
} from '@mui/icons-material';
import Layout from '../components/Layout/Layout';
import ApiService from '../services/api';
import { Patient, CarePlan } from '../types';
import { useAuth } from '../contexts/AuthContext';
import { useLocation, useNavigate } from 'react-router-dom';

const CarePlans: React.FC = () => {
  const { user } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [, setPatient] = useState<Patient | null>(null);
  const [carePlans, setCarePlans] = useState<CarePlan[]>([]);
  const [selectedPlan, setSelectedPlan] = useState<CarePlan | null>(null);
  const [detailsOpen, setDetailsOpen] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [reviewDialogOpen, setReviewDialogOpen] = useState<boolean>(false);
  const [reviewingPlan, setReviewingPlan] = useState<any | null>(null);
  const [submittingReview, setSubmittingReview] = useState<boolean>(false);

  // Get patient ID from authenticated user
  const patientId = user?.patient_id;
  const isPatient = user?.role === 'patient';
  const isClinician = user?.role === 'clinician';

  // Get status filter from URL parameters or default to 'all'
  const urlParams = new URLSearchParams(location.search);
  const [statusFilter, setStatusFilter] = useState<string>(
    urlParams.get('status') || 'all'
  );

  // Sync status filter with URL changes
  useEffect(() => {
    const urlParams = new URLSearchParams(location.search);
    const urlStatus = urlParams.get('status') || 'all';
    if (urlStatus !== statusFilter) {
      setStatusFilter(urlStatus);
    }
  }, [location.search, statusFilter]);

  const loadPatientCarePlans = useCallback(async () => {
    if (!patientId) return;
    
    setLoading(true);
    try {
      const [patientData, carePlansData] = await Promise.all([
        ApiService.getPatientProfile(patientId),
        ApiService.getPatientCarePlans(patientId)
      ]);

      setPatient(patientData);
      setCarePlans(carePlansData);
    } catch (error) {
      console.error('Error loading patient care plans:', error);
    } finally {
      setLoading(false);
    }
  }, [patientId]);

  const loadClinicianCarePlans = useCallback(async () => {
    setLoading(true);
    try {
      const filterStatus = statusFilter === 'all' ? undefined : statusFilter;
      const carePlansData = await ApiService.getClinicianCarePlans(filterStatus);
      setCarePlans(carePlansData);
      setPatient(null); // No specific patient for clinician view
    } catch (error) {
      console.error('Error loading clinician care plans:', error);
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => {
    if (isPatient && patientId) {
      loadPatientCarePlans();
    } else if (isClinician) {
      loadClinicianCarePlans();
    }
  }, [isPatient, isClinician, patientId, statusFilter, loadPatientCarePlans, loadClinicianCarePlans]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'success';
      case 'active': return 'primary';
      case 'completed': return 'info';
      case 'under_review': return 'secondary';
      default: return 'default';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const getActionIcon = (actionType: string) => {
    switch (actionType) {
      case 'medication': return <Medication />;
      case 'diagnostic': return <LocalHospital />;
      case 'lifestyle': return <FitnessCenter />;
      case 'monitoring': return <MonitorHeart />;
      case 'referral': return <PersonAdd />;
      default: return <Assignment />;
    }
  };

  const handlePlanDetails = (plan: CarePlan) => {
    setSelectedPlan(plan);
    setDetailsOpen(true);
  };

  const handleCloseDetails = () => {
    setDetailsOpen(false);
    setSelectedPlan(null);
  };

  const handleReviewPlan = (plan: any) => {
    setReviewingPlan(plan);
    setReviewDialogOpen(true);
  };

  const handleCloseReview = () => {
    setReviewDialogOpen(false);
    setReviewingPlan(null);
  };

  const handleSubmitReview = async (action: 'approve' | 'deny' | 'edit', comments: string, modifications?: any) => {
    if (!reviewingPlan) return;

    setSubmittingReview(true);
    try {
      // Optimistically update the plan status in the local state
      const updatedCarePlans = carePlans.map(plan => 
        plan.careplan_id === reviewingPlan.careplan_id 
          ? { 
              ...plan, 
              status: action === 'approve' ? 'approved' as const : 
                     action === 'deny' ? 'denied' as const : 
                     plan.status, // Keep current status for edit
              reviewer_comments: comments,
              // Apply modifications for edit action
              ...(action === 'edit' && modifications ? {
                clinical_summary: modifications.clinical_summary,
                actions: modifications.actions,
                short_term_goals: modifications.short_term_goals
              } : {})
            }
          : plan
      );
      setCarePlans(updatedCarePlans);

      // Submit the review to the backend
      await ApiService.submitCarePlanReview(reviewingPlan.careplan_id, {
        action,
        comments,
        modifications
      });

      handleCloseReview();
      
      // Refresh the care plans list to get the latest data
      if (isClinician) {
        setTimeout(() => loadClinicianCarePlans(), 500);
      }
    } catch (error) {
      console.error('Error submitting review:', error);
      // Revert the optimistic update on error
      loadClinicianCarePlans();
    } finally {
      setSubmittingReview(false);
    }
  };

  const handleStatusFilterChange = (newStatus: string) => {
    setStatusFilter(newStatus);
    
    // Update URL to reflect the status filter
    const urlParams = new URLSearchParams(location.search);
    if (newStatus === 'all') {
      urlParams.delete('status');
    } else {
      urlParams.set('status', newStatus);
    }
    
    const newSearch = urlParams.toString();
    const newUrl = newSearch ? `${location.pathname}?${newSearch}` : location.pathname;
    navigate(newUrl, { replace: true });
  };

  const calculateProgress = (plan: CarePlan) => {
    if (!plan.actions || plan.actions.length === 0) return 0;
    const completedActions = plan.actions.filter(action => 
      action.timeline === 'completed' || action.timeline === 'done'
    ).length;
    return (completedActions / plan.actions.length) * 100;
  };

  if (loading) {
    return (
      <Layout title="Care Plans">
        <Box sx={{ width: '100%', mt: 4 }}>
          <LinearProgress />
          <Typography sx={{ mt: 2, textAlign: 'center' }}>
            Loading your care plans...
          </Typography>
        </Box>
      </Layout>
    );
  }

  return (
    <Layout title="My Care Plans">
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'primary.main', mb: 1 }}>
            {isClinician ? 'Care Plans Management' : 'My Care Plans'}
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {isClinician 
              ? 'Review and manage patient care plans' 
              : 'Personalized treatment recommendations and health goals'
            }
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={isPatient ? loadPatientCarePlans : loadClinicianCarePlans}
          >
            Refresh
          </Button>
          <Button
            variant="outlined"
            startIcon={<Print />}
          >
            Print All
          </Button>
          <Button
            variant="outlined"
            startIcon={<Download />}
          >
            Export
          </Button>
        </Box>
      </Box>

      {/* Status Filter for Clinicians */}
      {isClinician && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>Filter by Status</Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {['all', 'under_review', 'approved', 'completed', 'denied'].map((status) => (
              <Button
                key={status}
                variant={statusFilter === status ? 'contained' : 'outlined'}
                size="small"
                onClick={() => handleStatusFilterChange(status)}
                sx={{ textTransform: 'capitalize' }}
              >
                {status === 'all' ? 'All Plans' : status.replace('_', ' ')}
              </Button>
            ))}
          </Box>
        </Box>
      )}

      {carePlans.length === 0 ? (
        <Alert severity="info" sx={{ mt: 3 }}>
          <Typography variant="h6">No Care Plans Available</Typography>
          <Typography>
            No personalized care plans have been generated for you yet. 
            Please contact your healthcare provider to discuss creating a care plan.
          </Typography>
        </Alert>
      ) : (
        <Grid container spacing={3}>
          {carePlans && carePlans.length > 0 ? carePlans.map((plan, index) => (
            <Grid item xs={12} key={plan.careplan_id}>
              <Card 
                sx={{ 
                  border: index === 0 ? 2 : 1, 
                  borderColor: index === 0 ? 'primary.main' : 'grey.300',
                  position: 'relative'
                }}
              >
                {index === 0 && (
                  <Chip
                    label="Current Plan"
                    color="primary"
                    sx={{ position: 'absolute', top: 16, right: 16, zIndex: 1 }}
                  />
                )}
                
                <CardContent>
                  {/* Plan Header */}
                  <Box sx={{ mb: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
                      <Box>
                        <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 1 }}>
                          {isClinician && plan.patient_name && (
                            <Box sx={{ mb: 1 }}>
                              <Typography component="span" variant="h6" color="primary.main">
                                {plan.patient_name} - 
                              </Typography>
                            </Box>
                          )}
                          {plan.primary_diagnosis} Care Plan
                        </Typography>
                        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                          {plan.clinical_summary || plan.chief_complaint}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                        <Chip
                          label={plan.status.replace('_', ' ')}
                          color={getStatusColor(plan.status) as any}
                          variant="outlined"
                        />
                        {plan.confidence_score && (
                          <Tooltip title={`AI Confidence: ${(plan.confidence_score * 100).toFixed(1)}%`}>
                            <Chip
                              label={`${(plan.confidence_score * 100).toFixed(0)}%`}
                              size="small"
                              color="info"
                              variant="outlined"
                            />
                          </Tooltip>
                        )}
                      </Box>
                    </Box>

                    {/* Plan Metadata */}
                    <Grid container spacing={2} sx={{ mb: 3 }}>
                      <Grid item xs={12} sm={6} md={3}>
                        <Typography variant="caption" color="text.secondary">
                          Created Date
                        </Typography>
                        <Typography variant="body2">
                          {new Date(plan.created_date).toLocaleDateString()}
                        </Typography>
                      </Grid>
                      <Grid item xs={12} sm={6} md={3}>
                        <Typography variant="caption" color="text.secondary">
                          Last Modified
                        </Typography>
                        <Typography variant="body2">
                          {new Date(plan.last_modified).toLocaleDateString()}
                        </Typography>
                      </Grid>
                      <Grid item xs={12} sm={6} md={3}>
                        <Typography variant="caption" color="text.secondary">
                          Version
                        </Typography>
                        <Typography variant="body2">
                          v{plan.version}
                        </Typography>
                      </Grid>
                      <Grid item xs={12} sm={6} md={3}>
                        <Typography variant="caption" color="text.secondary">
                          Actions
                        </Typography>
                        <Typography variant="body2">
                          {plan.actions.length} total
                        </Typography>
                      </Grid>
                    </Grid>

                    {/* Progress Bar */}
                    <Box sx={{ mb: 3 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          Progress
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {calculateProgress(plan).toFixed(0)}% Complete
                        </Typography>
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={calculateProgress(plan)}
                        sx={{ height: 8, borderRadius: 4 }}
                      />
                    </Box>
                  </Box>

                  {/* Goals Summary */}
                  <Grid container spacing={3} sx={{ mb: 3 }}>
                    <Grid item xs={12} md={6}>
                      <Typography variant="h6" sx={{ mb: 2 }}>
                        Short-term Goals
                      </Typography>
                      <List dense>
                        {plan.short_term_goals && plan.short_term_goals.map((goal, goalIndex) => (
                          <ListItem key={goalIndex} sx={{ pl: 0 }}>
                            <ListItemIcon sx={{ minWidth: 32 }}>
                              <CheckCircle color="primary" fontSize="small" />
                            </ListItemIcon>
                            <ListItemText primary={goal} />
                          </ListItem>
                        ))}
                      </List>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant="h6" sx={{ mb: 2 }}>
                        Success Metrics
                      </Typography>
                      <List dense>
                        {plan.success_metrics && plan.success_metrics.map((metric, metricIndex) => (
                          <ListItem key={metricIndex} sx={{ pl: 0 }}>
                            <ListItemIcon sx={{ minWidth: 32 }}>
                              <TimelineIcon color="success" fontSize="small" />
                            </ListItemIcon>
                            <ListItemText primary={metric} />
                          </ListItem>
                        ))}
                      </List>
                    </Grid>
                  </Grid>

                  {/* Actions Preview */}
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    Current Actions ({plan.actions ? plan.actions.length : 0})
                  </Typography>
                  
                  <Grid container spacing={2}>
                    {plan.actions && plan.actions.slice(0, 3).map((action, actionIndex) => (
                      <Grid item xs={12} sm={6} md={4} key={action.action_id}>
                        <Paper 
                          sx={{ 
                            p: 2, 
                            border: 1, 
                            borderColor: 'grey.200',
                            height: '100%'
                          }}
                        >
                          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                            {getActionIcon(action.action_type)}
                            <Chip
                              label={action.priority}
                              size="small"
                              color={getPriorityColor(action.priority) as any}
                              sx={{ ml: 'auto' }}
                            />
                          </Box>
                          <Typography variant="subtitle2" sx={{ mb: 1 }}>
                            {action.description}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Timeline: {action.timeline}
                          </Typography>
                        </Paper>
                      </Grid>
                    ))}
                    
                    {plan.actions && plan.actions.length > 3 && (
                      <Grid item xs={12}>
                        <Alert severity="info">
                          <Typography variant="body2">
                            +{plan.actions.length - 3} more actions. 
                            <Button 
                              size="small" 
                              onClick={() => handlePlanDetails(plan)}
                              sx={{ ml: 1 }}
                            >
                              View All
                            </Button>
                          </Typography>
                        </Alert>
                      </Grid>
                    )}
                  </Grid>
                </CardContent>

                <CardActions sx={{ justifyContent: 'space-between', px: 3, pb: 3 }}>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button
                      variant="contained"
                      startIcon={<Visibility />}
                      onClick={() => handlePlanDetails(plan)}
                    >
                      View Details
                    </Button>
                    {isClinician && plan.status === 'under_review' && (
                      <Button
                        variant="contained"
                        color="warning"
                        startIcon={<Assignment />}
                        onClick={() => handleReviewPlan(plan)}
                      >
                        Review & Approve
                      </Button>
                    )}
                    {isClinician && plan.status !== 'under_review' && (
                      <Button
                        variant="outlined"
                        color="primary"
                        startIcon={<Assignment />}
                        onClick={() => handleReviewPlan(plan)}
                      >
                        Edit Plan
                      </Button>
                    )}
                    <Button
                      variant="outlined"
                      startIcon={<Download />}
                    >
                      Download PDF
                    </Button>
                  </Box>
                  
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Tooltip title="Share Plan">
                      <IconButton>
                        <Share />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Print Plan">
                      <IconButton>
                        <Print />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </CardActions>
              </Card>
            </Grid>
          )) : (
            <Grid item xs={12}>
              <Alert severity="info">
                <Typography variant="h6">No Care Plans Available</Typography>
                <Typography>
                  {isClinician 
                    ? 'No care plans match the selected filter criteria.' 
                    : 'No personalized care plans have been generated for you yet.'}
                </Typography>
              </Alert>
            </Grid>
          )}
        </Grid>
      )}

      {/* Detailed Care Plan Dialog */}
      <Dialog
        open={detailsOpen}
        onClose={handleCloseDetails}
        maxWidth="lg"
        fullWidth
        PaperProps={{
          sx: { minHeight: '80vh' }
        }}
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h5">
              {selectedPlan?.primary_diagnosis} - Detailed Care Plan
            </Typography>
            <Chip
              label={selectedPlan?.status.replace('_', ' ')}
              color={getStatusColor(selectedPlan?.status || '') as any}
            />
          </Box>
        </DialogTitle>
        
        <DialogContent dividers>
          {selectedPlan && (
            <Box>
              {/* Clinical Summary */}
              <Box sx={{ mb: 4 }}>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  Clinical Summary
                </Typography>
                <Typography variant="body1" paragraph>
                  {selectedPlan.clinical_summary}
                </Typography>
                {selectedPlan.patient_instructions && (
                  <Alert severity="info" sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" sx={{ mb: 1 }}>
                      Patient Instructions:
                    </Typography>
                    <Typography variant="body2">
                      {selectedPlan.patient_instructions}
                    </Typography>
                  </Alert>
                )}
              </Box>

              <Divider sx={{ my: 3 }} />

              {/* Detailed Actions */}
              <Box sx={{ mb: 4 }}>
                <Typography variant="h6" sx={{ mb: 3 }}>
                  Action Plan ({selectedPlan.actions ? selectedPlan.actions.length : 0} items)
                </Typography>
                
                <Stepper orientation="vertical">
                  {selectedPlan.actions && selectedPlan.actions.map((action, index) => (
                    <Step key={action.action_id} active={true}>
                      <StepLabel
                        icon={getActionIcon(action.action_type)}
                        optional={
                          <Chip
                            label={action.priority}
                            size="small"
                            color={getPriorityColor(action.priority) as any}
                          />
                        }
                      >
                        <Typography variant="subtitle1">
                          {action.description}
                        </Typography>
                      </StepLabel>
                      <StepContent>
                        <Box sx={{ pb: 3 }}>
                          <Typography variant="body2" color="text.secondary" paragraph>
                            <strong>Rationale:</strong> {action.rationale}
                          </Typography>
                          <Typography variant="body2" color="text.secondary" paragraph>
                            <strong>Timeline:</strong> {action.timeline}
                          </Typography>
                          <Typography variant="body2" color="text.secondary" paragraph>
                            <strong>Type:</strong> {action.action_type.charAt(0).toUpperCase() + action.action_type.slice(1)}
                          </Typography>
                          {action.evidence_source && (
                            <Typography variant="body2" color="text.secondary" paragraph>
                              <strong>Evidence Source:</strong> {action.evidence_source}
                            </Typography>
                          )}
                          {action.contraindications.length > 0 && (
                            <Alert severity="warning" sx={{ mt: 1 }}>
                              <Typography variant="body2">
                                <strong>Contraindications:</strong> {action.contraindications.join(', ')}
                              </Typography>
                            </Alert>
                          )}
                        </Box>
                      </StepContent>
                    </Step>
                  ))}
                </Stepper>
              </Box>

              <Divider sx={{ my: 3 }} />

              {/* Goals and Metrics */}
              <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    Short-term Goals
                  </Typography>
                  <List>
                    {selectedPlan.short_term_goals && selectedPlan.short_term_goals.map((goal, index) => (
                      <ListItem key={index} sx={{ pl: 0 }}>
                        <ListItemIcon>
                          <CheckCircle color="primary" />
                        </ListItemIcon>
                        <ListItemText primary={goal} />
                      </ListItem>
                    ))}
                  </List>
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    Long-term Goals
                  </Typography>
                  <List>
                    {selectedPlan.long_term_goals && selectedPlan.long_term_goals.map((goal, index) => (
                      <ListItem key={index} sx={{ pl: 0 }}>
                        <ListItemIcon>
                          <TimelineIcon color="success" />
                        </ListItemIcon>
                        <ListItemText primary={goal} />
                      </ListItem>
                    ))}
                  </List>
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    Success Metrics
                  </Typography>
                  <List>
                    {selectedPlan.success_metrics && selectedPlan.success_metrics.map((metric, index) => (
                      <ListItem key={index} sx={{ pl: 0 }}>
                        <ListItemIcon>
                          <MonitorHeart color="info" />
                        </ListItemIcon>
                        <ListItemText primary={metric} />
                      </ListItem>
                    ))}
                  </List>
                </Grid>
              </Grid>

              {/* Educational Resources */}
              {selectedPlan.educational_resources && selectedPlan.educational_resources.length > 0 && (
                <Box sx={{ mt: 4 }}>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    Educational Resources
                  </Typography>
                  <List>
                    {selectedPlan.educational_resources && selectedPlan.educational_resources.map((resource, index) => (
                      <ListItem key={index} sx={{ pl: 0 }}>
                        <ListItemIcon>
                          <Info color="primary" />
                        </ListItemIcon>
                        <ListItemText primary={resource} />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}

              {/* Plan Metadata */}
              <Box sx={{ mt: 4, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                  Plan Information
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6} sm={3}>
                    <Typography variant="caption" color="text.secondary">
                      Plan ID
                    </Typography>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                      {selectedPlan.careplan_id.slice(-8)}
                    </Typography>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Typography variant="caption" color="text.secondary">
                      Version
                    </Typography>
                    <Typography variant="body2">
                      {selectedPlan.version}
                    </Typography>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Typography variant="caption" color="text.secondary">
                      Generated By
                    </Typography>
                    <Typography variant="body2">
                      {selectedPlan.llm_model_used || 'AI Assistant'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Typography variant="caption" color="text.secondary">
                      Confidence
                    </Typography>
                    <Typography variant="body2">
                      {selectedPlan.confidence_score 
                        ? `${(selectedPlan.confidence_score * 100).toFixed(1)}%`
                        : 'N/A'}
                    </Typography>
                  </Grid>
                </Grid>
              </Box>
            </Box>
          )}
        </DialogContent>
        
        <DialogActions>
          <Button onClick={handleCloseDetails}>
            Close
          </Button>
          <Button variant="outlined" startIcon={<Download />}>
            Download PDF
          </Button>
          <Button variant="outlined" startIcon={<Print />}>
            Print
          </Button>
        </DialogActions>
      </Dialog>

      {/* Care Plan Review Dialog */}
      <CarePlanReviewDialog
        open={reviewDialogOpen}
        plan={reviewingPlan}
        onClose={handleCloseReview}
        onSubmit={handleSubmitReview}
        submitting={submittingReview}
      />
    </Layout>
  );
};

// Care Plan Review Dialog Component
interface CarePlanReviewDialogProps {
  open: boolean;
  plan: any;
  onClose: () => void;
  onSubmit: (action: 'approve' | 'deny' | 'edit', comments: string, modifications?: any) => void;
  submitting?: boolean;
}

const CarePlanReviewDialog: React.FC<CarePlanReviewDialogProps> = ({
  open,
  plan,
  onClose,
  onSubmit,
  submitting = false
}) => {
  const [comments, setComments] = useState('');
  const [editableActions, setEditableActions] = useState<any[]>([]);
  const [editableSummary, setEditableSummary] = useState('');
  const [editableGoals, setEditableGoals] = useState<string[]>([]);

  useEffect(() => {
    if (plan) {
      setEditableActions(Array.isArray(plan.actions) ? plan.actions : []);
      setEditableSummary(plan.clinical_summary || '');
      setEditableGoals(Array.isArray(plan.short_term_goals) ? plan.short_term_goals : []);
      setComments('');
    }
  }, [plan]);

  const handleApprove = () => {
    const modifications = {
      actions: editableActions,
      clinical_summary: editableSummary,
      short_term_goals: editableGoals
    };
    
    // Determine action based on plan status
    const action = plan.status === 'under_review' ? 'approve' : 'edit';
    onSubmit(action, comments, modifications);
  };

  const handleDeny = () => {
    onSubmit('deny', comments);
  };

  const handleActionEdit = (index: number, field: string, value: string) => {
    const updatedActions = [...editableActions];
    updatedActions[index] = { ...updatedActions[index], [field]: value };
    setEditableActions(updatedActions);
  };

  const handleGoalEdit = (index: number, value: string) => {
    const updatedGoals = [...editableGoals];
    updatedGoals[index] = value;
    setEditableGoals(updatedGoals);
  };

  if (!plan) return null;

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="lg" 
      fullWidth
      PaperProps={{
        sx: { height: '90vh' }
      }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h5">
            {plan.status === 'under_review' ? 'Review Care Plan' : 'Edit Care Plan'} - {plan.patient_name}
          </Typography>
          <Chip 
            label={plan.status?.replace('_', ' ') || 'Under Review'} 
            color={plan.status === 'under_review' ? 'warning' : 'primary'} 
            variant="outlined" 
          />
        </Box>
      </DialogTitle>
      
      <DialogContent dividers>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Primary Diagnosis: {plan.primary_diagnosis}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Created: {new Date(plan.created_date).toLocaleDateString()}
          </Typography>
        </Box>

        <Divider sx={{ my: 3 }} />

        {/* Editable Clinical Summary */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Clinical Summary
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={3}
            value={editableSummary}
            onChange={(e) => setEditableSummary(e.target.value)}
            variant="outlined"
          />
        </Box>

        {/* Editable Actions */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Treatment Actions
          </Typography>
          {editableActions && editableActions.map((action, index) => (
            <Card key={index} sx={{ mb: 2 }}>
              <CardContent>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={8}>
                    <TextField
                      fullWidth
                      label="Action Description"
                      value={action.description || ''}
                      onChange={(e) => handleActionEdit(index, 'description', e.target.value)}
                      variant="outlined"
                      size="small"
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      label="Timeline"
                      value={action.timeline || ''}
                      onChange={(e) => handleActionEdit(index, 'timeline', e.target.value)}
                      variant="outlined"
                      size="small"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Rationale"
                      value={action.rationale || ''}
                      onChange={(e) => handleActionEdit(index, 'rationale', e.target.value)}
                      variant="outlined"
                      size="small"
                      multiline
                      rows={2}
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          ))}
        </Box>

        {/* Editable Goals */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Short-term Goals
          </Typography>
          {editableGoals && editableGoals.map((goal, index) => (
            <TextField
              key={index}
              fullWidth
              value={goal}
              onChange={(e) => handleGoalEdit(index, e.target.value)}
              variant="outlined"
              size="small"
              sx={{ mb: 1 }}
            />
          ))}
        </Box>

        {/* Review Comments */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Review Comments
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={4}
            value={comments}
            onChange={(e) => setComments(e.target.value)}
            placeholder="Enter your review comments here..."
            variant="outlined"
          />
        </Box>
      </DialogContent>
      
      <DialogActions sx={{ px: 3, py: 2 }}>
        <Button onClick={onClose} variant="outlined" disabled={submitting}>
          Cancel
        </Button>
        {plan.status === 'under_review' ? (
          <>
            <Button 
              onClick={handleDeny} 
              variant="contained" 
              color="error"
              startIcon={<Warning />}
              disabled={submitting}
            >
              {submitting ? 'Processing...' : 'Deny'}
            </Button>
            <Button 
              onClick={handleApprove} 
              variant="contained" 
              color="success"
              startIcon={<CheckCircle />}
              disabled={submitting}
            >
              {submitting ? 'Processing...' : 'Approve'}
            </Button>
          </>
        ) : (
          <Button 
            onClick={handleApprove} 
            variant="contained" 
            color="primary"
            startIcon={<CheckCircle />}
            disabled={submitting}
          >
            {submitting ? 'Saving...' : 'Save Changes'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default CarePlans;