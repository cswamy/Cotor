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

// Import networking and DB
import axios from 'axios';

const SearchIssue = () => {

    const theme = useTheme();
    const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'));

    // Input and search button logic
    const [ghLink, setGhLink] = useState('');
    const [issueNumber, setIssueNumber] = useState('');
    const [showAlert, setShowAlert] = useState(false);
    const [alertMessage, setAlertMessage] = useState('');

    const handleGHLinkChange = (event) => {
        setGhLink(event.target.value);
    };

    const handleissueNumberChange = (event) => {
        setIssueNumber(event.target.value);
    };

    const searchClicked = async () => {
        console.log('ghLink: ', ghLink);
        console.log('issueNumber: ', issueNumber);
        if (ghLink === '' || issueNumber === '') {
            setAlertMessage('Please enter a GitHub link and an issue number');
            setShowAlert(true);
        } else {
            let owner = ghLink.split('/')[3];
            let repo = ghLink.split('/')[4];
            if (!owner || !repo || isNaN(Number(issueNumber))) {
                setAlertMessage('Please enter a valid GitHub link and issue number');
                setShowAlert(true);
            } else {
                let url = 
                'http://127.0.0.1:8000/validateinputs/' + owner + '/' + repo;
                const response = await axios.request({
                    method: 'GET',
                    url: url,
                    params: {
                        issue: issueNumber,
                    },
                });
                if (response.data.repo_exists === false) {
                    setAlertMessage('Could not find repository. Please check and try again.')
                    setShowAlert(true);
                } else if (response.data.issue_exists === false) {
                    if (response.data.issue_status === 'open') {
                        setAlertMessage('Issue is still open. Please try again with a closed issue.')
                        setShowAlert(true);
                    } else {
                        setAlertMessage('Could not find issue. Please check and try again.')
                        setShowAlert(true);
                    }
                } else {
                    console.log("Valid inputs!!")
                }
            }
        }
    };

    useEffect(() => {
        if (setShowAlert) {
          const timer = setTimeout(() => {
            setShowAlert(false);
            setAlertMessage('');
          }, 2000);
      
          return () => {
            clearTimeout(timer);
          };
        }
      }, [showAlert]);

    return (
        <Box>
            <Box>
                <Collapse in={showAlert} transition='auto' easing='ease-out'>
                    <Alert severity='error'>
                        {alertMessage}
                    </Alert>   
                </Collapse>

                {!showAlert &&
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
                        width={isSmallScreen ? '50%' : '30%'} 
                        margin="auto"
                        sx={{mt: 4}}
                        >   
                            <Typography 
                            variant={isSmallScreen ? 'body1' : 'h6'} 
                            align="center"
                            sx={{mb: 1}}>
                            Enter a closed issue number
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