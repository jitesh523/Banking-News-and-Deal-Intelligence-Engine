import React, { useState, useEffect } from 'react';
import {
    Container,
    Grid,
    Paper,
    Typography,
    Card,
    CardContent,
    Box,
    CircularProgress,
    Chip,
    List,
    ListItem,
    ListItemText,
} from '@mui/material';
import {
    TrendingUp,
    Business,
    Assessment,
    Notifications,
} from '@mui/icons-material';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { analyticsAPI, newsAPI, companiesAPI, alertsAPI } from '../services/api';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const Dashboard = () => {
    const [loading, setLoading] = useState(true);
    const [dashboardData, setDashboardData] = useState(null);
    const [trendingNews, setTrendingNews] = useState([]);
    const [topCompanies, setTopCompanies] = useState([]);
    const [alerts, setAlerts] = useState([]);
    const [dealStats, setDealStats] = useState(null);

    useEffect(() => {
        loadDashboardData();
    }, []);

    const loadDashboardData = async () => {
        try {
            setLoading(true);

            // Load all dashboard data
            const [dashboard, trending, companies, alertsData, deals] = await Promise.all([
                analyticsAPI.getDashboard(),
                newsAPI.getTrending(7, 10),
                companiesAPI.getCompanies(10, 'mentions'),
                alertsAPI.getAlerts(null, 10),
                analyticsAPI.getDeals(30),
            ]);

            setDashboardData(dashboard.data);
            setTrendingNews(trending.data.articles || []);
            setTopCompanies(companies.data.companies || []);
            setAlerts(alertsData.data.alerts || []);
            setDealStats(deals.data.insights || null);

        } catch (error) {
            console.error('Error loading dashboard:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
                <CircularProgress size={60} />
            </Box>
        );
    }

    const dealTypeData = dealStats?.type_distribution
        ? Object.entries(dealStats.type_distribution).map(([name, value]) => ({ name, value }))
        : [];

    const sentimentData = dashboardData?.deal_summary?.sentiment_distribution
        ? [
            { name: 'Positive', value: dashboardData.deal_summary.sentiment_distribution.positive },
            { name: 'Neutral', value: dashboardData.deal_summary.sentiment_distribution.neutral },
            { name: 'Negative', value: dashboardData.deal_summary.sentiment_distribution.negative },
        ]
        : [];

    return (
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            <Typography variant="h4" gutterBottom fontWeight="bold" color="primary">
                Banking News & Deal Intelligence Dashboard
            </Typography>

            {/* Summary Cards */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} sm={6} md={3}>
                    <Card elevation={3}>
                        <CardContent>
                            <Box display="flex" alignItems="center" justifyContent="space-between">
                                <Box>
                                    <Typography color="textSecondary" gutterBottom>
                                        Total Deals
                                    </Typography>
                                    <Typography variant="h4" fontWeight="bold">
                                        {dashboardData?.deal_summary?.total_deals || 0}
                                    </Typography>
                                </Box>
                                <TrendingUp fontSize="large" color="primary" />
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                    <Card elevation={3}>
                        <CardContent>
                            <Box display="flex" alignItems="center" justifyContent="space-between">
                                <Box>
                                    <Typography color="textSecondary" gutterBottom>
                                        Companies Tracked
                                    </Typography>
                                    <Typography variant="h4" fontWeight="bold">
                                        {dashboardData?.relationship_summary?.total_companies || 0}
                                    </Typography>
                                </Box>
                                <Business fontSize="large" color="success" />
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                    <Card elevation={3}>
                        <CardContent>
                            <Box display="flex" alignItems="center" justifyContent="space-between">
                                <Box>
                                    <Typography color="textSecondary" gutterBottom>
                                        Relationships
                                    </Typography>
                                    <Typography variant="h4" fontWeight="bold">
                                        {dashboardData?.relationship_summary?.total_relationships || 0}
                                    </Typography>
                                </Box>
                                <Assessment fontSize="large" color="info" />
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                    <Card elevation={3}>
                        <CardContent>
                            <Box display="flex" alignItems="center" justifyContent="space-between">
                                <Box>
                                    <Typography color="textSecondary" gutterBottom>
                                        Active Alerts
                                    </Typography>
                                    <Typography variant="h4" fontWeight="bold">
                                        {dashboardData?.alert_summary?.total_alerts || 0}
                                    </Typography>
                                </Box>
                                <Notifications fontSize="large" color="warning" />
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Charts Row */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                {/* Deal Type Distribution */}
                <Grid item xs={12} md={6}>
                    <Paper elevation={3} sx={{ p: 3, height: '400px' }}>
                        <Typography variant="h6" gutterBottom fontWeight="bold">
                            Deal Type Distribution
                        </Typography>
                        {dealTypeData.length > 0 ? (
                            <ResponsiveContainer width="100%" height="90%">
                                <PieChart>
                                    <Pie
                                        data={dealTypeData}
                                        cx="50%"
                                        cy="50%"
                                        labelLine={false}
                                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                                        outerRadius={100}
                                        fill="#8884d8"
                                        dataKey="value"
                                    >
                                        {dealTypeData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip />
                                </PieChart>
                            </ResponsiveContainer>
                        ) : (
                            <Typography color="textSecondary" align="center" sx={{ mt: 10 }}>
                                No deal data available
                            </Typography>
                        )}
                    </Paper>
                </Grid>

                {/* Sentiment Distribution */}
                <Grid item xs={12} md={6}>
                    <Paper elevation={3} sx={{ p: 3, height: '400px' }}>
                        <Typography variant="h6" gutterBottom fontWeight="bold">
                            Sentiment Distribution
                        </Typography>
                        {sentimentData.length > 0 ? (
                            <ResponsiveContainer width="100%" height="90%">
                                <BarChart data={sentimentData}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="name" />
                                    <YAxis />
                                    <Tooltip />
                                    <Legend />
                                    <Bar dataKey="value" fill="#8884d8">
                                        {sentimentData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                        ))}
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        ) : (
                            <Typography color="textSecondary" align="center" sx={{ mt: 10 }}>
                                No sentiment data available
                            </Typography>
                        )}
                    </Paper>
                </Grid>
            </Grid>

            {/* Lists Row */}
            <Grid container spacing={3}>
                {/* Top Companies */}
                <Grid item xs={12} md={4}>
                    <Paper elevation={3} sx={{ p: 3, height: '400px', overflow: 'auto' }}>
                        <Typography variant="h6" gutterBottom fontWeight="bold">
                            Top Companies
                        </Typography>
                        <List>
                            {topCompanies.map((company, index) => (
                                <ListItem key={index} divider>
                                    <ListItemText
                                        primary={company.company}
                                        secondary={`${company.mention_count} mentions • ${company.deal_count} deals`}
                                    />
                                    <Chip label={`#${index + 1}`} color="primary" size="small" />
                                </ListItem>
                            ))}
                        </List>
                    </Paper>
                </Grid>

                {/* Trending News */}
                <Grid item xs={12} md={4}>
                    <Paper elevation={3} sx={{ p: 3, height: '400px', overflow: 'auto' }}>
                        <Typography variant="h6" gutterBottom fontWeight="bold">
                            Trending News
                        </Typography>
                        <List>
                            {trendingNews.map((article, index) => (
                                <ListItem key={index} divider>
                                    <ListItemText
                                        primary={article.title}
                                        secondary={`${article.source} • ${new Date(article.published_date).toLocaleDateString()}`}
                                        primaryTypographyProps={{ fontSize: '0.9rem' }}
                                    />
                                </ListItem>
                            ))}
                        </List>
                    </Paper>
                </Grid>

                {/* Recent Alerts */}
                <Grid item xs={12} md={4}>
                    <Paper elevation={3} sx={{ p: 3, height: '400px', overflow: 'auto' }}>
                        <Typography variant="h6" gutterBottom fontWeight="bold">
                            Recent Alerts
                        </Typography>
                        <List>
                            {alerts.map((alert, index) => (
                                <ListItem key={index} divider>
                                    <ListItemText
                                        primary={alert.title}
                                        secondary={alert.description}
                                        primaryTypographyProps={{ fontSize: '0.9rem' }}
                                    />
                                    <Chip
                                        label={alert.priority}
                                        color={alert.priority >= 3 ? 'error' : alert.priority >= 2 ? 'warning' : 'default'}
                                        size="small"
                                    />
                                </ListItem>
                            ))}
                        </List>
                    </Paper>
                </Grid>
            </Grid>
        </Container>
    );
};

export default Dashboard;
