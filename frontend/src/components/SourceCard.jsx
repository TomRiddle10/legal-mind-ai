import {
  Box,
  Button,
  Paper,
  Typography,
} from '@mui/material'

import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined'
import ArrowForwardRoundedIcon from '@mui/icons-material/ArrowForwardRounded'

function SourceCard({ source, onOpen }) {
  const score = Number(
    source.rerank_score || 0
  )

  return (
    <Paper
      elevation={0}
      sx={{
        p: 2,
        border: '1px solid #E3E6ED',
        borderRadius: 2.5,
        backgroundColor: '#FFFFFF',
        transition: '0.2s ease',

        '&:hover': {
          borderColor: '#BFCBF8',
          boxShadow:
            '0 6px 20px rgba(31,45,70,0.06)',
        },
      }}
    >
      <Box
        sx={{
          display: 'flex',
          gap: 1.5,
        }}
      >
        <Box
          sx={{
            width: 36,
            height: 36,
            minWidth: 36,
            borderRadius: 1.8,
            backgroundColor: '#EEF2FF',
            color: '#3155D9',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <DescriptionOutlinedIcon
            sx={{ fontSize: 19 }}
          />
        </Box>

        <Box
          sx={{
            flex: 1,
            minWidth: 0,
          }}
        >
          <Typography
            sx={{
              fontSize: 14,
              fontWeight: 650,
              lineHeight: 1.45,
              color: '#172033',
            }}
          >
            {source.case_name}
          </Typography>

          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              mt: 0.7,
            }}
          >
            <Box
              sx={{
                px: 1,
                py: 0.25,
                borderRadius: 5,
                backgroundColor: '#EEF2FF',
              }}
            >
              <Typography
                sx={{
                  fontSize: 11,
                  fontWeight: 600,
                  color: '#3155D9',
                }}
              >
                Source {source.source_number}
              </Typography>
            </Box>

            <Typography
              sx={{
                fontSize: 11,
                color: '#98A2B3',
              }}
            >
              Relevance {score.toFixed(2)}
            </Typography>
          </Box>
        </Box>
      </Box>

      <Button
        endIcon={
          <ArrowForwardRoundedIcon
            sx={{ fontSize: 16 }}
          />
        }
        onClick={() => onOpen?.(source)}
        sx={{
          mt: 1.2,
          ml: 5.2,
          p: 0,
          minWidth: 0,
          textTransform: 'none',
          fontSize: 12.5,
          fontWeight: 600,
          color: '#3155D9',

          '&:hover': {
            backgroundColor: 'transparent',
          },
        }}
      >
        View Judgment
      </Button>
    </Paper>
  )
}

export default SourceCard