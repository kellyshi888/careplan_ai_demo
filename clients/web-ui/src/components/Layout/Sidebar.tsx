import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Box,
  Typography,
  Chip
} from '@mui/material';
import {
  Dashboard,
  Assignment,
  History,
  Person,
  LocalHospital,
  Analytics,
  Notifications,
  Settings,
  Help,
  CloudSync
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const drawerWidth = 240;

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

interface NavItem {
  text: string;
  icon: React.ReactElement;
  path: string;
  badge?: number;
  divider?: boolean;
  roles?: string[]; // Optional roles that can access this item
}

const Sidebar: React.FC<SidebarProps> = ({ open, onClose }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();

  const navItems: NavItem[] = [
    {
      text: 'Dashboard',
      icon: <Dashboard />,
      path: '/dashboard'
    },
    {
      text: user?.role === 'clinician' ? 'Care Plans' : 'My Care Plans',
      icon: <Assignment />,
      path: '/care-plans',
      badge: user?.role === 'clinician' ? undefined : 2,
      roles: ['patient', 'clinician'] // Only show for patients and clinicians, not admin
    },
    {
      text: 'Patient Directory',
      icon: <LocalHospital />,
      path: '/patients',
      roles: ['clinician'] // Only show for clinicians
    },
    {
      text: 'Batch Operations',
      icon: <CloudSync />,
      path: '/batch',
      roles: ['admin'] // Only show for admins
    },
    {
      text: 'Medical History',
      icon: <History />,
      path: '/history',
      roles: ['patient'] // Only show for patients
    },
    {
      text: 'Health Records',
      icon: <LocalHospital />,
      path: '/records',
      roles: ['patient'] // Only show for patients
    },
    {
      text: 'Profile',
      icon: <Person />,
      path: '/profile',
      divider: true
    },
    {
      text: 'Health Analytics',
      icon: <Analytics />,
      path: '/analytics',
      roles: ['patient'] // Only show for patients
    },
    {
      text: 'Notifications',
      icon: <Notifications />,
      path: '/notifications',
      badge: 3
    },
    {
      text: 'Settings',
      icon: <Settings />,
      path: '/settings',
      divider: true
    },
    {
      text: 'Help & Support',
      icon: <Help />,
      path: '/help'
    }
  ];

  // Filter navigation items based on user role
  const filteredNavItems = navItems.filter(item => {
    if (!item.roles) return true; // Show items without role restrictions
    return item.roles.includes(user?.role || '');
  });

  const handleItemClick = (path: string) => {
    navigate(path);
    onClose();
  };

  const isSelected = (path: string) => {
    return location.pathname === path;
  };

  const drawerContent = (
    <Box sx={{ width: drawerWidth }} role="presentation">
      {/* Logo Section */}
      <Box 
        sx={{ 
          p: 2, 
          bgcolor: 'primary.main', 
          color: 'white',
          textAlign: 'center'
        }}
      >
        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
          CarePlan AI
        </Typography>
        <Typography variant="caption" sx={{ opacity: 0.8 }}>
          {user?.role === 'clinician' ? 'Clinician Portal' : 
           user?.role === 'admin' ? 'Admin Portal' : 'Patient Portal'}
        </Typography>
      </Box>

      {/* Navigation Items */}
      <List sx={{ pt: 1 }}>
        {filteredNavItems.map((item, index) => (
          <React.Fragment key={item.text}>
            <ListItem disablePadding>
              <ListItemButton
                selected={isSelected(item.path)}
                onClick={() => handleItemClick(item.path)}
                sx={{
                  mx: 1,
                  borderRadius: 1,
                  '&.Mui-selected': {
                    bgcolor: 'primary.light',
                    color: 'primary.contrastText',
                    '&:hover': {
                      bgcolor: 'primary.main',
                    },
                  },
                }}
              >
                <ListItemIcon 
                  sx={{ 
                    color: isSelected(item.path) ? 'inherit' : 'text.secondary',
                    minWidth: 40
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText 
                  primary={item.text} 
                  primaryTypographyProps={{
                    fontSize: '0.875rem',
                    fontWeight: isSelected(item.path) ? 'medium' : 'regular'
                  }}
                />
                {item.badge && (
                  <Chip
                    label={item.badge}
                    size="small"
                    color="error"
                    sx={{ 
                      minWidth: 20, 
                      height: 20, 
                      fontSize: '0.75rem',
                      ml: 1
                    }}
                  />
                )}
              </ListItemButton>
            </ListItem>
            {item.divider && <Divider sx={{ my: 1 }} />}
          </React.Fragment>
        ))}
      </List>

      {/* Footer */}
      <Box 
        sx={{ 
          position: 'absolute',
          bottom: 0,
          width: '100%',
          p: 2,
          bgcolor: 'grey.50',
          textAlign: 'center'
        }}
      >
        <Typography variant="caption" color="text.secondary">
          Version 1.0.0
        </Typography>
        <br />
        <Typography variant="caption" color="text.secondary">
          © 2024 CarePlan AI
        </Typography>
      </Box>
    </Box>
  );

  return (
    <Drawer
      anchor="left"
      open={open}
      onClose={onClose}
      variant="temporary"
      sx={{
        display: { xs: 'block', md: 'none' },
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
        },
      }}
    >
      {drawerContent}
    </Drawer>
  );
};

export default Sidebar;