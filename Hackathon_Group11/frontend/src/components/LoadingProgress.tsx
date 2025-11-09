import React from 'react'

interface Props {
  stage: string
  progress: number
}

const stageMessages: Record<string, string> = {
  retrieval: '🔍 Retrieving sources from web, papers, and news...',
  analysis: '📊 Analyzing findings and validating sources...',
  insights: '💡 Generating insights and hypotheses...',
  report: '📄 Compiling final report...',
  complete: '✅ Research complete!',
  error: '❌ Error occurred'
}

export const LoadingProgress: React.FC<Props> = ({ stage, progress }) => {
  const message = stageMessages[stage] || 'Processing...'

  return (
    <div 
      className="loading-progress" 
      role="status" 
      aria-live="polite"
      aria-label="Research progress"
    >
      <div className="progress-bar-container">
        <div 
          className="progress-bar" 
          style={{ width: `${progress}%` }}
          aria-valuenow={progress}
          aria-valuemin={0}
          aria-valuemax={100}
          role="progressbar"
        >
          <span className="sr-only">{progress}% complete</span>
        </div>
      </div>
      <p className="progress-message">{message}</p>
    </div>
  )
}

