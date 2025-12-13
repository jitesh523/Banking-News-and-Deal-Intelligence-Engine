import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// News API
export const newsAPI = {
    getArticles: (params) => api.get('/api/v1/news/', { params }),
    getArticle: (id) => api.get(`/api/v1/news/${id}`),
    searchArticles: (query, limit = 50) => api.get('/api/v1/news/search/', { params: { q: query, limit } }),
    getTrending: (days = 7, limit = 20) => api.get('/api/v1/news/trending/', { params: { days, limit } }),
    getStats: () => api.get('/api/v1/news/stats/'),
};

// Analytics API
export const analyticsAPI = {
    getSentiment: (days = 30, company = null) =>
        api.get('/api/v1/analytics/sentiment', { params: { days, company } }),
    getTopics: () => api.get('/api/v1/analytics/topics'),
    getEntities: (entityType = 'companies', limit = 20) =>
        api.get('/api/v1/analytics/entities', { params: { entity_type: entityType, limit } }),
    getDeals: (days = 30) => api.get('/api/v1/analytics/deals', { params: { days } }),
    getDashboard: () => api.get('/api/v1/analytics/dashboard'),
};

// Companies API
export const companiesAPI = {
    getCompanies: (limit = 50, sortBy = 'mentions') =>
        api.get('/api/v1/companies/', { params: { limit, sort_by: sortBy } }),
    getCompany: (name) => api.get(`/api/v1/companies/${encodeURIComponent(name)}`),
    getRelationships: (name, depth = 1) =>
        api.get(`/api/v1/companies/${encodeURIComponent(name)}/relationships`, { params: { depth } }),
    getSentiment: (name, days = 30) =>
        api.get(`/api/v1/companies/${encodeURIComponent(name)}/sentiment`, { params: { days } }),
    getNetworkGraph: () => api.get('/api/v1/companies/network/graph'),
};

// Alerts API
export const alertsAPI = {
    getAlerts: (priority = null, limit = 50) =>
        api.get('/api/v1/alerts/', { params: { priority, limit } }),
    getSummary: () => api.get('/api/v1/alerts/summary'),
};

export default api;
