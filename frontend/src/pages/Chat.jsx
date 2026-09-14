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

    const saved =
      localStorage.getItem(storageKey)

    if (!saved) {
      return null
    }

    return JSON.parse(saved)

  }
  catch (error) {

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
        question:
          chatState.question || '',

        answer:
          chatState.answer || '',

        sources:
          chatState.sources || [],

        error:
          chatState.error || '',
      })
    )

  }
  catch (error) {

    console.error(
      'Unable to save chat state:',
      error
    )

  }

}

// ============================================================
// CHAT
// ============================================================

function Chat() {

  const navigate = useNavigate()

  const { documentId } = useParams()

  // ==========================================================
  // READ QUESTION FROM URL
  // ==========================================================

  const [searchParams] =
    useSearchParams()

  const queryFromUrl =
    searchParams.get('q')?.trim() || ''

  // ==========================================================
  // CHAT MODE
  // ==========================================================

  /*
   * If documentId exists, this is the Judgment Chatbot.
   *
   * /chat
   *              -> General chatbot
   *
   * /chat/judgment/:documentId
   *              -> Judgment-specific chatbot
   */

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

  /*
   * Prevents the same ?q= question from being automatically
   * submitted more than once during the current mount.
   */

  const urlQuestionHandled =
    useRef(false)

  // ==========================================================
  // RESTORE CHAT WHEN CHAT KEY CHANGES
  // ==========================================================

  useEffect(() => {

    /*
     * This handles cases where React keeps the Chat component
     * mounted while documentId changes.
     */

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

      setAnswer(
        saved.answer ?? ''
      )

      setSources(
        saved.sources ?? []
      )

      setError(
        saved.error ?? ''
      )

    }
    else {

      setQuestion(
        isJudgmentChat
          ? ''
          : 'What are the principles governing grant of bail?'
      )

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

    /*
     * Prevent an old state from being written into a newly
     * selected chat immediately after restoring it.
     */

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
      selectedQuestion.trim()

    if (
      !trimmedQuestion ||
      loading
    ) {
      return
    }

    setQuestion(
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
            `${API_URL}/api/judgments/${encodeURIComponent(documentId)}/ask`,
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

    }
    catch (err) {

      console.error(
        'Chat error:',
        err
      )

      setError(
        err.message ||
          'Unable to connect to Legal Mind AI.'
      )

    }
    finally {

      setLoading(false)

    }

  }

  // ==========================================================
  // PROCESS URL QUESTION
  // ==========================================================

  useEffect(() => {

    /*
     * This is specifically for URLs such as:
     *
     * /chat?q=Can%20a%20person%20accused...
     *
     * The question is automatically sent to the chatbot.
     */

    if (
      !queryFromUrl ||
      urlQuestionHandled.current
    ) {
      return
    }

    urlQuestionHandled.current = true

    setQuestion(
      queryFromUrl
    )

    askQuestion(
      queryFromUrl
    )

    /*
     * Remove ?q= from the URL after processing.
     *
     * This prevents the same question from being
     * automatically submitted again when the user refreshes.
     */

    navigate(
      '/chat',
      {
        replace: true,
      }
    )

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

    setAnswer('')

    setSources([])

    setError('')

    // --------------------------------------------------------
    // IMPORTANT:
    // Also clear the saved version.
    // --------------------------------------------------------

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

    // ========================================================
    // CRITICAL FIX
    // SAVE THE CURRENT CHAT BEFORE LEAVING THIS PAGE
    // ========================================================

    saveChat(
      storageKey,
      {
        question,
        answer,
        sources,
        error,
      }
    )

    // ========================================================
    // OPEN SELECTED JUDGMENT
    // ========================================================

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

    if (
      documentId
    ) {

      navigate(
        `/judgment/${encodeURIComponent(
          documentId
        )}`
      )

      return

    }

    navigate(
      '/search'
    )

  }

  // ==========================================================
  // RETURN UI
  // ==========================================================

  return (

    <Box
      sx={{
        minHeight: '100vh',
        backgroundColor: '#F7F8FC',
      }}
    >

      <Navbar />

      <Container
        maxWidth="xl"
        sx={{
          py: {
            xs: 5,
            md: 7,
          },
        }}
      >

        {/* =================================================
            BACK BUTTON FOR JUDGMENT CHAT
        ================================================== */}

        {isJudgmentChat && (

          <Box
            sx={{
              maxWidth: 950,
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
                fontWeight: 500,

                '&:hover': {
                  backgroundColor:
                    'transparent',
                  color: '#3155D9',
                },
              }}
            >
              Back to Judgment
            </Button>

          </Box>

        )}

        {/* =================================================
            HEADER
        ================================================== */}

        <Box
          sx={{
            textAlign: 'center',
            maxWidth: 850,
            mx: 'auto',
          }}
        >

          <Box
            sx={{
              width: 50,
              height: 50,
              mx: 'auto',
              mb: 2,
              borderRadius: 2.5,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: '#EEF2FF',
              color: '#3155D9',
            }}
          >

            <AutoAwesomeOutlinedIcon />

          </Box>

          <Typography
            component="h1"
            sx={{
              fontSize: {
                xs: 34,
                md: 48,
              },
              lineHeight: 1.15,
              fontWeight: 700,
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
              lineHeight: 1.6,
              color: '#667085',
            }}
          >

            {isJudgmentChat
              ? 'Ask questions about this specific judgment using only its relevant legal context.'
              : 'Ask questions about Indian court judgments and explore the cases supporting the answer.'}

          </Typography>

        </Box>

        {/* =================================================
            JUDGMENT CHAT INFORMATION
        ================================================== */}

        {isJudgmentChat && (

          <Paper
            elevation={0}
            sx={{
              mt: 3,
              maxWidth: 950,
              mx: 'auto',
              px: 2.5,
              py: 1.5,
              borderRadius: 3,
              border:
                '1px solid #D9E0FA',
              backgroundColor:
                '#F7F9FF',
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

        {/* =================================================
            QUESTION INPUT
        ================================================== */}

        <Paper
          component="form"
          onSubmit={handleSubmit}
          elevation={0}
          sx={{
            mt: 4,
            maxWidth: 950,
            mx: 'auto',
            p: {
              xs: 2,
              md: 2.5,
            },
            borderRadius: 4,
            border:
              '1px solid #DFE3EB',
            backgroundColor:
              '#FFFFFF',
            boxShadow:
              '0 12px 40px rgba(31,45,70,0.07)',
          }}
        >

          <TextField
            fullWidth
            multiline
            minRows={3}
            maxRows={7}
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
                : 'Ask a question about Indian judgments...'
            }
            variant="standard"
            slotProps={{
              input: {
                disableUnderline:
                  true,
              },
            }}
            sx={{
              '& textarea': {
                fontSize: 16,
                lineHeight: 1.6,
                color: '#172033',
              },
            }}
          />

          <Box
            sx={{
              display: 'flex',
              justifyContent:
                'flex-end',
              mt: 1.5,
            }}
          >

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
                px: 2.8,
                py: 1.2,
                borderRadius: 2,
                textTransform:
                  'none',
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
            SUGGESTIONS
        ================================================== */}

        {!answer &&
          !loading &&
          !error && (

            <Box
              sx={{
                maxWidth: 950,
                mx: 'auto',
              }}
            >

              <SuggestedQuestions
                onSelect={
                  handleSuggestion
                }
              />

            </Box>

          )}

        {/* =================================================
            LOADING
        ================================================== */}

        {loading && (

          <Paper
            elevation={0}
            sx={{
              mt: 4,
              maxWidth: 950,
              mx: 'auto',
              p: 4,
              borderRadius: 3,
              border:
                '1px solid #E3E6ED',
              backgroundColor:
                '#FFFFFF',
            }}
          >

            <Box
              sx={{
                display: 'flex',
                alignItems:
                  'center',
                gap: 2,
              }}
            >

              <CircularProgress
                size={24}
                thickness={4}
              />

              <Box>

                <Typography
                  sx={{
                    fontWeight: 600,
                    color: '#172033',
                  }}
                >

                  {isJudgmentChat
                    ? 'Legal Mind AI is analyzing this judgment...'
                    : 'Legal Mind AI is researching...'}

                </Typography>

                <Typography
                  sx={{
                    mt: 0.3,
                    fontSize: 13,
                    color: '#667085',
                  }}
                >

                  {isJudgmentChat
                    ? 'Retrieving and ranking relevant passages from this judgment.'
                    : 'Searching and ranking relevant judgments before generating the answer.'}

                </Typography>

              </Box>

            </Box>

          </Paper>

        )}

        {/* =================================================
            ERROR
        ================================================== */}

        {error && (

          <Paper
            elevation={0}
            sx={{
              mt: 4,
              maxWidth: 950,
              mx: 'auto',
              p: 4,
              textAlign: 'center',
              borderRadius: 3,
              border:
                '1px solid #F0D0D0',
              backgroundColor:
                '#FFF8F8',
            }}
          >

            <Typography
              sx={{
                fontWeight: 600,
                color: '#B42318',
                mb: 1,
              }}
            >
              Unable to generate answer
            </Typography>

            <Typography
              sx={{
                fontSize: 14,
                color: '#667085',
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

          </Paper>

        )}

        {/* =================================================
            RESULTS
        ================================================== */}

        {(answer ||
          sources.length > 0) &&
          !loading && (

            <Box
              sx={{
                mt: 5,
                display: 'grid',
                gridTemplateColumns: {
                  xs: '1fr',
                  lg: 'minmax(0, 1fr) 360px',
                },
                gap: 3,
                alignItems:
                  'start',
              }}
            >

              {/* ===============================
                  ANSWER
              =============================== */}

              <Box>

                <ChatMessage type="user">
                  {question}
                </ChatMessage>

                <ChatMessage type="assistant">
                  {answer}
                </ChatMessage>

                <Typography
                  sx={{
                    mt: 2,
                    fontSize: 12,
                    lineHeight: 1.6,
                    color: '#98A2B3',
                  }}
                >

                  {isJudgmentChat
                    ? 'Legal Mind AI provides answers based only on the retrieved portions of this judgment. Always verify important legal information against the original judgment and applicable law.'
                    : 'Legal Mind AI provides answers based on retrieved judgments. Always verify important legal information against the original judgment and applicable law.'}

                </Typography>

              </Box>

              {/* ===============================
                  SOURCES
              =============================== */}

              <Box>

                <Box
                  sx={{
                    mb: 2,
                  }}
                >

                  <Typography
                    sx={{
                      fontSize: 22,
                      fontWeight: 700,
                      color: '#172033',
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
                      lineHeight: 1.5,
                      color: '#667085',
                    }}
                  >

                    {isJudgmentChat
                      ? 'Relevant passages retrieved from this judgment and used as supporting context.'
                      : 'Cases retrieved from the Legal Mind AI database and used as supporting context.'}

                  </Typography>

                </Box>

                <Box
                  sx={{
                    display: 'flex',
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

              </Box>

            </Box>

          )}

        {/* =================================================
            NEW QUESTION
        ================================================== */}

        {(answer ||
          error) &&
          !loading && (

            <Box
              sx={{
                display: 'flex',
                justifyContent:
                  'center',
                mt: 5,
                pb: 3,
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
                  borderRadius: 2,
                  px: 2.5,
                  borderColor:
                    '#D0D5DD',
                  color: '#344054',
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