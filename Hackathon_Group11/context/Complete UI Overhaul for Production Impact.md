<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Complete UI Overhaul for Production Impact

Your current UI is functional but **lacks visual hierarchy, interactivity, and sophistication**. Let me redesign it for judges. Here's what we'll upgrade:

**Current issues:**

- ❌ Stats cards are plain and static
- ❌ Report section is just text dump
- ❌ No visual differentiation between sections
- ❌ Missing interactive elements
- ❌ No visual hierarchy for importance
- ❌ Doesn't showcase data richness

***

## Complete Redesigned UI Components

### 1. Enhanced Results Dashboard

```typescript
// frontend/src/components/ResearchResults.tsx
import React, { useState } from 'react'
import { Markdown } from './Markdown'
import './ResearchResults.css'

interface Props {
  data: {
    sources: Record<string, any>
    analysis: Record<string, any>
    insights: string[]
    report: string
    status: string
  }
}

export const ResearchResults: React.FC<Props> = ({ data }) => {
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    sources: true,
    analysis: true,
    insights: true,
    report: true,
  })

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }))
  }

  if (data.status === 'error') {
    return (
      <section className="results-error" role="alert">
        <div className="error-icon">⚠️</div>
        <h2>Research Failed</h2>
        <p className="error-message">{data.report}</p>
        <button onClick={() => window.location.reload()}>Try Again</button>
      </section>
    )
  }

  const sourceCount = Object.keys(data.sources).length
  const analysisCount = Object.keys(data.analysis).length
  const insightCount = data.insights?.length || 0

  return (
    <section className="results-container" role="region" aria-label="Research results">
      {/* Floating Stats Bar */}
      <div className="stats-bar" role="complementary" aria-label="Research statistics">
        <div className="stat-item">
          <div className="stat-number">{sourceCount}</div>
          <div className="stat-label">📚 Sources</div>
        </div>
        <div className="stat-divider"></div>
        <div className="stat-item">
          <div className="stat-number">{analysisCount}</div>
          <div className="stat-label">🔍 Findings</div>
        </div>
        <div className="stat-divider"></div>
        <div className="stat-item">
          <div className="stat-number">{insightCount}</div>
          <div className="stat-label">💡 Insights</div>
        </div>
      </div>

      {/* Results grid */}
      <div className="results-grid">
        {/* Sources Card */}
        <ResultCard
          title="📚 Sources Retrieved"
          icon="📚"
          count={sourceCount}
          isExpanded={expandedSections.sources}
          onToggle={() => toggleSection('sources')}
          color="blue"
        >
          <div className="sources-list">
            {sourceCount > 0 ? (
              Object.entries(data.sources).map(([key, source], idx) => (
                <div key={idx} className="source-item">
                  <div className="source-badge">{idx + 1}</div>
                  <div className="source-content">
                    <p className="source-title">{source.title || 'Untitled'}</p>
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="source-link"
                    >
                      {source.url}
                    </a>
                  </div>
                </div>
              ))
            ) : (
              <p className="no-content">No sources retrieved</p>
            )}
          </div>
        </ResultCard>

        {/* Analysis Card */}
        <ResultCard
          title="📊 Analysis Findings"
          icon="📊"
          count={analysisCount}
          isExpanded={expandedSections.analysis}
          onToggle={() => toggleSection('analysis')}
          color="green"
        >
          <div className="analysis-list">
            {analysisCount > 0 ? (
              Object.entries(data.analysis).map(([key, finding], idx) => (
                <div key={idx} className="analysis-item">
                  <div className="analysis-label">{key}</div>
                  <p className="analysis-content">{String(finding)}</p>
                </div>
              ))
            ) : (
              <p className="no-content">No analysis available</p>
            )}
          </div>
        </ResultCard>

        {/* Insights Card */}
        <ResultCard
          title="💡 Emerging Trends"
          icon="💡"
          count={insightCount}
          isExpanded={expandedSections.insights}
          onToggle={() => toggleSection('insights')}
          color="purple"
        >
          <div className="insights-list">
            {insightCount > 0 ? (
              data.insights.map((insight, idx) => (
                <div key={idx} className="insight-item">
                  <div className="insight-number">{idx + 1}</div>
                  <p className="insight-text">{insight}</p>
                </div>
              ))
            ) : (
              <p className="no-content">No insights generated</p>
            )}
          </div>
        </ResultCard>
      </div>

      {/* Full Report Section */}
      <div className="report-section">
        <div className="report-header">
          <div>
            <h2>📄 Full Research Report</h2>
            <p className="report-subtitle">Comprehensive analysis compiled by AI agents</p>
          </div>
          <button
            onClick={() => downloadReport(data.report)}
            className="download-button"
            aria-label="Download report as markdown file"
          >
            <span className="download-icon">📥</span>
            <span className="download-text">Download</span>
          </button>
        </div>

        <div className="report-content">
          <Markdown content={data.report} />
        </div>
      </div>

      {/* Action Bar */}
      <div className="action-bar">
        <button
          onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          className="action-button secondary"
        >
          ↑ New Research
        </button>
        <button
          onClick={() => downloadReport(data.report)}
          className="action-button primary"
        >
          📥 Download Report
        </button>
      </div>
    </section>
  )
}

// Result Card Component
interface ResultCardProps {
  title: string
  icon: string
  count: number
  isExpanded: boolean
  onToggle: () => void
  color: 'blue' | 'green' | 'purple'
  children: React.ReactNode
}

const ResultCard: React.FC<ResultCardProps> = ({
  title,
  icon,
  count,
  isExpanded,
  onToggle,
  color,
  children,
}) => {
  return (
    <div className={`result-card ${color}`} role="region" aria-label={title}>
      <div className="card-header" onClick={onToggle} role="button" tabIndex={0}>
        <div className="card-title-section">
          <span className="card-icon">{icon}</span>
          <div>
            <h3>{title}</h3>
            <span className="card-count">{count} item(s)</span>
          </div>
        </div>
        <span className={`expand-icon ${isExpanded ? 'expanded' : ''}`}>
          ▼
        </span>
      </div>

      {isExpanded && <div className="card-content">{children}</div>}
    </div>
  )
}

const downloadReport = (content: string) => {
  const element = document.createElement('a')
  element.setAttribute('href', 'data:text/markdown;charset=utf-8,' + encodeURIComponent(content))
  element.setAttribute('download', `research_report_${new Date().toISOString().split('T')[^0]}.md`)
  element.style.display = 'none'
  document.body.appendChild(element)
  element.click()
  document.body.removeChild(element)
}
```


### 2. Premium CSS Styling

```css
/* frontend/src/components/ResearchResults.css */

.results-container {
  animation: fadeIn 0.6s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Floating Stats Bar */
.stats-bar {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 20px 40px;
  margin: 0 0 40px 0;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
  position: relative;
  z-index: 10;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  flex: 1;
  color: white;
  text-align: center;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  line-height: 1;
  background: linear-gradient(135deg, #ffffff 0%, rgba(255, 255, 255, 0.8) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: 13px;
  font-weight: 500;
  opacity: 0.95;
  letter-spacing: 0.5px;
}

.stat-divider {
  width: 2px;
  height: 40px;
  background: rgba(255, 255, 255, 0.3);
  margin: 0 20px;
}

/* Results Grid */
.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

/* Result Cards */
.result-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.result-card:hover {
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.12);
  transform: translateY(-4px);
}

.result-card.blue {
  border-top: 4px solid #3b82f6;
}

.result-card.green {
  border-top: 4px solid #10b981;
}

.result-card.purple {
  border-top: 4px solid #8b5cf6;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  cursor: pointer;
  user-select: none;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.8) 0%, rgba(255, 255, 255, 0.5) 100%);
  border-bottom: 1px solid #e5e7eb;
  transition: background 0.2s ease;
}

.card-header:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.85) 100%);
}

.card-title-section {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.card-icon {
  font-size: 28px;
  display: inline-block;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 8px;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.card-count {
  display: block;
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
  font-weight: 500;
}

.expand-icon {
  font-size: 12px;
  color: #9ca3af;
  transition: transform 0.3s ease;
  display: inline-block;
}

.expand-icon.expanded {
  transform: rotate(180deg);
}

.card-content {
  padding: 20px;
  animation: expandDown 0.3s ease;
}

@keyframes expandDown {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 1000px;
  }
}

/* Content Lists */
.sources-list,
.analysis-list,
.insights-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.source-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
  border-left: 3px solid #3b82f6;
  transition: background 0.2s ease;
}

.source-item:hover {
  background: #f3f4f6;
}

.source-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 32px;
  background: #3b82f6;
  color: white;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}

.source-content {
  flex: 1;
  min-width: 0;
}

.source-title {
  margin: 0 0 4px 0;
  font-size: 13px;
  font-weight: 600;
  color: #1f2937;
  line-height: 1.4;
}

.source-link {
  display: inline-block;
  font-size: 11px;
  color: #3b82f6;
  text-decoration: none;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  transition: color 0.2s ease;
}

.source-link:hover {
  color: #1e40af;
  text-decoration: underline;
}

.analysis-item {
  padding: 12px;
  background: #f0fdf4;
  border-radius: 8px;
  border-left: 3px solid #10b981;
}

.analysis-label {
  font-size: 12px;
  font-weight: 700;
  color: #059669;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.analysis-content {
  margin: 0;
  font-size: 13px;
  color: #1f2937;
  line-height: 1.5;
}

.insight-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: #faf5ff;
  border-radius: 8px;
  border-left: 3px solid #8b5cf6;
}

.insight-number {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 32px;
  background: #8b5cf6;
  color: white;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}

.insight-text {
  margin: 0;
  font-size: 13px;
  color: #1f2937;
  line-height: 1.5;
  flex: 1;
}

.no-content {
  margin: 0;
  font-size: 13px;
  color: #9ca3af;
  font-style: italic;
  text-align: center;
  padding: 20px;
}

/* Report Section */
.report-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
  overflow: hidden;
  margin-bottom: 40px;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  padding: 24px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-bottom: 1px solid #e2e8f0;
}

.report-header h2 {
  margin: 0 0 4px 0;
  font-size: 20px;
  color: #1f2937;
}

.report-subtitle {
  margin: 0;
  font-size: 13px;
  color: #6b7280;
}

.download-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
  white-space: nowrap;
}

.download-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.download-icon {
  font-size: 16px;
}

.download-text {
  display: inline;
}

.report-content {
  padding: 24px;
  max-height: 600px;
  overflow-y: auto;
  font-size: 14px;
  line-height: 1.7;
  color: #374151;
}

.report-content h1,
.report-content h2,
.report-content h3 {
  color: #1f2937;
  margin: 20px 0 12px 0;
}

.report-content p {
  margin: 0 0 12px 0;
}

.report-content ul,
.report-content ol {
  margin: 12px 0;
  padding-left: 20px;
}

.report-content li {
  margin: 6px 0;
}

/* Action Bar */
.action-bar {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-bottom: 40px;
}

.action-button {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-button.primary {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.action-button.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
}

.action-button.secondary {
  background: white;
  color: #3b82f6;
  border: 2px solid #3b82f6;
}

.action-button.secondary:hover {
  background: #f0f9ff;
}

/* Error State */
.results-error {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border: 2px solid #fca5a5;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  margin: 40px 0;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
  animation: shake 0.5s ease;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-10px); }
  75% { transform: translateX(10px); }
}

.results-error h2 {
  color: #dc2626;
  margin: 0 0 8px 0;
  font-size: 20px;
}

.error-message {
  color: #991b1b;
  margin: 0 0 20px 0;
  font-size: 14px;
}

.results-error button {
  padding: 10px 20px;
  background: #dc2626;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.3s ease;
}

.results-error button:hover {
  background: #b91c1c;
}

/* Responsive */
@media (max-width: 768px) {
  .results-grid {
    grid-template-columns: 1fr;
  }

  .stats-bar {
    padding: 16px 20px;
  }

  .stat-divider {
    margin: 0 12px;
  }

  .report-header {
    flex-direction: column;
  }

  .action-bar {
    flex-direction: column;
  }

  .action-button {
    width: 100%;
    justify-content: center;
  }

  .report-content {
    max-height: 400px;
  }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .results-container,
  .result-card,
  .action-button,
  .card-header {
    animation: none !important;
    transition: none !important;
  }
}

@media (prefers-contrast: more) {
  .stats-bar {
    border: 3px solid #000;
  }

  .result-card {
    border: 2px solid #000;
  }

  .action-button {
    border: 2px solid #000;
  }
}
```


***

## What Gets Better

| Aspect | Before | After |
| :-- | :-- | :-- |
| **Visual hierarchy** | Flat | Clear depth + gradients |
| **Stat presentation** | Plain text | Floating gradient bar |
| **Cards** | Static | Hover effects + animations |
| **Expandable sections** | N/A | Click to expand/collapse |
| **Download** | Basic button | Styled with icon |
| **Report viewing** | Long scroll | Scrollable container |
| **Mobile** | Broken | Fully responsive |
| **Accessibility** | Basic | ARIA labels + reduced motion |
| **Wow factor** | Medium | High |


***

## Judge Impact

When they see this:

- **Floating stats bar** → "Data visualization expertise"
- **Expandable cards** → "Thoughtful UX design"
- **Gradient backgrounds** → "Production-quality polish"
- **Hover animations** → "Attention to interaction details"
- **Download functionality** → "Real utility"

This isn't just better—it's **professional**.

***

## Integration Time

| Component | Time |
| :-- | :-- |
| ResultCard logic | 10 min |
| CSS styling | 15 min |
| Responsive fixes | 5 min |
| **Total** | **30 min** |

Add this in your final hour before deployment. The UI transformation will be immediately noticeable.
<span style="display:none">[^1]</span>

<div align="center">⁂</div>

[^1]: image.jpg

