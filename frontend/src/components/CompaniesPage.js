import React, { useState, useEffect } from 'react';
import {
    Container,
    Typography,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Chip,
    Box,
    CircularProgress,
    TextField,
    InputAdornment,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
} from '@mui/material';
import { Search, Hub } from '@mui/icons-material';
import { companiesAPI } from '../services/api';

const CompaniesPage = () => {
    const [companies, setCompanies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [sortBy, setSortBy] = useState('mentions');

    useEffect(() => {
        loadCompanies();
    }, [sortBy]);

    const loadCompanies = async () => {
        try {
            setLoading(true);
            const response = await companiesAPI.getCompanies(100, sortBy);
            setCompanies(response.data.companies || []);
        } catch (error) {
            console.error('Error loading companies:', error);
        } finally {
            setLoading(false);
        }
    };

    const filtered = companies.filter((c) =>
        c.company?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            <Typography variant="h4" gutterBottom fontWeight="bold" color="primary">
                Company Intelligence
            </Typography>

            {/* Filters */}
            <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
                <Box display="flex" gap={2} flexWrap="wrap" alignItems="center">
                    <TextField
                        placeholder="Search companies..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        InputProps={{
                            startAdornment: (
                                <InputAdornment position="start"><Search /></InputAdornment>
                            ),
                        }}
                        sx={{ flexGrow: 1, minWidth: 250 }}
                    />
                    <FormControl sx={{ minWidth: 180 }}>
                        <InputLabel>Sort By</InputLabel>
                        <Select value={sortBy} label="Sort By" onChange={(e) => setSortBy(e.target.value)}>
                            <MenuItem value="mentions">Mentions</MenuItem>
                            <MenuItem value="deals">Deals</MenuItem>
                            <MenuItem value="connections">Connections</MenuItem>
                        </Select>
                    </FormControl>
                    <Typography variant="body2" color="textSecondary">
                        {filtered.length} companies
                    </Typography>
                </Box>
            </Paper>

            {loading ? (
                <Box display="flex" justifyContent="center" py={8}>
                    <CircularProgress size={50} />
                </Box>
            ) : (
                <TableContainer component={Paper} elevation={2}>
                    <Table>
                        <TableHead>
                            <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                                <TableCell sx={{ fontWeight: 'bold' }}>#</TableCell>
                                <TableCell sx={{ fontWeight: 'bold' }}>Company</TableCell>
                                <TableCell sx={{ fontWeight: 'bold' }} align="center">Mentions</TableCell>
                                <TableCell sx={{ fontWeight: 'bold' }} align="center">Deals</TableCell>
                                <TableCell sx={{ fontWeight: 'bold' }} align="center">Connections</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {filtered.map((company, idx) => (
                                <TableRow
                                    key={idx}
                                    sx={{
                                        '&:hover': { backgroundColor: '#f0f7ff' },
                                        transition: 'background-color 0.15s',
                                    }}
                                >
                                    <TableCell>{idx + 1}</TableCell>
                                    <TableCell>
                                        <Box display="flex" alignItems="center" gap={1}>
                                            <Hub fontSize="small" color="primary" />
                                            <Typography fontWeight="bold">{company.company}</Typography>
                                        </Box>
                                    </TableCell>
                                    <TableCell align="center">
                                        <Chip
                                            label={company.mention_count || 0}
                                            color="primary"
                                            size="small"
                                            variant="outlined"
                                        />
                                    </TableCell>
                                    <TableCell align="center">
                                        <Chip
                                            label={company.deal_count || 0}
                                            color={company.deal_count > 0 ? 'success' : 'default'}
                                            size="small"
                                        />
                                    </TableCell>
                                    <TableCell align="center">
                                        <Chip
                                            label={company.connection_count || 0}
                                            color={company.connection_count > 0 ? 'info' : 'default'}
                                            size="small"
                                        />
                                    </TableCell>
                                </TableRow>
                            ))}
                            {filtered.length === 0 && (
                                <TableRow>
                                    <TableCell colSpan={5} align="center" sx={{ py: 6 }}>
                                        <Typography color="textSecondary">No companies found</Typography>
                                    </TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </TableContainer>
            )}
        </Container>
    );
};

export default CompaniesPage;
