import { React } from 'react';

// Import mui components
import { Paper } from '@mui/material';

const DemoVideo = () => {
    
    const videoSrc = process.env.PUBLIC_URL + '/CotorVideoEdited.mp4';
    return (
        <Paper elevation={2}>
            <video width="100%" height="100%" autoPlay loop muted>
                <source src={videoSrc} type="video/mp4"/>
            </video>
        </Paper>
    );
}

export default DemoVideo;