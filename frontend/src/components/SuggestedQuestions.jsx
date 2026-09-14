import {
  Box,
  Button,
  Typography,
} from '@mui/material'

const suggestions = [
  'What are the principles governing grant of bail?',
  'What factors are considered while granting bail?',
  'When can bail be cancelled?',
  'What is the difference between regular and anticipatory bail?',
]

function SuggestedQuestions({ onSelect }) {
  return (
    <Box sx={{ mt: 3 }}>
      <Typography
        sx={{
          fontSize: 13,
          fontWeight: 600,
          color: '#667085',
          mb: 1.2,
        }}
      >
        Suggested questions
      </Typography>

      <Box
        sx={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: 1,
        }}
      >
        {suggestions.map((question) => (
          <Button
            key={question}
            variant="outlined"
            onClick={() => onSelect(question)}
            sx={{
              textTransform: 'none',
              borderRadius: 5,
              borderColor: '#D9DEEA',
              color: '#475467',
              fontSize: 12.5,
              px: 1.8,
              py: 0.8,
              backgroundColor: '#FFFFFF',

              '&:hover': {
                borderColor: '#3155D9',
                color: '#3155D9',
                backgroundColor: '#F8F9FF',
              },
            }}
          >
            {question}
          </Button>
        ))}
      </Box>
    </Box>
  )
}

export default SuggestedQuestions