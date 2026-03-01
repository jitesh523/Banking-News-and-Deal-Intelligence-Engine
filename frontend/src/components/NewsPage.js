import React, { useState, useEffect, useCallback } from 'react';
import {
    Container,
    Typography,
    Paper,
    TextField,
    Grid,
    Card,
    CardContent,
    Chip,
    Box,
    CircularProgress,
    InputAdornment,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    Pagination,
} from '@mui/material';
import { Search, OpenInNew } from '@mui/icons-material';
import { newsAPI } from '../services/api';

const NewsPage = () => {
    const [articles, setArticles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [sourceFilter, setSourceFilter] = useState('');
    const [page, setPage] = useState(1);
    const articlesPerPage = 12;

    const loadArticles = useCallback(async () => {
        try {
            setLoading(true);
            let response;
            if (searchQuery.trim()) {
                response = await newsAPI.searchArticles(searchQuery, 100);
            } else {
                response = await newsAPI.getArticles({
                    limit: 100,
                    source: sourceFilter || undefined,
                });
            }
            setArticles(response.data.articles || []);
        } catch (error) {
            console.error('Error loading articles:', error);
        } finally {
            setLoading(false);
        }
    }, [searchQuery, sourceFilter]);

    useEffect(() => {
        const timer = setTimeout(() => loadArticles(), 400);
        return () => clearTimeout(timer);
    }, [loadArticles]);

    const paginatedArticles = articles.slice(
        (page - 1) * articlesPerPage,
        page * articlesPerPage
    );

    const sentimentColor = (label) => {
        if (!label) return 'default';
        if (label.toLowerCase().includes('pos')) return 'success';
        if (label.toLowerCase().includes('neg')) return 'error';
        return 'warning';
    };

    return (
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            <Typography variant="h4" gutterBottom fontWeight="bold" color="primary">
                News Articles
            </Typography>

            {/* Filters */}
            <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
                <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} md={6}>
                        <TextField
                            fullWidth
                            placeholder="Search articles..."
                            value={searchQuery}
                            onChange={(e) => { setSearchQuery(e.target.value); setPage(1); }}
                            InputProps={{
                                startAdornment: (
                                    <InputAdornment position="start"><Search /></InputAdornment>
                                ),
                            }}
                        />
                    </Grid>
                    <Grid item xs={12} md={3}>
                        <FormControl fullWidth>
                            <InputLabel>Source</InputLabel>
                            <Select
                                value={sourceFilter}
                                label="Source"
                                onChange={(e) => { setSourceFilter(e.target.value); setPage(1); }}
                            >
                                <MenuItem value="">All Sources</MenuItem>
                                <MenuItem value="newsapi">NewsAPI</MenuItem>
                                <MenuItem value="reuters">Reuters</MenuItem>
                                <MenuItem value="rss">RSS Feeds</MenuItem>
                            </Select>
                        </FormControl>
                    </Grid>
                    <Grid item xs={12} md={3}>
                        <Typography variant="body2" color="textSecondary">
                            {articles.length} articles found
                        </Typography>
                    </Grid>
                </Grid>
            </Paper>

            {loading ? (
                <Box display="flex" justifyContent="center" py={8}>
                    <CircularProgress size={50} />
                </Box>
            ) : (
                <>
                    <Grid container spacing={2}>
                        {paginatedArticles.map((article, idx) => (
                            <Grid item xs={12} md={6} lg={4} key={idx}>
                                <Card
                                    elevation={2}
                                    sx={{
                                        height: '100%',
                                        display: 'flex',
                                        flexDirection: 'column',
                                        transition: 'transform 0.15s, box-shadow 0.15s',
                                        '&:hover': { transform: 'translateY(-2px)', boxShadow: 6 },
                                    }}
                                >
                                    <CardContent sx={{ flexGrow: 1 }}>
                                        <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                                            {article.title}
                                        </Typography>
                                        <Box display="flex" gap={1} mb={1} flexWrap="wrap">
                                            <Chip label={article.source} size="small" color="primary" variant="outlined" />
                                            {article.sentiment?.label && (
                                                <Chip label={article.sentiment.label} size="small" color={sentimentColor(article.sentiment.label)} />
                                            )}
                                        </Box>
                                        <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                                            {article.author && `By ${article.author} • `}
                                            {new Date(article.published_date).toLocaleDateString()}
                                        </Typography>
                                        <Typography variant="body2" color="textSecondary" noWrap>
                                            {article.content?.substring(0, 150)}...
                                        </Typography>
                                    </CardContent>
                                    {article.url && (
                                        <Box sx={{ px: 2, pb: 1 }}>
                                            <Chip
                                                icon={<OpenInNew fontSize="small" />}
                                                label="Read Full Article"
                                                size="small"
                                                variant="outlined"
                                                clickable
                                                component="a"
                                                href={article.url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                            />
                                        </Box>
                                    )}
                                </Card>
                            </Grid>
                        ))}
                    </Grid>

                    {articles.length > articlesPerPage && (
                        <Box display="flex" justifyContent="center" mt={3}>
                            <Pagination
                                count={Math.ceil(articles.length / articlesPerPage)}
                                page={page}
                                onChange={(_, v) => setPage(v)}
                                color="primary"
                            />
                        </Box>
                    )}
                </>
            )}
        </Container>
    );
};

export default NewsPage;
