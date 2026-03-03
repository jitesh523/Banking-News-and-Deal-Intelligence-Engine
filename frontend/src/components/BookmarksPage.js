import React, { useState, useEffect, useCallback } from 'react';
import {
    Container,
    Typography,
    Paper,
    Grid,
    Card,
    CardContent,
    CardActions,
    IconButton,
    Chip,
    Box,
    CircularProgress,
    TextField,
    Tooltip,
    Snackbar,
    Alert,
} from '@mui/material';
import { Bookmark, BookmarkBorder, Delete, OpenInNew } from '@mui/icons-material';
import { newsAPI } from '../services/api';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const BookmarksPage = () => {
    const [bookmarks, setBookmarks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [addArticleId, setAddArticleId] = useState('');
    const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

    const loadBookmarks = useCallback(async () => {
        try {
            setLoading(true);
            const res = await axios.get(`${API_BASE}/api/v1/bookmarks/`, { params: { limit: 100 } });
            setBookmarks(res.data.bookmarks || []);
        } catch (err) {
            console.error('Error loading bookmarks:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        loadBookmarks();
    }, [loadBookmarks]);

    const removeBookmark = async (articleId) => {
        try {
            await axios.delete(`${API_BASE}/api/v1/bookmarks/${articleId}`);
            setBookmarks((prev) => prev.filter((b) => b.article_id !== articleId));
            setSnackbar({ open: true, message: 'Bookmark removed', severity: 'info' });
        } catch (err) {
            console.error('Error removing bookmark:', err);
            setSnackbar({ open: true, message: 'Failed to remove bookmark', severity: 'error' });
        }
    };

    const addBookmark = async () => {
        if (!addArticleId.trim()) return;
        try {
            await axios.post(`${API_BASE}/api/v1/bookmarks/`, { article_id: addArticleId.trim() });
            setAddArticleId('');
            setSnackbar({ open: true, message: 'Bookmark added!', severity: 'success' });
            loadBookmarks();
        } catch (err) {
            const msg = err.response?.data?.detail || 'Failed to add bookmark';
            setSnackbar({ open: true, message: msg, severity: 'error' });
        }
    };

    return (
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            <Typography variant="h4" gutterBottom fontWeight="bold" color="primary">
                <Bookmark sx={{ mr: 1, verticalAlign: 'middle' }} />
                My Bookmarks
            </Typography>

            {/* Add Bookmark */}
            <Paper elevation={2} sx={{ p: 2, mb: 3, display: 'flex', gap: 2, alignItems: 'center' }}>
                <TextField
                    placeholder="Enter Article ID to bookmark..."
                    value={addArticleId}
                    onChange={(e) => setAddArticleId(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && addBookmark()}
                    size="small"
                    sx={{ flexGrow: 1 }}
                />
                <Tooltip title="Add Bookmark">
                    <IconButton color="primary" onClick={addBookmark}>
                        <BookmarkBorder />
                    </IconButton>
                </Tooltip>
                <Typography variant="body2" color="textSecondary">
                    {bookmarks.length} bookmarked
                </Typography>
            </Paper>

            {loading ? (
                <Box display="flex" justifyContent="center" py={8}>
                    <CircularProgress size={50} />
                </Box>
            ) : bookmarks.length === 0 ? (
                <Box textAlign="center" py={8}>
                    <BookmarkBorder sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
                    <Typography variant="h6" color="textSecondary">
                        No bookmarks yet
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                        Save important articles for quick access
                    </Typography>
                </Box>
            ) : (
                <Grid container spacing={2}>
                    {bookmarks.map((bm, idx) => (
                        <Grid item xs={12} sm={6} md={4} key={idx}>
                            <Card
                                elevation={2}
                                sx={{
                                    transition: 'transform 0.15s',
                                    '&:hover': { transform: 'translateY(-2px)', boxShadow: 6 },
                                }}
                            >
                                <CardContent>
                                    <Box display="flex" justifyContent="space-between" alignItems="start">
                                        <Typography variant="subtitle1" fontWeight="bold">
                                            {bm.article_id}
                                        </Typography>
                                        <Chip
                                            label={<Bookmark fontSize="small" />}
                                            color="primary"
                                            size="small"
                                        />
                                    </Box>
                                    {bm.notes && (
                                        <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                                            {bm.notes}
                                        </Typography>
                                    )}
                                    <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                                        Saved: {new Date(bm.created_at).toLocaleString()}
                                    </Typography>
                                </CardContent>
                                <CardActions>
                                    <Tooltip title="Remove Bookmark">
                                        <IconButton
                                            size="small"
                                            color="error"
                                            onClick={() => removeBookmark(bm.article_id)}
                                        >
                                            <Delete fontSize="small" />
                                        </IconButton>
                                    </Tooltip>
                                </CardActions>
                            </Card>
                        </Grid>
                    ))}
                </Grid>
            )}

            <Snackbar
                open={snackbar.open}
                autoHideDuration={3000}
                onClose={() => setSnackbar({ ...snackbar, open: false })}
            >
                <Alert severity={snackbar.severity} variant="filled">
                    {snackbar.message}
                </Alert>
            </Snackbar>
        </Container>
    );
};

export default BookmarksPage;
