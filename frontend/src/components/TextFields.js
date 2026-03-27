//components/TextFields.js

import { TextField, alpha, styled } from '@mui/material';

// Styled TextField
export const StyledTextField = styled(TextField)(({ theme }) => ({
  '& .MuiOutlinedInput-root': {
    borderRadius: '12px',
    backgroundColor:
      theme.palette.mode === 'dark'
        ? alpha('#FFFFFF', 0.05)
        : alpha('#000000', 0.02),
    '& fieldset': {
      borderColor:
        theme.palette.mode === 'dark'
          ? alpha('#9A7CFF', 0.3)
          : alpha('#7C4DFF', 0.3),
      borderWidth: '2px',
    },
    '&:hover fieldset': {
      borderColor:
        theme.palette.mode === 'dark'
          ? alpha('#9A7CFF', 0.5)
          : alpha('#7C4DFF', 0.5),
    },
    '&.Mui-focused fieldset': {
      borderColor: theme.palette.primary.main,
      borderWidth: '2px',
    },
  },
  '& .MuiInputBase-input': {
    color: theme.palette.mode === 'dark' ? '#FFFFFF' : '#14142B',
    '&::placeholder': {
      color:
        theme.palette.mode === 'dark'
          ? alpha('#FFFFFF', 0.5)
          : alpha('#14142B', 0.5),
    },
  },
}));

// Hidden file input
export const VisuallyHiddenInput = styled('input')({
  clip: 'rect(0 0 0 0)',
  clipPath: 'inset(50%)',
  height: 1,
  overflow: 'hidden',
  position: 'absolute',
  bottom: 0,
  left: 0,
  whiteSpace: 'nowrap',
  width: 1,
});
