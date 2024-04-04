import { React, useState, useEffect } from 'react';
import { supabase } from '../../supabaseClient';

// Import mui components
import {
    Grid,
    Box,
    Button,
    Typography,
    CircularProgress,
    useTheme,
    useMediaQuery,
} from '@mui/material';

// Import custom components
import DemoVideo from './DemoVideo/DemoVideo';

// Import networking
import { useSearchParams, useNavigate } from 'react-router-dom';

const HomePage = () => {

    const theme = useTheme();
    const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'));
    const [loading, setLoading] = useState(false);

    const [searchParams] = useSearchParams();
    const id = searchParams.get('id');
    const navigate = useNavigate();

    // GitHub signin button click
    const handleGitHubSignIn = async () => {
        setLoading(true);
        let redirectURL;
        if (id) {
            redirectURL = `${process.env.REACT_APP_OAUTH_REDIRECT_URL}?id=${id}`;
        } else {
            redirectURL = process.env.REACT_APP_OAUTH_REDIRECT_URL;
        }
        const { error } = await supabase.auth.signInWithOAuth({ 
            provider: 'github',
            options: {
                redirectTo: redirectURL,
            },
        });
        if (error) {
            console.log('GitHub signin error: ', error);
        } else {
            setLoading(false);
        }
    };

    // Check if user session exists
    useEffect(() => {
        const checkSession = async () => {
            const { data } = await supabase.auth.getSession();
            if (data.session !== null) {
                setLoading(true);
                let redirectURL;
                if (id) {
                    redirectURL = `/search?id=${id}`;
                } else {
                    redirectURL = `/search`;
                }
                navigate(redirectURL);
                setLoading(false);
            }
        }

        checkSession();
    }, [id, navigate]);


    // Return component
    return (
        loading ?
        <Box
        sx={{
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            mt: 10,
          }}>
            <CircularProgress sx={{color: 'black'}}/>
        </Box>
        :
        <Grid container 
        justify="center" 
        alignItems="center"
        sx={{ 
            minHeight: '90vh', 
            p: isSmallScreen ? 5 : 10, 
        }}>

            <Grid item xs={12} sm={6}>
                <Box>
                    <Typography variant={isSmallScreen? 'h4': 'h3'}>
                        Welcome to Cotor
                    </Typography>
                    <Typography variant={isSmallScreen? 'h6': 'h5'} sx={{ mt: 1 }}>
                        Learn an open source codebase and start contributing.
                    </Typography>
                    <Typography variant={isSmallScreen? 'subtitle2': 'subtitle1'} sx={{ mt: 1 }}>
                        Closed issues for bugs and enhancements are a great way to learn a new codebase. Use Cotor and learn what code changes occurred in a merged pull request.  
                    </Typography>
                </Box>
                <Box 
                sx={{
                    mt: 2,
                }}>
                    <Button
                    sx={{
                        backgroundColor: 'white',
                        color: 'black',
                        border: '1px solid black',
                        borderRadius: '25px',
                        '&:hover': {
                            backgroundColor: 'black',
                            color: 'white',
                        },
                        textTransform: 'none',
                    }}
                    onClick={handleGitHubSignIn}
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 1792 1792">
                            <path d="M896 128q209 0 385.5 103t279.5 279.5 103 385.5q0 251-146.5 451.5t-378.5 277.5q-27 5-40-7t-13-30q0-3 .5-76.5t.5-134.5q0-97-52-142 57-6 102.5-18t94-39 81-66.5 53-105 20.5-150.5q0-119-79-206 37-91-8-204-28-9-81 11t-92 44l-38 24q-93-26-192-26t-192 26q-16-11-42.5-27t-83.5-38.5-85-13.5q-45 113-8 204-79 87-79 206 0 85 20.5 150t52.5 105 80.5 67 94 39 102.5 18q-39 36-49 103-21 10-45 15t-57 5-65.5-21.5-55.5-62.5q-19-32-48.5-52t-49.5-24l-20-3q-21 0-29 4.5t-5 11.5 9 14 13 12l7 5q22 10 43.5 38t31.5 51l10 23q13 38 44 61.5t67 30 69.5 7 55.5-3.5l23-4q0 38 .5 88.5t.5 54.5q0 18-13 30t-40 7q-232-77-378.5-277.5t-146.5-451.5q0-209 103-385.5t279.5-279.5 385.5-103zm-477 1103q3-7-7-12-10-3-13 2-3 7 7 12 9 6 13-2zm31 34q7-5-2-16-10-9-16-3-7 5 2 16 10 10 16 3zm30 45q9-7 0-19-8-13-17-6-9 5 0 18t17 7zm42 42q8-8-4-19-12-12-20-3-9 8 4 19 12 12 20 3zm57 25q3-11-13-16-15-4-19 7t13 15q15 6 19-6zm63 5q0-13-17-11-16 0-16 11 0 13 17 11 16 0 16-11zm58-10q-2-11-18-9-16 3-14 15t18 8 14-14z"></path>
                        </svg>
                        <Typography sx={{ml: 1}}>
                            Login with GitHub
                        </Typography>
                    </Button>
                </Box>
            </Grid>

            <Grid item xs={12} sm={6}>
                <DemoVideo />
            </Grid>

        </Grid>
    );
}

export default HomePage;