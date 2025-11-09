import { useState, useCallback, useRef } from 'react'

export interface TTSOptions {
  rate?: number
  pitch?: number
  volume?: number
  lang?: string
}

export const useTextToSpeech = (options: TTSOptions = {}) => {
  const [isPlaying, setIsPlaying] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [progress, setProgress] = useState(0)
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null)
  const synth = typeof window !== 'undefined' ? window.speechSynthesis : null

  // Check browser support
  const isSupported = !!synth

  const speak = useCallback(
    (text: string) => {
      if (!isSupported || !synth) {
        console.warn('Speech Synthesis not supported in this browser')
        return
      }

      // Cancel any ongoing speech
      synth.cancel()

      // Create new utterance
      const utterance = new SpeechSynthesisUtterance(text)

      // Configure
      utterance.rate = options.rate ?? 1
      utterance.pitch = options.pitch ?? 1
      utterance.volume = options.volume ?? 1
      utterance.lang = options.lang ?? 'en-US'

      // Event handlers
      utterance.onstart = () => {
        setIsPlaying(true)
        setIsPaused(false)
        setProgress(0)
      }

      utterance.onend = () => {
        setIsPlaying(false)
        setIsPaused(false)
        setProgress(100)
      }

      utterance.onerror = () => {
        setIsPlaying(false)
        console.error('Speech synthesis error')
      }

      // Track progress (estimate based on characters)
      utterance.onboundary = (event) => {
        const charIndex = (event as any).charIndex || 0
        const totalChars = text.length
        const estimatedProgress = totalChars > 0 ? (charIndex / totalChars) * 100 : 0
        setProgress(Math.min(estimatedProgress, 99))
      }

      utteranceRef.current = utterance
      synth.speak(utterance)
    },
    [synth, isSupported, options]
  )

  const pause = useCallback(() => {
    if (isSupported && isPlaying && synth) {
      synth.pause()
      setIsPaused(true)
    }
  }, [synth, isSupported, isPlaying])

  const resume = useCallback(() => {
    if (isSupported && isPaused && synth) {
      synth.resume()
      setIsPaused(false)
    }
  }, [synth, isSupported, isPaused])

  const stop = useCallback(() => {
    if (isSupported && synth) {
      synth.cancel()
      setIsPlaying(false)
      setIsPaused(false)
      setProgress(0)
    }
  }, [synth, isSupported])

  const getAvailableVoices = useCallback(() => {
    if (!isSupported || !synth) return []
    return synth.getVoices()
  }, [synth, isSupported])

  const setVoice = useCallback(
    (voiceIndex: number) => {
      if (utteranceRef.current && isSupported && synth) {
        const voices = synth.getVoices()
        if (voices[voiceIndex]) {
          utteranceRef.current.voice = voices[voiceIndex]
        }
      }
    },
    [synth, isSupported]
  )

  return {
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
  }
}

