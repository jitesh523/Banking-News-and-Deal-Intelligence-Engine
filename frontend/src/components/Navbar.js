import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
    AppBar,
    Toolbar,
    Typography,
    Button,
    Box,
    IconButton,
} from '@mui/material';
import {
    Dashboard as DashboardIcon,
    Article,
    Business,
    NotificationsActive,
    ShowChart,
} from '@mui/icons-material';

const navItems = [
    { label: 'Dashboard', path: '/', icon: <DashboardIcon /> },
    { label: 'News', path: '/news', icon: <Article /> },
    { label: 'Companies', path: '/companies', icon: <Business /> },
    { label: 'Alerts', path: '/alerts', icon: <NotificationsActive /> },
];

const Navbar = () => {
    const location = useLocation();

    return (
        <AppBar
            position="sticky"
            elevation={0}
            sx={{
                background: 'linear-gradient(135deg, #1a237e 0%, #0d47a1 100%)',
                borderBottom: '2px solid rgba(255,255,255,0.12)',
            }}
        >
            <Toolbar>
                <IconButton edge="start" color="inherit" sx={{ mr: 1 }}>
                    <ShowChart />
                </IconButton>
                <Typography
                    variant="h6"
                    component={Link}
                    to="/"
                    sx={{
                        flexGrow: 0,
                        mr: 4,
                        textDecoration: 'none',
                        color: 'inherit',
                        fontWeight: 700,
                        letterSpacing: '0.5px',
                    }}
                >
                    Banking Intelligence
                </Typography>

                <Box sx={{ flexGrow: 1, display: 'flex', gap: 0.5 }}>
                    {navItems.map((item) => (
                        <Button
                            key={item.path}
                            component={Link}
                            to={item.path}
                            startIcon={item.icon}
                            sx={{
                                color: 'white',
                                textTransform: 'none',
                                fontWeight: location.pathname === item.path ? 700 : 400,
                                backgroundColor:
                                    location.pathname === item.path
                                        ? 'rgba(255,255,255,0.15)'
                                        : 'transparent',
                                borderRadius: 2,
                                px: 2,
                                '&:hover': {
                                    backgroundColor: 'rgba(255,255,255,0.1)',
                                },
                            }}
                        >
                            {item.label}
                        </Button>
                    ))}
                </Box>
            </Toolbar>
        </AppBar>
    );
};

export default Navbar;
