import { React, useState, useEffect } from 'react';

// Import mui components
import {
    Box,
    Typography,
    Grid,
    TextField,
    useTheme,
    useMediaQuery,
    Button,
    Alert,
    Collapse,
} from '@mui/material';

// Import custom components
import HeaderMenu from '../HeaderMenu/HeaderMenu';

const SearchIssue = () => {

    const theme = useTheme();
    const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'));

    // Input and search button logic
    const [ghLink, setGhLink] = useState('');
    const [issueNumber, setIssueNumber] = useState('');
    const [emptyFieldsAlert, setEmptyFieldsAlert] = useState(false);

    const handleGHLinkChange = (event) => {
        setGhLink(event.target.value);
    };

    const handleissueNumberChange = (event) => {
        setIssueNumber(event.target.value);
    };

    const searchClicked = () => {
        if (ghLink === '' || issueNumber === '') {
            setEmptyFieldsAlert(true);
        } else {
            console.log('GH link: ', ghLink);
            console.log('Issue number: ', issueNumber);
        }
    };

    useEffect(() => {
        if (emptyFieldsAlert) {
          const timer = setTimeout(() => {
            setEmptyFieldsAlert(false);
          }, 2000);
      
          return () => {
            clearTimeout(timer);
          };
        }
      }, [emptyFieldsAlert]);

    return (
        <Box>
            <Box>
                <Collapse in={emptyFieldsAlert} transition='auto' easing='ease-out'>
                    <Alert severity='error'>
                        Please enter a valid GitHub link and an issue number
                    </Alert>   
                </Collapse>

                {!emptyFieldsAlert &&
                <HeaderMenu page='search'/>
                }
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
                            placeholder='https://github.com/gradio-app/gradio'
                            value={ghLink}
                            onChange={handleGHLinkChange}
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
                            placeholder='6973'
                            value={issueNumber}
                            onChange={handleissueNumberChange}
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
                                backgroundColor: '#dadada',
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