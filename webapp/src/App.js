import { React } from 'react';

// Import networking
import { Routes, Route } from 'react-router-dom';

// Import mui components
import {
	Box,
} from '@mui/material';

// Import custom components
import HomePage from './components/HomePage/HomePage';
import NotFoundPage from './components/NotFoundPage/NotFoundPage';

const App = () => {
  return (
    <Box>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Box>
  );
};

export default App;
