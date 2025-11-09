import { useState } from 'react'

export interface ProgressStage {
  name: string
  icon: string
  status: 'pending' | 'active' | 'complete' | 'error'
  message: string
  progress: number  // 0-100
  startTime: number
  endTime?: number
}

export const useResearchProgress = () => {
  const [stages, setStages] = useState<ProgressStage[]>([
    {
      name: 'Retriever',
      icon: '🔍',
      status: 'pending',
      message: 'Preparing to fetch sources...',
      progress: 0,
      startTime: 0,
    },
    {
      name: 'Enricher',
      icon: '📊',
      status: 'pending',
      message: 'Waiting for sources...',
      progress: 0,
      startTime: 0,
    },
    {
      name: 'Analyzer',
      icon: '🔬',
      status: 'pending',
      message: 'Waiting for enrichment...',
      progress: 0,
      startTime: 0,
    },
    {
      name: 'Insight',
      icon: '💡',
      status: 'pending',
      message: 'Waiting for analysis...',
      progress: 0,
      startTime: 0,
    },
    {
      name: 'Reporter',
      icon: '📄',
      status: 'pending',
      message: 'Waiting for insights...',
      progress: 0,
      startTime: 0,
    },
  ])

  const updateStage = (
    stageIndex: number,
    updates: Partial<ProgressStage>
  ) => {
    setStages((prev) =>
      prev.map((stage, idx) =>
        idx === stageIndex ? { ...stage, ...updates } : stage
      )
    )
  }

  const startStage = (stageIndex: number) => {
    updateStage(stageIndex, {
      status: 'active',
      startTime: Date.now(),
      progress: 10, // Start animation
    })
  }

  const completeStage = (stageIndex: number, message?: string) => {
    updateStage(stageIndex, {
      status: 'complete',
      progress: 100,
      endTime: Date.now(),
      message: message || 'Complete',
    })
  }

  const errorStage = (stageIndex: number, error: string) => {
    updateStage(stageIndex, {
      status: 'error',
      message: error,
      progress: 0,
    })
  }

  const resetStages = () => {
    setStages([
      {
        name: 'Retriever',
        icon: '🔍',
        status: 'pending',
        message: 'Preparing to fetch sources...',
        progress: 0,
        startTime: 0,
      },
      {
        name: 'Enricher',
        icon: '📊',
        status: 'pending',
        message: 'Waiting for sources...',
        progress: 0,
        startTime: 0,
      },
      {
        name: 'Analyzer',
        icon: '🔬',
        status: 'pending',
        message: 'Waiting for enrichment...',
        progress: 0,
        startTime: 0,
      },
      {
        name: 'Insight',
        icon: '💡',
        status: 'pending',
        message: 'Waiting for analysis...',
        progress: 0,
        startTime: 0,
      },
      {
        name: 'Reporter',
        icon: '📄',
        status: 'pending',
        message: 'Waiting for insights...',
        progress: 0,
        startTime: 0,
      },
    ])
  }

  return {
    stages,
    updateStage,
    startStage,
    completeStage,
    errorStage,
    resetStages,
  }
}

