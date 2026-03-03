import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { CssBaseline } from '@mui/material';
import { ThemeProvider } from './context/ThemeContext';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import NewsPage from './components/NewsPage';
import CompaniesPage from './components/CompaniesPage';
import AlertsPage from './components/AlertsPage';
import SearchPage from './components/SearchPage';
import BookmarksPage from './components/BookmarksPage';

function App() {
  return (
    <ThemeProvider>
      <CssBaseline />
      <Router>
        <Navbar />
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/news" element={<NewsPage />} />
          <Route path="/companies" element={<CompaniesPage />} />
          <Route path="/alerts" element={<AlertsPage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/bookmarks" element={<BookmarksPage />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
