//components/Modals.js
import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  alpha,
  useTheme,
} from '@mui/material';

export const StyledModal = ({
  open,
  onClose,
  title,
  children,
  maxWidth = 'sm',
  fullWidth = true,
}) => {
  const theme = useTheme();

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth={maxWidth}
      fullWidth={fullWidth}
      PaperProps={{
        sx: {
          backgroundColor:
            theme.palette.mode === 'dark' ? '#1C1C3C' : '#FFFFFF',
          borderRadius: '16px',
          border: `1px solid ${
            theme.palette.mode === 'dark'
              ? alpha('#9A7CFF', 0.3)
              : alpha('#7C4DFF', 0.2)
          }`,
        },
      }}
    >
      <DialogTitle
        sx={{
          color: theme.palette.mode === 'dark' ? '#FFFFFF' : '#14142B',
          borderBottom: `1px solid ${
            theme.palette.mode === 'dark'
              ? alpha('#FFFFFF', 0.1)
              : alpha('#000000', 0.1)
          }`,
          fontSize: '1.1rem',
          fontWeight: 600,
        }}
      >
        {title}
      </DialogTitle>

      <DialogContent sx={{ pt: 3 }}>{children}</DialogContent>
    </Dialog>
  );
};
