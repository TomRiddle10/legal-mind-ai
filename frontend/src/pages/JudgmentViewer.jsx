import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'

import {
  Box,
  Button,
  Chip,
  Container,
  Divider,
  Paper,
  Stack,
  Typography,
  CircularProgress,
  TextField,
  Collapse,
  IconButton,
} from '@mui/material'

import ArrowBackRoundedIcon from '@mui/icons-material/ArrowBackRounded'
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined'
import AutoAwesomeOutlinedIcon from '@mui/icons-material/AutoAwesomeOutlined'
import SummarizeOutlinedIcon from '@mui/icons-material/SummarizeOutlined'
import ChatOutlinedIcon from '@mui/icons-material/ChatOutlined'
import CalendarTodayOutlinedIcon from '@mui/icons-material/CalendarTodayOutlined'
import GavelOutlinedIcon from '@mui/icons-material/GavelOutlined'
import FormatQuoteOutlinedIcon from '@mui/icons-material/FormatQuoteOutlined'
import OpenInNewRoundedIcon from '@mui/icons-material/OpenInNewRounded'
import SendRoundedIcon from '@mui/icons-material/SendRounded'
import CloseRoundedIcon from '@mui/icons-material/CloseRounded'
import ExpandMoreRoundedIcon from '@mui/icons-material/ExpandMoreRounded'
import SourceOutlinedIcon from '@mui/icons-material/SourceOutlined'

import Navbar from '../components/Navbar'

// ============================================================
// API CONFIGURATION
// ============================================================

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  'http://localhost:5000'

// ============================================================
// JUDGMENT VIEWER
// ============================================================

function JudgmentViewer() {

  const { id } = useParams()
  const navigate = useNavigate()

  // ==========================================================
  // JUDGMENT STATE
  // ==========================================================

  const [judgment, setJudgment] = useState(null)

  const [loading, setLoading] = useState(true)

  const [error, setError] = useState('')

  // ==========================================================
  // SUMMARY STATE
  // ==========================================================

  const [summary, setSummary] = useState('')

  const [summaryLoading, setSummaryLoading] =
    useState(false)

  const [summaryError, setSummaryError] =
    useState('')

  // ==========================================================
  // ASK AI STATE
  // ==========================================================

  const [askOpen, setAskOpen] = useState(false)

  const [question, setQuestion] = useState('')

  const [answer, setAnswer] = useState('')

  const [sources, setSources] = useState([])

  const [askLoading, setAskLoading] =
    useState(false)

  const [askError, setAskError] =
    useState('')

  // ==========================================================
  // SOURCE EXPANSION
  // ==========================================================

  const [expandedSource, setExpandedSource] =
    useState(null)

  // ==========================================================
  // LOCAL STORAGE STATE
  // ==========================================================
  //
  // This prevents the save effect from running before
  // previously saved data has been restored.
  //
  // ==========================================================

  const [storageReady, setStorageReady] =
    useState(false)

  const storageKey = id
    ? `legal-mind-ai-judgment-${id}`
    : null

  // ==========================================================
  // FETCH JUDGMENT
  // ==========================================================

  useEffect(() => {

    const fetchJudgment = async () => {

      setLoading(true)
      setError('')
      setJudgment(null)

      // ------------------------------------------------------
      // Reset temporary UI state when changing judgment
      // ------------------------------------------------------

      setStorageReady(false)

      setSummary('')
      setSummaryError('')

      setAskOpen(false)
      setQuestion('')
      setAnswer('')
      setSources([])
      setAskError('')
      setExpandedSource(null)

      try {

        const url =
          `${API_BASE_URL}/api/judgments/${encodeURIComponent(id)}`

        console.log(
          'Loading judgment:',
          url
        )

        const response =
          await fetch(url)

        if (!response.ok) {

          if (response.status === 404) {

            setJudgment(null)
            return

          }

          throw new Error(
            `API returned status ${response.status}`
          )

        }

        const data =
          await response.json()

        console.log(
          'Judgment API response:',
          data
        )

        const judgmentData =
          data.judgment || data

        // ====================================================
        // FORMAT BACKEND DATA
        // ====================================================

        const formattedJudgment = {

          id:
            judgmentData.document_id,

          caseName:
            judgmentData.case_name ||
            'Unknown Case',

          date:
            judgmentData.judgment_date ||
            'Not available',

          citation:
            Array.isArray(judgmentData.citations) &&
            judgmentData.citations.length > 0
              ? judgmentData.citations.join(' | ')
              : 'Not available',

          petitioner:
            judgmentData.petitioner ||
            'Not available',

          respondent:
            judgmentData.respondent ||
            'Not available',

          judges:
            judgmentData.judges ||
            [],

          court:
            judgmentData.court ||
            'Not available',

          caseNumber:
            judgmentData.case_number ||
            'Not available',

          citations:
            judgmentData.citations ||
            [],

          legalTopics:
            judgmentData.legal_topics ||
            [],

          acts:
            judgmentData.acts ||
            [],

          headnote:
            judgmentData.headnote ||
            '',

          judgment:
            judgmentData.judgment ||
            '',

          verdict:
            judgmentData.verdict ||
            '',

          filename:
            judgmentData.filename ||
            '',

        }

        setJudgment(
          formattedJudgment
        )

        // ====================================================
        // RESTORE SAVED AI STATE
        // ====================================================

        const savedData =
          localStorage.getItem(
            `legal-mind-ai-judgment-${judgmentData.document_id}`
          )

        if (savedData) {

          try {

            const parsed =
              JSON.parse(savedData)

            console.log(
              'Restoring saved AI state:',
              parsed
            )

            // Restore summary
            setSummary(
              parsed.summary || ''
            )

            // Restore last question
            setQuestion(
              parsed.question || ''
            )

            // Restore answer
            setAnswer(
              parsed.answer || ''
            )

            // Restore retrieved sources
            setSources(
              Array.isArray(parsed.sources)
                ? parsed.sources
                : []
            )

            // Restore whether Ask AI panel was open
            setAskOpen(
              Boolean(parsed.askOpen)
            )

          }
          catch (storageError) {

            console.error(
              'Failed to restore saved AI state:',
              storageError
            )

          }

        }

        // ----------------------------------------------------
        // Important:
        // Enable saving only AFTER restoration is complete.
        // ----------------------------------------------------

        setStorageReady(true)

      }
      catch (err) {

        console.error(
          'Judgment loading error:',
          err
        )

        setError(
          'Unable to connect to the judgment database.'
        )

      }
      finally {

        setLoading(false)

      }

    }

    if (id) {

      fetchJudgment()

    }

  }, [id])

  // ==========================================================
  // SAVE AI STATE TO LOCAL STORAGE
  // ==========================================================
  //
  // Whenever summary, question, answer, sources or panel
  // state changes, save it for this particular judgment.
  //
  // ==========================================================

  useEffect(() => {

    if (!storageReady) {
      return
    }

    if (!storageKey) {
      return
    }

    const aiState = {

      summary:

        summary || '',

      question:

        question || '',

      answer:

        answer || '',

      sources:

        Array.isArray(sources)
          ? sources
          : [],

      askOpen:

        askOpen,

      savedAt:

        new Date().toISOString(),

    }

    try {

      localStorage.setItem(
        storageKey,
        JSON.stringify(aiState)
      )

      console.log(
        'AI state saved:',
        storageKey
      )

    }
    catch (storageError) {

      console.error(
        'Failed to save AI state:',
        storageError
      )

    }

  }, [
    storageReady,
    storageKey,
    summary,
    question,
    answer,
    sources,
    askOpen,
  ])

  // ============================================================
  // JUDGMENT NOT FOUND
  // ============================================================

  if (!loading && (!judgment || error)) {

    return (

      <Box
        sx={{
          minHeight: '100vh',
          backgroundColor: '#F7F8FC',
        }}
      >

        <Navbar />

        <Container
          maxWidth="lg"
          sx={{
            py: 10,
          }}
        >

          <Paper
            elevation={0}
            sx={{
              p: 6,
              textAlign: 'center',
              border: '1px solid #E3E6ED',
              borderRadius: 4,
              backgroundColor: '#FFFFFF',
            }}
          >

            <Box
              sx={{
                width: 64,
                height: 64,
                mx: 'auto',
                mb: 3,
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: '#EEF2FF',
                color: '#3155D9',
              }}
            >

              <DescriptionOutlinedIcon
                sx={{ fontSize: 30 }}
              />

            </Box>

            <Typography
              sx={{
                fontSize: 28,
                fontWeight: 700,
                color: '#172033',
                mb: 1,
              }}
            >
              {error
                ? 'Unable to Load Judgment'
                : 'Judgment Not Found'}
            </Typography>

            <Typography
              sx={{
                color: '#667085',
                mb: 4,
              }}
            >
              {error ||
                'The requested judgment could not be found in the Legal Mind AI dataset.'}
            </Typography>

            <Button
              variant="contained"
              startIcon={
                <ArrowBackRoundedIcon />
              }
              onClick={() =>
                navigate('/search')
              }
              sx={{
                textTransform: 'none',
                borderRadius: 2,
                px: 3,
                boxShadow: 'none',
              }}
            >
              Back to Search
            </Button>

          </Paper>

        </Container>

      </Box>
    )
  }

  // ============================================================
  // LOADING
  // ============================================================

  if (loading) {

    return (

      <Box
        sx={{
          minHeight: '100vh',
          backgroundColor: '#F7F8FC',
        }}
      >

        <Navbar />

        <Container
          maxWidth="lg"
          sx={{
            py: 12,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >

          <CircularProgress />

          <Typography
            sx={{
              mt: 2,
              color: '#667085',
            }}
          >
            Loading judgment...
          </Typography>

        </Container>

      </Box>
    )
  }

  // ============================================================
  // OPEN INLINE ASK AI
  // ============================================================

  const handleAskAI = () => {

    setAskOpen(true)

    setAskError('')

    setTimeout(() => {

      const element =
        document.getElementById(
          'judgment-ai-panel'
        )

      if (element) {

        element.scrollIntoView({
          behavior: 'smooth',
          block: 'center',
        })

      }

    }, 100)

  }

  // ============================================================
  // CLOSE INLINE ASK AI
  // ============================================================

  const handleCloseAskAI = () => {

    setAskOpen(false)

    setQuestion('')

    setAnswer('')

    setSources([])

    setAskError('')

    setExpandedSource(null)

  }

  // ============================================================
  // ASK QUESTION
  // ============================================================

  const handleAskQuestion = async () => {

    const trimmedQuestion =
      question.trim()

    if (!trimmedQuestion) {
      return
    }

    if (!judgment?.id) {
      return
    }

    setAskLoading(true)
    setAskError('')
    setAnswer('')
    setSources([])
    setExpandedSource(null)

    try {

      const url =
        `${API_BASE_URL}/api/judgments/${encodeURIComponent(judgment.id)}/ask`

      console.log(
        'Asking about judgment:',
        url
      )

      const response =
        await fetch(
          url,
          {
            method: 'POST',

            headers: {
              'Content-Type': 'application/json',
            },

            body: JSON.stringify({
              question:
                trimmedQuestion,
            }),
          }
        )

      const data =
        await response.json()

      console.log(
        'Judgment Ask API response:',
        data
      )

      if (!response.ok) {

        throw new Error(
          data.message ||
          'Failed to answer the question.'
        )

      }

      setAnswer(
        data.answer ||
        'No answer was returned.'
      )

      setSources(
        Array.isArray(data.sources)
          ? data.sources
          : []
      )

    }
    catch (err) {

      console.error(
        'Judgment Ask error:',
        err
      )

      setAskError(
        err.message ||
        'Unable to get an answer from Legal Mind AI.'
      )

    }
    finally {

      setAskLoading(false)

    }

  }

  // ============================================================
  // SUMMARY
  // ============================================================

  const handleSummary = async () => {

    if (!judgment?.id) {
      return
    }

    setSummaryLoading(true)
    setSummaryError('')
    setSummary('')

    try {

      const url =
        `${API_BASE_URL}/api/judgments/${encodeURIComponent(judgment.id)}/summarize`

      console.log(
        'Generating judgment summary:',
        url
      )

      const response =
        await fetch(
          url,
          {
            method: 'POST',

            headers: {
              'Content-Type': 'application/json',
            },
          }
        )

      const data =
        await response.json()

      console.log(
        'Summary API response:',
        data
      )

      if (!response.ok) {

        throw new Error(
          data.message ||
          'Failed to generate summary.'
        )

      }

      setSummary(
        data.summary ||
        'No summary was returned.'
      )

      setTimeout(() => {

        const element =
          document.getElementById(
            'ai-summary'
          )

        if (element) {

          element.scrollIntoView({
            behavior: 'smooth',
            block: 'start',
          })

        }

      }, 100)

    }
    catch (err) {

      console.error(
        'Summary generation error:',
        err
      )

      setSummaryError(
        err.message ||
        'Unable to generate the judgment summary.'
      )

    }
    finally {

      setSummaryLoading(false)

    }

  }

  // ============================================================
  // RETURN UI
  // ============================================================

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
            xs: 3,
            md: 5,
          },
        }}
      >

        {/* =====================================================
            BACK
        ====================================================== */}

        <Button
          startIcon={
            <ArrowBackRoundedIcon />
          }
          onClick={() => navigate(-1)}
          sx={{
            mb: 3,
            textTransform: 'none',
            color: '#667085',
            fontWeight: 500,

            '&:hover': {
              backgroundColor: 'transparent',
              color: '#3155D9',
            },
          }}
        >
          Back to Search
        </Button>


        {/* =====================================================
            JUDGMENT HEADER
        ====================================================== */}

        <Paper
          elevation={0}
          sx={{
            p: {
              xs: 3,
              md: 4,
            },
            mb: 3,
            border: '1px solid #E3E6ED',
            borderRadius: 4,
            backgroundColor: '#FFFFFF',
          }}
        >

          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'flex-start',
              gap: 3,
              flexWrap: 'wrap',
            }}
          >

            {/* LEFT */}

            <Box
              sx={{
                display: 'flex',
                gap: 2,
                flex: 1,
                minWidth: 280,
              }}
            >

              <Box
                sx={{
                  width: 52,
                  height: 52,
                  minWidth: 52,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  borderRadius: 2.5,
                  backgroundColor: '#EEF2FF',
                  color: '#3155D9',
                }}
              >

                <GavelOutlinedIcon />

              </Box>

              <Box>

                <Typography
                  sx={{
                    fontSize: {
                      xs: 23,
                      md: 31,
                    },
                    lineHeight: 1.25,
                    fontWeight: 700,
                    color: '#172033',
                    mb: 1.2,
                  }}
                >
                  {judgment.caseName}
                </Typography>

                <Typography
                  sx={{
                    color: '#667085',
                    fontSize: 14,
                    lineHeight: 1.6,
                  }}
                >
                  {judgment.court}
                </Typography>

              </Box>

            </Box>


            {/* ACTIONS */}

            <Stack
              direction={{
                xs: 'column',
                sm: 'row',
              }}
              spacing={1.2}
            >

              <Button
                variant="outlined"
                startIcon={
                  <SummarizeOutlinedIcon />
                }
                onClick={handleSummary}
                disabled={summaryLoading}
                sx={{
                  textTransform: 'none',
                  borderRadius: 2,
                  px: 2,
                  fontWeight: 600,
                }}
              >

                {summaryLoading
                  ? 'Generating...'
                  : 'Summarize'}

              </Button>


              <Button
                variant="contained"
                startIcon={
                  <AutoAwesomeOutlinedIcon />
                }
                onClick={handleAskAI}
                sx={{
                  textTransform: 'none',
                  borderRadius: 2,
                  px: 2.2,
                  fontWeight: 600,
                  boxShadow:
                    '0 5px 15px rgba(49,85,217,0.18)',
                }}
              >
                Ask Legal AI
              </Button>

            </Stack>

          </Box>


          <Divider
            sx={{
              my: 3,
            }}
          />


          {/* METADATA */}

          <Box
            sx={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: 1.2,
            }}
          >

            <MetadataItem
              icon={
                <CalendarTodayOutlinedIcon />
              }
              label="Judgment Date"
              value={
                judgment.date ||
                'Not available'
              }
            />

            <MetadataItem
              icon={
                <FormatQuoteOutlinedIcon />
              }
              label="Citation"
              value={
                judgment.citation ||
                'Not available'
              }
            />

            <Chip
              label={judgment.court}
              sx={{
                height: 34,
                backgroundColor: '#F2F4F7',
                color: '#344054',
                fontWeight: 500,
                borderRadius: 2,
              }}
            />

          </Box>

        </Paper>


        {/* =====================================================
            INLINE ASK AI PANEL
        ====================================================== */}

        <Collapse
          in={askOpen}
          timeout={350}
        >

          <Paper
            id="judgment-ai-panel"
            elevation={0}
            sx={{
              mb: 3,
              border:
                '1px solid #CBD6FA',
              borderRadius: 4,
              overflow: 'hidden',
              background:
                'linear-gradient(180deg, #F5F7FF 0%, #FFFFFF 100%)',
              boxShadow:
                '0 12px 35px rgba(49,85,217,0.07)',
            }}
          >

            {/* AI HEADER */}

            <Box
              sx={{
                px: {
                  xs: 2.5,
                  md: 3,
                },
                py: 2,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                borderBottom:
                  '1px solid #E1E6F5',
              }}
            >

              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1.4,
                }}
              >

                <Box
                  sx={{
                    width: 42,
                    height: 42,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    borderRadius: 2,
                    backgroundColor: '#E9EEFF',
                    color: '#3155D9',
                  }}
                >

                  <AutoAwesomeOutlinedIcon />

                </Box>

                <Box>

                  <Typography
                    sx={{
                      fontSize: 17,
                      fontWeight: 700,
                      color: '#172033',
                    }}
                  >
                    Ask About This Judgment
                  </Typography>

                  <Typography
                    sx={{
                      fontSize: 12,
                      color: '#667085',
                    }}
                  >
                    Answers are based only on this judgment
                  </Typography>

                </Box>

              </Box>


              <IconButton
                onClick={handleCloseAskAI}
                size="small"
                sx={{
                  color: '#667085',
                }}
              >

                <CloseRoundedIcon />

              </IconButton>

            </Box>


            {/* QUESTION AREA */}

            <Box
              sx={{
                p: {
                  xs: 2.5,
                  md: 3,
                },
              }}
            >

              <Typography
                sx={{
                  fontSize: 13,
                  fontWeight: 600,
                  color: '#344054',
                  mb: 1,
                }}
              >
                Your question
              </Typography>


              <TextField
                fullWidth
                multiline
                minRows={2}
                maxRows={5}
                value={question}
                onChange={(event) => {
                  setQuestion(event.target.value)
                }}
                onKeyDown={(event) => {

                  if (
                    event.key === 'Enter' &&
                    !event.shiftKey
                  ) {

                    event.preventDefault()

                    handleAskQuestion()

                  }

                }}
                placeholder="Ask something about this judgment..."
                disabled={askLoading}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: '#FFFFFF',
                    borderRadius: 2.5,
                    fontSize: 14,
                  },
                }}
              />


              <Box
                sx={{
                  mt: 1,
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  gap: 2,
                  flexWrap: 'wrap',
                }}
              >

                <Typography
                  sx={{
                    fontSize: 11,
                    color: '#98A2B3',
                  }}
                >
                  Press Enter to ask · Shift + Enter for a new line
                </Typography>


                <Button
                  variant="contained"
                  endIcon={
                    askLoading
                      ? (
                        <CircularProgress
                          size={17}
                          sx={{
                            color: '#FFFFFF',
                          }}
                        />
                      )
                      : (
                        <SendRoundedIcon />
                      )
                  }
                  onClick={handleAskQuestion}
                  disabled={
                    askLoading ||
                    !question.trim()
                  }
                  sx={{
                    textTransform: 'none',
                    borderRadius: 2,
                    px: 2.5,
                    boxShadow: 'none',
                    fontWeight: 600,
                  }}
                >
                  {askLoading
                    ? 'Analyzing...'
                    : 'Ask Question'}
                </Button>

              </Box>


              {/* ERROR */}

              {askError && (

                <Box
                  sx={{
                    mt: 2,
                    p: 1.8,
                    borderRadius: 2,
                    backgroundColor: '#FFF4F2',
                    border:
                      '1px solid #FECACA',
                  }}
                >

                  <Typography
                    sx={{
                      fontSize: 13,
                      color: '#B42318',
                      lineHeight: 1.6,
                    }}
                  >
                    {askError}
                  </Typography>

                </Box>

              )}


              {/* =================================================
                  ANSWER
              ================================================== */}

              {askLoading && (

                <Box
                  sx={{
                    mt: 3,
                    p: 3,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1.5,
                    borderRadius: 3,
                    backgroundColor: '#FFFFFF',
                    border:
                      '1px solid #EAECF0',
                  }}
                >

                  <CircularProgress
                    size={22}
                  />

                  <Box>

                    <Typography
                      sx={{
                        fontSize: 14,
                        fontWeight: 600,
                        color: '#344054',
                      }}
                    >
                      Legal Mind AI is analyzing this judgment...
                    </Typography>

                    <Typography
                      sx={{
                        mt: 0.3,
                        fontSize: 12,
                        color: '#98A2B3',
                      }}
                    >
                      Retrieving relevant portions of the judgment.
                    </Typography>

                  </Box>

                </Box>

              )}


              {answer && !askLoading && (

                <Box
                  sx={{
                    mt: 3,
                  }}
                >

                  {/* ANSWER HEADER */}

                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 1,
                      mb: 1.5,
                    }}
                  >

                    <AutoAwesomeOutlinedIcon
                      sx={{
                        fontSize: 19,
                        color: '#3155D9',
                      }}
                    />

                    <Typography
                      sx={{
                        fontSize: 16,
                        fontWeight: 700,
                        color: '#172033',
                      }}
                    >
                      Legal Mind AI
                    </Typography>

                  </Box>


                  {/* ANSWER CARD */}

                  <Paper
                    elevation={0}
                    sx={{
                      p: {
                        xs: 2.5,
                        md: 3,
                      },
                      backgroundColor: '#FFFFFF',
                      border:
                        '1px solid #E3E6ED',
                      borderRadius: 3,
                    }}
                  >

                    <Typography
                      component="div"
                      sx={{
                        fontSize: 14.5,
                        lineHeight: 1.85,
                        color: '#344054',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                      }}
                    >
                      {answer}
                    </Typography>

                  </Paper>


                  {/* =================================================
                      SOURCES
                  ================================================== */}

                  {sources.length > 0 && (

                    <Box
                      sx={{
                        mt: 2.5,
                      }}
                    >

                      <Box
                        sx={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: 1,
                          mb: 1.5,
                        }}
                      >

                        <SourceOutlinedIcon
                          sx={{
                            fontSize: 18,
                            color: '#667085',
                          }}
                        />

                        <Typography
                          sx={{
                            fontSize: 14,
                            fontWeight: 700,
                            color: '#344054',
                          }}
                        >
                          Sources from this judgment
                        </Typography>

                      </Box>


                      <Stack spacing={1}>

                        {sources.map(
                          (source, index) => {

                            const isExpanded =
                              expandedSource === index

                            return (

                              <Paper
                                key={
                                  source.chunk_id ||
                                  index
                                }
                                elevation={0}
                                sx={{
                                  border:
                                    '1px solid #E3E6ED',
                                  borderRadius: 2.5,
                                  overflow: 'hidden',
                                  backgroundColor:
                                    '#FFFFFF',
                                }}
                              >

                                {/* SOURCE HEADER */}

                                <Box
                                  sx={{
                                    px: 2,
                                    py: 1.4,
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent:
                                      'space-between',
                                    cursor: 'pointer',
                                  }}
                                  onClick={() => {

                                    setExpandedSource(
                                      isExpanded
                                        ? null
                                        : index
                                    )

                                  }}
                                >

                                  <Box>

                                    <Typography
                                      sx={{
                                        fontSize: 12,
                                        fontWeight: 700,
                                        color: '#344054',
                                      }}
                                    >
                                      Source {index + 1}
                                    </Typography>

                                    <Typography
                                      sx={{
                                        mt: 0.3,
                                        fontSize: 11,
                                        color: '#667085',
                                      }}
                                    >
                                      Chunk {
                                        source.chunk_index
                                      }

                                      {' · '}

                                      Context {
                                        source.context_start
                                      }

                                      {' – '}

                                      {
                                        source.context_end
                                      }

                                    </Typography>

                                  </Box>


                                  <IconButton
                                    size="small"
                                    sx={{
                                      color: '#667085',
                                      transform:
                                        isExpanded
                                          ? 'rotate(180deg)'
                                          : 'rotate(0deg)',
                                      transition:
                                        'transform 0.2s ease',
                                    }}
                                  >

                                    <ExpandMoreRoundedIcon />

                                  </IconButton>

                                </Box>


                                {/* SOURCE TEXT */}

                                <Collapse
                                  in={isExpanded}
                                >

                                  <Box
                                    sx={{
                                      px: 2,
                                      pb: 2,
                                    }}
                                  >

                                    <Divider
                                      sx={{
                                        mb: 1.5,
                                      }}
                                    />

                                    <Typography
                                      sx={{
                                        fontSize: 12.5,
                                        lineHeight: 1.75,
                                        color: '#667085',
                                        whiteSpace:
                                          'pre-wrap',
                                      }}
                                    >
                                      {source.text}
                                    </Typography>

                                  </Box>

                                </Collapse>

                              </Paper>

                            )

                          }
                        )}

                      </Stack>

                    </Box>

                  )}

                </Box>

              )}

            </Box>

          </Paper>

        </Collapse>


        {/* =====================================================
            AI SUMMARY
        ====================================================== */}

        {(summaryLoading ||
          summary ||
          summaryError) && (

          <Paper
            id="ai-summary"
            elevation={0}
            sx={{
              mb: 3,
              p: {
                xs: 3,
                md: 4,
              },
              border:
                '1px solid #D9E0FA',
              borderRadius: 4,
              background:
                'linear-gradient(180deg, #F7F9FF 0%, #FFFFFF 100%)',
            }}
          >

            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1.5,
                mb: 2.5,
              }}
            >

              <Box
                sx={{
                  width: 42,
                  height: 42,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  borderRadius: 2,
                  backgroundColor: '#EEF2FF',
                  color: '#3155D9',
                }}
              >

                <SummarizeOutlinedIcon />

              </Box>

              <Box>

                <Typography
                  sx={{
                    fontSize: 19,
                    fontWeight: 700,
                    color: '#172033',
                  }}
                >
                  AI Summary
                </Typography>

                <Typography
                  sx={{
                    fontSize: 12,
                    color: '#667085',
                  }}
                >
                  Generated from this judgment
                </Typography>

              </Box>

            </Box>


            {summaryLoading && (

              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1.5,
                }}
              >

                <CircularProgress
                  size={22}
                />

                <Typography
                  sx={{
                    color: '#667085',
                    fontSize: 14,
                  }}
                >
                  Generating summary using Legal Mind AI...
                </Typography>

              </Box>

            )}


            {summaryError && (

              <Typography
                sx={{
                  color: '#D92D20',
                  fontSize: 14,
                  lineHeight: 1.7,
                }}
              >
                {summaryError}
              </Typography>

            )}


            {summary && !summaryLoading && (

              <Typography
                component="div"
                sx={{
                  fontSize: 15,
                  lineHeight: 1.9,
                  color: '#344054',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                }}
              >
                {summary}
              </Typography>

            )}

          </Paper>

        )}


        {/* =====================================================
            MAIN CONTENT
        ====================================================== */}

        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: {
              xs: '1fr',
              lg: 'minmax(0, 1fr) 300px',
            },
            gap: 3,
            alignItems: 'start',
          }}
        >

          {/* =================================================
              DOCUMENT
          ================================================== */}

          <Paper
            elevation={0}
            sx={{
              border: '1px solid #E3E6ED',
              borderRadius: 4,
              backgroundColor: '#FFFFFF',
              overflow: 'hidden',
            }}
          >

            {/* Document toolbar */}

            <Box
              sx={{
                px: {
                  xs: 2.5,
                  md: 3,
                },
                py: 2,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: 2,
                borderBottom:
                  '1px solid #E3E6ED',
              }}
            >

              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                }}
              >

                <DescriptionOutlinedIcon
                  sx={{
                    color: '#3155D9',
                    fontSize: 21,
                  }}
                />

                <Typography
                  sx={{
                    fontWeight: 650,
                    color: '#172033',
                  }}
                >
                  Judgment Document
                </Typography>

              </Box>


              <Button
                size="small"
                endIcon={
                  <OpenInNewRoundedIcon
                    sx={{ fontSize: 16 }}
                  />
                }
                sx={{
                  textTransform: 'none',
                  color: '#3155D9',
                  fontWeight: 600,
                }}
              >
                Open PDF
              </Button>

            </Box>


            {/* =================================================
                ACTUAL JUDGMENT TEXT
            ================================================== */}

            <Box
              sx={{
                p: {
                  xs: 2.5,
                  md: 5,
                },
              }}
            >

              {/* CASE INFORMATION */}

              <Box
                sx={{
                  mb: 4,
                }}
              >

                <Typography
                  sx={{
                    fontSize: 16,
                    fontWeight: 700,
                    color: '#172033',
                    mb: 2,
                  }}
                >
                  {judgment.caseName}
                </Typography>


                <Typography
                  sx={{
                    fontSize: 14,
                    color: '#667085',
                    lineHeight: 1.8,
                  }}
                >
                  <strong>
                    Petitioner:
                  </strong>{' '}
                  {judgment.petitioner}
                </Typography>


                <Typography
                  sx={{
                    fontSize: 14,
                    color: '#667085',
                    lineHeight: 1.8,
                  }}
                >
                  <strong>
                    Respondent:
                  </strong>{' '}
                  {judgment.respondent}
                </Typography>


                <Typography
                  sx={{
                    fontSize: 14,
                    color: '#667085',
                    lineHeight: 1.8,
                  }}
                >
                  <strong>
                    Case Number:
                  </strong>{' '}
                  {judgment.caseNumber}
                </Typography>


                {judgment.judges.length > 0 && (

                  <Typography
                    sx={{
                      fontSize: 14,
                      color: '#667085',
                      lineHeight: 1.8,
                    }}
                  >
                    <strong>
                      Judges:
                    </strong>{' '}
                    {judgment.judges.join(', ')}
                  </Typography>

                )}

              </Box>


              <Divider
                sx={{
                  mb: 4,
                }}
              />


              {/* HEADNOTE */}

              {judgment.headnote && (

                <Box
                  sx={{
                    mb: 4,
                    p: 2.5,
                    backgroundColor: '#F8F9FC',
                    borderRadius: 3,
                    border:
                      '1px solid #EAECF0',
                  }}
                >

                  <Typography
                    sx={{
                      fontSize: 15,
                      fontWeight: 700,
                      color: '#172033',
                      mb: 1,
                    }}
                  >
                    Headnote
                  </Typography>

                  <Typography
                    sx={{
                      fontSize: 14,
                      color: '#667085',
                      lineHeight: 1.8,
                      whiteSpace: 'pre-wrap',
                    }}
                  >
                    {judgment.headnote}
                  </Typography>

                </Box>

              )}


              {/* FULL JUDGMENT */}

              {/* =====================================================
    JUDGMENT READING AREA
====================================================== */}

<Box
  sx={{
    maxWidth: 900,
    mx: 'auto',
  }}
>

  {/* DOCUMENT INTRO */}

  <Box
    sx={{
      mb: 4,
      pb: 3,
      borderBottom: '1px solid #EAECF0',
    }}
  >

    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 1,
        mb: 1.5,
      }}
    >

      <Box
        sx={{
          width: 34,
          height: 34,
          borderRadius: 1.8,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: '#EEF2FF',
          color: '#3155D9',
        }}
      >
        <DescriptionOutlinedIcon
          sx={{ fontSize: 19 }}
        />
      </Box>

      <Typography
        sx={{
          fontSize: 18,
          fontWeight: 700,
          color: '#172033',
        }}
      >
        Judgment
      </Typography>

    </Box>


    <Typography
      sx={{
        fontSize: 13,
        color: '#98A2B3',
        lineHeight: 1.6,
      }}
    >
      Official judgment text · {judgment.court}
    </Typography>

  </Box>


  {/* ACTUAL JUDGMENT */}

  <Box
    sx={{
      position: 'relative',
    }}
  >

    {judgment.judgment
      ? judgment.judgment
          .split(/\n\s*\n/)
          .filter(
            paragraph =>
              paragraph.trim()
          )
          .map(
            (paragraph, index) => (

              <Typography
                key={index}
                component="p"
                sx={{
                  fontFamily:
                    '"Georgia", "Times New Roman", serif',

                  fontSize: {
                    xs: 15.5,
                    md: 16.5,
                  },

                  lineHeight: {
                    xs: 1.9,
                    md: 2.0,
                  },

                  letterSpacing:
                    '0.01em',

                  color: '#344054',

                  mb: 2.8,

                  whiteSpace:
                    'pre-wrap',

                  wordBreak:
                    'break-word',

                  textAlign:
                    'left',

                  '&:first-of-type': {
                    marginTop: 0,
                  },
                }}
              >
                {paragraph.trim()}
              </Typography>

            )
          )
      : (
        <Typography
          sx={{
            color: '#667085',
            fontSize: 15,
          }}
        >
          Judgment text is not available.
        </Typography>
      )
    }

  </Box>

</Box>


              {/* VERDICT */}

              {judgment.verdict && (

                <Box
                  sx={{
                    mt: 5,
                    p: 2.5,
                    backgroundColor: '#F8F9FC',
                    border:
                      '1px solid #EAECF0',
                    borderRadius: 3,
                  }}
                >

                  <Typography
                    sx={{
                      fontSize: 15,
                      fontWeight: 700,
                      color: '#172033',
                      mb: 1,
                    }}
                  >
                    Verdict
                  </Typography>

                  <Typography
                    sx={{
                      fontSize: 14,
                      color: '#344054',
                      lineHeight: 1.8,
                    }}
                  >
                    {judgment.verdict}
                  </Typography>

                </Box>

              )}

            </Box>

          </Paper>


          {/* =================================================
              RIGHT SIDEBAR
          ================================================== */}

          <Box
            sx={{
              position: {
                lg: 'sticky',
              },
              top: {
                lg: 90,
              },
            }}
          >

            {/* AI CARD */}

            <Paper
              elevation={0}
              sx={{
                p: 2.5,
                mb: 2,
                border:
                  '1px solid #D9E0FA',
                borderRadius: 3,
                background:
                  'linear-gradient(180deg, #F7F9FF 0%, #FFFFFF 100%)',
              }}
            >

              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1.2,
                  mb: 1,
                }}
              >

                <Box
                  sx={{
                    width: 36,
                    height: 36,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    borderRadius: 2,
                    backgroundColor: '#EEF2FF',
                    color: '#3155D9',
                  }}
                >

                  <AutoAwesomeOutlinedIcon
                    sx={{ fontSize: 20 }}
                  />

                </Box>

                <Typography
                  sx={{
                    fontWeight: 700,
                    color: '#172033',
                  }}
                >
                  Legal Mind AI
                </Typography>

              </Box>


              <Typography
                sx={{
                  fontSize: 13,
                  lineHeight: 1.65,
                  color: '#667085',
                  mb: 2.5,
                }}
              >
                Ask questions about this judgment
                and receive answers based on its
                relevant passages.
              </Typography>


              <Button
                fullWidth
                variant="contained"
                startIcon={
                  <ChatOutlinedIcon />
                }
                onClick={handleAskAI}
                sx={{
                  py: 1.2,
                  textTransform: 'none',
                  borderRadius: 2,
                  boxShadow: 'none',
                  fontWeight: 600,
                }}
              >
                Ask About This Judgment
              </Button>

            </Paper>


            {/* CONTENT CARD */}

            <Paper
              elevation={0}
              sx={{
                p: 2.5,
                border:
                  '1px solid #E3E6ED',
                borderRadius: 3,
                backgroundColor: '#FFFFFF',
              }}
            >

              <Typography
                sx={{
                  fontSize: 15,
                  fontWeight: 700,
                  color: '#172033',
                  mb: 2,
                }}
              >
                Judgment Information
              </Typography>


              <InfoRow
                label="Court"
                value={
                  judgment.court ||
                  'Not available'
                }
              />


              <InfoRow
                label="Date"
                value={
                  judgment.date ||
                  'Not available'
                }
              />


              <InfoRow
                label="Case Number"
                value={
                  judgment.caseNumber ||
                  'Not available'
                }
              />


              <InfoRow
                label="Citation"
                value={
                  judgment.citation ||
                  'Not available'
                }
              />


              {judgment.legalTopics.length > 0 && (

                <InfoRow
                  label="Legal Topics"
                  value={
                    judgment.legalTopics.join(', ')
                  }
                />

              )}


              {judgment.acts.length > 0 && (

                <InfoRow
                  label="Acts"
                  value={
                    judgment.acts.join(', ')
                  }
                />

              )}

            </Paper>

          </Box>

        </Box>


        {/* =====================================================
            AI INFORMATION
        ====================================================== */}

        <Paper
          elevation={0}
          sx={{
            mt: 3,
            p: {
              xs: 3,
              md: 4,
            },
            border:
              '1px solid #E3E6ED',
            borderRadius: 4,
            backgroundColor: '#FFFFFF',
          }}
        >

          <Box
            sx={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: 2,
            }}
          >

            <Box
              sx={{
                width: 44,
                height: 44,
                minWidth: 44,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                borderRadius: 2,
                backgroundColor: '#EEF2FF',
                color: '#3155D9',
              }}
            >

              <AutoAwesomeOutlinedIcon />

            </Box>


            <Box>

              <Typography
                sx={{
                  fontSize: 18,
                  fontWeight: 700,
                  color: '#172033',
                  mb: 0.7,
                }}
              >
                Understand this judgment with AI
              </Typography>


              <Typography
                sx={{
                  fontSize: 14,
                  color: '#667085',
                  lineHeight: 1.7,
                  mb: 2,
                  maxWidth: 760,
                }}
              >
                Ask Legal Mind AI questions about
                this judgment or generate a concise
                structured summary using the
                judgment's legal context.
              </Typography>


              <Stack
                direction={{
                  xs: 'column',
                  sm: 'row',
                }}
                spacing={1.5}
              >

                <Button
                  variant="contained"
                  startIcon={
                    <ChatOutlinedIcon />
                  }
                  onClick={handleAskAI}
                  sx={{
                    textTransform: 'none',
                    borderRadius: 2,
                    boxShadow: 'none',
                  }}
                >
                  Ask a Question
                </Button>


                <Button
                  variant="outlined"
                  startIcon={
                    <SummarizeOutlinedIcon />
                  }
                  onClick={handleSummary}
                  disabled={summaryLoading}
                  sx={{
                    textTransform: 'none',
                    borderRadius: 2,
                  }}
                >
                  {summaryLoading
                    ? 'Generating...'
                    : 'Generate Summary'}
                </Button>

              </Stack>

            </Box>

          </Box>

        </Paper>

      </Container>

    </Box>
  )
}


// ============================================================
// METADATA ITEM
// ============================================================

function MetadataItem({
  icon,
  label,
  value,
}) {

  return (

    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 1,
        px: 1.5,
        py: 0.8,
        borderRadius: 2,
        backgroundColor: '#F8F9FC',
        border: '1px solid #EAECF0',
      }}
    >

      <Box
        sx={{
          display: 'flex',
          color: '#667085',

          '& svg': {
            fontSize: 16,
          },
        }}
      >
        {icon}
      </Box>


      <Box>

        <Typography
          sx={{
            fontSize: 10,
            color: '#98A2B3',
            lineHeight: 1.2,
          }}
        >
          {label}
        </Typography>


        <Typography
          sx={{
            fontSize: 12,
            fontWeight: 600,
            color: '#344054',
          }}
        >
          {value}
        </Typography>

      </Box>

    </Box>

  )
}


// ============================================================
// INFO ROW
// ============================================================

function InfoRow({
  label,
  value,
}) {

  return (

    <Box
      sx={{
        py: 1.4,
        borderBottom:
          '1px solid #F0F1F4',

        '&:last-child': {
          borderBottom: 'none',
        },
      }}
    >

      <Typography
        sx={{
          fontSize: 11,
          color: '#98A2B3',
          mb: 0.4,
        }}
      >
        {label}
      </Typography>


      <Typography
        sx={{
          fontSize: 13,
          fontWeight: 600,
          color: '#344054',
          lineHeight: 1.5,
        }}
      >
        {value}
      </Typography>

    </Box>

  )
}


export default JudgmentViewer