import { React, useEffect } from 'react';

// Import networking and dB
import { useSearchParams } from 'react-router-dom';
import { supabase } from '../../supabaseClient';

const SharedIssueDisplay = () => {

    // Get link id from URL
    const [searchParams] = useSearchParams();
    const link_id = searchParams.get('id');

    // Get issue from dB
    useEffect(() => {
        const getIssue = async () => {
            const { data, error } = await supabase
                .from('Issues')
                .select('*')
                .eq('public_link_id', link_id);
            if (error) {
                console.log('Error getting issue:', error);
            } else {
                console.log('Issue:', data);
            }
        };
        getIssue();
    });

    return (
        <div>
        <h1>Shared Issue display</h1>
        </div>
    );
};

export default SharedIssueDisplay;
