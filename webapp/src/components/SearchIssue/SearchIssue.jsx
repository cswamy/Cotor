import { React } from 'react';

// Import mui components
import {
    Box,
    Typography,
    Grid,
    TextField,
    useTheme,
    useMediaQuery,
    Button,
} from '@mui/material';

// Import custom components
import HeaderMenu from '../HeaderMenu/HeaderMenu';

const SearchIssue = () => {

    const theme = useTheme();
    const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'));

    // Search button logic
    const searchClicked = () => {
        console.log('Search clicked');
    };

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
                <Grid container justify="center">
                    <Grid item xs={12}>
                        <Box 
                        width={isSmallScreen ? '70%' : '40%'} 
                        margin="auto"
                        sx={{mt: 3}}
                        >   
                            <Typography 
                            variant={isSmallScreen ? 'body1' : 'h6'} 
                            align="center"
                            sx={{mb: 1}}>
                            Paste link to a public GitHub repository
                            </Typography>
                            <TextField
                            size='small' 
                            fullWidth
                            placeholder="https://github.com/gradio-app/gradio"
                            inputProps={{
                                style: {
                                    fontSize: isSmallScreen ? "0.8rem" : "1rem", 
                                    textAlign: "center" 
                                }
                            }}
                            sx={{
                                '& .MuiOutlinedInput-root': {
                                    '& fieldset': {
                                        borderColor: 'grey',
                                        borderRadius: '25px',
                                    },
                                    '&:hover fieldset': {
                                        borderColor: 'black',
                                        border: '1px solid',
                                    },
                                    '&.Mui-focused fieldset': {
                                        borderColor: 'black',
                                        border: '1px solid',
                                    },
                                },
                            }}
                            />
                        </Box>
                    </Grid>

                    <Grid item xs={12}>
                        <Box 
                        width={isSmallScreen ? '40%' : '20%'} 
                        margin="auto"
                        sx={{mt: 4}}
                        >   
                            <Typography 
                            variant={isSmallScreen ? 'body1' : 'h6'} 
                            align="center"
                            sx={{mb: 1}}>
                            Enter an issue number
                            </Typography>
                            <TextField 
                            size='small'
                            fullWidth
                            placeholder="6973"
                            inputProps={{
                                style: {
                                    fontSize: isSmallScreen ? "0.8rem" : "1rem", 
                                    textAlign: "center" 
                                }
                            }}
                            sx={{
                                '& .MuiOutlinedInput-root': {
                                    '& fieldset': {
                                        borderColor: 'grey',
                                        borderRadius: '25px',
                                    },
                                    '&:hover fieldset': {
                                        borderColor: 'black',
                                        border: '1px solid',
                                    },
                                    '&.Mui-focused fieldset': {
                                        borderColor: 'black',
                                        border: '1px solid',
                                    },
                                },
                            }}
                            />
                        </Box>
                    </Grid>

                    <Grid item xs={12}>
                        <Box 
                        margin="auto"
                        sx={{mt: 3, display: 'flex', justifyContent: 'center'}}
                        >   
                            <Button
                            sx={{
                                backgroundColor: 'white',
                                color: 'black',
                                border: '1px solid #dadada',
                                borderRadius: '25px',
                                '&:hover': {
                                    backgroundColor: 'black',
                                    color: 'white',
                                },
                                textTransform: 'none',
                                width: isSmallScreen ? '30%' : '10%',
                            }}
                            onClick={searchClicked}
                            >
                                Search
                            </Button>
                        </Box>
                    </Grid>

                </Grid>
            </Box>
        </Box>
    );
};

export default SearchIssue;