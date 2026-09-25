import { useEffect, useRef, useState } from 'react'
import {
  useNavigate,
  useParams,
  useSearchParams,
} from 'react-router-dom'

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
import AddRoundedIcon from '@mui/icons-material/AddRounded'
import AutoAwesomeOutlinedIcon from '@mui/icons-material/AutoAwesomeOutlined'
import ArrowBackRoundedIcon from '@mui/icons-material/ArrowBackRounded'

import Navbar from '../components/Navbar'
import ChatMessage from '../components/ChatMessage'
import SourceCard from '../components/SourceCard'
import SuggestedQuestions from '../components/SuggestedQuestions'

// ============================================================
// API CONFIGURATION
// ============================================================

const API_URL =
  import.meta.env.VITE_API_BASE_URL ||
  'http://127.0.0.1:5000'

// ============================================================
// CHAT STORAGE
// ============================================================

const getChatStorageKey = (documentId) => {
  if (documentId) {
    return `legalMindAI:judgmentChat:${documentId}`
  }

  return 'legalMindAI:generalChat'
}

// ============================================================
// GET SAVED CHAT
// ============================================================

const getSavedChat = (storageKey) => {
  try {
    const saved = localStorage.getItem(storageKey)

    if (!saved) {
      return null
    }

    return JSON.parse(saved)
  } catch (error) {
    console.error(
      'Unable to restore chat state:',
      error
    )

    return null
  }
}

// ============================================================
// SAVE CHAT
// ============================================================

const saveChat = (
  storageKey,
  chatState
) => {
  try {
    localStorage.setItem(
      storageKey,
      JSON.stringify({
        question: chatState.question || '',
        answer: chatState.answer || '',
        sources: chatState.sources || [],
        error: chatState.error || '',
      })
    )
  } catch (error) {
    console.error(
      'Unable to save chat state:',
      error
    )
  }
}

// ============================================================
// CHAT COMPONENT
// ============================================================

function Chat() {
  const navigate = useNavigate()

  const { documentId } = useParams()

  // ==========================================================
  // READ QUESTION FROM URL
  // ==========================================================

  const [searchParams] = useSearchParams()

  const queryFromUrl =
    searchParams.get('q')?.trim() || ''

  // ==========================================================
  // CHAT MODE
  // ==========================================================

  const isJudgmentChat =
    Boolean(documentId)

  // ==========================================================
  // STORAGE KEY
  // ==========================================================

  const storageKey =
    getChatStorageKey(documentId)

  const savedChat =
    getSavedChat(storageKey)

  // ==========================================================
  // STATE
  // ==========================================================

  const [question, setQuestion] =
    useState(
      queryFromUrl ||
      savedChat?.question ||
      (
        isJudgmentChat
          ? ''
          : 'What are the principles governing grant of bail?'
      )
    )

  const [submittedQuestion, setSubmittedQuestion] =
    useState(
      queryFromUrl ||
      (
        savedChat?.answer
          ? savedChat?.question || ''
          : ''
      )
    )

  const [answer, setAnswer] =
    useState(
      savedChat?.answer ?? ''
    )

  const [sources, setSources] =
    useState(
      savedChat?.sources ?? []
    )

  const [loading, setLoading] =
    useState(false)

  const [error, setError] =
    useState(
      savedChat?.error ?? ''
    )

  // ==========================================================
  // STORAGE REFS
  // ==========================================================

  const previousStorageKey =
    useRef(storageKey)

  const skipSave =
    useRef(false)

  // ==========================================================
  // URL QUESTION REF
  // ==========================================================

  const urlQuestionHandled =
    useRef(false)

  // ==========================================================
  // RESTORE CHAT WHEN CHAT KEY CHANGES
  // ==========================================================

  useEffect(() => {
    if (
      previousStorageKey.current ===
      storageKey
    ) {
      return
    }

    previousStorageKey.current =
      storageKey

    const saved =
      getSavedChat(storageKey)

    skipSave.current = true

    if (saved) {
      setQuestion(
        saved.question ?? ''
      )

      setSubmittedQuestion(
        saved.answer
          ? saved.question ?? ''
          : ''
      )

      setAnswer(
        saved.answer ?? ''
      )

      setSources(
        saved.sources ?? []
      )

      setError(
        saved.error ?? ''
      )
    } else {
      const defaultQuestion =
        isJudgmentChat
          ? ''
          : 'What are the principles governing grant of bail?'

      setQuestion(defaultQuestion)

      setSubmittedQuestion('')

      setAnswer('')

      setSources([])

      setError('')
    }
  }, [
    storageKey,
    isJudgmentChat,
  ])

  // ==========================================================
  // SAVE CHAT STATE
  // ==========================================================

  useEffect(() => {
    if (skipSave.current) {
      skipSave.current = false
      return
    }

    if (loading) {
      return
    }

    saveChat(
      storageKey,
      {
        question,
        answer,
        sources,
        error,
      }
    )
  }, [
    storageKey,
    question,
    answer,
    sources,
    error,
    loading,
  ])

  // ==========================================================
  // ASK QUESTION
  // ==========================================================

  const askQuestion = async (
    selectedQuestion = question
  ) => {
    const trimmedQuestion =
      (selectedQuestion || '').trim()

    if (
      !trimmedQuestion ||
      loading
    ) {
      return
    }

    // --------------------------------------------------------
    // SHOW QUESTION IMMEDIATELY
    // --------------------------------------------------------

    setQuestion(
      trimmedQuestion
    )

    setSubmittedQuestion(
      trimmedQuestion
    )

    setAnswer('')

    setSources([])

    setError('')

    setLoading(true)

    try {
      // ======================================================
      // GENERAL CHAT
      // ======================================================

      if (!isJudgmentChat) {
        const response =
          await fetch(
            `${API_URL}/api/chat`,
            {
              method: 'POST',

              headers: {
                'Content-Type':
                  'application/json',
              },

              body: JSON.stringify({
                question:
                  trimmedQuestion,
              }),
            }
          )

        const data =
          await response.json()

        if (!response.ok) {
          throw new Error(
            data.message ||
            'Unable to generate an answer.'
          )
        }

        if (
          data.status !==
          'success'
        ) {
          throw new Error(
            data.message ||
            'Unable to generate an answer.'
          )
        }

        setAnswer(
          data.answer ||
          'No answer generated.'
        )

        setSources(
          data.sources ||
          []
        )
      }

      // ======================================================
      // JUDGMENT-SPECIFIC CHAT
      // ======================================================

      else {
        const response =
          await fetch(
            `${API_URL}/api/judgments/${encodeURIComponent(
              documentId
            )}/ask`,
            {
              method: 'POST',

              headers: {
                'Content-Type':
                  'application/json',
              },

              body: JSON.stringify({
                question:
                  trimmedQuestion,
              }),
            }
          )

        const data =
          await response.json()

        if (!response.ok) {
          throw new Error(
            data.message ||
            'Unable to generate an answer.'
          )
        }

        if (
          data.status !==
          'success'
        ) {
          throw new Error(
            data.message ||
            'Unable to generate an answer.'
          )
        }

        setAnswer(
          data.answer ||
          'No answer generated.'
        )

        setSources(
          data.sources ||
          []
        )
      }
    } catch (err) {
      console.error(
        'Chat error:',
        err
      )

      setError(
        err.message ||
        'Unable to connect to Legal Mind AI.'
      )
    } finally {
      setLoading(false)
    }
  }

  // ==========================================================
  // PROCESS QUESTION FROM HOME PAGE
  // ==========================================================

  useEffect(() => {
    if (
      !queryFromUrl ||
      urlQuestionHandled.current
    ) {
      return
    }

    urlQuestionHandled.current =
      true

    const processUrlQuestion =
      async () => {
        console.log(
          'AUTO QUESTION FROM HOME:',
          queryFromUrl
        )

        // Display immediately
        setQuestion(
          queryFromUrl
        )

        setSubmittedQuestion(
          queryFromUrl
        )

        // Automatically call backend
        await askQuestion(
          queryFromUrl
        )

        // Remove ?q= only after request finishes
        navigate(
          '/chat',
          {
            replace: true,
          }
        )
      }

    processUrlQuestion()
  }, [
    queryFromUrl,
    navigate,
  ])

  // ==========================================================
  // SUBMIT
  // ==========================================================

  const handleSubmit = (
    event
  ) => {
    event.preventDefault()

    askQuestion()
  }

  // ==========================================================
  // SUGGESTION
  // ==========================================================

  const handleSuggestion = (
    value
  ) => {
    setQuestion(value)

    askQuestion(value)
  }

  // ==========================================================
  // NEW QUESTION
  // ==========================================================

  const handleNewQuestion = () => {
    setQuestion('')

    setSubmittedQuestion('')

    setAnswer('')

    setSources([])

    setError('')

    saveChat(
      storageKey,
      {
        question: '',
        answer: '',
        sources: [],
        error: '',
      }
    )
  }

  // ==========================================================
  // OPEN SOURCE
  // ==========================================================

  const handleOpenSource = (
    source
  ) => {
    if (
      !source?.document_id
    ) {
      return
    }

    saveChat(
      storageKey,
      {
        question,
        answer,
        sources,
        error,
      }
    )

    navigate(
      `/judgment/${encodeURIComponent(
        source.document_id
      )}`
    )
  }

  // ==========================================================
  // BACK TO JUDGMENT
  // ==========================================================

  const handleBackToJudgment = () => {
    if (documentId) {
      navigate(
        `/judgment/${encodeURIComponent(
          documentId
        )}`
      )

      return
    }

    navigate('/search')
  }

  // ==========================================================
  // RETURN UI
  // ==========================================================

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background:
          'linear-gradient(180deg, #F8FAFF 0%, #F7F8FC 45%, #FFFFFF 100%)',
      }}
    >
      <Navbar />

      <Container
        maxWidth="xl"
        sx={{
          py: {
            xs: 3,
            md: 5,
          },
          pb: 8,
        }}
      >
        {/* ==================================================
            BACK BUTTON
        ================================================== */}

        {isJudgmentChat && (
          <Box
            sx={{
              maxWidth: 1100,
              mx: 'auto',
              mb: 2,
            }}
          >
            <Button
              startIcon={
                <ArrowBackRoundedIcon />
              }
              onClick={
                handleBackToJudgment
              }
              sx={{
                textTransform: 'none',
                color: '#667085',
                fontWeight: 600,
                borderRadius: 2,
                px: 1.5,

                '&:hover': {
                  backgroundColor:
                    '#EEF2FF',
                  color: '#3155D9',
                },
              }}
            >
              Back to Judgment
            </Button>
          </Box>
        )}

        {/* ==================================================
            HEADER
        ================================================== */}

        {!submittedQuestion && (
          <Box
            sx={{
              textAlign: 'center',
              maxWidth: 850,
              mx: 'auto',
              mt: {
                xs: 2,
                md: 4,
              },
              mb: 4,
            }}
          >
            <Box
              sx={{
                width: 58,
                height: 58,
                mx: 'auto',
                mb: 2,
                borderRadius: 3,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background:
                  'linear-gradient(135deg, #EEF2FF, #E0E7FF)',
                color: '#3155D9',
                boxShadow:
                  '0 8px 24px rgba(49,85,217,0.12)',
              }}
            >
              <AutoAwesomeOutlinedIcon
                sx={{
                  fontSize: 27,
                }}
              />
            </Box>

            <Typography
              component="h1"
              sx={{
                fontSize: {
                  xs: 32,
                  md: 46,
                },
                lineHeight: 1.15,
                fontWeight: 750,
                letterSpacing: '-1.5px',
                color: '#172033',
              }}
            >
              {isJudgmentChat
                ? 'Ask About This Judgment'
                : 'Ask Legal Mind AI'}
            </Typography>

            <Typography
              sx={{
                mt: 1.5,
                fontSize: 16,
                lineHeight: 1.7,
                color: '#667085',
                maxWidth: 720,
                mx: 'auto',
              }}
            >
              {isJudgmentChat
                ? 'Ask questions about this specific judgment using its relevant legal context.'
                : 'Ask questions about Indian court judgments and explore the cases supporting the answer.'}
            </Typography>
          </Box>
        )}

        {/* ==================================================
            JUDGMENT INFORMATION
        ================================================== */}

        {isJudgmentChat && (
          <Paper
            elevation={0}
            sx={{
              mt: submittedQuestion ? 1 : 3,
              mb: 3,
              maxWidth: 1100,
              mx: 'auto',
              px: 2.5,
              py: 1.7,
              borderRadius: 3,
              border:
                '1px solid #D9E0FA',
              background:
                'linear-gradient(135deg, #F7F9FF, #FFFFFF)',
            }}
          >
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1.2,
              }}
            >
              <AutoAwesomeOutlinedIcon
                sx={{
                  fontSize: 20,
                  color: '#3155D9',
                }}
              />

              <Typography
                sx={{
                  fontSize: 13,
                  color: '#344054',
                  lineHeight: 1.6,
                }}
              >
                <strong>
                  Judgment-specific mode:
                </strong>{' '}
                Legal Mind AI will retrieve
                information only from this
                judgment.
              </Typography>
            </Box>
          </Paper>
        )}

        {/* ==================================================
            CHAT AREA
        ================================================== */}

        {submittedQuestion && (
          <Box
            sx={{
              maxWidth: 1100,
              mx: 'auto',
              mb: 4,
            }}
          >
            {/* USER MESSAGE */}

            <Box
              sx={{
                display: 'flex',
                justifyContent: 'flex-end',
                mb: 3,
              }}
            >
              <Paper
                elevation={0}
                sx={{
                  maxWidth: {
                    xs: '92%',
                    md: '78%',
                  },
                  px: 2.5,
                  py: 1.8,
                  borderRadius:
                    '18px 18px 4px 18px',
                  background:
                    'linear-gradient(135deg, #3155D9, #4267E8)',
                  color: '#FFFFFF',
                  boxShadow:
                    '0 8px 24px rgba(49,85,217,0.16)',
                }}
              >
                <Typography
                  sx={{
                    fontSize: 15,
                    lineHeight: 1.65,
                    whiteSpace:
                      'pre-wrap',
                    wordBreak:
                      'break-word',
                  }}
                >
                  {submittedQuestion}
                </Typography>
              </Paper>
            </Box>

            {/* AI RESPONSE / LOADING */}

            {(loading || answer || error) && (
              <Box
                sx={{
                  display: 'flex',
                  justifyContent:
                    'flex-start',
                }}
              >
                <Paper
                  elevation={0}
                  sx={{
                    width: '100%',
                    px: {
                      xs: 2,
                      md: 3,
                    },
                    py: {
                      xs: 2,
                      md: 2.5,
                    },
                    borderRadius:
                      '4px 18px 18px 18px',
                    border:
                      '1px solid #E2E6EF',
                    backgroundColor:
                      '#FFFFFF',
                    boxShadow:
                      '0 8px 30px rgba(31,45,70,0.06)',
                  }}
                >
                  {/* AI HEADER */}

                  <Box
                    sx={{
                      display: 'flex',
                      alignItems:
                        'center',
                      gap: 1.2,
                      mb: 2,
                    }}
                  >
                    <Box
                      sx={{
                        width: 38,
                        height: 38,
                        borderRadius: 2,
                        display:
                          'flex',
                        alignItems:
                          'center',
                        justifyContent:
                          'center',
                        background:
                          '#EEF2FF',
                        color:
                          '#3155D9',
                      }}
                    >
                      <AutoAwesomeOutlinedIcon
                        sx={{
                          fontSize: 20,
                        }}
                      />
                    </Box>

                    <Box>
                      <Typography
                        sx={{
                          fontWeight: 700,
                          fontSize: 14,
                          color:
                            '#172033',
                        }}
                      >
                        Legal Mind AI
                      </Typography>

                      <Typography
                        sx={{
                          fontSize: 12,
                          color:
                            '#98A2B3',
                        }}
                      >
                        AI Legal Research Assistant
                      </Typography>
                    </Box>
                  </Box>

                  {/* LOADING */}

                  {loading && (
                    <Box
                      sx={{
                        display:
                          'flex',
                        alignItems:
                          'center',
                        gap: 1.5,
                        py: 2,
                      }}
                    >
                      <CircularProgress
                        size={22}
                        thickness={4}
                      />

                      <Box>
                        <Typography
                          sx={{
                            fontWeight: 600,
                            color:
                              '#172033',
                            fontSize: 14,
                          }}
                        >
                          {isJudgmentChat
                            ? 'Analyzing this judgment...'
                            : 'Researching your question...'}
                        </Typography>

                        <Typography
                          sx={{
                            mt: 0.3,
                            fontSize: 12,
                            color:
                              '#667085',
                          }}
                        >
                          {isJudgmentChat
                            ? 'Retrieving relevant passages from the judgment.'
                            : 'Searching and ranking relevant judgments.'}
                        </Typography>
                      </Box>
                    </Box>
                  )}

                  {/* ERROR */}

                  {error && !loading && (
                    <Box
                      sx={{
                        p: 2,
                        borderRadius: 2,
                        backgroundColor:
                          '#FFF7F7',
                        border:
                          '1px solid #F0D0D0',
                      }}
                    >
                      <Typography
                        sx={{
                          fontWeight: 700,
                          color:
                            '#B42318',
                          mb: 0.5,
                        }}
                      >
                        Unable to generate answer
                      </Typography>

                      <Typography
                        sx={{
                          fontSize: 14,
                          lineHeight: 1.6,
                          color:
                            '#667085',
                          mb: 2,
                        }}
                      >
                        {error}
                      </Typography>

                      <Button
                        variant="outlined"
                        onClick={() =>
                          askQuestion()
                        }
                        sx={{
                          textTransform:
                            'none',
                          borderRadius: 2,
                        }}
                      >
                        Try Again
                      </Button>
                    </Box>
                  )}

                  {/* ANSWER */}

                  {answer && !loading && (
                    <>
                      <Box
                        sx={{
                          '& p': {
                            marginTop: 0,
                            marginBottom: 1.5,
                          },
                        }}
                      >
                        <ChatMessage type="assistant">
                          {answer}
                        </ChatMessage>
                      </Box>

                      <Box
                        sx={{
                          mt: 2.5,
                          pt: 2,
                          borderTop:
                            '1px solid #EAECF0',
                        }}
                      >
                        <Typography
                          sx={{
                            fontSize: 12,
                            lineHeight: 1.7,
                            color:
                              '#98A2B3',
                          }}
                        >
                          {isJudgmentChat
                            ? 'Legal Mind AI provides answers based only on the retrieved portions of this judgment. Verify important legal information against the original judgment and applicable law.'
                            : 'Legal Mind AI provides answers based on retrieved judgments. Verify important legal information against the original judgment and applicable law.'}
                        </Typography>
                      </Box>
                    </>
                  )}
                </Paper>
              </Box>
            )}
          </Box>
        )}

        {/* ==================================================
            QUESTION INPUT
        ================================================== */}

        <Paper
          component="form"
          onSubmit={handleSubmit}
          elevation={0}
          sx={{
            mt: submittedQuestion ? 2 : 1,
            maxWidth: 1100,
            mx: 'auto',
            p: {
              xs: 1.5,
              md: 2,
            },
            borderRadius: 4,
            border:
              '1px solid #D9DEE8',
            backgroundColor:
              '#FFFFFF',
            boxShadow:
              '0 12px 40px rgba(31,45,70,0.08)',
            position: 'relative',
          }}
        >
          <TextField
            fullWidth
            multiline
            minRows={2}
            maxRows={6}
            value={question}
            onChange={(event) =>
              setQuestion(
                event.target.value
              )
            }
            onKeyDown={(event) => {
              if (
                event.key === 'Enter' &&
                !event.shiftKey
              ) {
                event.preventDefault()

                handleSubmit(event)
              }
            }}
            placeholder={
              isJudgmentChat
                ? 'Ask a question about this judgment...'
                : 'Ask a question about Indian law and judgments...'
            }
            variant="standard"
            slotProps={{
              input: {
                disableUnderline: true,
              },
            }}
            sx={{
              px: 1,
              '& textarea': {
                fontSize: 15,
                lineHeight: 1.6,
                color: '#172033',
              },

              '& textarea::placeholder': {
                color: '#98A2B3',
                opacity: 1,
              },
            }}
          />

          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent:
                'space-between',
              mt: 1,
              px: 0.5,
            }}
          >
            <Typography
              sx={{
                display: {
                  xs: 'none',
                  sm: 'block',
                },
                fontSize: 11,
                color: '#98A2B3',
              }}
            >
              Press Enter to ask · Shift + Enter for new line
            </Typography>

            <Button
              type="submit"
              variant="contained"
              disabled={
                loading ||
                !question.trim()
              }
              endIcon={
                loading ? (
                  <CircularProgress
                    size={17}
                    color="inherit"
                  />
                ) : (
                  <SendRoundedIcon />
                )
              }
              sx={{
                ml: 'auto',
                px: 2.5,
                py: 1.1,
                borderRadius: 2.5,
                textTransform:
                  'none',
                fontWeight: 700,
                boxShadow:
                  '0 6px 16px rgba(49,85,217,0.18)',

                '&:hover': {
                  boxShadow:
                    '0 8px 20px rgba(49,85,217,0.24)',
                },
              }}
            >
              {loading
                ? 'Researching...'
                : 'Ask Legal AI'}
            </Button>
          </Box>
        </Paper>

        {/* ==================================================
            SUGGESTIONS
        ================================================== */}

        {!submittedQuestion &&
          !loading &&
          !error && (
            <Box
              sx={{
                maxWidth: 1100,
                mx: 'auto',
                mt: 3,
              }}
            >
              <SuggestedQuestions
                onSelect={
                  handleSuggestion
                }
              />
            </Box>
          )}

        {/* ==================================================
            SOURCES
        ================================================== */}

        {answer &&
          sources.length > 0 &&
          !loading && (
            <Box
              sx={{
                maxWidth: 1100,
                mx: 'auto',
                mt: 4,
              }}
            >
              <Paper
                elevation={0}
                sx={{
                  p: {
                    xs: 2,
                    md: 2.5,
                  },
                  borderRadius: 3,
                  border:
                    '1px solid #E2E6EF',
                  backgroundColor:
                    '#FFFFFF',
                }}
              >
                <Box
                  sx={{
                    mb: 2,
                  }}
                >
                  <Typography
                    sx={{
                      fontSize: 19,
                      fontWeight: 750,
                      color:
                        '#172033',
                    }}
                  >
                    {isJudgmentChat
                      ? 'Retrieved Passages'
                      : 'Related Judgments'}
                  </Typography>

                  <Typography
                    sx={{
                      mt: 0.5,
                      fontSize: 13,
                      lineHeight: 1.6,
                      color:
                        '#667085',
                    }}
                  >
                    {isJudgmentChat
                      ? 'Relevant passages retrieved from this judgment and used as supporting context.'
                      : 'Cases retrieved from the Legal Mind AI database and used as supporting context.'}
                  </Typography>
                </Box>

                <Box
                  sx={{
                    display:
                      'flex',
                    flexDirection:
                      'column',
                    gap: 1.5,
                  }}
                >
                  {sources.map(
                    (
                      source,
                      index
                    ) => (
                      <SourceCard
                        key={
                          source.chunk_id ||
                          source.document_id ||
                          index
                        }
                        source={
                          source
                        }
                        onOpen={
                          handleOpenSource
                        }
                      />
                    )
                  )}
                </Box>
              </Paper>
            </Box>
          )}

        {/* ==================================================
            NEW QUESTION
        ================================================== */}

        {(answer || error) &&
          !loading && (
            <Box
              sx={{
                display:
                  'flex',
                justifyContent:
                  'center',
                mt: 4,
              }}
            >
              <Button
                variant="outlined"
                startIcon={
                  <AddRoundedIcon />
                }
                onClick={
                  handleNewQuestion
                }
                sx={{
                  textTransform:
                    'none',
                  borderRadius: 2.5,
                  px: 2.5,
                  py: 1,
                  borderColor:
                    '#D0D5DD',
                  color:
                    '#344054',
                  fontWeight: 600,

                  '&:hover': {
                    borderColor:
                      '#3155D9',
                    color:
                      '#3155D9',
                    backgroundColor:
                      '#F7F9FF',
                  },
                }}
              >
                Ask another question
              </Button>
            </Box>
          )}
      </Container>
    </Box>
  )
}

export default Chat