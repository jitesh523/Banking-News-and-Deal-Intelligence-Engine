import React, { useState, useCallback } from 'react';
import {
    Container,
    Typography,
    Paper,
    TextField,
    InputAdornment,
    Box,
    CircularProgress,
    Card,
    CardContent,
    Chip,
    Grid,
    Tabs,
    Tab,
    Divider,
} from '@mui/material';
import { Search as SearchIcon, Article, Business, TrendingUp } from '@mui/icons-material';
import { newsAPI, companiesAPI, analyticsAPI } from '../services/api';

const SearchPage = () => {
    const [query, setQuery] = useState('');
    const [loading, setLoading] = useState(false);
    const [tab, setTab] = useState(0);
    const [results, setResults] = useState({ articles: [], companies: [], deals: [] });
    const [searched, setSearched] = useState(false);

    const handleSearch = useCallback(async () => {
        if (!query.trim()) return;
        setLoading(true);
        setSearched(true);

        try {
            const [articlesRes, companiesRes, dealsRes] = await Promise.allSettled([
                newsAPI.searchArticles(query, 50),
                companiesAPI.getCompanies(100, 'mentions'),
                analyticsAPI.getDealStats(90),
            ]);

            // Filter articles from API response
            const articles = articlesRes.status === 'fulfilled'
                ? (articlesRes.value.data.data || articlesRes.value.data.articles || [])
                : [];

            // Filter companies matching search query
            const allCompanies = companiesRes.status === 'fulfilled'
                ? (companiesRes.value.data.companies || [])
                : [];
            const matchedCompanies = allCompanies.filter((c) =>
                c.company?.toLowerCase().includes(query.toLowerCase())
            );

            // Deals data
            const dealsData = dealsRes.status === 'fulfilled'
                ? dealsRes.value.data
                : {};
            const dealTypes = dealsData?.insights?.type_distribution || {};
            const deals = Object.entries(dealTypes).map(([type, count]) => ({
                deal_type: type,
                count,
            }));

            setResults({ articles, companies: matchedCompanies, deals });
        } catch (err) {
            console.error('Search error:', err);
        } finally {
            setLoading(false);
        }
    }, [query]);

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') handleSearch();
    };

    const sentimentColor = (label) => {
        if (!label) return 'default';
        if (label.toLowerCase().includes('pos')) return 'success';
        if (label.toLowerCase().includes('neg')) return 'error';
        return 'warning';
    };

    const totalResults = results.articles.length + results.companies.length + results.deals.length;

    return (
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            <Typography variant="h4" gutterBottom fontWeight="bold" color="primary">
                Global Search
            </Typography>

            {/* Search Bar */}
            <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
                <TextField
                    fullWidth
                    placeholder="Search articles, companies, and deals..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={handleKeyDown}
                    InputProps={{
                        startAdornment: (
                            <InputAdornment position="start"><SearchIcon /></InputAdornment>
                        ),
                    }}
                    variant="outlined"
                    autoFocus
                />
                {searched && !loading && (
                    <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                        {totalResults} results found for "{query}"
                    </Typography>
                )}
            </Paper>

            {loading ? (
                <Box display="flex" justifyContent="center" py={8}>
                    <CircularProgress size={50} />
                </Box>
            ) : searched ? (
                <>
                    <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 2 }}>
                        <Tab icon={<Article />} label={`Articles (${results.articles.length})`} iconPosition="start" />
                        <Tab icon={<Business />} label={`Companies (${results.companies.length})`} iconPosition="start" />
                        <Tab icon={<TrendingUp />} label={`Deals (${results.deals.length})`} iconPosition="start" />
                    </Tabs>

                    <Divider sx={{ mb: 2 }} />

                    {/* Articles Tab */}
                    {tab === 0 && (
                        <Grid container spacing={2}>
                            {results.articles.length === 0 && (
                                <Grid item xs={12}>
                                    <Typography color="textSecondary" align="center" py={4}>
                                        No articles match your query
                                    </Typography>
                                </Grid>
                            )}
                            {results.articles.map((article, idx) => (
                                <Grid item xs={12} md={6} key={idx}>
                                    <Card
                                        elevation={2}
                                        sx={{
                                            transition: 'transform 0.15s',
                                            '&:hover': { transform: 'translateY(-2px)', boxShadow: 6 },
                                        }}
                                    >
                                        <CardContent>
                                            <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                                                {article.title}
                                            </Typography>
                                            <Box display="flex" gap={1} mb={1} flexWrap="wrap">
                                                <Chip label={article.source} size="small" color="primary" variant="outlined" />
                                                {article.sentiment?.label && (
                                                    <Chip label={article.sentiment.label} size="small"
                                                        color={sentimentColor(article.sentiment.label)} />
                                                )}
                                            </Box>
                                            <Typography variant="body2" color="textSecondary">
                                                {new Date(article.published_date).toLocaleDateString()}
                                            </Typography>
                                        </CardContent>
                                    </Card>
                                </Grid>
                            ))}
                        </Grid>
                    )}

                    {/* Companies Tab */}
                    {tab === 1 && (
                        <Grid container spacing={2}>
                            {results.companies.length === 0 && (
                                <Grid item xs={12}>
                                    <Typography color="textSecondary" align="center" py={4}>
                                        No companies match your query
                                    </Typography>
                                </Grid>
                            )}
                            {results.companies.map((company, idx) => (
                                <Grid item xs={12} sm={6} md={4} key={idx}>
                                    <Card elevation={2}>
                                        <CardContent>
                                            <Typography variant="h6" fontWeight="bold">{company.company}</Typography>
                                            <Box display="flex" gap={1} mt={1}>
                                                <Chip label={`${company.mention_count || 0} mentions`} color="primary" size="small" />
                                                <Chip label={`${company.deal_count || 0} deals`} color="success" size="small" />
                                            </Box>
                                        </CardContent>
                                    </Card>
                                </Grid>
                            ))}
                        </Grid>
                    )}

                    {/* Deals Tab */}
                    {tab === 2 && (
                        <Grid container spacing={2}>
                            {results.deals.length === 0 && (
                                <Grid item xs={12}>
                                    <Typography color="textSecondary" align="center" py={4}>
                                        No deal data available
                                    </Typography>
                                </Grid>
                            )}
                            {results.deals.map((deal, idx) => (
                                <Grid item xs={12} sm={6} md={4} key={idx}>
                                    <Card elevation={2}>
                                        <CardContent>
                                            <Typography variant="h6" fontWeight="bold" textTransform="capitalize">
                                                {deal.deal_type}
                                            </Typography>
                                            <Typography variant="h4" color="primary" fontWeight="bold">
                                                {deal.count}
                                            </Typography>
                                            <Typography variant="body2" color="textSecondary">
                                                detected in the last 90 days
                                            </Typography>
                                        </CardContent>
                                    </Card>
                                </Grid>
                            ))}
                        </Grid>
                    )}
                </>
            ) : (
                <Box textAlign="center" py={8}>
                    <SearchIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
                    <Typography variant="h6" color="textSecondary">
                        Search across articles, companies, and deals
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                        Press Enter to search
                    </Typography>
                </Box>
            )}
        </Container>
    );
};

export default SearchPage;
