import { React } from 'react';

// Import mui components
import {
    Box,
    Typography,
    TextField,
    useTheme,
    useMediaQuery,
} from '@mui/material';

// Import custom components
import HeaderMenu from '../HeaderMenu/HeaderMenu';

const SearchIssue = () => {

    const theme = useTheme();
    const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'));

    return (
        <Box>
            <Box>
                <HeaderMenu page='search'/>
            </Box>
            <Box
            sx={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                mt: 8,
            }}>
                <Box>
                    <Typography variant={isSmallScreen ? 'h2' : 'h1'} align="center">
                        Cotor
                    </Typography>
                </Box>
            </Box>
        </Box>
    );
};

export default SearchIssue;