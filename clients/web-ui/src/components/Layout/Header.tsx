import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  IconButton,
  Menu,
  MenuItem,
  Avatar,
  Chip
} from '@mui/material';
import {
  AccountCircle,
  Notifications,
  Logout,
  Settings,
  HealthAndSafety
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

interface HeaderProps {
  title?: string;
}

const Header: React.FC<HeaderProps> = ({ 
  title = "CarePlan AI"
}) => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const [notificationCount] = React.useState(3); // Mock notification count

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    handleClose();
    await logout();
    navigate('/login');
  };

  const handleProfile = () => {
    handleClose();
    navigate('/profile');
  };

  const handleSettings = () => {
    handleClose();
    navigate('/settings');
  };

  return (
    <AppBar position="static" sx={{ bgcolor: 'primary.main' }}>
      <Toolbar>
        {/* Logo and Title */}
        <HealthAndSafety sx={{ mr: 2 }} />
        <Typography 
          variant="h6" 
          component="div" 
          sx={{ flexGrow: 1, fontWeight: 'bold' }}
        >
          {title}
        </Typography>

        {/* User Name Display */}
        {user && (
          <Chip
            label={`${user.first_name} ${user.last_name}`}
            color="secondary"
            variant="outlined"
            sx={{ 
              mr: 2,
              color: 'white',
              borderColor: 'white',
              '& .MuiChip-label': {
                color: 'white'
              }
            }}
          />
        )}

        {/* Navigation Buttons */}
        <Box sx={{ display: { xs: 'none', md: 'flex' }, mr: 2 }}>
          <Button 
            color="inherit" 
            onClick={() => navigate('/dashboard')}
            sx={{ mx: 1 }}
          >
            Dashboard
          </Button>
          {(user?.role === 'patient' || user?.role === 'clinician') && (
            <Button 
              color="inherit" 
              onClick={() => navigate('/care-plans')}
              sx={{ mx: 1 }}
            >
              {user?.role === 'clinician' ? 'Care Plans' : 'My Care Plans'}
            </Button>
          )}
          {user?.role === 'clinician' && (
            <Button 
              color="inherit" 
              onClick={() => navigate('/patients')}
              sx={{ mx: 1 }}
            >
              Patient Directory
            </Button>
          )}
          {user?.role === 'patient' && (
            <Button 
              color="inherit" 
              onClick={() => navigate('/history')}
              sx={{ mx: 1 }}
            >
              Medical History
            </Button>
          )}
          {user?.role === 'admin' && (
            <Button 
              color="inherit" 
              onClick={() => navigate('/batch')}
              sx={{ mx: 1 }}
            >
              Batch Operations
            </Button>
          )}
        </Box>

        {/* Notifications */}
        <IconButton
          size="large"
          color="inherit"
          onClick={() => navigate('/notifications')}
          sx={{ mr: 1 }}
        >
          <Notifications />
          {notificationCount > 0 && (
            <Chip
              label={notificationCount}
              size="small"
              color="error"
              sx={{
                position: 'absolute',
                top: 8,
                right: 8,
                minWidth: 20,
                height: 20,
                fontSize: '0.75rem'
              }}
            />
          )}
        </IconButton>

        {/* User Menu */}
        <div>
          <IconButton
            size="large"
            aria-label="account of current user"
            aria-controls="menu-appbar"
            aria-haspopup="true"
            onClick={handleMenu}
            color="inherit"
          >
            <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>
              <AccountCircle />
            </Avatar>
          </IconButton>
          <Menu
            id="menu-appbar"
            anchorEl={anchorEl}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
            keepMounted
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            open={Boolean(anchorEl)}
            onClose={handleClose}
          >
            <MenuItem onClick={handleProfile}>
              <AccountCircle sx={{ mr: 1 }} />
              Profile
            </MenuItem>
            <MenuItem onClick={handleSettings}>
              <Settings sx={{ mr: 1 }} />
              Settings
            </MenuItem>
            <MenuItem onClick={handleLogout}>
              <Logout sx={{ mr: 1 }} />
              Logout
            </MenuItem>
          </Menu>
        </div>
      </Toolbar>
    </AppBar>
  );
};

export default Header;