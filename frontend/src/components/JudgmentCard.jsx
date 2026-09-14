import {
  Box,
  Button,
  Paper,
  Typography,
} from '@mui/material'

import CalendarTodayOutlinedIcon from '@mui/icons-material/CalendarTodayOutlined'
import ArrowForwardRoundedIcon from '@mui/icons-material/ArrowForwardRounded'
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined'

function JudgmentCard({ judgment, onOpen }) {
  return (
    <Paper
      elevation={0}
      sx={{
        p: 3,
        border: '1px solid #E3E6ED',
        borderRadius: 3,
        backgroundColor: '#FFFFFF',
        transition: 'all 0.2s ease',

        '&:hover': {
          borderColor: '#C9D2F5',
          boxShadow:
            '0 10px 30px rgba(31, 45, 70, 0.07)',
          transform: 'translateY(-2px)',
        },
      }}
    >
      {/* Top section */}

      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          gap: 3,
        }}
      >
        <Box>
          <Typography
            component="h2"
            sx={{
              fontSize: 20,
              fontWeight: 650,
              color: '#172033',
              mb: 1.5,
            }}
          >
            {judgment.caseName}
          </Typography>

          {/* Metadata */}

          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 2,
              flexWrap: 'wrap',
            }}
          >
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 0.7,
              }}
            >
              <CalendarTodayOutlinedIcon
                sx={{
                  fontSize: 15,
                  color: '#7B8497',
                }}
              />

              <Typography
                sx={{
                  fontSize: 13,
                  color: '#667085',
                }}
              >
                {judgment.date}
              </Typography>
            </Box>

            <Typography
              sx={{
                fontSize: 13,
                color: '#667085',
              }}
            >
              {judgment.citation}
            </Typography>
          </Box>
        </Box>

        {/* Document icon */}

        <Box
          sx={{
            width: 42,
            height: 42,
            minWidth: 42,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderRadius: 2,
            backgroundColor: '#EEF2FF',
            color: '#3155D9',
          }}
        >
          <DescriptionOutlinedIcon />
        </Box>
      </Box>

      {/* Snippet */}

      <Typography
        sx={{
          mt: 2.5,
          fontSize: 14,
          lineHeight: 1.7,
          color: '#667085',
          maxWidth: 850,
        }}
      >
        {judgment.snippet}
      </Typography>

      {/* Action */}

      <Box
        sx={{
          display: 'flex',
          justifyContent: 'flex-end',
          mt: 3,
        }}
      >
        <Button
          variant="contained"
          endIcon={<ArrowForwardRoundedIcon />}
          onClick={() => onOpen(judgment)}
          sx={{
            textTransform: 'none',
            borderRadius: 2,
            boxShadow: 'none',
            fontWeight: 600,
          }}
        >
          Open Judgment
        </Button>
      </Box>
    </Paper>
  )
}

export default JudgmentCard