import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import {
  Box,
  Button,
  Container,
  Paper,
  TextField,
  Typography,
  ToggleButton,
  ToggleButtonGroup,
  InputAdornment,
} from '@mui/material'

import SearchIcon from '@mui/icons-material/Search'
import FindInPageOutlinedIcon from '@mui/icons-material/FindInPageOutlined'
import SmartToyOutlinedIcon from '@mui/icons-material/SmartToyOutlined'
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined'
import ArrowForwardRoundedIcon from '@mui/icons-material/ArrowForwardRounded'
import AutoAwesomeOutlinedIcon from '@mui/icons-material/AutoAwesomeOutlined'
import GavelOutlinedIcon from '@mui/icons-material/GavelOutlined'

import Navbar from '../components/Navbar'


function Home() {

  const [mode, setMode] = useState('judgments')
  const [query, setQuery] = useState('')

  const navigate = useNavigate()


  // ============================================================
  // JUDGMENT SEARCH
  // ============================================================

  const handleSearch = () => {

    const trimmedQuery = query.trim()

    if (!trimmedQuery) {
      return
    }

    navigate(
      `/search?q=${encodeURIComponent(trimmedQuery)}`
    )
  }


  // ============================================================
  // GENERAL AI CHAT
  // ============================================================

  const handleAskAI = () => {

    const trimmedQuery = query.trim()

    if (!trimmedQuery) {
      return
    }

    navigate(
      `/chat?q=${encodeURIComponent(trimmedQuery)}`
    )
  }


  // ============================================================
  // EXAMPLE SEARCH
  // ============================================================

  const handleExampleSearch = () => {

    const exampleQuery =
      'A.K. Gopalan vs The State of Madras'

    setMode('judgments')
    setQuery(exampleQuery)

    navigate(
      `/search?q=${encodeURIComponent(exampleQuery)}`
    )
  }


  // ============================================================
  // MODE CHANGE
  // ============================================================

  const handleModeChange = (_, newMode) => {

    if (!newMode) {
      return
    }

    setMode(newMode)
    setQuery('')
  }


  // ============================================================
  // FEATURE CARD ACTIONS
  // ============================================================

  const openJudgmentSearch = () => {

    navigate('/search')

  }


  const openGeneralChat = () => {

    navigate('/chat')

  }


  return (

    <Box
      sx={{
        minHeight: '100vh',
        backgroundColor: '#F7F8FC',
      }}
    >

      <Navbar />

      <Box
        component="main"
        sx={{
          py: {
            xs: 6,
            md: 10,
          },
        }}
      >

        <Container
          maxWidth="lg"
        >

          {/* =====================================================
              HERO
          ====================================================== */}

          <Box
            sx={{
              textAlign: 'center',
              maxWidth: 920,
              mx: 'auto',
            }}
          >

            {/* Badge */}

            <Box
              sx={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 0.8,
                px: 2,
                py: 0.8,
                mb: 3,
                border: '1px solid #D9DEEA',
                borderRadius: 10,
                backgroundColor: '#FFFFFF',
              }}
            >

              <GavelOutlinedIcon
                sx={{
                  fontSize: 16,
                  color: '#3155D9',
                }}
              />

              <Typography
                sx={{
                  fontSize: 12,
                  fontWeight: 700,
                  letterSpacing: 1,
                  color: '#667085',
                }}
              >
                AI-POWERED LEGAL PLATFORM
              </Typography>

            </Box>


            {/* Heading */}

            <Typography
              component="h1"
              sx={{
                fontSize: {
                  xs: 42,
                  sm: 52,
                  md: 64,
                },
                lineHeight: 1.08,
                letterSpacing: {
                  xs: '-1.5px',
                  md: '-2.5px',
                },
                fontWeight: 750,
                color: '#172033',
              }}
            >
              Legal Research.

              <br />

              <Box
                component="span"
                sx={{
                  color: '#3155D9',
                }}
              >
                Smarter with AI.
              </Box>

            </Typography>


            {/* Description */}

            <Typography
              sx={{
                maxWidth: 700,
                mx: 'auto',
                mt: 3,
                color: '#667085',
                fontSize: {
                  xs: 16,
                  md: 18,
                },
                lineHeight: 1.7,
              }}
            >
              Search Indian court judgments, ask legal questions,
              and explore powerful AI-assisted legal workflows
              from one platform.
            </Typography>


            {/* =================================================
                MODE TOGGLE
            ================================================== */}

            <Box
              sx={{
                display: 'flex',
                justifyContent: 'center',
                mt: 5,
              }}
            >

              <ToggleButtonGroup
                value={mode}
                exclusive
                onChange={handleModeChange}
                sx={{
                  p: 0.6,
                  backgroundColor: '#FFFFFF',
                  border: '1px solid #DDE2EC',
                  borderRadius: 3,
                  boxShadow:
                    '0 8px 30px rgba(31,45,70,0.06)',

                  '& .MuiToggleButton-root': {
                    border: 'none',
                    borderRadius: 2.2,
                    px: {
                      xs: 2,
                      sm: 3,
                    },
                    py: 1.2,
                    minWidth: {
                      xs: 145,
                      sm: 190,
                    },
                    textTransform: 'none',
                    fontWeight: 600,
                    color: '#667085',
                  },

                  '& .MuiToggleButton-root.Mui-selected': {
                    backgroundColor: '#3155D9',
                    color: '#FFFFFF',
                  },

                  '& .MuiToggleButton-root.Mui-selected:hover': {
                    backgroundColor: '#2949C4',
                  },

                  '& .MuiToggleButton-root:hover': {
                    backgroundColor: '#F3F5FA',
                  },

                  '& .MuiToggleButton-root.Mui-selected:hover': {
                    color: '#FFFFFF',
                  },
                }}
              >

                <ToggleButton value="judgments">

                  <FindInPageOutlinedIcon
                    sx={{
                      fontSize: 19,
                      mr: 1,
                    }}
                  />

                  Judgment Retrieval

                </ToggleButton>


                <ToggleButton value="chat">

                  <SmartToyOutlinedIcon
                    sx={{
                      fontSize: 19,
                      mr: 1,
                    }}
                  />

                  General Legal AI

                </ToggleButton>

              </ToggleButtonGroup>

            </Box>


            {/* =================================================
                MAIN WORKSPACE PANEL
            ================================================== */}

            <Paper
              elevation={0}
              sx={{
                mt: 4,
                p: {
                  xs: 1.2,
                  sm: 1.4,
                },
                maxWidth: 800,
                mx: 'auto',
                border: '1px solid #DFE3EB',
                borderRadius: 3.5,
                backgroundColor: '#FFFFFF',
                boxShadow:
                  '0 18px 50px rgba(31,45,70,0.09)',
              }}
            >

              {/* ================================
                  JUDGMENT SEARCH MODE
              ================================= */}

              {mode === 'judgments' && (

                <Box>

                  <TextField
                    fullWidth
                    variant="outlined"
                    value={query}
                    onChange={(event) => {
                      setQuery(event.target.value)
                    }}
                    onKeyDown={(event) => {

                      if (event.key === 'Enter') {
                        handleSearch()
                      }

                    }}
                    placeholder="Search by case name, citation, judge, court, or legal issue..."
                    slotProps={{
                      input: {
                        startAdornment: (
                          <InputAdornment position="start">

                            <SearchIcon
                              sx={{
                                color: '#7B8497',
                              }}
                            />

                          </InputAdornment>
                        ),

                        endAdornment: (
                          <InputAdornment position="end">

                            <Button
                              variant="contained"
                              onClick={handleSearch}
                              disabled={!query.trim()}
                              endIcon={
                                <ArrowForwardRoundedIcon />
                              }
                              sx={{
                                height: 48,
                                px: 2.8,
                                borderRadius: 2,
                                textTransform: 'none',
                                fontWeight: 650,
                                boxShadow: 'none',
                                whiteSpace: 'nowrap',
                              }}
                            >
                              Search
                            </Button>

                          </InputAdornment>
                        ),

                        disableUnderline: true,
                      },
                    }}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        minHeight: 66,
                        borderRadius: 2.5,
                        fontSize: 15,
                      },

                      '& .MuiOutlinedInput-notchedOutline': {
                        border: 'none',
                      },
                    }}
                  />

                </Box>

              )}


              {/* ================================
                  GENERAL AI MODE
              ================================= */}

              {mode === 'chat' && (

                <Box>

                  <TextField
                    fullWidth
                    variant="outlined"
                    value={query}
                    onChange={(event) => {
                      setQuery(event.target.value)
                    }}
                    onKeyDown={(event) => {

                      if (
                        event.key === 'Enter' &&
                        !event.shiftKey
                      ) {

                        event.preventDefault()
                        handleAskAI()

                      }

                    }}
                    placeholder="Ask a general legal question..."
                    slotProps={{
                      input: {
                        startAdornment: (
                          <InputAdornment position="start">

                            <AutoAwesomeOutlinedIcon
                              sx={{
                                color: '#3155D9',
                              }}
                            />

                          </InputAdornment>
                        ),

                        endAdornment: (
                          <InputAdornment position="end">

                            <Button
                              variant="contained"
                              onClick={handleAskAI}
                              disabled={!query.trim()}
                              endIcon={
                                <ArrowForwardRoundedIcon />
                              }
                              sx={{
                                height: 48,
                                px: 2.8,
                                borderRadius: 2,
                                textTransform: 'none',
                                fontWeight: 650,
                                boxShadow: 'none',
                                whiteSpace: 'nowrap',
                              }}
                            >
                              Ask AI
                            </Button>

                          </InputAdornment>
                        ),

                        disableUnderline: true,
                      },
                    }}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        minHeight: 66,
                        borderRadius: 2.5,
                        fontSize: 15,
                      },

                      '& .MuiOutlinedInput-notchedOutline': {
                        border: 'none',
                      },
                    }}
                  />

                </Box>

              )}

            </Paper>


            {/* =================================================
                MODE DESCRIPTION
            ================================================== */}

            <Box
              sx={{
                mt: 2,
                minHeight: 24,
              }}
            >

              {mode === 'judgments' ? (

                <Typography
                  sx={{
                    fontSize: 13,
                    color: '#8992A5',
                  }}
                >
                  Search across the judgment database by case,
                  citation, judge, court, date, or legal issue.
                </Typography>

              ) : (

                <Typography
                  sx={{
                    fontSize: 13,
                    color: '#8992A5',
                  }}
                >
                  Ask general legal questions and get
                  AI-assisted explanations.
                </Typography>

              )}

            </Box>


            {/* =================================================
                EXAMPLE SEARCH
            ================================================== */}

            {mode === 'judgments' && (

              <Typography
                sx={{
                  mt: 1.5,
                  fontSize: 13,
                  color: '#8992A5',
                }}
              >

                Try searching:{' '}

                <Box
                  component="button"
                  onClick={handleExampleSearch}
                  sx={{
                    border: 'none',
                    background: 'none',
                    padding: 0,
                    cursor: 'pointer',
                    color: '#3155D9',
                    fontWeight: 600,
                    fontSize: 'inherit',
                  }}
                >
                  A.K. Gopalan vs The State of Madras
                </Box>

              </Typography>

            )}

          </Box>


          {/* =====================================================
              FEATURE CARDS
          ====================================================== */}

          <Box
            sx={{
              mt: {
                xs: 7,
                md: 9,
              },

              display: 'grid',

              gridTemplateColumns: {
                xs: '1fr',
                md: 'repeat(3, 1fr)',
              },

              gap: 3,
            }}
          >

            {/* =================================================
                JUDGMENT RETRIEVAL
            ================================================== */}

            <FeatureCard
              icon={<FindInPageOutlinedIcon />}
              title="Judgment Retrieval"
              description="Search and explore Indian court judgments using case names, citations, judges, courts, dates, and legal issues."
              onClick={openJudgmentSearch}
              actionText="Search judgments"
            />


            {/* =================================================
                GENERAL LEGAL AI
            ================================================== */}

            <FeatureCard
              icon={<SmartToyOutlinedIcon />}
              title="General Legal AI"
              description="Ask general legal questions and interact with an AI assistant for explanations and legal research assistance."
              onClick={openGeneralChat}
              actionText="Ask Legal AI"
            />


            {/* =================================================
                DOCUMENT DRAFTING
            ================================================== */}

            <FeatureCard
              icon={<DescriptionOutlinedIcon />}
              title="Document Drafting"
              description="Create, structure, and refine legal documents with AI-assisted drafting workflows."
              comingSoon
              actionText="Coming soon"
            />

          </Box>


          {/* =====================================================
              TRUST / PRODUCT STATEMENT
          ====================================================== */}

          <Box
            sx={{
              mt: 8,
              textAlign: 'center',
            }}
          >

            <Typography
              sx={{
                fontSize: 13,
                color: '#98A2B3',
              }}
            >
              Built for legal research, judgment analysis,
              and AI-assisted legal workflows.
            </Typography>

          </Box>

        </Container>

      </Box>

    </Box>
  )
}


/* ============================================================
   FEATURE CARD
============================================================ */

function FeatureCard({
  icon,
  title,
  description,
  onClick,
  actionText,
  comingSoon = false,
}) {

  return (

    <Paper
      elevation={0}
      onClick={
        !comingSoon
          ? onClick
          : undefined
      }
      sx={{
        position: 'relative',

        p: {
          xs: 3,
          md: 3.5,
        },

        minHeight: 245,

        display: 'flex',
        flexDirection: 'column',

        border: '1px solid #E3E6ED',
        borderRadius: 3,

        backgroundColor: '#FFFFFF',

        cursor:
          comingSoon
            ? 'default'
            : 'pointer',

        transition:
          'transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease',

        '&:hover': comingSoon
          ? {}
          : {
              transform: 'translateY(-5px)',
              boxShadow:
                '0 18px 40px rgba(31,45,70,0.09)',
              borderColor: '#D3D9E8',
            },
      }}
    >

      {/* Icon */}

      <Box
        sx={{
          width: 48,
          height: 48,

          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',

          borderRadius: 2,

          backgroundColor: '#EEF2FF',
          color: '#3155D9',

          mb: 2.5,
        }}
      >
        {icon}
      </Box>


      {/* Coming Soon Badge */}

      {comingSoon && (

        <Box
          sx={{
            position: 'absolute',
            top: 22,
            right: 22,

            px: 1.2,
            py: 0.5,

            borderRadius: 10,

            backgroundColor: '#F2F4F7',
            color: '#667085',

            fontSize: 11,
            fontWeight: 650,
          }}
        >
          COMING SOON
        </Box>

      )}


      {/* Title */}

      <Typography
        variant="h6"
        sx={{
          fontWeight: 650,
          color: '#172033',
          mb: 1,
        }}
      >
        {title}
      </Typography>


      {/* Description */}

      <Typography
        sx={{
          color: '#667085',
          lineHeight: 1.65,
          fontSize: 14,
          flexGrow: 1,
        }}
      >
        {description}
      </Typography>


      {/* Action */}

      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 0.7,
          mt: 2.5,

          color:
            comingSoon
              ? '#98A2B3'
              : '#3155D9',

          fontSize: 13,
          fontWeight: 650,
        }}
      >

        {actionText}

        {!comingSoon && (

          <ArrowForwardRoundedIcon
            sx={{
              fontSize: 17,
            }}
          />

        )}

      </Box>

    </Paper>

  )
}


export default Home