import { BrowserRouter, Routes, Route } from 'react-router-dom'

import Home from './pages/Home'
import SearchResults from './pages/SearchResults'
import JudgmentViewer from './pages/JudgmentViewer'
import LegalChat from './pages/LegalChat'
import Chat from './pages/Chat'

function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* Home */}
        <Route
          path="/"
          element={<Home />}
        />

        {/* Judgment Search */}
        <Route
          path="/search"
          element={<SearchResults />}
        />

        {/* Judgment Viewer */}
        <Route
          path="/judgment/:id"
          element={<JudgmentViewer />}
        />

        {/* Existing General Legal Chat */}
        <Route
          path="/chat"
          element={<LegalChat />}
        />

        {/* Judgment-Specific AI Chat */}
        <Route
          path="/chat/judgment/:documentId"
          element={<Chat />}
        />

      </Routes>
    </BrowserRouter>
  )
}

export default App