import React from "react"
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom"
import Navigation from "./components/Navigation"
import ChatPage from "./pages/ChatPage"
import UploadPage from "./pages/UploadPage"
import CRMPage from "./pages/CRMPage"
import LeasePreviewPage from "./pages/LeasePreviewPage"
import "./App.css"

const App: React.FC = () => {
  return (
    <Router>
      <div className="app">
        <Navigation/>
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Navigate to="/chat" replace />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/crm" element={<CRMPage />} />
            <Route path="/lease-preview" element={<LeasePreviewPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
