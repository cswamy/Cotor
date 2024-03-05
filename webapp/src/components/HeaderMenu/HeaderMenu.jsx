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
import { supabase } from '../../supabaseClient';

const HeaderMenu = (props) => {

    const theme = useTheme();
    const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'));
    const navigate = useNavigate();

    const sourcePage = props.page;
    let button1Text = '';
    let button2Text = '';
    if (sourcePage === 'search') {
        button1Text = 'Logout';
    } else if (sourcePage === 'issue') {
        button1Text = 'Search';
        button2Text = 'Logout';
    } else {
        button1Text = 'Search';
        button2Text = 'Logout';
    } 

    const handleSignout = async () => {
        await supabase.auth.signOut();
    };

    const buttonClicked = (event) => {
        if (event.target.textContent === 'Search') {
            navigate('/search');
        } else if (event.target.textContent === 'Logout') {
            handleSignout();
            navigate('/', { replace: true });
        }
    };

    return (
        <Box
        sx={{
            position: 'fixed',
            right: isSmallScreen ? 0 : 8,
            top: isSmallScreen ? 'auto' : 2,
            bottom: isSmallScreen ? 8 : 'auto',
            left: isSmallScreen ? 0 : 'auto',
            width: isSmallScreen ? '100vw' : 'auto',
            maxWidth: isSmallScreen ? '100%' : 'auto',
            margin: isSmallScreen ? 'auto' : 'auto',
            textAlign: isSmallScreen ? 'center' : 'right',
        }}>
            <Button
            sx={{
                color: 'black',
                textTransform: 'none',
                borderBottom: isSmallScreen ? 'none' : '0.5px solid black',
                borderRadius: 0,
                '&:hover': {
                    borderBottom: isSmallScreen ? 'none' : '1px solid black',
                },
            }}
            onClick={buttonClicked}
            >
                <Typography variant="subtitle2">
                    {button1Text}
                </Typography>
            </Button>
            { sourcePage === 'issue' &&
            <Button
            sx={{
                color: 'black',
                textTransform: 'none',
                borderBottom: isSmallScreen ? 'none' : '0.5px solid black',
                borderRadius: 0,
                ml: 2,
                '&:hover': {
                    borderBottom: isSmallScreen ? 'none' : '1px solid black',
                },
            }}
            onClick={buttonClicked}
            >
                <Typography variant="subtitle2">
                    {button2Text}
                </Typography>
            </Button>
            }
        </Box>
    )
};

export default HeaderMenu;