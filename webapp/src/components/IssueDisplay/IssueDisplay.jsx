import { React, useState, useEffect } from 'react';

import Markdown from 'react-markdown'

// Import mui components
import {
  Box,
  Typography,
  Divider,
  CircularProgress,
  useTheme,
  useMediaQuery,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  useScrollTrigger,
  Grid,
} from '@mui/material';

// Import networking and dB
import { useLocation } from 'react-router-dom';
import { supabase } from '../../supabaseClient';
import axios from 'axios';

// Import custom components
import HeaderMenu from '../HeaderMenu/HeaderMenu';
import CodeBlock from './CodeBlock/CodeBlock'

const IssueDisplay = () => {

    const [issueInDB, setIssueInDB] = useState(true);
    const [issueData, setIssueData] = useState({});
    const {
        owner, 
        repo, 
        issue, 
        issue_url, 
        issue_title,
        issue_body,
    } = useLocation().state;

    const theme = useTheme();
    const isExtraSmallScreen = useMediaQuery(theme.breakpoints.down('xs'));
    const [dataLoading, setDataLoading] = useState(true);
    const typoVariant = 'subtitle1'
    const trigger = useScrollTrigger({
        disableHysteresis: true,
        threshold: 10,
      });

    useEffect(() => {

        const getIssueFromDB = async () => {
            const { data, error } = await supabase
                .from('Issues')
                .select('*')
                .eq('repo_owner', owner)
                .eq('repo', repo)
                .eq('issue_id', issue);
            if (error) {
                return;
            } else {
                if (data.length > 0) {
                    setIssueData(data[0]);
                } else {
                    setIssueInDB(false);
                }
            }
        }

        getIssueFromDB();
    }, [owner, repo, issue]);

    useEffect(() => {

        const getIssueFromAPI = async () => {
            let url = 'http://127.0.0.1:8000/researchissue'
            const response = await axios.request({
                method: 'GET',
                url: url,
                params: {
                    owner: owner,
                    repo: repo,
                    issue: issue,
                    issue_url: issue_url,
                    issue_title: issue_title,
                    issue_body: issue_body,
                }
            });
            if (response.data) {
                setIssueData(response.data);
                if (response.data['commit_details']['file_details'][0]['patch_explains'] !== 'Empty') {
                    await supabase.from('Issues').insert(response.data);
                }
            }
        }

        if (!issueInDB) {
            getIssueFromAPI();
        }
    }, [issueInDB, owner, repo, issue, issue_url, issue_title, issue_body]);

    useEffect(() => {
        if (Object.keys(issueData).length > 0) {
            setDataLoading(false);
        }
    }, [issueData]);

    return (
        <Box>
            {!trigger &&
                <Box>
                    <HeaderMenu page='issue'/>
                </Box>
            }
            
            {dataLoading ?
            (
                <Box sx={{
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    height: isExtraSmallScreen ? '50vh' : '80vh',
                }}>
                    <CircularProgress sx={{color: 'black'}}/>
                </Box>
            ) : (
            <Box sx={{mt:10, ml: 4, mr: 6}}>   
                
                <Box>
                    <Typography variant='h4'>
                        Issue details
                    </Typography>
                    <Paper elevation={2} sx={{p: 2, my: 2, backgroundColor: '#f6f6f6'}}>
                        <Typography variant={typoVariant}>
                            <b>Repository</b>: {issueData['repo'] + ' '}
                        </Typography>
                        <Typography variant={typoVariant}>
                            <b>Issue</b>: {issueData['issue_id']}
                        </Typography>
                        <Typography variant={typoVariant}>
                            <b>Title</b>: {issueData['issue_title'].replace(/`/g, '')} 
                        </Typography>
                        <Typography variant={typoVariant}>
                            <b>Merged pull request</b>: {issueData['merged_pr_id']}
                        </Typography>
                        <Typography variant={typoVariant}>
                            <b>Link to repo</b>: {' '}
                            <a href={'https://github.com/'+owner+'/'+repo} target="_blank" rel="noreferrer">
                                {'https://github.com/'+owner+'/'+repo}
                            </a>
                        </Typography>
                        <Typography variant={typoVariant}>
                            <b>Link to issue</b>: {' '}
                            <a href={issue_url} target="_blank" rel="noreferrer">
                                {issue_url}
                            </a>
                        </Typography>
                    </Paper>
                    <Divider sx= {{my: 4}}/>
                </Box>
                
                <Box>
                    <Typography variant='h4' sx={{mb: 2}}>
                        Summary of changes
                    </Typography>
                    <b>{issueData['commit_details']['files_changed']} files </b> 
                    changed on pull request that closed issue.
                    <TableContainer component={Paper} sx={{mt: 2}}>
                        <Table sx={{minWidth: 650}} size="small" aria-label="a dense table">
                            <TableHead sx={{backgroundColor: 'black'}}>
                                <TableRow>
                                    <TableCell sx={{fontWeight: 'bold', color: 'white'}}>File</TableCell>
                                    <TableCell align="center" sx={{fontWeight: 'bold', color: 'white'}}>
                                        Type of change
                                    </TableCell>
                                    <TableCell align="center" sx={{fontWeight: 'bold', color: 'white'}}>
                                        Changes
                                    </TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {issueData['commit_details']['file_details']
                                .sort((a, b) => b['changes'] - a['changes'])
                                .map((file) => (
                                    <TableRow key={file['filename']}>
                                        <TableCell component="th" scope="row">
                                            {file['filename']}
                                        </TableCell>
                                        <TableCell align="center">
                                            {file['status']}
                                        </TableCell>
                                        <TableCell align="center">
                                            {file['changes']}
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </TableContainer>
                    <Divider sx= {{my: 4}}/>
                </Box>

                <Box>
                    <Typography variant='h4' sx={{mb: 2}}>
                        Code changes
                    </Typography>
                    {issueData['commit_details']['file_details']
                    .sort((a, b) => b['changes'] - a['changes'])
                    .map((file) => (
                        <Paper key={file['filename']} elevation={2} sx={{ my: 2 }}>
                            <Typography variant={typoVariant} sx={{mb: 2, px: 2, py: 1, backgroundColor: '#f6f6f6'}}>
                                <b>File: </b>{file['filename']}
                            </Typography>
                            <Grid container sx={{ px: 2 }} spacing={2}>
                                <Grid item xs={12} sm={4}>
                                    <Paper elevation={2} sx={{p: 1, mb: 2, backgroundColor: '#f6f6f6'}}>
                                        <Markdown>
                                            {file['patch_explains']}
                                        </Markdown>
                                    </Paper>
                                </Grid>

                                <Grid item xs={12} sm={8}>
                                    <Paper 
                                    sx={{ 
                                        overflowX: 'auto', 
                                        whiteSpace: 'pre-wrap', 
                                        wordWrap: 'break-word',
                                        maxHeight: '100vh',
                                        p: 2,
                                        mb: 2,
                                    }}> 
                                        <CodeBlock 
                                        code={file['raw_code']} 
                                        highlights={file['processed_patch']}
                                        />
                                    </Paper>
                                </Grid>
                            </Grid> 
                        </Paper>
                    ))}
                    
                    <Divider sx= {{my: 4}}/>
                </Box>

            </Box>
            )}

        </Box>
    );
};

export default IssueDisplay;
