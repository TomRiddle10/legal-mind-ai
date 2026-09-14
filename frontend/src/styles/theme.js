import { createTheme } from '@mui/material/styles'

const theme = createTheme({
  palette: {
    primary: {
      main: '#3155D9',
    },
    background: {
      default: '#F7F8FC',
      paper: '#FFFFFF',
    },
    text: {
      primary: '#172033',
      secondary: '#667085',
    },
  },

  typography: {
    fontFamily: 'Inter, Arial, sans-serif',

    h1: {
      fontWeight: 700,
    },

    h2: {
      fontWeight: 700,
    },

    h3: {
      fontWeight: 600,
    },
  },

  shape: {
    borderRadius: 12,
  },
})

export default theme