//components/Cards.js

import { Card, alpha, styled } from '@mui/material';

// Styled Card for documents
export const DocumentCard = styled(Card)(({ theme }) => ({
  backgroundColor:
    theme.palette.mode === 'dark'
      ? alpha('#1C1C3C', 0.8)
      : alpha('#FFFFFF', 0.95),
  backdropFilter: 'blur(10px)',
  border: `2px solid ${theme.palette.mode === 'dark' ? alpha('#9A7CFF', 0.3) : alpha('#7C4DFF', 0.2)}`,
  borderRadius: '16px',
  transition: 'all 0.3s ease',
  marginBottom: '16px',
  '&:hover': {
    boxShadow:
      theme.palette.mode === 'dark'
        ? '0 8px 32px rgba(154, 124, 255, 0.2)'
        : '0 8px 32px rgba(124, 77, 255, 0.15)',
    transform: 'translateY(-2px)',
    borderColor:
      theme.palette.mode === 'dark'
        ? alpha('#9A7CFF', 0.5)
        : alpha('#7C4DFF', 0.4),
  },
}));

// Styled Card for projects
export const ProjectCard = styled(Card)(({ theme }) => ({
  backgroundColor:
    theme.palette.mode === 'dark'
      ? alpha('#1C1C3C', 0.8)
      : alpha('#FFFFFF', 0.95),
  backdropFilter: 'blur(10px)',
  border: `2px solid ${theme.palette.mode === 'dark' ? alpha('#9A7CFF', 0.3) : alpha('#7C4DFF', 0.2)}`,
  borderRadius: '16px',
  transition: 'all 0.3s ease',
  marginBottom: '16px',
  '&:hover': {
    boxShadow:
      theme.palette.mode === 'dark'
        ? '0 8px 32px rgba(154, 124, 255, 0.2)'
        : '0 8px 32px rgba(124, 77, 255, 0.15)',
    transform: 'translateY(-2px)',
    borderColor:
      theme.palette.mode === 'dark'
        ? alpha('#9A7CFF', 0.5)
        : alpha('#7C4DFF', 0.4),
  },
}));
