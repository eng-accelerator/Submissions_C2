import { useEffect } from 'react'

interface ShortcutCallbacks {
  onPlayPause?: () => void
  onStop?: () => void
  onSettings?: () => void
}

export const useKeyboardShortcuts = (callbacks: ShortcutCallbacks, enabled: boolean = true) => {
  useEffect(() => {
    if (!enabled) return

    const handleKeyPress = (e: KeyboardEvent) => {
      // Don't trigger if user is typing in an input/textarea
      const target = e.target as HTMLElement
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
        return
      }

      // Space - Play/Pause
      if (e.code === 'Space') {
        e.preventDefault()
        callbacks.onPlayPause?.()
      }
      // Escape - Stop
      if (e.code === 'Escape') {
        callbacks.onStop?.()
      }
      // Shift+S - Settings
      if (e.code === 'KeyS' && e.shiftKey) {
        e.preventDefault()
        callbacks.onSettings?.()
      }
    }

    window.addEventListener('keydown', handleKeyPress)
    return () => window.removeEventListener('keydown', handleKeyPress)
  }, [callbacks, enabled])
}

