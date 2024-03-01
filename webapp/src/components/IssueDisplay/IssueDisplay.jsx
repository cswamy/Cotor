import { React, useState, useEffect } from 'react';

// Import mui components
import {
  Box,
  Typography,
  Divider,
} from '@mui/material';

// Import networking and dB
import { useLocation } from 'react-router-dom';
import { supabase } from '../../supabaseClient';
import axios from 'axios';

// Import custom components
import HeaderMenu from '../HeaderMenu/HeaderMenu';

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

    return (
        <Box>
            <Box>
                <HeaderMenu page='issue'/>
            </Box>

            <Box sx={{mt:10, ml: 4, mr: 6}}>
                <Typography variant='subtitle1'>
                    <b>Repository</b>: {issueData['repo'] + ' '}
                </Typography>
                <Typography variant='subtitle1'>
                    <b>Issue</b>: {issueData['issue_id']}
                </Typography>
                <Typography variant='subtitle1'>
                    <b>Title</b>: {issueData['issue_title'].replace(/`/g, '')}
                </Typography>
                <Typography variant='subtitle1'>
                    <b>Merged PR</b>: {issueData['merged_pr_id']}
                </Typography>
                <Divider sx= {{mt:1}}/>
            </Box>
        </Box>
    );
};

export default IssueDisplay;
