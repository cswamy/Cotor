import { React, useState, useEffect } from 'react';

// Import mui components
import {
  Box,
} from '@mui/material';

// Import networking and dB
import { useLocation } from 'react-router-dom';
import { supabase } from '../../supabaseClient';
// import { useAuth } from '../../context/AuthProvider';

// Import custom components
import HeaderMenu from '../HeaderMenu/HeaderMenu';

const IssueDisplay = () => {

    const [issueData, setIssueData] = useState({});
    const {owner, repo, issue} = useLocation().state;

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
                }
            }
        }

        getIssueFromDB();
    }, [owner, repo, issue]);

    return (
        <Box>
            <Box>
                <HeaderMenu page='issue'/>
            </Box>

            <Box>
                <p>{issueData['merged_pr_id']}</p>
            </Box>
        </Box>
    );
};

export default IssueDisplay;
