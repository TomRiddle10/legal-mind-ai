import { Box, Button, Container, Typography } from '@mui/material'

function Navbar() {
  return (
    <Box
      component="header"
      sx={{
        height: 72,
        display: 'flex',
        alignItems: 'center',
        borderBottom: '1px solid #E3E6ED',
        backgroundColor: '#FFFFFF',
      }}
    >
      <Container
        maxWidth="lg"
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <Typography
          sx={{
            fontSize: 21,
            fontWeight: 700,
            color: '#172033',
          }}
        >
          ⚖ Legal Mind{' '}
          <Box
            component="span"
            sx={{ color: '#3155D9' }}
          >
            AI
          </Box>
        </Typography>

        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            sx={{
              color: '#667085',
              textTransform: 'none',
            }}
          >
            About
          </Button>

          <Button
            variant="outlined"
            sx={{
              textTransform: 'none',
              borderColor: '#D9DEEA',
              color: '#172033',
            }}
          >
            Sign In
          </Button>
        </Box>
      </Container>
    </Box>
  )
}

export default Navbar