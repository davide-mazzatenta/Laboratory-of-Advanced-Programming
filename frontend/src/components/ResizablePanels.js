import React, { useState, useCallback, useRef, useEffect } from 'react';
import { Box } from '@mui/material';

const ResizablePanels = ({ 
  leftPanel, 
  rightPanel, 
  defaultLeftWidth = 40,
  minLeftWidth = 20,
  maxLeftWidth = 80,
  storageKey = 'resizable-panels-width' 
}) => {
  // Load saved width from localStorage or use default
  const [leftWidth, setLeftWidth] = useState(() => {
    const saved = localStorage.getItem(storageKey);
    return saved ? parseFloat(saved) : defaultLeftWidth;
  });
  
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef(null);

  // Save width to localStorage when it changes
  useEffect(() => {
    localStorage.setItem(storageKey, leftWidth.toString());
  }, [leftWidth, storageKey]);

  const handleMouseDown = useCallback((e) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleMouseMove = useCallback((e) => {
    if (!isDragging || !containerRef.current) return;

    const container = containerRef.current;
    const containerRect = container.getBoundingClientRect();
    const newLeftWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100;
    
    // Constrain within min/max bounds
    const constrainedWidth = Math.max(minLeftWidth, Math.min(maxLeftWidth, newLeftWidth));
    setLeftWidth(constrainedWidth);
  }, [isDragging, minLeftWidth, maxLeftWidth]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    } else {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isDragging, handleMouseMove, handleMouseUp]);

  return (
    <Box 
      ref={containerRef}
      sx={{ 
        display: 'flex',
        height: '100%',
        position: 'relative'
      }}
    >
      {/* Left Panel */}
      <Box 
        sx={{ 
          width: `${leftWidth}%`,
          height: '100%',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        {leftPanel}
      </Box>

      {/* Resizer */}
      <Box
        onMouseDown={handleMouseDown}
        sx={{
          width: '4px',
          height: '100%',
          backgroundColor: isDragging ? '#1976d2' : 'rgba(0, 0, 0, 0.12)',
          cursor: 'col-resize',
          position: 'relative',
          flexShrink: 0,
          transition: isDragging ? 'none' : 'background-color 0.2s ease',
          '&:hover': {
            backgroundColor: '#1976d2',
          },
          '&::before': {
            content: '""',
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: '16px',
            height: '40px',
            backgroundColor: 'transparent',
            borderLeft: '2px solid rgba(255, 255, 255, 0.8)',
            borderRight: '2px solid rgba(255, 255, 255, 0.8)',
            borderRadius: '2px',
            opacity: isDragging ? 1 : 0.6,
          }
        }}
      />

      {/* Right Panel */}
      <Box 
        sx={{ 
          width: `${100 - leftWidth}%`,
          height: '100%',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        {rightPanel}
      </Box>
    </Box>
  );
};

export default ResizablePanels;
