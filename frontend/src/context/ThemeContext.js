// src/context/ThemeContext.js
import React, { createContext, useState, useMemo, useEffect } from 'react';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';

export const ThemeContext = createContext({
  toggleColorMode: () => {},
  theme: null,
  systemThemeEnabled: true,
  setSystemThemeEnabled: () => {},
});

export const ThemeContextProvider = ({ children }) => {
  // Aggiungiamo uno state per permettere all'utente di abilitare/disabilitare
  // la sincronizzazione automatica con il tema di sistema
  const [systemThemeEnabled, setSystemThemeEnabled] = useState(() => {
    const savedPreference = localStorage.getItem('systemThemeEnabled');
    return savedPreference === null ? true : savedPreference === 'true';
  });

  const [mode, setMode] = useState(() => {
    // Recupera il tema dalle impostazioni locali o usa le preferenze del sistema
    const savedMode = localStorage.getItem('themeMode');
    if (savedMode && !systemThemeEnabled) {
      return savedMode;
    }
    return window.matchMedia &&
      window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark'
      : 'light';
  });

  // Effetto per ascoltare i cambiamenti delle preferenze di tema del sistema
  useEffect(() => {
    if (!systemThemeEnabled) return; // Non ascoltare se la funzione è disabilitata

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    const handleSystemThemeChange = (e) => {
      setMode(e.matches ? 'dark' : 'light');
    };

    // Aggiungi il listener con supporto per browser più vecchi
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleSystemThemeChange);
    } else {
      // Fallback per browser meno recenti
      mediaQuery.addListener(handleSystemThemeChange);
    }

    // Pulizia all'unmount
    return () => {
      if (mediaQuery.removeEventListener) {
        mediaQuery.removeEventListener('change', handleSystemThemeChange);
      } else {
        // Fallback per browser meno recenti
        mediaQuery.removeListener(handleSystemThemeChange);
      }
    };
  }, [systemThemeEnabled]);

  // Effetto per salvare la preferenza systemThemeEnabled
  useEffect(() => {
    localStorage.setItem('systemThemeEnabled', systemThemeEnabled);
  }, [systemThemeEnabled]);

  const colorMode = useMemo(
    () => ({
      toggleColorMode: () => {
        setMode((prevMode) => {
          const newMode = prevMode === 'light' ? 'dark' : 'light';
          localStorage.setItem('themeMode', newMode);
          return newMode;
        });

        // Se l'utente cambia manualmente il tema, disabilitiamo l'auto-rilevamento
        if (systemThemeEnabled) {
          setSystemThemeEnabled(false);
        }
      },
      systemThemeEnabled,
      setSystemThemeEnabled: (value) => {
        setSystemThemeEnabled(value);

        // Se riattiva la sincronizzazione con il sistema, aggiorna immediatamente il tema
        if (value === true) {
          const prefersDarkMode =
            window.matchMedia &&
            window.matchMedia('(prefers-color-scheme: dark)').matches;
          setMode(prefersDarkMode ? 'dark' : 'light');
        }
      },
    }),
    [systemThemeEnabled],
  );

  // Aggiungi attributo data-theme al body
  useEffect(() => {
    document.body.setAttribute('data-theme', mode);
    localStorage.setItem('themeMode', mode);
  }, [mode]);

  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode,
          ...(mode === 'light'
            ? {
                // Tema chiaro - Viola
                primary: {
                  main: '#7C4DFF', // Viola primario aggiornato
                  light: '#B39DDB',
                  dark: '#6200EE',
                  contrastText: '#ffffff',
                },
                secondary: {
                  main: '#00BFA5', // Teal/verde acqua per accenti
                  light: '#64FFDA',
                  dark: '#008975',
                  contrastText: '#ffffff',
                },
                background: {
                  default: '#F5F7FA', // Bianco con sfumatura blu-grigio chiaro
                  paper: '#FFFFFF',
                },
                text: {
                  primary: '#1E293B', // Blu scuro per testo primario
                  secondary: '#64748B', // Grigio-blu per testo secondario
                },
                divider: 'rgba(124, 77, 255, 0.12)',
              }
            : {
                // Tema scuro - Viola
                primary: {
                  main: '#B388FF', // Viola chiaro
                  light: '#D7B8FF',
                  dark: '#7B61FF',
                  contrastText: '#ffffff',
                },
                secondary: {
                  main: '#03DAC5', // Teal/verde acqua più brillante
                  light: '#5EFFEE',
                  dark: '#00867D',
                  contrastText: '#000000',
                },
                background: {
                  default: '#0B0B1A', // Viola-blu scuro profondo
                  paper: '#14142B', // Viola-blu scuro per elementi
                  contrast: '#1E1E2D', // Viola-blu scuro leggermente più chiaro
                },
                text: {
                  primary: '#F3F4F6', // Quasi bianco per testo
                  secondary: '#B0B8C4', // Grigio chiaro per testo secondario
                },
                divider: 'rgba(179, 136, 255, 0.12)',
              }),
        },
        typography: {
          fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
          h1: {
            fontWeight: 800,
            letterSpacing: '-0.025em',
          },
          h2: {
            fontWeight: 800,
            letterSpacing: '-0.025em',
          },
          h3: {
            fontWeight: 700,
            letterSpacing: '-0.02em',
          },
          h4: {
            fontWeight: 700,
            letterSpacing: '-0.015em',
          },
          h5: {
            fontWeight: 600,
            letterSpacing: '-0.01em',
          },
          h6: {
            fontWeight: 600,
            letterSpacing: '-0.005em',
          },
          button: {
            fontWeight: 600,
            letterSpacing: '0.02em',
            textTransform: 'none',
          },
        },
        shape: {
          borderRadius: 16,
        },
        shadows: [
          'none',
          '0px 2px 4px rgba(0, 0, 0, 0.05), 0px 1px 2px rgba(0, 0, 0, 0.05)',
          '0px 4px 8px rgba(0, 0, 0, 0.05), 0px 2px 4px rgba(0, 0, 0, 0.05)',
          '0px 8px 16px rgba(0, 0, 0, 0.05), 0px 4px 8px rgba(0, 0, 0, 0.05)',
          '0px 12px 24px rgba(0, 0, 0, 0.05), 0px 6px 12px rgba(0, 0, 0, 0.05)',
          '0 15px 30px rgba(27, 10, 59, 0.12), 0 8px 16px rgba(27, 10, 59, 0.08)',
        ],
        components: {
          MuiButton: {
            styleOverrides: {
              root: {
                textTransform: 'none',
                borderRadius: 12,
                fontWeight: 600,
              },
              containedPrimary: {
                boxShadow:
                  mode === 'light'
                    ? '0 8px 20px rgba(124, 77, 255, 0.15)'
                    : '0 8px 20px rgba(179, 136, 255, 0.2)',
                '&:hover': {
                  boxShadow:
                    mode === 'light'
                      ? '0 12px 30px rgba(124, 77, 255, 0.25)'
                      : '0 12px 30px rgba(179, 136, 255, 0.3)',
                  transform: 'translateY(-2px)',
                },
              },
            },
          },
          MuiCard: {
            styleOverrides: {
              root: {
                borderRadius: 16,
                overflow: 'hidden',
                border:
                  mode === 'light'
                    ? '1px solid rgba(124, 77, 255, 0.08)'
                    : '1px solid rgba(179, 136, 255, 0.1)',
              },
            },
          },
          MuiPaper: {
            styleOverrides: {
              root: {
                backgroundImage: 'none',
                borderRadius: 16,
              },
              elevation1: {
                boxShadow:
                  mode === 'light'
                    ? '0 4px 12px rgba(124, 77, 255, 0.08)'
                    : '0 4px 12px rgba(0, 0, 0, 0.2)',
              },
              elevation2: {
                boxShadow:
                  mode === 'light'
                    ? '0 8px 20px rgba(124, 77, 255, 0.1)'
                    : '0 8px 20px rgba(0, 0, 0, 0.25)',
              },
              elevation3: {
                boxShadow:
                  mode === 'light'
                    ? '0 12px 30px rgba(124, 77, 255, 0.12)'
                    : '0 12px 30px rgba(0, 0, 0, 0.3)',
              },
            },
          },
          MuiTextField: {
            styleOverrides: {
              root: {
                '& .MuiOutlinedInput-root': {
                  borderRadius: 12,
                  '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                    borderColor: mode === 'light' ? '#7C4DFF' : '#B388FF',
                    borderWidth: 2,
                  },
                },
              },
            },
          },
          MuiSwitch: {
            styleOverrides: {
              switchBase: {
                color: mode === 'light' ? '#7C4DFF' : '#B388FF',
              },
              track: {
                backgroundColor: mode === 'light' ? '#D7B8FF' : '#1E1E2D',
              },
            },
          },
          MuiCssBaseline: {
            styleOverrides: {
              body: {
                scrollbarWidth: 'thin',
                '&::-webkit-scrollbar': {
                  width: '6px',
                  height: '6px',
                },
                '&::-webkit-scrollbar-thumb': {
                  backgroundColor: mode === 'dark' ? '#4B5563' : '#CBD5E1',
                  borderRadius: '3px',
                },
                '&::-webkit-scrollbar-track': {
                  backgroundColor: mode === 'dark' ? '#1F2937' : '#F1F5F9',
                },
                backgroundAttachment: 'fixed',
                background:
                  mode === 'dark'
                    ? `radial-gradient(circle at 0% 0%, rgba(179, 136, 255, 0.4) 0%, transparent 30%),
                     radial-gradient(circle at 100% 0%, rgba(157, 92, 255, 0.3) 0%, transparent 40%),
                     radial-gradient(circle at 50% 100%, rgba(124, 77, 255, 0.25) 0%, transparent 50%),
                     linear-gradient(180deg, #0B0B1A 0%, #050510 100%)`
                    : `radial-gradient(circle at 0% 0%, rgba(124, 77, 255, 0.1) 0%, transparent 30%),
                     radial-gradient(circle at 100% 0%, rgba(124, 77, 255, 0.08) 0%, transparent 30%),
                     radial-gradient(circle at 50% 100%, rgba(124, 77, 255, 0.1) 0%, transparent 50%),
                     #F5F7FA`,
              },
            },
          },
          MuiIconButton: {
            styleOverrides: {
              root: {
                transition: 'all 0.3s cubic-bezier(0.05, 0.7, 0.1, 1)',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  backgroundColor:
                    mode === 'dark'
                      ? 'rgba(179, 136, 255, 0.15)'
                      : 'rgba(124, 77, 255, 0.08)',
                },
                '&:active': {
                  transform: 'translateY(0) scale(0.97)',
                },
              },
            },
          },
          MuiTooltip: {
            styleOverrides: {
              tooltip: {
                borderRadius: 8,
                backgroundColor:
                  mode === 'dark'
                    ? 'rgba(20, 20, 43, 0.95)'
                    : 'rgba(30, 41, 59, 0.95)',
                padding: '8px 12px',
                fontSize: '0.75rem',
                boxShadow:
                  mode === 'dark'
                    ? '0 4px 20px rgba(0, 0, 0, 0.4)'
                    : '0 4px 20px rgba(0, 0, 0, 0.1)',
              },
              arrow: {
                color:
                  mode === 'dark'
                    ? 'rgba(20, 20, 43, 0.95)'
                    : 'rgba(30, 41, 59, 0.95)',
              },
            },
          },
        },
      }),
    [mode],
  );

  return (
    <ThemeContext.Provider
      value={{ ...colorMode, theme, systemThemeEnabled, setSystemThemeEnabled }}
    >
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </ThemeContext.Provider>
  );
};
