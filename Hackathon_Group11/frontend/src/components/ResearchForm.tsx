import React, { useState, useEffect } from 'react'
import { VoiceInput } from './VoiceInput'
import './ResearchForm.css'

type InputMode = 'text' | 'voice'

interface Props {
  onSubmit: (query: string) => void
  loading: boolean
  disabled?: boolean
  initialQuery?: string
  onQueryChange?: (query: string) => void
}

export const ResearchForm: React.FC<Props> = ({ 
  onSubmit, 
  loading, 
  disabled = false,
  initialQuery = '',
  onQueryChange
}) => {
  const [query, setQuery] = useState(initialQuery)
  const [inputMode, setInputMode] = useState<InputMode>('text')

  // Update query when initialQuery changes (from sidebar demo queries)
  useEffect(() => {
    if (initialQuery) {
      setQuery(initialQuery)
    }
  }, [initialQuery])

  const handleQueryChange = (value: string) => {
    setQuery(value)
    if (onQueryChange) {
      onQueryChange(value)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim() && !loading) {
      onSubmit(query)
    }
  }

  const handleVoiceCapture = (text: string) => {
    handleQueryChange(text)
    // Auto-submit after voice capture (optional - you can remove this if you want manual submit)
    // if (text.trim() && !loading) {
    //   onSubmit(text)
    // }
  }

  return (
    <form onSubmit={handleSubmit} className="research-form" role="search" aria-label="Research query form">
      <label htmlFor="query-input" className="form-label">
        What would you like to research?
      </label>
      
      {/* Input Mode Toggle */}
      <div className="input-mode-toggle" role="tablist" aria-label="Input method selection">
        <button
          type="button"
          className={`mode-button ${inputMode === 'text' ? 'active' : ''}`}
          onClick={() => setInputMode('text')}
          aria-pressed={inputMode === 'text'}
          aria-label="Switch to text input mode"
          disabled={loading || disabled}
        >
          <span className="mode-icon">⌨️</span>
          <span className="mode-text">Type</span>
        </button>
        <button
          type="button"
          className={`mode-button ${inputMode === 'voice' ? 'active' : ''}`}
          onClick={() => setInputMode('voice')}
          aria-pressed={inputMode === 'voice'}
          aria-label="Switch to voice input mode"
          disabled={loading || disabled}
        >
          <span className="mode-icon">🎤</span>
          <span className="mode-text">Speak</span>
        </button>
      </div>
      
      {/* Voice Input Section */}
      {inputMode === 'voice' && (
        <div className="voice-input-container">
          <VoiceInput 
            onVoiceCapture={handleVoiceCapture}
            disabled={loading || disabled}
          />
          {query && (
            <div className="captured-query">
              <p className="captured-label">Captured query:</p>
              <p className="captured-text">{query}</p>
            </div>
          )}
        </div>
      )}
      
      {/* Text Input Section */}
      {inputMode === 'text' && (
        <div className="text-input-container">
          <input
            id="query-input"
            type="text"
            value={query}
            onChange={(e) => handleQueryChange(e.target.value)}
            placeholder="e.g., Latest developments in quantum computing 2024"
            disabled={loading || disabled}
            aria-busy={loading}
            aria-describedby="query-hint"
            aria-required="true"
            className="query-input"
            autoComplete="off"
          />
          <p id="query-hint" className="form-hint">
            Enter your research topic. Results will appear below.
          </p>
        </div>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        disabled={loading || !query.trim() || disabled}
        aria-label={loading ? 'Research in progress, please wait' : 'Start research'}
        aria-busy={loading}
        className="submit-button"
      >
        {loading ? '⏳ Researching...' : '🔍 Start Research'}
      </button>
    </form>
  )
}

