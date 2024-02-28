import { React } from 'react';

// Import mui components
import {
    Box,
} from '@mui/material';

// Import custom components
import HeaderMenu from '../HeaderMenu/HeaderMenu';

const SearchIssue = () => {
    return (
        <Box
        align="right"
        p={1}
        >
            <HeaderMenu page='search'/>
        </Box>
    );
};

export default SearchIssue;