import React, { useState, useEffect } from 'react'
import { useTextToSpeech } from '../hooks/useTextToSpeech'
import { useKeyboardShortcuts } from '../hooks/useKeyboardShortcuts'
import './TextToSpeechControls.css'

interface Props {
  text: string
  title?: string
}

export const TextToSpeechControls: React.FC<Props> = ({
  text,
}) => {
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([])
  const [selectedVoiceIndex, setSelectedVoiceIndex] = useState(0)
  const [rate, setRate] = useState(1)
  const [showSettings, setShowSettings] = useState(false)

  const {
    isSupported,
    isPlaying,
    isPaused,
    progress,
    speak,
    pause,
    resume,
    stop,
    getAvailableVoices,
    setVoice,
  } = useTextToSpeech({
    rate: rate,
    pitch: 1,
    volume: 1,
    lang: 'en-US',
  })

  // Load available voices
  useEffect(() => {
    if (!isSupported) return

    const loadVoices = () => {
      const availableVoices = getAvailableVoices()
      setVoices(availableVoices)
      // Set default voice
      if (availableVoices.length > 0) {
        const defaultVoice = availableVoices.findIndex(v => v.default) || 0
        setSelectedVoiceIndex(defaultVoice >= 0 ? defaultVoice : 0)
      }
    }

    // Voices might not be loaded immediately
    loadVoices()
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.onvoiceschanged = loadVoices
    }

    return () => {
      if (typeof window !== 'undefined' && window.speechSynthesis) {
        window.speechSynthesis.onvoiceschanged = null
      }
    }
  }, [isSupported, getAvailableVoices])

  const handleVoiceChange = (index: number) => {
    setSelectedVoiceIndex(index)
    setVoice(index)
  }

  const handlePlayClick = () => {
    if (isPlaying) {
      pause()
    } else if (isPaused) {
      resume()
    } else {
      // Clean text for better TTS
      const cleanText = text
        .replace(/\[.*?\]\(.*?\)/g, '') // Remove markdown links
        .replace(/#{1,6}\s/g, '') // Remove headers
        .replace(/\*\*/g, '') // Remove bold markers
        .replace(/\*/g, '') // Remove italic markers
        .replace(/`/g, '') // Remove code markers
        .replace(/\n{3,}/g, '\n\n') // Normalize multiple newlines
        .trim()

      if (cleanText) {
        speak(cleanText)
      }
    }
  }

  // Keyboard shortcuts
  useKeyboardShortcuts({
    onPlayPause: handlePlayClick,
    onStop: stop,
    onSettings: () => setShowSettings(!showSettings),
  }, !showSettings)

  if (!isSupported) {
    return (
      <div className="tts-unavailable" role="status">
        <span className="warning-icon">⚠️</span>
        <p>Text-to-Speech is not supported in your browser</p>
      </div>
    )
  }

  return (
    <div className="tts-container" role="region" aria-label="Text-to-speech controls">
      {/* Main Controls */}
      <div className="tts-main">
        <button
          onClick={handlePlayClick}
          className={`tts-button play-button ${isPlaying ? 'playing' : ''}`}
          aria-label={isPlaying ? 'Pause audio' : 'Play audio'}
          title={isPlaying ? 'Pause' : 'Play'}
        >
          <span className="play-icon">
            {isPlaying && !isPaused ? '⏸' : '▶'}
          </span>
          <span className="play-text">
            {isPlaying && !isPaused ? 'Pause' : isPlaying && isPaused ? 'Resume' : 'Listen'}
          </span>
        </button>

        {isPlaying && (
          <button
            onClick={stop}
            className="tts-button stop-button"
            aria-label="Stop audio"
            title="Stop"
          >
            <span className="stop-icon">⏹</span>
          </button>
        )}

        <button
          onClick={() => setShowSettings(!showSettings)}
          className={`tts-button settings-button ${showSettings ? 'active' : ''}`}
          aria-label="Show audio settings"
          title="Settings"
        >
          <span className="settings-icon">⚙️</span>
        </button>
      </div>

      {/* Progress Bar */}
      {isPlaying && (
        <div className="tts-progress">
          <div
            className="progress-fill"
            style={{ width: `${progress}%` }}
            role="progressbar"
            aria-valuenow={Math.round(progress)}
            aria-valuemin={0}
            aria-valuemax={100}
          >
            <div className="progress-indicator" />
          </div>
          <span className="progress-text">{Math.round(progress)}%</span>
        </div>
      )}

      {/* Settings Panel */}
      {showSettings && (
        <div className="tts-settings" role="region" aria-label="Audio settings">
          {/* Voice Selection */}
          {voices.length > 0 && (
            <div className="setting-group">
              <label htmlFor="voice-select" className="setting-label">
                🎤 Voice
              </label>
              <select
                id="voice-select"
                value={selectedVoiceIndex}
                onChange={(e) => handleVoiceChange(parseInt(e.target.value))}
                className="setting-select"
                aria-label="Select voice for text-to-speech"
              >
                {voices.map((voice, idx) => (
                  <option key={idx} value={idx}>
                    {voice.name} {voice.default ? '(Default)' : ''}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Speed Control */}
          <div className="setting-group">
            <label htmlFor="speed-slider" className="setting-label">
              🚀 Speed: {rate}x
            </label>
            <input
              id="speed-slider"
              type="range"
              min="0.5"
              max="2"
              step="0.1"
              value={rate}
              onChange={(e) => setRate(parseFloat(e.target.value))}
              className="setting-slider"
              aria-label="Adjust playback speed"
            />
            <div className="speed-presets">
              {[0.75, 1, 1.25, 1.5].map((speed) => (
                <button
                  key={speed}
                  onClick={() => setRate(speed)}
                  className={`preset-btn ${rate === speed ? 'active' : ''}`}
                >
                  {speed}x
                </button>
              ))}
            </div>
          </div>

          {/* Info */}
          <div className="setting-info">
            <p className="info-text">
              💡 <strong>Tip:</strong> Use your keyboard:
            </p>
            <ul className="keyboard-shortcuts">
              <li><code>Space</code> - Play/Pause</li>
              <li><code>Esc</code> - Stop</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}

