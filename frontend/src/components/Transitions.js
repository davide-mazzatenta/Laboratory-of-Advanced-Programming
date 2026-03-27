//components/Transitions.js

import React from 'react';
import { Box, styled } from '@mui/material';

// Componente per l'effetto di transizione pagina
export const PageTransition = styled(Box)(({ theme, active }) => ({
  position: 'fixed',
  top: 0,
  left: 0,
  width: '100%',
  height: '100%',
  pointerEvents: active ? 'all' : 'none',
  zIndex: 9999,
  opacity: active ? 1 : 0,
  transition: 'opacity 0.3s ease',
}));

// Effetto circolare che si espande
export const CircleExpand = styled(Box)(
  ({ theme, active, originX, originY }) => ({
    position: 'absolute',
    top: originY || '50%',
    left: originX || '50%',
    width: active ? '300vw' : '0',
    height: active ? '300vh' : '0',
    borderRadius: '50%',
    background: 'linear-gradient(135deg, #7C4DFF, #956AFF)',
    transform: 'translate(-50%, -50%)',
    transition: active
      ? 'all 1.5s cubic-bezier(0.19, 1, 0.22, 1)'
      : 'all 0.6s cubic-bezier(0.55, 0.085, 0.68, 0.53)',
    boxShadow: active ? '0 0 100px 50px rgba(124, 77, 255, 0.3)' : 'none',
  }),
);
