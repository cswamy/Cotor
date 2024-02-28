import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from './AuthProvider';

const ProtectedRoute = ({ children }) => {
    const { user } = useAuth(); 

    if (!user) {
      // User not authenticated, redirect to home page
      // return <Navigate to="/" replace />;
      console.log('User not authenticated, redirect to home page')
    }
  
    return children;
}

export default ProtectedRoute;