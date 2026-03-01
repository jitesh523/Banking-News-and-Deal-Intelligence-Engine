import React, { useState, useEffect } from 'react';
import {
    Container,
    Typography,
    Paper,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Chip,
    Box,
    CircularProgress,
    ToggleButton,
    ToggleButtonGroup,
    Divider,
} from '@mui/material';
import {
    Warning,
    Error as ErrorIcon,
    Info,
    ReportProblem,
} from '@mui/icons-material';
import { alertsAPI } from '../services/api';

const priorityConfig = {
    CRITICAL: { icon: <ErrorIcon />, color: 'error', bg: '#fdecea' },
    HIGH: { icon: <Warning />, color: 'warning', bg: '#fff4e5' },
    MEDIUM: { icon: <ReportProblem />, color: 'info', bg: '#e8f4fd' },
    LOW: { icon: <Info />, color: 'default', bg: '#f5f5f5' },
};

const AlertsPage = () => {
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [priorityFilter, setPriorityFilter] = useState(null);
    const [summary, setSummary] = useState(null);

    useEffect(() => {
        loadAlerts();
    }, [priorityFilter]);

    const loadAlerts = async () => {
        try {
            setLoading(true);
            const [alertsRes, summaryRes] = await Promise.all([
                alertsAPI.getAlerts(priorityFilter, 100),
                alertsAPI.getSummary(),
            ]);
            setAlerts(alertsRes.data.alerts || []);
            setSummary(summaryRes.data);
        } catch (error) {
            console.error('Error loading alerts:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            <Typography variant="h4" gutterBottom fontWeight="bold" color="primary">
                Alert Center
            </Typography>

            {/* Summary Cards */}
            {summary && (
                <Box display="flex" gap={2} mb={3} flexWrap="wrap">
                    <Paper elevation={2} sx={{ p: 2, minWidth: 150, textAlign: 'center' }}>
                        <Typography variant="h4" fontWeight="bold" color="primary">
                            {summary.total_alerts || 0}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">Total Alerts</Typography>
                    </Paper>
                    {Object.entries(summary.by_priority || {}).map(([priority, count]) => {
                        const config = priorityConfig[priority] || priorityConfig.LOW;
                        return (
                            <Paper key={priority} elevation={2} sx={{ p: 2, minWidth: 120, textAlign: 'center', backgroundColor: config.bg }}>
                                <Typography variant="h4" fontWeight="bold">
                                    {count}
                                </Typography>
                                <Chip label={priority} color={config.color} size="small" />
                            </Paper>
                        );
                    })}
                </Box>
            )}

            {/* Priority Filter */}
            <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>Filter by Priority:</Typography>
                <ToggleButtonGroup
                    value={priorityFilter}
                    exclusive
                    onChange={(_, val) => setPriorityFilter(val)}
                    size="small"
                >
                    <ToggleButton value={null}>All</ToggleButton>
                    <ToggleButton value="CRITICAL">Critical</ToggleButton>
                    <ToggleButton value="HIGH">High</ToggleButton>
                    <ToggleButton value="MEDIUM">Medium</ToggleButton>
                    <ToggleButton value="LOW">Low</ToggleButton>
                </ToggleButtonGroup>
            </Paper>

            {loading ? (
                <Box display="flex" justifyContent="center" py={8}>
                    <CircularProgress size={50} />
                </Box>
            ) : (
                <Paper elevation={2}>
                    <List>
                        {alerts.length === 0 && (
                            <ListItem>
                                <ListItemText
                                    primary="No alerts"
                                    secondary="No alerts match the current filter"
                                />
                            </ListItem>
                        )}
                        {alerts.map((alert, idx) => {
                            const config = priorityConfig[alert.priority] || priorityConfig.LOW;
                            return (
                                <React.Fragment key={idx}>
                                    <ListItem
                                        sx={{
                                            backgroundColor: config.bg,
                                            transition: 'background-color 0.15s',
                                            '&:hover': { filter: 'brightness(0.97)' },
                                        }}
                                    >
                                        <ListItemIcon>{config.icon}</ListItemIcon>
                                        <ListItemText
                                            primary={
                                                <Box display="flex" alignItems="center" gap={1}>
                                                    <Typography fontWeight="bold">{alert.title}</Typography>
                                                    <Chip label={alert.priority} color={config.color} size="small" />
                                                    {alert.alert_type && (
                                                        <Chip label={alert.alert_type} size="small" variant="outlined" />
                                                    )}
                                                </Box>
                                            }
                                            secondary={alert.description}
                                        />
                                    </ListItem>
                                    {idx < alerts.length - 1 && <Divider />}
                                </React.Fragment>
                            );
                        })}
                    </List>
                </Paper>
            )}
        </Container>
    );
};

export default AlertsPage;
