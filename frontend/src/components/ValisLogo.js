//components/ValisLogo.js

import React from 'react';
import { Box, Typography } from '@mui/material';
import { useTheme } from '@mui/material/styles';

const ValisLogo = () => {
  const theme = useTheme();
  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        position: 'relative',
        cursor: 'pointer',
        '&:hover .valis-dot': {
          transform: 'scale(1.5)',
          boxShadow: `0 0 12px ${theme.palette.primary.main}`,
        },
        '&:hover .valis-line': {
          width: '100%',
          boxShadow: `0 0 8px ${theme.palette.primary.main}`,
        },
      }}
    >
      {/* Punto viola in alto a destra del logo */}
      <Box
        className="valis-dot"
        sx={{
          position: 'absolute',
          width: 6,
          height: 6,
          borderRadius: '50%',
          bgcolor: '#9A7CFF',
          right: -6,
          top: 0,
          transition: 'all 0.4s cubic-bezier(0.17, 0.67, 0.83, 0.67)',
        }}
      />

      {/* Punto viola in basso a sinistra del logo */}
      <Box
        className="valis-dot"
        sx={{
          position: 'absolute',
          width: 6,
          height: 6,
          borderRadius: '50%',
          bgcolor: '#9A7CFF',
          left: -6,
          bottom: 8,
          transition: 'all 0.4s cubic-bezier(0.17, 0.67, 0.83, 0.67)',
        }}
      />

      {/* Logo text */}
      <Typography
        variant="h3"
        fontFamily="'Times New Roman', Times, serif"
        fontWeight={600}
        letterSpacing="0.02em"
        sx={{
          color: theme.palette.mode === 'dark' ? '#FFFFFF' : '#14142B',
          fontSize: '2rem', // Reduced from 2.5rem
          position: 'relative',
        }}
      >
        VALIS
      </Typography>

      {/* Linea decorativa sotto il logo */}
      <Box
        className="valis-line"
        sx={{
          position: 'absolute',
          height: 2.5,
          width: '20%',
          bgcolor: '#9A7CFF',
          left: 0,
          bottom: -4,
          borderRadius: 3,
          transition: 'all 0.4s cubic-bezier(0.17, 0.67, 0.83, 0.67)',
        }}
      />
    </Box>
  );
};

export default ValisLogo;
