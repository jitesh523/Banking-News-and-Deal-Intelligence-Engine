import React, { createContext, useContext, useState, useMemo, useEffect } from 'react';
import { createTheme, ThemeProvider as MuiThemeProvider } from '@mui/material';

const ThemeContext = createContext({
    isDarkMode: false,
    toggleTheme: () => { },
});

export const useThemeMode = () => useContext(ThemeContext);

const STORAGE_KEY = 'banking-news-dark-mode';

/**
 * Provides a dark/light mode toggle that persists the user's
 * preference in localStorage.
 */
export const ThemeProvider = ({ children }) => {
    const [isDarkMode, setIsDarkMode] = useState(() => {
        try {
            return localStorage.getItem(STORAGE_KEY) === 'true';
        } catch {
            return false;
        }
    });

    useEffect(() => {
        try {
            localStorage.setItem(STORAGE_KEY, String(isDarkMode));
        } catch {
            // Ignore storage errors
        }
    }, [isDarkMode]);

    const toggleTheme = () => setIsDarkMode((prev) => !prev);

    const theme = useMemo(
        () =>
            createTheme({
                palette: {
                    mode: isDarkMode ? 'dark' : 'light',
                    primary: { main: isDarkMode ? '#90caf9' : '#1565c0' },
                    secondary: { main: isDarkMode ? '#f48fb1' : '#d32f2f' },
                    background: {
                        default: isDarkMode ? '#0a1929' : '#f4f6f9',
                        paper: isDarkMode ? '#132f4c' : '#ffffff',
                    },
                },
                typography: {
                    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
                },
                shape: { borderRadius: 10 },
                components: {
                    MuiCard: {
                        styleOverrides: {
                            root: { borderRadius: 12 },
                        },
                    },
                    MuiPaper: {
                        styleOverrides: {
                            root: { borderRadius: 12 },
                        },
                    },
                    MuiAppBar: {
                        styleOverrides: {
                            root: {
                                background: isDarkMode
                                    ? 'linear-gradient(135deg, #0d1b2a 0%, #1b263b 100%)'
                                    : 'linear-gradient(135deg, #1a237e 0%, #0d47a1 100%)',
                            },
                        },
                    },
                },
            }),
        [isDarkMode],
    );

    return (
        <ThemeContext.Provider value={{ isDarkMode, toggleTheme }}>
            <MuiThemeProvider theme={theme}>
                {children}
            </MuiThemeProvider>
        </ThemeContext.Provider>
    );
};

export default ThemeContext;
