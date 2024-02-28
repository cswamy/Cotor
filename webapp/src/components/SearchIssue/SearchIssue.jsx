import { React } from 'react';

// Import mui components
import {
    Box,
    Typography,
} from '@mui/material';

const SearchIssue = () => {
    return (
        <Box>
            <Typography variant="h3" align="center">
                Search for an issue
            </Typography>
            <Typography variant="h6" align="center">
                Search for an issue on an open source project
            </Typography>
            <Typography variant="subtitle1" align="center">
                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            </Typography>
        </Box>
    );
};

export default SearchIssue;