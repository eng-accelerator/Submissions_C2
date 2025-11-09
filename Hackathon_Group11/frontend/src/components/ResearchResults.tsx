import React, { useState, useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { ResearchData } from '../App'
import { TextToSpeechControls } from './TextToSpeechControls'
import { ResearchMetrics } from './ResearchMetrics'
import './ResearchResults.css'

interface Props {
  data: ResearchData
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
      <div 
        className="card-header" 
        onClick={onToggle} 
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault()
            onToggle()
          }
        }}
        role="button" 
        tabIndex={0}
        aria-expanded={isExpanded}
      >
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

const downloadReportMD = (content: string) => {
  const element = document.createElement('a')
  const blob = new Blob([content], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  element.setAttribute('href', url)
  const timestamp = new Date().toISOString().split('T')[0]
  element.setAttribute('download', `research_report_${timestamp}.md`)
  element.style.display = 'none'
  document.body.appendChild(element)
  element.click()
  document.body.removeChild(element)
  URL.revokeObjectURL(url)
}

// Process report to ensure sources are clickable links
const processReportSources = (report: string, sources: Record<string, any>): string => {
  if (!report || !sources) return report
  
  // Collect all source URLs
  const sourceMap: Record<string, string> = {}
  
  Object.values(sources).forEach((sourceArray) => {
    if (Array.isArray(sourceArray)) {
      sourceArray.forEach((source: any) => {
        if (source?.title && source?.url) {
          sourceMap[source.title] = source.url
        }
      })
    }
  })
  
  // Convert sources to markdown links if they're not already links
  let processedReport = report
  
  // Pattern: "1. Title" or "Title" followed by URL on next line
  Object.entries(sourceMap).forEach(([title, url]) => {
    // If title is not already a markdown link, convert it
    const titlePattern = new RegExp(`(\\d+\\.\\s*)(${title.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})(?!\\]\\()`, 'g')
    if (titlePattern.test(processedReport)) {
      // Replace with markdown link
      processedReport = processedReport.replace(
        titlePattern,
        `$1[$2](${url})`
      )
    }
    
    // Also handle cases where URL is on a separate line
    const urlPattern = new RegExp(`(${title.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})\\s*\\n\\s*(${url.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'g')
    processedReport = processedReport.replace(
      urlPattern,
      `[$1]($2)`
    )
  })
  
  return processedReport
}

const downloadReportPDF = (content: string) => {
  // Convert markdown to HTML for PDF
  const convertMarkdownToHTML = (md: string): string => {
    let html = md
    const lines = html.split('\n')
    const htmlLines: string[] = []
    let inList = false
    
    for (let i = 0; i < lines.length; i++) {
      let line = lines[i]
      const trimmed = line.trim()
      
      // Headers
      if (trimmed.match(/^#{1,6}\s/)) {
        if (inList) {
          htmlLines.push('</ul>')
          inList = false
        }
        const level = trimmed.match(/^(#{1,6})/)?.[1].length || 1
        const text = trimmed.replace(/^#{1,6}\s/, '')
        htmlLines.push(`<h${level}>${text}</h${level}>`)
        continue
      }
      
      // Lists
      if (trimmed.match(/^[-*]\s/)) {
        if (!inList) {
          htmlLines.push('<ul>')
          inList = true
        }
        const text = trimmed.replace(/^[-*]\s/, '')
        htmlLines.push(`<li>${text}</li>`)
        continue
      } else if (inList) {
        htmlLines.push('</ul>')
        inList = false
      }
      
      // Paragraphs
      if (trimmed) {
        // Bold
        line = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // Italic
        line = line.replace(/\*(.*?)\*/g, '<em>$1</em>')
        // Code
        line = line.replace(/`([^`]+)`/g, '<code>$1</code>')
        htmlLines.push(`<p>${line}</p>`)
      } else {
        htmlLines.push('<br>')
      }
    }
    
    if (inList) {
      htmlLines.push('</ul>')
    }
    
    return htmlLines.join('\n')
  }
  
  const htmlContent = `
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="UTF-8">
        <title>Research Report</title>
        <style>
          @media print {
            @page {
              margin: 2cm;
            }
          }
          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
          }
          h1, h2, h3, h4, h5, h6 {
            color: #1f2937;
            margin-top: 24px;
            margin-bottom: 12px;
            page-break-after: avoid;
          }
          h1 { font-size: 28px; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px; }
          h2 { font-size: 24px; }
          h3 { font-size: 20px; }
          p { margin: 12px 0; }
          ul, ol { margin: 12px 0; padding-left: 30px; }
          li { margin: 6px 0; page-break-inside: avoid; }
          code {
            background: #f3f4f6;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 13px;
            font-family: 'Courier New', monospace;
          }
          pre {
            background: #1f2937;
            color: #f9fafb;
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 16px 0;
            page-break-inside: avoid;
          }
          pre code {
            background: transparent;
            padding: 0;
          }
          blockquote {
            border-left: 4px solid #3b82f6;
            padding-left: 16px;
            margin: 16px 0;
            color: #6b7280;
            font-style: italic;
          }
          table {
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
          }
          th, td {
            border: 1px solid #e5e7eb;
            padding: 8px 12px;
            text-align: left;
          }
          th {
            background: #f3f4f6;
            font-weight: 600;
          }
        </style>
      </head>
      <body>
        ${convertMarkdownToHTML(content)}
      </body>
    </html>
  `
  
  // Open print dialog for PDF (user can save as PDF)
  const printWindow = window.open('', '_blank')
  if (printWindow) {
    printWindow.document.write(htmlContent)
    printWindow.document.close()
    printWindow.onload = () => {
      // Small delay to ensure content is rendered
      setTimeout(() => {
        printWindow.print()
      }, 250)
    }
  }
}

export const ResearchResults: React.FC<Props> = ({ data }) => {
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    sources: true,
    analysis: true,
    insights: true,
    report: true,
  })
  const headerDropdownRef = useRef<HTMLDivElement>(null)

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }))
  }

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Node
      if (
        headerDropdownRef.current && 
        !headerDropdownRef.current.contains(target)
      ) {
        const menus = document.querySelectorAll('.download-menu')
        menus.forEach(menu => menu.classList.remove('show'))
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  if (data.status === 'error') {
    return (
      <section className="results-error" role="alert">
        <div className="error-icon">⚠️</div>
        <h2>Research Failed</h2>
        <p className="error-message">{data.report || data.error || 'An unknown error occurred'}</p>
        <button onClick={() => window.location.reload()}>Try Again</button>
      </section>
    )
  }

  // Calculate counts
  const sourcesCount = Object.values(data.sources || {}).reduce(
    (acc, sources) => acc + (Array.isArray(sources) ? sources.length : 0),
    0
  )
  
  const analysisCount = data.analysis 
    ? Object.keys(data.analysis).reduce((acc, key) => {
        const value = data.analysis[key]
        return acc + (Array.isArray(value) ? value.length : value ? 1 : 0)
      }, 0)
    : 0
  
  const insightCount = data.insights?.insights?.length || 0

  // Get sources list
  const sourcesList: Array<{ title: string; url: string; snippet?: string }> = []
  if (data.sources) {
    Object.values(data.sources).forEach((sourceArray) => {
      if (Array.isArray(sourceArray)) {
        sourceArray.forEach((source: any) => {
          if (source && (source.url || source.title)) {
            sourcesList.push({
              title: source.title || 'Untitled',
              url: source.url || '',
              snippet: source.snippet || source.summary || '',
            })
          }
        })
      }
    })
  }

  // Get analysis items
  const analysisItems: Array<{ key: string; value: string }> = []
  if (data.analysis) {
    Object.entries(data.analysis).forEach(([key, value]) => {
      if (value) {
        if (Array.isArray(value)) {
          value.forEach((item) => {
            analysisItems.push({ key, value: String(item) })
          })
        } else {
          analysisItems.push({ key, value: String(value) })
        }
      }
    })
  }

  // Get insights list
  const insightsList = data.insights?.insights || []

  return (
    <section className="results-container" role="region" aria-label="Research results">
      {/* Research Metrics */}
      <ResearchMetrics data={data} />
      
      {/* Floating Stats Bar */}
      <div className="stats-bar" role="complementary" aria-label="Research statistics">
        <div className="stat-item">
          <div className="stat-number">{sourcesCount}</div>
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
          count={sourcesCount}
          isExpanded={expandedSections.sources}
          onToggle={() => toggleSection('sources')}
          color="blue"
        >
          <div className="sources-list">
            {sourcesList.length > 0 ? (
              sourcesList.map((source, idx) => (
                <div key={idx} className="source-item">
                  <div className="source-badge">{idx + 1}</div>
                  <div className="source-content">
                    <p className="source-title">{source.title}</p>
                    {source.url && (
                      <a
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="source-link"
                      >
                        {source.url}
                      </a>
                    )}
                    {source.snippet && (
                      <p className="source-snippet">{source.snippet.substring(0, 150)}...</p>
                    )}
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
            {analysisItems.length > 0 ? (
              analysisItems.map((item, idx) => (
                <div key={idx} className="analysis-item">
                  <div className="analysis-label">{item.key}</div>
                  <p className="analysis-content">{item.value}</p>
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
            {insightsList.length > 0 ? (
              insightsList.map((insight: any, idx: number) => (
                <div key={idx} className="insight-item">
                  <div className="insight-number">{idx + 1}</div>
                  <p className="insight-text">{String(insight)}</p>
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
          <div className="download-options">
            <div className="download-dropdown" ref={headerDropdownRef}>
              <button
                className="download-button primary"
                aria-label="Download options"
                onClick={(e) => {
                  e.stopPropagation()
                  const dropdown = e.currentTarget.nextElementSibling as HTMLElement
                  dropdown?.classList.toggle('show')
                }}
              >
                <span className="download-icon">📥</span>
                <span className="download-text">Download</span>
                <span className="dropdown-arrow">▼</span>
              </button>
              <div className="download-menu">
                <button
                  onClick={() => {
                    downloadReportMD(data.report || '')
                    const menu = document.querySelector('.download-menu') as HTMLElement
                    menu?.classList.remove('show')
                  }}
                  className="download-option"
                  aria-label="Download as Markdown"
                >
                  <span className="option-icon">📄</span>
                  <span>Download as Markdown (.md)</span>
                </button>
                <button
                  onClick={() => {
                    downloadReportPDF(data.report || '')
                    const menu = document.querySelector('.download-menu') as HTMLElement
                    menu?.classList.remove('show')
                  }}
                  className="download-option"
                  aria-label="Download as PDF"
                >
                  <span className="option-icon">📑</span>
                  <span>Download as PDF (.pdf)</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Text-to-Speech Controls */}
        <div className="report-tts-section">
          <TextToSpeechControls
            text={data.report || ''}
            title="Listen to Report"
          />
        </div>

        <div className="report-content">
          <ReactMarkdown 
            remarkPlugins={[remarkGfm]}
            className="markdown-content"
            components={{
              // Custom link component to ensure links open in new tab
              a: ({ node, ...props }) => (
                <a {...props} target="_blank" rel="noopener noreferrer" />
              ),
            }}
          >
            {processReportSources(data.report || '', data.sources || {})}
          </ReactMarkdown>
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
      </div>
    </section>
  )
}
