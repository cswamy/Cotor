import { React } from 'react';

// Import mui components
import {
    Box,
    Button,
    Typography,
    useTheme,
    useMediaQuery,
} from '@mui/material';

// Import networking
import { useNavigate } from 'react-router-dom';

const NotFoundPage = () => {

    const navigate = useNavigate();
    const theme = useTheme();
    const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'));

    return (
        <Box
        sx={{
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            mt: 10,
        }}>
            <Typography variant="h3" align="center">
                Nooooooo!
            </Typography>
            <Typography variant="h6" align="center">
                {`How did we find ourselves here :(`}
            </Typography>
            <Typography variant="subtitle1" align="center">
                Please click on search and try again
            </Typography>
            <Button
            sx={{ 
                mt: 2,
                backgroundColor: '#dadada',
                color: 'black',
                borderRadius: '25px',
                '&:hover': {
                    backgroundColor: 'black',
                    color: 'white',
                },
                textTransform: 'none',
                width: isSmallScreen ? '30%' : '10%',
            }}
            onClick={() => {navigate('/search', {'replace': true});}}
            >
                Search
            </Button>
        </Box>
    );
}

export default NotFoundPage;