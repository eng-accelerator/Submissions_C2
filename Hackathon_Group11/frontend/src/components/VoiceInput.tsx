import React, { useState, useEffect, useRef } from 'react'
import './VoiceInput.css'

// TypeScript declarations for Web Speech API
interface SpeechRecognition extends EventTarget {
  continuous: boolean
  interimResults: boolean
  lang: string
  start(): void
  stop(): void
  onresult: ((event: SpeechRecognitionEvent) => void) | null
  onerror: ((event: SpeechRecognitionErrorEvent) => void) | null
  onend: (() => void) | null
}

interface SpeechRecognitionEvent {
  resultIndex: number
  results: SpeechRecognitionResultList
}

interface SpeechRecognitionResultList {
  length: number
  item(index: number): SpeechRecognitionResult
  [index: number]: SpeechRecognitionResult
}

interface SpeechRecognitionResult {
  length: number
  item(index: number): SpeechRecognitionAlternative
  [index: number]: SpeechRecognitionAlternative
  isFinal: boolean
}

interface SpeechRecognitionAlternative {
  transcript: string
  confidence: number
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string
  message: string
}

declare global {
  interface Window {
    SpeechRecognition: {
      new (): SpeechRecognition
    }
    webkitSpeechRecognition: {
      new (): SpeechRecognition
    }
  }
}

interface Props {
  onVoiceCapture: (text: string) => void
  disabled?: boolean
}

export const VoiceInput: React.FC<Props> = ({ onVoiceCapture, disabled = false }) => {
  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [error, setError] = useState<string | null>(null)
  const recognitionRef = useRef<SpeechRecognition | null>(null)

  // Check if browser supports Web Speech API
  const isSupported = typeof window !== 'undefined' && 
    (window.SpeechRecognition || (window as any).webkitSpeechRecognition)

  useEffect(() => {
    // Cleanup on unmount
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop()
        recognitionRef.current = null
      }
    }
  }, [])

  const handleVoiceInput = async () => {
    if (disabled || !isSupported) return
    
    try {
      setIsListening(true)
      setError(null)
      setTranscript('')
      
      // Get SpeechRecognition class
      const SpeechRecognition = window.SpeechRecognition || (window as any).webkitSpeechRecognition
      const recognition = new SpeechRecognition()
      
      // Configure recognition
      recognition.continuous = false
      recognition.interimResults = true
      recognition.lang = 'en-US'
      
      // Store reference for cleanup
      recognitionRef.current = recognition
      
      // Handle results
      recognition.onresult = (event: SpeechRecognitionEvent) => {
        let interimTranscript = ''
        let finalTranscript = ''
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript
          if (event.results[i].isFinal) {
            finalTranscript += transcript + ' '
          } else {
            interimTranscript += transcript
          }
        }
        
        // Update transcript display
        setTranscript(finalTranscript || interimTranscript)
        
        // If we have final results, use them
        if (finalTranscript) {
          const finalText = finalTranscript.trim()
          setTranscript(finalText)
          onVoiceCapture(finalText)
          setIsListening(false)
        }
      }
      
      // Handle errors
      recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
        let errorMessage = 'Speech recognition error'
        
        switch (event.error) {
          case 'no-speech':
            errorMessage = 'No speech detected. Please try again.'
            break
          case 'audio-capture':
            errorMessage = 'No microphone found. Please check your microphone.'
            break
          case 'not-allowed':
            errorMessage = 'Microphone permission denied. Please allow microphone access.'
            break
          case 'network':
            errorMessage = 'Network error. Please check your connection.'
            break
          default:
            errorMessage = `Speech recognition error: ${event.error}`
        }
        
        setError(errorMessage)
        setIsListening(false)
      }
      
      // Handle end
      recognition.onend = () => {
        setIsListening(false)
        recognitionRef.current = null
      }
      
      // Start recognition
      recognition.start()
      
    } catch (err: any) {
      setError(err.message || 'Voice input failed')
      setIsListening(false)
    }
  }

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop()
      recognitionRef.current = null
    }
    setIsListening(false)
  }

  if (!isSupported) {
    return (
      <div className="voice-input-unavailable" role="status">
        <span className="warning-icon">⚠️</span>
        <p>Voice input is not supported in your browser</p>
        <p className="hint">Please use Chrome, Edge, or Safari for voice input</p>
      </div>
    )
  }

  return (
    <div className="voice-input" role="region" aria-label="Voice input">
      <button
        onClick={isListening ? stopListening : handleVoiceInput}
        disabled={disabled}
        className={`voice-button ${isListening ? 'listening' : ''}`}
        aria-label={isListening ? 'Stop listening' : 'Start voice input'}
        aria-pressed={isListening}
      >
        <span className="voice-icon">
          {isListening ? '🛑' : '🎤'}
        </span>
        <span className="voice-text">
          {isListening ? 'Stop Listening' : 'Speak Your Research Query'}
        </span>
      </button>
      
      {isListening && (
        <div className="listening-indicator" aria-live="polite">
          <div className="pulse-dot"></div>
          <span>Listening...</span>
        </div>
      )}
      
      {transcript && (
        <div className="voice-transcript" role="status" aria-live="polite">
          <span className="transcript-label">Transcript:</span>
          <p className="transcript-text">{transcript}</p>
        </div>
      )}
      
      {error && (
        <div className="voice-error" role="alert">
          <span className="error-icon">⚠️</span>
          <p>{error}</p>
        </div>
      )}
    </div>
  )
}

