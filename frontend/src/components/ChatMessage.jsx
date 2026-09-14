import {
  Box,
  Paper,
  Typography,
} from '@mui/material'

import SmartToyOutlinedIcon from '@mui/icons-material/SmartToyOutlined'
import PersonOutlineOutlinedIcon from '@mui/icons-material/PersonOutlineOutlined'

import ReactMarkdown from 'react-markdown'

function ChatMessage({ type, children }) {
  const isUser = type === 'user'

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isUser
          ? 'flex-end'
          : 'flex-start',
        mb: 3,
      }}
    >
      <Box
        sx={{
          display: 'flex',
          flexDirection: isUser
            ? 'row-reverse'
            : 'row',
          alignItems: 'flex-start',
          gap: 1.5,
          width: '100%',
        }}
      >
        {/* Avatar */}

        <Box
          sx={{
            width: 38,
            height: 38,
            minWidth: 38,
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: isUser
              ? '#3155D9'
              : '#EEF2FF',
            color: isUser
              ? '#FFFFFF'
              : '#3155D9',
          }}
        >
          {isUser ? (
            <PersonOutlineOutlinedIcon />
          ) : (
            <SmartToyOutlinedIcon />
          )}
        </Box>

        {/* Message */}

        <Paper
          elevation={0}
          sx={{
            px: 3,
            py: 2.5,
            borderRadius: 3,
            maxWidth: isUser
              ? '80%'
              : 'calc(100% - 55px)',

            backgroundColor: isUser
              ? '#3155D9'
              : '#FFFFFF',

            color: isUser
              ? '#FFFFFF'
              : '#172033',

            border: isUser
              ? 'none'
              : '1px solid #E3E6ED',

            boxShadow: isUser
              ? '0 6px 18px rgba(49,85,217,0.16)'
              : '0 5px 20px rgba(31,45,70,0.04)',
          }}
        >

          {!isUser && (
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                mb: 2,
              }}
            >
              <Typography
                sx={{
                  fontSize: 12,
                  fontWeight: 700,
                  color: '#3155D9',
                  letterSpacing: 0.6,
                }}
              >
                LEGAL MIND AI
              </Typography>

              <Box
                sx={{
                  width: 6,
                  height: 6,
                  borderRadius: '50%',
                  backgroundColor: '#3155D9',
                }}
              />
            </Box>
          )}

          {isUser ? (
            <Typography
              sx={{
                fontSize: 15,
                lineHeight: 1.6,
                color: '#FFFFFF',
              }}
            >
              {children}
            </Typography>
          ) : (
            <Box
              sx={{
                color: '#344054',

                '& p': {
                  marginTop: 0,
                  marginBottom: 2,
                  fontSize: 15,
                  lineHeight: 1.8,
                },

                '& p:last-child': {
                  marginBottom: 0,
                },

                '& strong': {
                  color: '#172033',
                  fontWeight: 700,
                },

                '& ol': {
                  paddingLeft: 3,
                  marginTop: 1,
                  marginBottom: 2,
                },

                '& ul': {
                  paddingLeft: 3,
                  marginTop: 1,
                  marginBottom: 2,
                },

                '& li': {
                  marginBottom: 1,
                  paddingLeft: 0.5,
                  fontSize: 15,
                  lineHeight: 1.75,
                },

                '& blockquote': {
                  margin: '20px 0',
                  padding: '14px 18px',
                  borderLeft:
                    '4px solid #3155D9',
                  backgroundColor: '#F7F8FC',
                  borderRadius: 1.5,
                  color: '#475467',
                },

                '& code': {
                  backgroundColor: '#F2F4F7',
                  padding: '2px 5px',
                  borderRadius: 1,
                  fontSize: 13,
                },
              }}
            >
              <ReactMarkdown>
                {children}
              </ReactMarkdown>
            </Box>
          )}
        </Paper>
      </Box>
    </Box>
  )
}

export default ChatMessage