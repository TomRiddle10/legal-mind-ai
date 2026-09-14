import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import {
  Box,
  Button,
  CircularProgress,
  Container,
  Paper,
  TextField,
  Typography,
} from '@mui/material'

import SendRoundedIcon from '@mui/icons-material/SendRounded'
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined'
import ArrowForwardRoundedIcon from '@mui/icons-material/ArrowForwardRounded'

import Navbar from '../components/Navbar'
import { askLegalAI } from '../services/api'


function LegalChat() {

  const navigate = useNavigate()

  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [sources, setSources] = useState([])

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')


  const handleAsk = async () => {

    const trimmedQuestion = question.trim()

    if (!trimmedQuestion || loading) {
      return
    }

    setLoading(true)
    setError('')
    setAnswer('')
    setSources([])

    try {

      const data = await askLegalAI(
        trimmedQuestion
      )

      setAnswer(
        data.answer || 'No answer generated.'
      )

      setSources(
        data.sources || []
      )

    } catch (err) {

      setError(
        err.message ||
        'Something went wrong while contacting Legal Mind AI.'
      )

    } finally {

      setLoading(false)

    }
  }


  const handleKeyDown = (event) => {

    if (
      event.key === 'Enter' &&
      !event.shiftKey
    ) {

      event.preventDefault()

      handleAsk()
    }
  }


  const handleOpenJudgment = (source) => {

    navigate(
      `/judgment/${source.document_id}`
    )
  }


  return (
    <Box
      sx={{
        minHeight: '100vh',
        backgroundColor: '#F7F8FC',
      }}
    >

      <Navbar />

      <Container
        maxWidth="md"
        sx={{
          py: 6,
        }}
      >

        {/* =================================================
            HEADER
        ================================================= */}

        <Box
          sx={{
            textAlign: 'center',
            mb: 5,
          }}
        >

          <Typography
            sx={{
              fontSize: {
                xs: 32,
                md: 42,
              },
              fontWeight: 700,
              color: '#172033',
              mb: 1,
            }}
          >
            Ask Legal Mind AI
          </Typography>

          <Typography
            sx={{
              color: '#667085',
              fontSize: 16,
            }}
          >
            Ask questions about Indian court judgments
            and explore the cases supporting the answer.
          </Typography>

        </Box>


        {/* =================================================
            QUESTION BOX
        ================================================= */}

        <Paper
          elevation={0}
          sx={{
            p: 1.5,
            borderRadius: 3,
            border: '1px solid #DFE3EB',
            backgroundColor: '#FFFFFF',
            boxShadow:
              '0 10px 35px rgba(31,45,70,0.07)',
          }}
        >

          <TextField
            fullWidth
            multiline
            minRows={3}
            maxRows={7}
            value={question}
            onChange={(event) =>
              setQuestion(event.target.value)
            }
            onKeyDown={handleKeyDown}
            placeholder="Ask a legal question, for example: What are the principles governing grant of bail?"
            sx={{
              '& .MuiOutlinedInput-root': {
                border: 'none',
                '& fieldset': {
                  border: 'none',
                },
              },
            }}
          />

          <Box
            sx={{
              display: 'flex',
              justifyContent: 'flex-end',
              px: 1,
              pb: 1,
            }}
          >

            <Button
              variant="contained"
              onClick={handleAsk}
              disabled={
                !question.trim() ||
                loading
              }
              endIcon={
                loading
                  ? <CircularProgress
                      size={18}
                      color="inherit"
                    />
                  : <SendRoundedIcon />
              }
              sx={{
                px: 3,
                borderRadius: 2,
                textTransform: 'none',
                fontWeight: 600,
                boxShadow: 'none',
              }}
            >
              {loading
                ? 'Researching...'
                : 'Ask Legal AI'}
            </Button>

          </Box>

        </Paper>


        {/* =================================================
            ERROR
        ================================================= */}

        {error && (

          <Paper
            elevation={0}
            sx={{
              mt: 3,
              p: 2.5,
              borderRadius: 2,
              border: '1px solid #F1C5C5',
              backgroundColor: '#FFF7F7',
            }}
          >

            <Typography
              sx={{
                color: '#B42318',
                fontSize: 14,
              }}
            >
              {error}
            </Typography>

          </Paper>

        )}


        {/* =================================================
            ANSWER
        ================================================= */}

        {answer && (

          <Paper
            elevation={0}
            sx={{
              mt: 5,
              p: {
                xs: 3,
                md: 4,
              },
              borderRadius: 3,
              border: '1px solid #E3E6ED',
              backgroundColor: '#FFFFFF',
            }}
          >

            <Typography
              sx={{
                fontSize: 13,
                fontWeight: 700,
                letterSpacing: 0.8,
                color: '#3155D9',
                mb: 2,
              }}
            >
              LEGAL MIND AI
            </Typography>

            <Typography
              sx={{
                fontSize: 15,
                lineHeight: 1.8,
                color: '#344054',
                whiteSpace: 'pre-line',
              }}
            >
              {answer}
            </Typography>

          </Paper>

        )}


        {/* =================================================
            SOURCES
        ================================================= */}

        {sources.length > 0 && (

          <Box
            sx={{
              mt: 5,
            }}
          >

            <Typography
              sx={{
                fontSize: 22,
                fontWeight: 700,
                color: '#172033',
                mb: 1,
              }}
            >
              Related Judgments
            </Typography>

            <Typography
              sx={{
                color: '#667085',
                fontSize: 14,
                mb: 3,
              }}
            >
              These judgments were retrieved from the
              Legal Mind AI database and used as supporting
              context for the answer.
            </Typography>


            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                gap: 2,
              }}
            >

              {sources.map((source) => (

                <Paper
                  key={source.document_id}
                  elevation={0}
                  sx={{
                    p: 3,
                    borderRadius: 3,
                    border: '1px solid #E3E6ED',
                    backgroundColor: '#FFFFFF',
                    transition: '0.2s ease',

                    '&:hover': {
                      borderColor: '#C9D2F5',
                      boxShadow:
                        '0 8px 25px rgba(31,45,70,0.07)',
                    },
                  }}
                >

                  <Box
                    sx={{
                      display: 'flex',
                      gap: 2,
                    }}
                  >

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


                    <Box
                      sx={{
                        flex: 1,
                        minWidth: 0,
                      }}
                    >

                      <Typography
                        sx={{
                          fontWeight: 600,
                          fontSize: 16,
                          color: '#172033',
                          lineHeight: 1.5,
                        }}
                      >
                        {source.case_name}
                      </Typography>


                      <Typography
                        sx={{
                          mt: 0.8,
                          fontSize: 13,
                          color: '#667085',
                        }}
                      >
                        Relevance score:{' '}
                        {source.rerank_score
                          ? source.rerank_score.toFixed(2)
                          : 'N/A'}
                      </Typography>


                      <Button
                        onClick={() =>
                          handleOpenJudgment(source)
                        }
                        endIcon={
                          <ArrowForwardRoundedIcon />
                        }
                        sx={{
                          mt: 1.5,
                          px: 0,
                          textTransform: 'none',
                          fontWeight: 600,
                        }}
                      >
                        View Judgment
                      </Button>

                    </Box>

                  </Box>

                </Paper>

              ))}

            </Box>

          </Box>

        )}

      </Container>

    </Box>
  )
}

export default LegalChat