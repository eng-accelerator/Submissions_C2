import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import App from './App.tsx'
import ProjectsDashboard from './ProjectsDashboard.tsx'
import ReportViewer from './ReportViewer.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/projects" element={<ProjectsDashboard />} />
        <Route path="/project/:jobId" element={<ReportViewer />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
)
