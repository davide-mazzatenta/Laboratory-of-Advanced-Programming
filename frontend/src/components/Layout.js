//components/Layout.js
import { useTheme } from '@mui/material/styles';
import React from 'react';
import { Box, Container, alpha } from '@mui/material';
import { styled } from '@mui/system';

// Background container with gradient and patterns
export const PageBackground = ({ children, transitioning = false }) => {
  const theme = useTheme();
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
        background:
          theme.palette.mode === 'dark'
            ? `radial-gradient(circle at 0% 20%, ${alpha('#2D2B55', 0.7)} 0%, transparent 30%),
         radial-gradient(circle at 100% 80%, ${alpha('#28284D', 0.7)} 0%, transparent 30%),
         ${theme.palette.background.default}`
            : `radial-gradient(circle at 0% 20%, ${alpha('#F0E7FF', 0.5)} 0%, transparent 30%),
         radial-gradient(circle at 100% 80%, ${alpha('#EDF5FF', 0.5)} 0%, transparent 30%),
         ${theme.palette.background.default}`,
        backgroundAttachment: 'fixed',
        position: 'relative',
        transition: 'background 0.5s ease-in-out',
      }}
    >
      {/* Background particle pattern */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          pointerEvents: 'none',
          zIndex: 0,
          opacity: 0.4,
          backgroundImage:
            theme.palette.mode === 'dark'
              ? "url(\"data:image/svg+xml,%3Csvg width='20' height='20' viewBox='0 0 20 20' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%239C92AC' fill-opacity='0.03' fill-rule='evenodd'%3E%3Ccircle cx='3' cy='3' r='3'/%3E%3Ccircle cx='13' cy='13' r='3'/%3E%3C/g%3E%3C/svg%3E\")"
              : "url(\"data:image/svg+xml,%3Csvg width='20' height='20' viewBox='0 0 20 20' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23B39DDB' fill-opacity='0.05' fill-rule='evenodd'%3E%3Ccircle cx='3' cy='3' r='3'/%3E%3Ccircle cx='13' cy='13' r='3'/%3E%3C/g%3E%3C/svg%3E\")",
          animation: 'backgroundAnimation 120s linear infinite',
          '@keyframes backgroundAnimation': {
            '0%': { backgroundPosition: '0% 0%' },
            '100%': { backgroundPosition: '100% 100%' },
          },
          ...(transitioning && {
            animation: 'fadeBackground 0.8s forwards',
            '@keyframes fadeBackground': {
              to: { opacity: 0 },
            },
          }),
        }}
      />

      {children}
    </Box>
  );
};

// Page header with logo and action buttons
export const PageHeader = ({ children }) => (
  <Box
    sx={{
      p: 1,
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      position: 'relative',
      zIndex: 10,
    }}
  >
    {children}
  </Box>
);

// Main content container
export const PageContent = ({ children, transitioning = false }) => (
  <Container
    maxWidth="lg"
    sx={{
      position: 'relative',
      zIndex: 2,
      flexGrow: 1,
      py: 0, // Removed padding
      ...(transitioning && {
        animation: 'contentExit 0.8s forwards cubic-bezier(0.19, 1, 0.22, 1)',
        '@keyframes contentExit': {
          '0%': {
            opacity: 1,
            transform: 'scale(1)',
          },
          '100%': {
            opacity: 0,
            transform: 'scale(0.95)',
          },
        },
      }),
    }}
  >
    {children}
  </Container>
);

// Dashboard specific background with glow effects
export const DashboardBackground = styled('div')(({ theme }) => ({
  minHeight: '100vh',
  width: '100%',
  display: 'flex',
  flexDirection: 'column',
  position: 'relative',
  overflow: 'hidden',
  backgroundColor: theme.palette.background.default,
}));
