import React from 'react';
import { useAuth } from './AuthProvider';

import HomePage from '../components/HomePage/HomePage';

const ProtectedRoute = ({ children }) => {
    const { user } = useAuth(); 

    if (!user) {
      // User not authenticated, redirect to home page
      return <HomePage />;
    }
  
    return children;
}

export default ProtectedRoute;