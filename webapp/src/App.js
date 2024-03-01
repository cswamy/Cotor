import { React } from 'react';

// Import networking
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './context/AuthProvider';
import ProtectedRoute from './context/ProtectedRoute';

// Import mui components
import {
  ThemeProvider,
  createTheme,
} from '@mui/material';

// Import custom components
import HomePage from './components/HomePage/HomePage';
import SearchIssue from './components/SearchIssue/SearchIssue';
import IssueDisplay from './components/IssueDisplay/IssueDisplay';
import NotFoundPage from './components/NotFoundPage/NotFoundPage';

// Create theme
const theme = createTheme ({
  typography: {
    fontFamily: "'DM Sans', sans-serif",
  },
});

const App = () => {
  return (
    <ThemeProvider theme={theme}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/search" 
            element={
              <ProtectedRoute>
                <SearchIssue />
              </ProtectedRoute>
              } 
            />
            <Route path="/issue" 
            element={
              <ProtectedRoute>
                <IssueDisplay />
              </ProtectedRoute>
              } 
            />
            
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </ThemeProvider>
  );
};

export default App;
