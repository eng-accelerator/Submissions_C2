import React from 'react'
import { ResearchData } from '../App'
import './ResearchMetrics.css'

interface Props {
  data: ResearchData
}

export const ResearchMetrics: React.FC<Props> = ({ data }) => {
  const sources = data.sources || {}
  const metadata = sources.metadata || {}
  
  // Collect enriched data from sources
  const enrichedSources: Array<{
    title: string
    domain_score?: number
    sentiment?: { label: string; score: number }
    category?: string
    url?: string
  }> = []
  
  // Extract enriched data from web and news sources
  Object.values(sources).forEach((sourceArray) => {
    if (Array.isArray(sourceArray)) {
      sourceArray.forEach((source: any) => {
        if (source && (source.domain_score !== undefined || source.sentiment || source.category)) {
          enrichedSources.push({
            title: source.title || 'Untitled',
            domain_score: source.domain_score,
            sentiment: source.sentiment,
            category: source.category,
            url: source.url,
          })
        }
      })
    }
  })
  
  // Calculate statistics
  const totalSources = metadata.total_sources || enrichedSources.length
  const enrichmentApplied = metadata.enrichment_applied || false
  
  // Sentiment distribution
  const sentimentCounts = {
    positive: 0,
    negative: 0,
    neutral: 0,
  }
  
  enrichedSources.forEach((source) => {
    if (source.sentiment) {
      const label = source.sentiment.label
      if (label === 'positive') sentimentCounts.positive++
      else if (label === 'negative') sentimentCounts.negative++
      else sentimentCounts.neutral++
    }
  })
  
  // Category distribution
  const categoryCounts: Record<string, number> = {}
  enrichedSources.forEach((source) => {
    if (source.category) {
      categoryCounts[source.category] = (categoryCounts[source.category] || 0) + 1
    }
  })
  
  // Average domain score
  const domainScores = enrichedSources
    .map((s) => s.domain_score)
    .filter((score): score is number => score !== undefined)
  const avgDomainScore = domainScores.length > 0
    ? domainScores.reduce((a, b) => a + b, 0) / domainScores.length
    : 0
  
  // Quality breakdown
  const highQuality = domainScores.filter((s) => s >= 0.8).length
  const mediumQuality = domainScores.filter((s) => s >= 0.5 && s < 0.8).length
  const lowQuality = domainScores.filter((s) => s < 0.5).length
  
  if (!enrichmentApplied && enrichedSources.length === 0) {
    return (
      <div className="research-metrics">
        <div className="metrics-placeholder">
          <p>📊 Enrichment metrics will appear here after research completes</p>
          <p className="hint">Source enrichment adds metadata, sentiment, and quality scores</p>
        </div>
      </div>
    )
  }
  
  return (
    <div className="research-metrics" role="region" aria-label="Research metrics">
      <h2 className="metrics-title">📈 Research Metrics</h2>
      
      {/* Summary Cards */}
      <div className="metrics-summary">
        <div className="metric-card">
          <div className="metric-icon">📚</div>
          <div className="metric-value">{totalSources}</div>
          <div className="metric-label">Total Sources</div>
        </div>
        
        <div className="metric-card">
          <div className="metric-icon">⭐</div>
          <div className="metric-value">{avgDomainScore.toFixed(2)}</div>
          <div className="metric-label">Avg Domain Score</div>
        </div>
        
        <div className="metric-card">
          <div className="metric-icon">✅</div>
          <div className="metric-value">{enrichmentApplied ? 'Yes' : 'No'}</div>
          <div className="metric-label">Enrichment Applied</div>
        </div>
      </div>
      
      {/* Sentiment Analysis */}
      {sentimentCounts.positive + sentimentCounts.negative + sentimentCounts.neutral > 0 && (
        <div className="metrics-section">
          <h3 className="section-title">📊 Sentiment Analysis</h3>
          <div className="sentiment-chart">
            <div className="sentiment-bar">
              <div 
                className="sentiment-fill positive" 
                style={{ width: `${(sentimentCounts.positive / totalSources) * 100}%` }}
                title={`Positive: ${sentimentCounts.positive}`}
              />
              <div 
                className="sentiment-fill neutral" 
                style={{ width: `${(sentimentCounts.neutral / totalSources) * 100}%` }}
                title={`Neutral: ${sentimentCounts.neutral}`}
              />
              <div 
                className="sentiment-fill negative" 
                style={{ width: `${(sentimentCounts.negative / totalSources) * 100}%` }}
                title={`Negative: ${sentimentCounts.negative}`}
              />
            </div>
            <div className="sentiment-legend">
              <span className="legend-item">
                <span className="legend-color positive"></span>
                Positive: {sentimentCounts.positive}
              </span>
              <span className="legend-item">
                <span className="legend-color neutral"></span>
                Neutral: {sentimentCounts.neutral}
              </span>
              <span className="legend-item">
                <span className="legend-color negative"></span>
                Negative: {sentimentCounts.negative}
              </span>
            </div>
          </div>
        </div>
      )}
      
      {/* Category Distribution */}
      {Object.keys(categoryCounts).length > 0 && (
        <div className="metrics-section">
          <h3 className="section-title">🏷️ Category Distribution</h3>
          <div className="category-list">
            {Object.entries(categoryCounts)
              .sort(([, a], [, b]) => b - a)
              .map(([category, count]) => (
                <div key={category} className="category-item">
                  <span className="category-name">{category}</span>
                  <div className="category-bar">
                    <div 
                      className="category-fill" 
                      style={{ width: `${(count / totalSources) * 100}%` }}
                    />
                  </div>
                  <span className="category-count">{count}</span>
                </div>
              ))}
          </div>
        </div>
      )}
      
      {/* Source Quality Breakdown */}
      {domainScores.length > 0 && (
        <div className="metrics-section">
          <h3 className="section-title">⭐ Source Quality Breakdown</h3>
          <div className="quality-breakdown">
            <div className="quality-item">
              <span className="quality-label">High Quality (≥0.8)</span>
              <div className="quality-bar">
                <div 
                  className="quality-fill high" 
                  style={{ width: `${(highQuality / domainScores.length) * 100}%` }}
                />
              </div>
              <span className="quality-count">{highQuality}</span>
            </div>
            <div className="quality-item">
              <span className="quality-label">Medium Quality (0.5-0.8)</span>
              <div className="quality-bar">
                <div 
                  className="quality-fill medium" 
                  style={{ width: `${(mediumQuality / domainScores.length) * 100}%` }}
                />
              </div>
              <span className="quality-count">{mediumQuality}</span>
            </div>
            <div className="quality-item">
              <span className="quality-label">Low Quality (&lt;0.5)</span>
              <div className="quality-bar">
                <div 
                  className="quality-fill low" 
                  style={{ width: `${(lowQuality / domainScores.length) * 100}%` }}
                />
              </div>
              <span className="quality-count">{lowQuality}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

