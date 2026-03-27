//components/Buttons.js

import React, { useState, useEffect, useRef } from 'react';
import {
  Button,
  IconButton,
  Box,
  Typography,
  alpha,
  styled,
} from '@mui/material';

// Header Action Button
export const HeaderActionButton = styled(IconButton)(({ theme }) => ({
  width: 40, // Reduced from 46
  height: 40, // Reduced from 46
  backgroundColor:
    theme.palette.mode === 'dark'
      ? alpha('#1C1C3C', 0.6)
      : alpha('#FFFFFF', 0.8),
  backdropFilter: 'blur(8px)',
  border: `1px solid ${theme.palette.mode === 'dark' ? alpha('#FFFFFF', 0.1) : alpha('#7C4DFF', 0.1)}`,
  borderRadius: 12,
  transition: 'all 0.2s cubic-bezier(0.17, 0.67, 0.83, 0.67)',
  '&:hover': {
    backgroundColor:
      theme.palette.mode === 'dark'
        ? alpha('#1C1C3C', 0.9)
        : alpha('#FFFFFF', 1),
    transform: 'translateY(-2px)',
    boxShadow:
      theme.palette.mode === 'dark'
        ? '0 6px 12px rgba(0, 0, 0, 0.2), 0 0 0 1px rgba(154, 124, 255, 0.2)'
        : '0 6px 12px rgba(124, 77, 255, 0.12), 0 0 0 1px rgba(124, 77, 255, 0.1)',
  },
  '&:active': {
    transform: 'translateY(-1px) scale(0.97)',
  },
  '& .MuiSvgIcon-root': {
    fontSize: 20, // Reduced from 22
    color:
      theme.palette.mode === 'dark'
        ? theme.palette.primary.light
        : theme.palette.primary.main,
    transition: 'transform 0.2s ease',
  },
  '&:hover .MuiSvgIcon-root': {
    transform: 'scale(1.1)',
  },
}));

// Action Button
export const ActionButton = styled(Button)(({ theme }) => ({
  minWidth: 'auto',
  padding: '6px 12px', // Reduced from 8px 16px
  fontSize: '0.75rem', // Reduced from 0.875rem
  fontWeight: 600,
  border: `1px solid ${theme.palette.mode === 'dark' ? alpha('#9A7CFF', 0.5) : alpha('#7C4DFF', 0.5)}`,
  borderRadius: '8px',
  color: theme.palette.mode === 'dark' ? '#9A7CFF' : '#7C4DFF',
  backgroundColor: 'transparent',
  transition: 'all 0.2s ease',
  '&:hover': {
    backgroundColor:
      theme.palette.mode === 'dark'
        ? alpha('#9A7CFF', 0.1)
        : alpha('#7C4DFF', 0.1),
    borderColor: theme.palette.mode === 'dark' ? '#9A7CFF' : '#7C4DFF',
    transform: 'translateY(-1px)',
  },
}));

// Delete Button
export const DeleteButton = styled(IconButton)(({ theme }) => ({
  minWidth: 'auto',
  padding: '6px',
  border: `1px solid ${theme.palette.mode === 'dark' ? alpha('#FF6B6B', 0.5) : alpha('#F44336', 0.5)}`,
  borderRadius: '8px',
  color: theme.palette.mode === 'dark' ? '#FF6B6B' : '#F44336',
  backgroundColor: 'transparent',
  transition: 'all 0.2s ease',
  '&:hover': {
    backgroundColor:
      theme.palette.mode === 'dark'
        ? alpha('#FF6B6B', 0.1)
        : alpha('#F44336', 0.1),
    borderColor: theme.palette.mode === 'dark' ? '#FF6B6B' : '#F44336',
    transform: 'translateY(-1px)',
  },
}));

// Create Button - more prominent
export const CreateButton = styled(Button)(({ theme }) => ({
  padding: '10px 20px', // Reduced from 12px 24px
  fontSize: '0.9rem', // Reduced from 1rem
  fontWeight: 600,
  border: `2px solid ${theme.palette.mode === 'dark' ? '#9A7CFF' : '#7C4DFF'}`,
  borderRadius: '12px',
  color: theme.palette.mode === 'dark' ? '#FFFFFF' : '#7C4DFF',
  backgroundColor:
    theme.palette.mode === 'dark'
      ? alpha('#9A7CFF', 0.1)
      : alpha('#7C4DFF', 0.05),
  transition: 'all 0.3s ease',
  '&:hover': {
    backgroundColor:
      theme.palette.mode === 'dark'
        ? alpha('#9A7CFF', 0.2)
        : alpha('#7C4DFF', 0.1),
    borderColor: theme.palette.mode === 'dark' ? '#B79CFF' : '#9A7CFF',
    transform: 'translateY(-2px)',
    boxShadow:
      theme.palette.mode === 'dark'
        ? '0 6px 20px rgba(154, 124, 255, 0.3)'
        : '0 6px 20px rgba(124, 77, 255, 0.2)',
  },
}));

// Futuristic Button with animated effects
export const FuturisticButton = styled(Button)(({ theme }) => ({
  position: 'relative',
  padding: '12px 36px', // Reduced from 16px 48px
  fontSize: '1.1rem', // Reduced from 1.4rem
  fontWeight: 700,
  letterSpacing: '0.8px',
  textTransform: 'none',
  color: theme.palette.mode === 'dark' ? '#FFFFFF' : '#7C4DFF',
  background:
    theme.palette.mode === 'dark'
      ? alpha('#1C1C3C', 0.7)
      : alpha('#FFFFFF', 0.9),
  border: 'none',
  borderRadius: '18px',
  overflow: 'hidden',
  minWidth: '180px', // Reduced from 220px
  minHeight: '52px', // Reduced from 64px
  transition: 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)',

  '&::before': {
    content: '""',
    position: 'absolute',
    inset: 0,
    borderRadius: '18px',
    padding: '2px',
    background:
      'linear-gradient(45deg, #7C4DFF, #956AFF, #B79CFF, #956AFF, #7C4DFF)',
    backgroundSize: '300% 300%',
    animation: 'borderAnimation 8s linear infinite',
    WebkitMask:
      'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
    WebkitMaskComposite: 'xor',
    maskComposite: 'exclude',
    opacity: 0.6,
    transition: 'all 0.4s ease',
  },

  '&::after': {
    content: '""',
    position: 'absolute',
    inset: '3px',
    borderRadius: '16px',
    zIndex: -1,
    transition: 'all 0.4s ease',
  },

  '&:hover': {
    transform: 'translateY(-3px)',
    boxShadow:
      theme.palette.mode === 'dark'
        ? '0 10px 25px -5px rgba(124, 77, 255, 0.4)'
        : '0 10px 25px -5px rgba(124, 77, 255, 0.25)',

    '& .button-glow': {
      opacity: 0.9,
      transform: 'scale(1.2)',
    },

    '& .button-scanner': {
      opacity: 0.8,
      transform: 'translateX(120%)',
    },

    '&::before': {
      opacity: 1,
      boxShadow: '0 0 15px rgba(124, 77, 255, 0.5)',
      animation: 'borderAnimation 3s linear infinite',
    },
  },

  '&:active': {
    transform: 'translateY(-1px) scale(0.98)',
    '& .button-glow': {
      opacity: 1,
      transform: 'scale(0.9)',
    },
  },

  '@keyframes borderAnimation': {
    '0%': { backgroundPosition: '0% 50%' },
    '50%': { backgroundPosition: '100% 50%' },
    '100%': { backgroundPosition: '0% 50%' },
  },
}));

// Dynamic Start Button with enhanced effects
export const DynamicStartButton = ({ onClick, isTransitioning }) => {
  const theme = { palette: { mode: 'dark' } }; // We'll get this from props later
  const [animation, setAnimation] = useState(false);
  const buttonRef = useRef(null);

  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimation(true);
    }, 500);

    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (animation && buttonRef.current) {
      buttonRef.current.animate(
        [
          { transform: 'scale(0.9)', opacity: 0.7 },
          { transform: 'scale(1.05)', opacity: 1 },
          { transform: 'scale(1)', opacity: 1 },
        ],
        {
          duration: 800,
          easing: 'cubic-bezier(0.175, 0.885, 0.32, 1.275)',
          fill: 'forwards',
        },
      );
    }
  }, [animation]);

  const handleClick = (e) => {
    const button = e.currentTarget;
    const circle = document.createElement('span');
    const diameter = Math.max(button.clientWidth, button.clientHeight);
    const radius = diameter / 2;

    const rect = button.getBoundingClientRect();
    const x = e.clientX - rect.left - radius;
    const y = e.clientY - rect.top - radius;

    circle.style.width = circle.style.height = `${diameter}px`;
    circle.style.left = `${x}px`;
    circle.style.top = `${y}px`;
    circle.style.position = 'absolute';
    circle.style.borderRadius = '50%';
    circle.style.backgroundColor = 'rgba(255, 255, 255, 0.4)';
    circle.style.transform = 'scale(0)';
    circle.style.animation = 'ripple 0.6s linear';
    circle.style.pointerEvents = 'none';

    button.appendChild(circle);

    if (onClick) onClick(e);
  };

  return (
    <Box
      sx={{
        position: 'relative',
        ...(isTransitioning && {
          animation: 'buttonExit 0.6s forwards cubic-bezier(0.65, 0, 0.35, 1)',
          '@keyframes buttonExit': {
            '0%': {
              transform: 'scale(1) translateY(0)',
              opacity: 1,
            },
            '60%': {
              transform: 'scale(1.1) translateY(-10px)',
              opacity: 0.7,
            },
            '100%': {
              transform: 'scale(0.9) translateY(-20px)',
              opacity: 0,
            },
          },
        }),
      }}
    >
      <Box
        className="button-glow"
        sx={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          width: '140px', // Reduced from 180px
          height: '140px', // Reduced from 180px
          transform: 'translate(-50%, -50%) scale(0.9)',
          borderRadius: '50%',
          background:
            theme.palette.mode === 'dark'
              ? 'radial-gradient(circle, rgba(124, 77, 255, 0.15) 0%, rgba(0, 0, 0, 0) 70%)'
              : 'radial-gradient(circle, rgba(124, 77, 255, 0.1) 0%, rgba(255, 255, 255, 0) 70%)',
          opacity: 0.5,
          transition: 'all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
          filter: 'blur(8px)',
          zIndex: 0,
        }}
      />

      <FuturisticButton ref={buttonRef} onClick={handleClick} disableRipple>
        <Box
          className="button-scanner"
          sx={{
            position: 'absolute',
            top: 0,
            left: '-50%',
            width: '30%',
            height: '100%',
            background:
              'linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.2) 50%, rgba(255,255,255,0) 100%)',
            transform: 'translateX(-100%)',
            opacity: 0.5,
            transition: 'transform 0.8s ease, opacity 0.3s ease',
            zIndex: 3,
            pointerEvents: 'none',
          }}
        />

        <Typography
          sx={{
            position: 'relative',
            zIndex: 2,
            fontWeight: 700,
            textShadow:
              theme.palette.mode === 'dark'
                ? '0 0 10px rgba(124, 77, 255, 0.6)'
                : 'none',
            fontFamily: '"Inter", system-ui, sans-serif',
          }}
        >
          Inizia
        </Typography>

        {/* Floating particles */}
        {animation &&
          [...Array(6)].map((_, i) => (
            <Box
              key={i}
              sx={{
                position: 'absolute',
                width: `${Math.random() * 3 + 1}px`,
                height: `${Math.random() * 3 + 1}px`,
                backgroundColor:
                  theme.palette.mode === 'dark'
                    ? 'rgba(255, 255, 255, 0.6)'
                    : 'rgba(124, 77, 255, 0.6)',
                borderRadius: '50%',
                top: `${Math.random() * 100}%`,
                left: `${Math.random() * 100}%`,
                filter: 'blur(1px)',
                opacity: Math.random() * 0.5 + 0.3,
                animation: `float${i} ${Math.random() * 3 + 2}s infinite ease-in-out`,
                zIndex: 1,
                [`@keyframes float${i}`]: {
                  '0%, 100%': { transform: 'translate(0, 0)' },
                  '50%': {
                    transform: `translate(${Math.random() * 10 - 5}px, ${Math.random() * 10 - 5}px)`,
                  },
                },
              }}
            />
          ))}

        <Box
          sx={{
            '@keyframes ripple': {
              to: {
                opacity: 0,
                transform: 'scale(3)',
              },
            },
          }}
        />
      </FuturisticButton>
    </Box>
  );
};
