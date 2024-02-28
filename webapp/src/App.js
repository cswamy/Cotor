import { React } from 'react';

// Import networking
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './context/AuthProvider';
import ProtectedRoute from './context/ProtectedRoute';

// Import custom components
import HomePage from './components/HomePage/HomePage';
import SearchIssue from './components/SearchIssue/SearchIssue';
import NotFoundPage from './components/NotFoundPage/NotFoundPage';

const App = () => {
  return (
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
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;
