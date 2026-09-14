import { useState, useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'

import {
  Box,
  Button,
  Container,
  TextField,
  Typography,
  CircularProgress,
} from '@mui/material'

import SearchIcon from '@mui/icons-material/Search'

import Navbar from '../components/Navbar'
import JudgmentCard from '../components/JudgmentCard'


// ============================================================
// API CONFIGURATION
// ============================================================

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  'http://localhost:5000'


// ============================================================
// SEARCH RESULTS
// ============================================================

function SearchResults() {

  const [searchParams, setSearchParams] =
    useSearchParams()

  const navigate = useNavigate()

  const query =
    searchParams.get('q') || ''


  // Search input
  const [searchInput, setSearchInput] =
    useState(query)


  // Judgments returned by backend
  const [judgments, setJudgments] =
    useState([])


  // Loading state
  const [loading, setLoading] =
    useState(false)


  // Error state
  const [error, setError] =
    useState('')


  // ============================================================
  // KEEP INPUT SYNCHRONIZED WITH URL
  // ============================================================

  useEffect(() => {

    setSearchInput(query)

  }, [query])


  // ============================================================
  // SEARCH JUDGMENTS
  // ============================================================

  useEffect(() => {

    const fetchJudgments = async () => {

      setLoading(true)
      setError('')
      setJudgments([])

      try {

        // ======================================================
        // IF THERE IS NO QUERY
        // ======================================================

        if (!query.trim()) {

          setLoading(false)
          return

        }


        // ======================================================
        // FETCH FIRST PAGE
        // ======================================================

        const firstPageUrl =
          `${API_BASE_URL}/api/judgments/search` +
          `?q=${encodeURIComponent(query)}` +
          `&page=1` +
          `&limit=100`


        console.log(
          'Searching judgments:',
          firstPageUrl
        )


        const firstResponse =
          await fetch(firstPageUrl)


        if (!firstResponse.ok) {

          throw new Error(
            `API returned status ${firstResponse.status}`
          )

        }


        const firstData =
          await firstResponse.json()


        console.log(
          'First API response:',
          firstData
        )


        // ======================================================
        // GET FIRST PAGE RESULTS
        // ======================================================

        let allResults =
          firstData.results || []


        const totalPages =
          firstData.total_pages || 1


        // ======================================================
        // FETCH REMAINING PAGES
        // ======================================================

        if (totalPages > 1) {

          const pageRequests = []


          for (
            let page = 2;
            page <= totalPages;
            page++
          ) {

            const pageUrl =
              `${API_BASE_URL}/api/judgments/search` +
              `?q=${encodeURIComponent(query)}` +
              `&page=${page}` +
              `&limit=100`


            pageRequests.push(
              fetch(pageUrl)
                .then((response) => {

                  if (!response.ok) {

                    throw new Error(
                      `API returned status ${response.status}`
                    )

                  }

                  return response.json()

                })
            )

          }


          const remainingPages =
            await Promise.all(pageRequests)


          remainingPages.forEach(
            (pageData) => {

              allResults = [
                ...allResults,
                ...(pageData.results || [])
              ]

            }
          )

        }


        console.log(
          `Total judgments retrieved: ${allResults.length}`
        )


        // ======================================================
        // FORMAT BACKEND DATA FOR JudgmentCard
        // ======================================================

        const formattedJudgments =
          allResults.map(
            (judgment) => {


              // ------------------------------------------------
              // CASE NAME
              // ------------------------------------------------

              const caseName =
                judgment.case_name ||
                'Unknown Case'


              // ------------------------------------------------
              // DATE
              // ------------------------------------------------

              const date =
                judgment.judgment_date ||
                'Date not available'


              // ------------------------------------------------
              // CITATION
              // ------------------------------------------------

              let citation =
                'Citation not available'


              if (
                Array.isArray(
                  judgment.citations
                ) &&
                judgment.citations.length > 0
              ) {

                citation =
                  judgment.citations.join(' | ')

              }


              // ------------------------------------------------
              // SNIPPET
              // ------------------------------------------------

              let snippet =
                judgment.headnote ||
                ''


              if (!snippet) {

                snippet =
                  judgment.verdict ||
                  ''

              }


              if (!snippet) {

                snippet =
                  'No summary available.'

              }


              // ------------------------------------------------
              // RETURN FRONTEND OBJECT
              // ------------------------------------------------

              return {

                // Important:
                // document_id comes from documents_v2

                id:
                  judgment.document_id ||
                  judgment.filename,


                // Existing JudgmentCard fields

                caseName,

                date,

                citation,

                snippet,


                // Additional metadata
                // kept available for JudgmentCard
                // without changing existing features

                petitioner:
                  judgment.petitioner || '',

                respondent:
                  judgment.respondent || '',

                judges:
                  judgment.judges || [],

                court:
                  judgment.court || '',

                caseNumber:
                  judgment.case_number || '',

                citations:
                  judgment.citations || [],

                legalTopics:
                  judgment.legal_topics || [],

                acts:
                  judgment.acts || [],

                headnote:
                  judgment.headnote || '',

                verdict:
                  judgment.verdict || '',

                filename:
                  judgment.filename || '',

                documentId:
                  judgment.document_id || '',

                relevanceScore:
                  judgment.relevance_score || 0,

              }

            }
          )


        setJudgments(
          formattedJudgments
        )

      }
      catch (err) {

        console.error(
          'Judgment search error:',
          err
        )


        setError(
          'Unable to connect to the judgment database.'
        )


        setJudgments([])

      }
      finally {

        setLoading(false)

      }

    }


    fetchJudgments()

  }, [query])


  // ============================================================
  // SEARCH FORM
  // ============================================================

  const handleSearch = (event) => {

    event.preventDefault()


    const newQuery =
      searchInput.trim()


    if (!newQuery) {

      return

    }


    setSearchParams({
      q: newQuery
    })

  }


  // ============================================================
  // OPEN JUDGMENT
  // ============================================================

  const handleOpenJudgment = (judgment) => {

    navigate(
      `/judgment/${judgment.id}`
    )

  }


  // ============================================================
  // CLEAR SEARCH
  // ============================================================

  const handleViewAll = () => {

    setSearchParams({})

  }


  // ============================================================
  // UI
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
        maxWidth="lg"
        sx={{
          py: 6,
        }}
      >

        {/* ====================================================
            PAGE HEADER
        ==================================================== */}

        <Typography
          component="h1"
          sx={{
            fontSize: {
              xs: 30,
              md: 36,
            },
            fontWeight: 700,
            color: '#172033',
            mb: 1,
          }}
        >
          Search Judgments
        </Typography>


        <Typography
          sx={{
            color: '#667085',
            mb: 4,
          }}
        >
          Find relevant judgments from the Legal Mind AI
          dataset.
        </Typography>


        {/* ====================================================
            SEARCH BAR
        ==================================================== */}

        <Box
          component="form"
          onSubmit={handleSearch}
          sx={{
            display: 'flex',
            gap: 1.5,
            maxWidth: 850,
            mb: 5,

            flexDirection: {
              xs: 'column',
              sm: 'row',
            },
          }}
        >

          <TextField
            name="search"
            fullWidth
            value={searchInput}
            onChange={(event) =>
              setSearchInput(
                event.target.value
              )
            }
            placeholder="Search by case name, citation, or legal issue..."
            sx={{
              backgroundColor: '#FFFFFF',

              '& .MuiOutlinedInput-root': {
                borderRadius: 2,
              },
            }}
          />


          <Button
            type="submit"
            variant="contained"
            startIcon={
              <SearchIcon />
            }
            sx={{
              px: 3,
              minWidth: 120,
              borderRadius: 2,
              textTransform: 'none',
              boxShadow: 'none',

              height: {
                xs: 48,
                sm: 56,
              },
            }}
          >
            Search
          </Button>

        </Box>


        {/* ====================================================
            RESULT INFORMATION
        ==================================================== */}

        <Box
          sx={{
            mb: 3,
          }}
        >

          {query && (

            <Typography
              sx={{
                fontSize: 15,
                color: '#172033',
                mb: 0.5,
              }}
            >

              Results for{' '}

              <strong>
                "{query}"
              </strong>

            </Typography>

          )}


          {!loading &&
            !error && (

              <Typography
                sx={{
                  fontSize: 14,
                  color: '#667085',
                }}
              >

                {judgments.length} judgment
                {judgments.length !== 1
                  ? 's'
                  : ''} found

              </Typography>

            )}

        </Box>


        {/* ====================================================
            LOADING
        ==================================================== */}

        {loading && (

          <Box
            sx={{
              py: 10,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 2,
            }}
          >

            <CircularProgress />

            <Typography
              sx={{
                color: '#667085',
              }}
            >
              Searching judgments...
            </Typography>

          </Box>

        )}


        {/* ====================================================
            API ERROR
        ==================================================== */}

        {!loading &&
          error && (

            <Box
              sx={{
                py: 10,
                px: 3,
                textAlign: 'center',
                backgroundColor: '#FFFFFF',
                border: '1px solid #E3E6ED',
                borderRadius: 3,
              }}
            >

              <Typography
                sx={{
                  fontSize: 20,
                  fontWeight: 600,
                  color: '#172033',
                  mb: 1,
                }}
              >
                Unable to load judgments
              </Typography>


              <Typography
                sx={{
                  color: '#667085',
                  mb: 3,
                }}
              >
                {error}
              </Typography>


              <Button
                variant="outlined"
                onClick={() =>
                  window.location.reload()
                }
                sx={{
                  textTransform: 'none',
                  borderRadius: 2,
                }}
              >
                Try Again
              </Button>

            </Box>

          )}


        {/* ====================================================
            JUDGMENT RESULTS
        ==================================================== */}

        {!loading &&
          !error &&
          judgments.length > 0 && (

            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                gap: 2,
              }}
            >

              {judgments.map(
                (judgment) => (

                  <JudgmentCard
                    key={judgment.id}
                    judgment={judgment}
                    onOpen={
                      handleOpenJudgment
                    }
                  />

                )
              )}

            </Box>

          )}


        {/* ====================================================
            NO RESULTS
        ==================================================== */}

        {!loading &&
          !error &&
          judgments.length === 0 && (

            <Box
              sx={{
                py: 10,
                px: 3,
                textAlign: 'center',
                backgroundColor: '#FFFFFF',
                border: '1px solid #E3E6ED',
                borderRadius: 3,
              }}
            >

              <Typography
                sx={{
                  fontSize: 20,
                  fontWeight: 600,
                  color: '#172033',
                  mb: 1,
                }}
              >
                No judgments found
              </Typography>


              <Typography
                sx={{
                  color: '#667085',
                  mb: 3,
                }}
              >

                {query
                  ? 'Try another case name, citation, or legal issue.'
                  : 'Search for a case name, citation, or legal issue.'}

              </Typography>


              {query && (

                <Button
                  variant="outlined"
                  onClick={
                    handleViewAll
                  }
                  sx={{
                    textTransform: 'none',
                    borderRadius: 2,
                  }}
                >
                  View All Judgments
                </Button>

              )}

            </Box>

          )}

      </Container>

    </Box>

  )

}


export default SearchResults