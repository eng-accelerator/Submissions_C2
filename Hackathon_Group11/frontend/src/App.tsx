import React, { useState } from 'react'
import { ResearchForm } from './components/ResearchForm'
import { ResearchResults } from './components/ResearchResults'
import { ResearchProgress } from './components/ResearchProgress'
import { Sidebar } from './components/Sidebar'
import { useResearchProgress } from './hooks/useResearchProgress'
import './App.css'

// API URL from environment variable or default to localhost
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface ResearchData {
  sources: Record<string, any>
  analysis: Record<string, any>
  insights: Record<string, any>
  report: string
  status: string
  error?: string
}

export const App: React.FC = () => {
  const [, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<ResearchData | null>(null)
  const [demoMode, setDemoMode] = useState(false)
  const [initialQuery, setInitialQuery] = useState<string>('')
  const { stages, startStage, updateStage, completeStage, errorStage, resetStages } =
    useResearchProgress()

  const handleQuerySelect = (selectedQuery: string) => {
    setInitialQuery(selectedQuery)
    // Auto-submit the query
    handleStreamingResearch(selectedQuery)
  }

  const handleStreamingResearch = async (q: string) => {
    setQuery(q)
    setLoading(true)
    setResults(null)
    resetStages()

    try {
      const response = await fetch(`${API_URL}/api/research-stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new Error('No response body')
      }

      // Stage mapping: Map backend stages to our progress stages
      const stageMap: Record<string, number> = {
        'retrieval': 0,   // Retriever
        'enrichment': 1,  // Enricher
        'analyzer': 2,    // Analyzer
        'insight': 3,     // Insight
        'report': 4,      // Reporter
      }

      // Track which stages have been started
      const startedStages = new Set<number>()

      while (true) {
        const { done, value } = await reader.read()
        
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              
              // Handle stage updates
              if (data.stage) {
                const stageIndex = stageMap[data.stage]
                
                if (stageIndex !== undefined) {
                  // Start the stage if not already started
                  if (!startedStages.has(stageIndex)) {
                    startStage(stageIndex)
                    startedStages.add(stageIndex)
                  }
                  
                  // Update stage with message and progress
                  if (data.message) {
                    updateStage(stageIndex, { message: data.message })
                  }
                  
                  if (data.progress !== undefined) {
                    updateStage(stageIndex, { progress: data.progress })
                  }
                }
              }

              // Handle completion
              if (data.stage === 'complete' && data.data) {
                // Complete all stages
                completeStage(0, '✓ Retrieved sources')
                completeStage(1, '✓ Enrichment complete')
                completeStage(2, '✓ Analysis complete')
                completeStage(3, '✓ Insights generated')
                completeStage(4, '✓ Report compiled')
                
                setResults(data.data)
                setLoading(false)
                return
              }

              // Handle errors
              if (data.stage === 'error') {
                // Find the last started stage (most likely to be active)
                if (startedStages.size > 0) {
                  const lastStartedIndex = Math.max(...Array.from(startedStages))
                  errorStage(lastStartedIndex, data.message || 'Unknown error')
                }
                throw new Error(data.message || 'Unknown error')
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e)
            }
          }
        }
      }
    } catch (error) {
      console.error('Streaming research failed:', error)
      // Mark the last stage as error if any stages were started
      if (stages.some(s => s.status === 'active' || s.status === 'complete')) {
        const lastActiveIndex = stages.length - 1
        errorStage(lastActiveIndex, error instanceof Error ? error.message : 'Unknown error')
      }
      setResults({
        sources: {},
        analysis: {},
        insights: {},
        report: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        status: 'error',
        error: error instanceof Error ? error.message : 'Unknown error'
      })
      setLoading(false)
    }
  }

  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <div className={`app-container ${sidebarOpen ? 'sidebar-open' : ''}`} role="main">
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      
      <Sidebar
        onQuerySelect={handleQuerySelect}
        demoMode={demoMode}
        onDemoModeChange={setDemoMode}
        isOpen={sidebarOpen}
        onToggle={setSidebarOpen}
      />
      
      <header className="app-header" role="banner">
        <h1>🤖 Multi-Agent AI Deep Researcher</h1>
        <p>Accessible research powered by specialized AI agents</p>
      </header>

      <main id="main-content" className="app-main">
        <ResearchForm 
          onSubmit={handleStreamingResearch} 
          loading={loading}
          disabled={loading}
          initialQuery={initialQuery}
          onQueryChange={setInitialQuery}
        />
        
        {loading && (
          <ResearchProgress stages={stages} />
        )}
        
        {results && !loading && (
          <ResearchResults data={results} />
        )}
      </main>

      <footer className="app-footer" role="contentinfo">
        <p>Multi-Agent AI Deep Researcher | Built with React, Vite, and FastAPI</p>
      </footer>
    </div>
  )
}

