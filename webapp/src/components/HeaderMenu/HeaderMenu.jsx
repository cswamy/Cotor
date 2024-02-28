import { React } from 'react';

// Import mui components
import {
    Box,
    Button,
    Typography,
} from '@mui/material';

const HeaderMenu = (props) => {

    const sourcePage = props.page;
    let button1Text = '';
    let button2Text = '';
    if (sourcePage === 'search') {
        button1Text = 'History';
        button2Text = 'Logout';
    } else if (sourcePage === 'issue') {
        button1Text = 'Search';
        button2Text = 'Logout';
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

    return (
        <Box
        sx={{
            mr: 2,
        }}>
            <Button
            sx={{
                color: 'black',
                textTransform: 'none',
                borderBottom: '0.5px solid black',
                borderRadius: 0,
                mr: 2,
                '&:hover': {
                    borderBottom: '1px solid black',
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
                borderBottom: '0.5px solid black',
                borderRadius: 0,
                '&:hover': {
                    borderBottom: '1px solid black',
                },
            }}
            onClick={button2Clicked}
            >
                <Typography variant="subtitle2">
                    {button2Text}
                </Typography>
            </Button>
        </Box>
    )
};

export default HeaderMenu;