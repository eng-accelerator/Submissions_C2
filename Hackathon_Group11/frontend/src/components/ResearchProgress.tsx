import React from 'react'
import { ProgressStage } from '../hooks/useResearchProgress'
import './ResearchProgress.css'

interface Props {
  stages: ProgressStage[]
}

export const ResearchProgress: React.FC<Props> = ({ stages }) => {
  const getStatusColor = (status: ProgressStage['status']) => {
    switch (status) {
      case 'complete':
        return '#10b981'  // Green
      case 'active':
        return '#3b82f6'  // Blue
      case 'error':
        return '#ef4444'  // Red
      case 'pending':
      default:
        return '#d1d5db'  // Gray
    }
  }

  const getStatusIcon = (status: ProgressStage['status']) => {
    switch (status) {
      case 'complete':
        return '✓'
      case 'active':
        return '⟳'  // Spinning
      case 'error':
        return '✕'
      case 'pending':
      default:
        return '○'
    }
  }

  const formatTime = (ms: number) => {
    const seconds = Math.floor(ms / 1000)
    return `${seconds}s`
  }

  return (
    <section
      className="research-progress"
      role="region"
      aria-label="Research progress"
      aria-live="polite"
    >
      <div className="progress-header">
        <h2>Research in Progress</h2>
        <span className="overall-progress">
          {Math.round(
            stages.reduce((acc, s) => acc + s.progress, 0) / stages.length
          )}%
        </span>
      </div>

      <div className="stages-container">
        {stages.map((stage, index) => {
          const isActive = stage.status === 'active'
          const isComplete = stage.status === 'complete'
          const duration = stage.endTime
            ? formatTime(stage.endTime - stage.startTime)
            : null

          return (
            <div
              key={index}
              className={`stage ${stage.status}`}
              role="progressbar"
              aria-valuenow={stage.progress}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-label={`${stage.name}: ${stage.message}`}
            >
              {/* Stage header */}
              <div className="stage-header">
                <div className="stage-title">
                  <span className="stage-icon">{stage.icon}</span>
                  <span className="stage-name">{stage.name}</span>
                </div>

                <div className="stage-meta">
                  <span
                    className={`status-badge ${stage.status}`}
                    aria-hidden="true"
                  >
                    {getStatusIcon(stage.status)}
                  </span>
                  {duration && (
                    <span className="stage-time" aria-label={`Duration: ${duration}`}>
                      {duration}
                    </span>
                  )}
                </div>
              </div>

              {/* Progress bar */}
              <div className="progress-bar-container">
                <div
                  className={`progress-bar ${stage.status}`}
                  style={{
                    width: `${stage.progress}%`,
                    backgroundColor: getStatusColor(stage.status),
                  }}
                  aria-hidden="true"
                >
                  {isActive && <div className="shimmer" />}
                </div>
              </div>

              {/* Message */}
              <p className={`stage-message ${stage.status}`}>
                {stage.message}
              </p>

              {/* Connector line (except last stage) */}
              {index < stages.length - 1 && (
                <div
                  className={`stage-connector ${
                    isComplete ? 'complete' : 'pending'
                  }`}
                  aria-hidden="true"
                />
              )}
            </div>
          )
        })}
      </div>

      {/* Overall status */}
      <div className="progress-footer" role="status">
        <span className="status-text">
          {stages.every((s) => s.status === 'complete')
            ? '✓ Research complete!'
            : stages.some((s) => s.status === 'error')
              ? '✕ Research encountered an error'
              : '⟳ Researching...'}
        </span>
      </div>
    </section>
  )
}

