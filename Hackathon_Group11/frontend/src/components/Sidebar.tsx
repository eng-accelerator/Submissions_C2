import React from 'react'
import './Sidebar.css'

interface Props {
  onQuerySelect: (query: string) => void
  demoMode: boolean
  onDemoModeChange: (enabled: boolean) => void
  isOpen: boolean
  onToggle: (open: boolean) => void
}

const DEMO_QUERIES = [
  {
    id: 'quantum_computing',
    query: 'Latest developments in quantum computing 2024',
    icon: '🔬'
  },
  {
    id: 'ai_safety',
    query: 'Current state of AI safety research and regulations',
    icon: '🛡️'
  },
  {
    id: 'climate_tech',
    query: 'Emerging climate technology solutions 2024',
    icon: '🌱'
  }
]

export const Sidebar: React.FC<Props> = ({ onQuerySelect, demoMode, onDemoModeChange, isOpen, onToggle }) => {
  const handleQueryClick = (query: string) => {
    onQuerySelect(query)
  }

  return (
    <aside className={`sidebar ${isOpen ? 'open' : 'closed'}`} role="complementary" aria-label="Settings and demo queries">
      <button
        className="sidebar-toggle"
        onClick={() => onToggle(!isOpen)}
        aria-label={isOpen ? 'Close sidebar' : 'Open sidebar'}
        aria-expanded={isOpen}
      >
        {isOpen ? '◀' : '▶'}
      </button>

      {isOpen && (
        <div className="sidebar-content">
          {/* Settings Section */}
          <div className="sidebar-section">
            <h2 className="sidebar-heading">
              <span className="sidebar-icon">⚙️</span>
              Settings
            </h2>
            <label className="demo-mode-toggle">
              <input
                type="checkbox"
                checked={demoMode}
                onChange={(e) => onDemoModeChange(e.target.checked)}
                aria-label="Use demo mode with cached results"
              />
              <span className="checkbox-label">Use Demo Mode (Cached Results)</span>
            </label>
          </div>

          <div className="sidebar-divider"></div>

          {/* Demo Queries Section */}
          <div className="sidebar-section">
            <h2 className="sidebar-heading">
              <span className="sidebar-icon">📝</span>
              Demo Queries
            </h2>
            <div className="demo-queries">
              {DEMO_QUERIES.map((item) => (
                <button
                  key={item.id}
                  className="demo-query-button"
                  onClick={() => handleQueryClick(item.query)}
                  aria-label={`Select demo query: ${item.query}`}
                >
                  <span className="query-icon">📌</span>
                  <span className="query-text">{item.query}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </aside>
  )
}

