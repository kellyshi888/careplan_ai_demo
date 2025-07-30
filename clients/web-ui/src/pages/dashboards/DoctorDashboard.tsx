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
  IconButton,
  Button
} from '@mui/material';
import {
  Person,
  Assignment,
  Schedule,
  PendingActions,
  CheckCircle,
  Refresh,
  Visibility,
  Group,
  Today,
  Event
} from '@mui/icons-material';
import ApiService from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

interface DoctorStats {
  totalPatients: number;
  todayAppointments: number;
  tomorrowAppointments: number;
  activeCarePlans: number;
  pendingApprovals: number;
  draftPlans: number;
}

const DoctorDashboard: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<DoctorStats>({
    totalPatients: 0,
    todayAppointments: 0,
    tomorrowAppointments: 0,
    activeCarePlans: 0,
    pendingApprovals: 0,
    draftPlans: 0
  });
  const [recentActivities, setRecentActivities] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  const generateRecentActivities = (carePlans: any[]) => {
    const activities: any[] = [];
    
    // Sort care plans by last modified date to get most recent
    const sortedPlans = carePlans
      .filter(plan => plan.last_modified)
      .sort((a, b) => new Date(b.last_modified).getTime() - new Date(a.last_modified).getTime())
      .slice(0, 5); // Get top 5 most recent
    
    sortedPlans.forEach((plan, index) => {
      const lastModified = new Date(plan.last_modified);
      const now = new Date();
      const diffHours = Math.floor((now.getTime() - lastModified.getTime()) / (1000 * 60 * 60));
      
      let timeAgo = '';
      if (diffHours < 1) {
        timeAgo = 'Just now';
      } else if (diffHours < 24) {
        timeAgo = `${diffHours} hours ago`;
      } else {
        const diffDays = Math.floor(diffHours / 24);
        timeAgo = `${diffDays} days ago`;
      }
      
      let activityType = '';
      let description = '';
      
      switch (plan.status) {
        case 'approved':
          activityType = 'care_plan_approved';
          description = `Care plan approved for ${plan.patient_name}`;
          break;
        case 'completed':
          activityType = 'care_plan_completed';
          description = `Care plan completed for ${plan.patient_name}`;
          break;
        case 'under_review':
          activityType = 'care_plan_review';
          description = `Care plan updated for ${plan.patient_name}`;
          break;
        default:
          activityType = 'care_plan_updated';
          description = `Care plan modified for ${plan.patient_name}`;
      }
      
      activities.push({
        id: `activity_${plan.careplan_id}_${index}`,
        type: activityType,
        time: timeAgo,
        description: description
      });
    });
    
    return activities;
  };

  const loadDoctorDashboard = useCallback(async () => {
    setLoading(true);
    try {
      // Load dashboard stats and care plans
      const [dashboardStats, carePlans] = await Promise.all([
        ApiService.getDashboardStats(),
        ApiService.getClinicianCarePlans()
      ]);

      // Calculate stats specific to doctor dashboard
      const pendingApprovals = carePlans.filter(plan => plan.status === 'under_review').length;
      const activeCarePlans = carePlans.filter(plan => 
        plan.status === 'approved' || plan.status === 'active'
      ).length;

      // Generate recent activities from care plans
      const recentActivities = generateRecentActivities(carePlans);
      
      setStats({
        totalPatients: dashboardStats.totalPatients || 0,
        todayAppointments: 8, // Mock data
        tomorrowAppointments: 12, // Mock data
        activeCarePlans,
        pendingApprovals,
        draftPlans: 0
      });
      setRecentActivities(recentActivities);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Error loading doctor dashboard data:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDoctorDashboard();
  }, [loadDoctorDashboard]);



  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'care_plan_approved':
        return <CheckCircle color="success" />;
      case 'care_plan_completed':
        return <CheckCircle color="info" />;
      case 'care_plan_review':
        return <PendingActions color="warning" />;
      case 'care_plan_updated':
        return <Assignment color="primary" />;
      case 'appointment_completed':
        return <Schedule color="primary" />;
      default:
        return <Assignment />;
    }
  };

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 4 }}>
        <LinearProgress />
        <Typography sx={{ mt: 2, textAlign: 'center' }}>
          Loading doctor dashboard...
        </Typography>
      </Box>
    );
  }

  return (
    <>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
            Doctor Dashboard
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Welcome Dr. {user?.last_name || user?.first_name || 'Doctor'}
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="caption" color="text.secondary">
            Last updated: {lastUpdated.toLocaleTimeString()}
          </Typography>
          <IconButton onClick={loadDoctorDashboard} size="small">
            <Refresh />
          </IconButton>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Doctor Profile Card */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                  <Person />
                </Avatar>
                <Box>
                  <Typography variant="h6">
                    Dr. {user?.first_name} {user?.last_name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Clinician
                  </Typography>
                </Box>
              </Box>
              
              <Divider sx={{ my: 2 }} />
              
              <Box sx={{ mb: 1 }}>
                <Typography variant="body2" color="text.secondary">Department</Typography>
                <Typography variant="body1">Primary Care</Typography>
              </Box>
              
              <Box sx={{ mb: 1 }}>
                <Typography variant="body2" color="text.secondary">Specialization</Typography>
                <Typography variant="body1">Family Medicine</Typography>
              </Box>
              
              <Box sx={{ mb: 1 }}>
                <Typography variant="body2" color="text.secondary">License</Typography>
                <Chip label="Active" size="small" color="success" variant="outlined" />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Key Statistics */}
        <Grid item xs={12} md={8}>
          <Grid container spacing={2}>
            <Grid item xs={6} md={4}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Group color="primary" sx={{ fontSize: 40, mb: 1 }} />
                  <Typography variant="h6">{stats.totalPatients}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Patients
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} md={4}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Today color="warning" sx={{ fontSize: 40, mb: 1 }} />
                  <Typography variant="h6">{stats.todayAppointments}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Today's Appointments
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} md={4}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Event color="info" sx={{ fontSize: 40, mb: 1 }} />
                  <Typography variant="h6">{stats.tomorrowAppointments}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Tomorrow's Appointments
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} md={4}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Assignment color="success" sx={{ fontSize: 40, mb: 1 }} />
                  <Typography variant="h6">{stats.activeCarePlans}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Active Care Plans
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} md={4}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <PendingActions color="error" sx={{ fontSize: 40, mb: 1 }} />
                  <Typography variant="h6">{stats.pendingApprovals}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Pending Approvals
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} md={4}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Assignment color="warning" sx={{ fontSize: 40, mb: 1 }} />
                  <Typography variant="h6">{stats.draftPlans}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Draft Plans
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Grid>

        {/* Care Plans Summary */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Care Plans Overview
                </Typography>
                <Button 
                  variant="outlined" 
                  startIcon={<Visibility />}
                  onClick={() => window.location.href = '/care-plans'}
                  size="small"
                >
                  View All
                </Button>
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Pending Approvals</Typography>
                  <Chip label={stats.pendingApprovals} size="small" color="error" />
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Completed Plans</Typography>
                  <Chip label={stats.activeCarePlans} size="small" color="info" />
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Active Plans</Typography>
                  <Chip label={stats.activeCarePlans} size="small" color="success" />
                </Box>
              </Box>

              {stats.pendingApprovals > 0 && (
                <Button 
                  variant="contained" 
                  color="error"
                  startIcon={<PendingActions />}
                  onClick={() => window.location.href = '/care-plans?status=under_review'}
                  fullWidth
                >
                  Review {stats.pendingApprovals} Pending Plans
                </Button>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activities */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Recent Activities
              </Typography>
              <List>
                {recentActivities.map((activity, index) => (
                  <React.Fragment key={activity.id}>
                    <ListItem>
                      <ListItemIcon>
                        {getActivityIcon(activity.type)}
                      </ListItemIcon>
                      <ListItemText
                        primary={activity.patient}
                        secondary={
                          <Box>
                            <Typography variant="body2">{activity.description}</Typography>
                            <Typography variant="caption" color="text.secondary">
                              {activity.time}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                    {index < recentActivities.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Quick Actions
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Button 
                    variant="outlined" 
                    fullWidth
                    startIcon={<Assignment />}
                    onClick={() => window.location.href = '/care-plans'}
                  >
                    Manage Care Plans
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Button 
                    variant="outlined" 
                    fullWidth
                    startIcon={<Schedule />}
                  >
                    View Schedule
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Button 
                    variant="outlined" 
                    fullWidth
                    startIcon={<Group />}
                  >
                    Patient Directory
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Button 
                    variant="outlined" 
                    fullWidth
                    startIcon={<PendingActions />}
                    onClick={() => window.location.href = '/care-plans?status=under_review'}
                  >
                    Review Queue
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </>
  );
};

export default DoctorDashboard;