import { React } from 'react';

// Import mui components
import {
    Box,
    Button,
    Typography,
    useTheme,
    useMediaQuery,
} from '@mui/material';

const HeaderMenu = (props) => {

    const theme = useTheme();
    const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'));

    const sourcePage = props.page;
    let button1Text = '';
    let button2Text = '';
    let button3Text = '';
    if (sourcePage === 'search') {
        button1Text = 'History';
        button2Text = 'Logout';
    } else if (sourcePage === 'issue') {
        button1Text = 'Search';
        button2Text = 'History';
        button3Text = 'Logout';
    } else if (sourcePage === 'history') {
        button1Text = 'Search';
        button2Text = 'Logout';
    } else {
        button1Text = 'Search';
        button2Text = 'History';
    } 

    const button1Clicked = () => {
        console.log('Clicked: ', button1Text);
    };

    const button2Clicked = () => {
        console.log('Clicked: ', button2Text);
    };

    const button3Clicked = () => {
        console.log('Clicked: ', button3Text);
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
            onClick={button1Clicked}
            >
                <Typography variant="subtitle2">
                    {button1Text}
                </Typography>
            </Button>
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
            onClick={button2Clicked}
            >
                <Typography variant="subtitle2">
                    {button2Text}
                </Typography>
            </Button>
            {sourcePage !== 'search' &&
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
            onClick={button3Clicked}
            >
                <Typography variant="subtitle2">
                    {button3Text}
                </Typography>
            </Button>
            }
        </Box>
    )
};

export default HeaderMenu;