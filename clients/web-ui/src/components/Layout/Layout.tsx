import React, { useState } from 'react';
import { Box, Container, useTheme, useMediaQuery } from '@mui/material';
import Header from './Header';
import Sidebar from './Sidebar';

interface LayoutProps {
  children: React.ReactNode;
  title?: string;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | false;
}

const Layout: React.FC<LayoutProps> = ({ 
  children, 
  title, 
  maxWidth = 'lg'
}) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const handleSidebarClose = () => {
    setSidebarOpen(false);
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* Header */}
      <Header 
        title={title}
      />

      {/* Sidebar */}
      <Sidebar 
        open={sidebarOpen}
        onClose={handleSidebarClose}
      />

      {/* Main Content Area */}
      <Box 
        component="main" 
        sx={{ 
          flexGrow: 1,
          bgcolor: 'grey.50',
          minHeight: 'calc(100vh - 64px)', // Subtract header height
          py: 3
        }}
      >
        <Container maxWidth={maxWidth}>
          {children}
        </Container>
      </Box>

      {/* Floating Action Button for Mobile Sidebar */}
      {isMobile && (
        <Box
          sx={{
            position: 'fixed',
            top: 80,
            left: 16,
            zIndex: theme.zIndex.speedDial,
          }}
        >
          {/* Mobile menu button can be added here if needed */}
        </Box>
      )}
    </Box>
  );
};

export default Layout;