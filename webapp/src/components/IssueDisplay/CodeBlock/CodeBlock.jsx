import { React } from 'react';

// Import mui components
import { Box, Typography } from '@mui/material';

const CodeBlock = (props) => {
    
    const lines = props.code.split('\n');
    return (
        <Box component="pre" sx={{ overflow: 'auto' }}>
          {lines.map((line, index) => {
            const lineNumber = index + 1;
            const isHighlighted = props.highlights.includes(lineNumber);
            return (
              <Typography
                variant="body2"
                component="span"
                key={index}
                sx={{
                  display: 'flex',
                  backgroundColor: isHighlighted ? '#effbfa' : 'transparent',
                  padding: '0 8px',
                  borderRadius: '4px',
                }}
              >
                <Box component="span" sx={{ width: '30px', textAlign: 'left', marginRight: '1em', color: 'grey' }}>
                  {lineNumber}
                </Box>
                <Box component="span">
                  {line}
                </Box>
              </Typography>
            );
          })}
        </Box>
      );
};

export default CodeBlock;