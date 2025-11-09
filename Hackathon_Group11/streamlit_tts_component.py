"""
Streamlit Text-to-Speech Component
Uses Web Speech API via JavaScript injection
"""

import streamlit.components.v1 as components

def text_to_speech_component(text: str, title: str = "Listen to Report"):
    """
    Create a text-to-speech component for Streamlit using Web Speech API.
    
    Args:
        text: The text to be read aloud
        title: Title for the TTS controls
    
    Returns:
        HTML component with TTS controls
    """
    
    # Clean text for better TTS
    clean_text = text.replace('"', '&quot;').replace("'", "&#39;").replace('\n', ' ')
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .tts-container {{
                background: linear-gradient(135deg, #f0f4ff 0%, #f9f5ff 100%);
                border: 2px solid #e0e7ff;
                border-radius: 12px;
                padding: 16px;
                margin: 20px 0;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }}
            
            .tts-main {{
                display: flex;
                gap: 8px;
                align-items: center;
                flex-wrap: wrap;
            }}
            
            .tts-button {{
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 10px 16px;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                white-space: nowrap;
                user-select: none;
            }}
            
            .play-button {{
                background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
                color: white;
                flex: 1;
                box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
                min-height: 44px;
                font-size: 15px;
            }}
            
            .play-button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4);
            }}
            
            .play-button.playing {{
                background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
                box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);
                animation: pulse-button 1s ease-in-out infinite;
            }}
            
            @keyframes pulse-button {{
                0%, 100% {{ box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3); }}
                50% {{ box-shadow: 0 4px 20px rgba(249, 115, 22, 0.6); }}
            }}
            
            .stop-button {{
                background: #ef4444;
                color: white;
                padding: 10px 12px;
                box-shadow: 0 2px 8px rgba(239, 68, 68, 0.2);
            }}
            
            .stop-button:hover {{
                background: #dc2626;
                transform: scale(1.05);
            }}
            
            .settings-button {{
                background: white;
                color: #6366f1;
                border: 2px solid #e0e7ff;
                padding: 10px 12px;
            }}
            
            .settings-button:hover {{
                background: #f0f4ff;
                border-color: #c7d2fe;
            }}
            
            .settings-button.active {{
                background: #6366f1;
                color: white;
                border-color: #6366f1;
            }}
            
            .tts-progress {{
                display: flex;
                align-items: center;
                gap: 12px;
                margin-top: 12px;
            }}
            
            .progress-fill {{
                flex: 1;
                height: 6px;
                background: #e0e7ff;
                border-radius: 3px;
                overflow: hidden;
                position: relative;
                transition: width 0.1s linear;
            }}
            
            .progress-indicator {{
                width: 12px;
                height: 12px;
                background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
                border-radius: 50%;
                position: absolute;
                right: -6px;
                top: 50%;
                transform: translateY(-50%);
                box-shadow: 0 0 8px rgba(99, 102, 241, 0.5);
            }}
            
            .progress-text {{
                font-size: 12px;
                font-weight: 600;
                color: #6366f1;
                min-width: 35px;
                text-align: right;
            }}
            
            .tts-settings {{
                background: white;
                border-radius: 8px;
                padding: 16px;
                margin-top: 12px;
                border: 1px solid #e0e7ff;
            }}
            
            .setting-group {{
                display: flex;
                flex-direction: column;
                gap: 8px;
                margin-bottom: 16px;
            }}
            
            .setting-label {{
                font-size: 13px;
                font-weight: 600;
                color: #374151;
            }}
            
            .setting-select {{
                padding: 8px 12px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                font-size: 13px;
                background: white;
                cursor: pointer;
            }}
            
            .setting-slider {{
                width: 100%;
                height: 6px;
                border-radius: 3px;
                background: #e0e7ff;
                outline: none;
                -webkit-appearance: none;
                appearance: none;
                cursor: pointer;
            }}
            
            .setting-slider::-webkit-slider-thumb {{
                -webkit-appearance: none;
                appearance: none;
                width: 18px;
                height: 18px;
                border-radius: 50%;
                background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
                cursor: pointer;
                box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
            }}
            
            .speed-presets {{
                display: flex;
                gap: 8px;
                margin-top: 8px;
            }}
            
            .preset-btn {{
                padding: 6px 12px;
                border: 1px solid #d1d5db;
                background: white;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 600;
                cursor: pointer;
                color: #6b7280;
            }}
            
            .preset-btn:hover {{
                border-color: #6366f1;
                color: #6366f1;
            }}
            
            .preset-btn.active {{
                background: #6366f1;
                color: white;
                border-color: #6366f1;
            }}
            
            .tts-unavailable {{
                background: #fef2f2;
                border: 2px solid #fca5a5;
                border-radius: 12px;
                padding: 12px;
                display: flex;
                align-items: center;
                gap: 12px;
                color: #991b1b;
                font-size: 13px;
            }}
        </style>
    </head>
    <body>
        <div class="tts-container" id="tts-container">
            <div class="tts-main">
                <button class="tts-button play-button" id="play-btn" onclick="togglePlay()">
                    <span>▶</span>
                    <span id="play-text">Listen</span>
                </button>
                <button class="tts-button stop-button" id="stop-btn" onclick="stopSpeech()" style="display: none;">
                    <span>⏹</span>
                </button>
                <button class="tts-button settings-button" id="settings-btn" onclick="toggleSettings()">
                    <span>⚙️</span>
                </button>
            </div>
            
            <div class="tts-progress" id="progress-bar" style="display: none;">
                <div class="progress-fill" id="progress-fill" style="width: 0%;">
                    <div class="progress-indicator"></div>
                </div>
                <span class="progress-text" id="progress-text">0%</span>
            </div>
            
            <div class="tts-settings" id="settings-panel" style="display: none;">
                <div class="setting-group">
                    <label class="setting-label">🎤 Voice</label>
                    <select class="setting-select" id="voice-select" onchange="changeVoice()"></select>
                </div>
                <div class="setting-group">
                    <label class="setting-label">🚀 Speed: <span id="rate-value">1</span>x</label>
                    <input type="range" class="setting-slider" id="rate-slider" min="0.5" max="2" step="0.1" value="1" oninput="changeRate(this.value)">
                    <div class="speed-presets">
                        <button class="preset-btn" onclick="setRate(0.75)">0.75x</button>
                        <button class="preset-btn active" onclick="setRate(1)">1x</button>
                        <button class="preset-btn" onclick="setRate(1.25)">1.25x</button>
                        <button class="preset-btn" onclick="setRate(1.5)">1.5x</button>
                    </div>
                </div>
            </div>
            
            <div class="tts-unavailable" id="unavailable" style="display: none;">
                <span>⚠️</span>
                <p>Text-to-Speech is not supported in your browser</p>
            </div>
        </div>
        
        <script>
            const synth = window.speechSynthesis;
            let utterance = null;
            let isPlaying = false;
            let isPaused = false;
            let currentRate = 1;
            let voices = [];
            
            // Check browser support
            if (!synth) {{
                document.getElementById('unavailable').style.display = 'flex';
                document.getElementById('play-btn').disabled = true;
            }}
            
            // Load voices
            function loadVoices() {{
                voices = synth.getVoices();
                const select = document.getElementById('voice-select');
                select.innerHTML = '';
                voices.forEach((voice, idx) => {{
                    const option = document.createElement('option');
                    option.value = idx;
                    option.textContent = voice.name + (voice.default ? ' (Default)' : '');
                    select.appendChild(option);
                }});
            }}
            
            loadVoices();
            synth.onvoiceschanged = loadVoices;
            
            // Clean text
            const cleanText = `{clean_text}`.replace(/\\[.*?\\]\\(.*?\\)/g, '')
                .replace(/#{{1,6}}\\s/g, '')
                .replace(/\\*\\*/g, '')
                .replace(/\\*/g, '')
                .replace(/`/g, '')
                .replace(/\\n{{3,}}/g, '\\n\\n')
                .trim();
            
            function togglePlay() {{
                if (isPlaying) {{
                    synth.pause();
                    isPaused = true;
                    document.getElementById('play-text').textContent = 'Resume';
                    document.querySelector('#play-btn span:first-child').textContent = '▶';
                }} else if (isPaused) {{
                    synth.resume();
                    isPaused = false;
                    document.getElementById('play-text').textContent = 'Pause';
                    document.querySelector('#play-btn span:first-child').textContent = '⏸';
                }} else {{
                    if (utterance) synth.cancel();
                    
                    utterance = new SpeechSynthesisUtterance(cleanText);
                    utterance.rate = currentRate;
                    utterance.pitch = 1;
                    utterance.volume = 1;
                    utterance.lang = 'en-US';
                    
                    const voiceIndex = document.getElementById('voice-select').value;
                    if (voices[voiceIndex]) {{
                        utterance.voice = voices[voiceIndex];
                    }}
                    
                    utterance.onstart = () => {{
                        isPlaying = true;
                        isPaused = false;
                        document.getElementById('play-btn').classList.add('playing');
                        document.getElementById('play-text').textContent = 'Pause';
                        document.querySelector('#play-btn span:first-child').textContent = '⏸';
                        document.getElementById('stop-btn').style.display = 'flex';
                        document.getElementById('progress-bar').style.display = 'flex';
                    }};
                    
                    utterance.onend = () => {{
                        isPlaying = false;
                        isPaused = false;
                        document.getElementById('play-btn').classList.remove('playing');
                        document.getElementById('play-text').textContent = 'Listen';
                        document.querySelector('#play-btn span:first-child').textContent = '▶';
                        document.getElementById('stop-btn').style.display = 'none';
                        document.getElementById('progress-bar').style.display = 'none';
                        document.getElementById('progress-fill').style.width = '0%';
                        document.getElementById('progress-text').textContent = '0%';
                    }};
                    
                    utterance.onerror = () => {{
                        isPlaying = false;
                        isPaused = false;
                        document.getElementById('play-btn').classList.remove('playing');
                        document.getElementById('play-text').textContent = 'Listen';
                        document.querySelector('#play-btn span:first-child').textContent = '▶';
                        document.getElementById('stop-btn').style.display = 'none';
                        document.getElementById('progress-bar').style.display = 'none';
                    }};
                    
                    utterance.onboundary = (event) => {{
                        const charIndex = event.charIndex || 0;
                        const totalChars = cleanText.length;
                        const progress = totalChars > 0 ? (charIndex / totalChars) * 100 : 0;
                        document.getElementById('progress-fill').style.width = Math.min(progress, 99) + '%';
                        document.getElementById('progress-text').textContent = Math.round(Math.min(progress, 99)) + '%';
                    }};
                    
                    synth.speak(utterance);
                }}
            }}
            
            function stopSpeech() {{
                synth.cancel();
                isPlaying = false;
                isPaused = false;
                document.getElementById('play-btn').classList.remove('playing');
                document.getElementById('play-text').textContent = 'Listen';
                document.querySelector('#play-btn span:first-child').textContent = '▶';
                document.getElementById('stop-btn').style.display = 'none';
                document.getElementById('progress-bar').style.display = 'none';
                document.getElementById('progress-fill').style.width = '0%';
                document.getElementById('progress-text').textContent = '0%';
            }}
            
            function toggleSettings() {{
                const panel = document.getElementById('settings-panel');
                const btn = document.getElementById('settings-btn');
                if (panel.style.display === 'none') {{
                    panel.style.display = 'block';
                    btn.classList.add('active');
                }} else {{
                    panel.style.display = 'none';
                    btn.classList.remove('active');
                }}
            }}
            
            function changeVoice() {{
                if (utterance) {{
                    const voiceIndex = document.getElementById('voice-select').value;
                    if (voices[voiceIndex]) {{
                        utterance.voice = voices[voiceIndex];
                    }}
                }}
            }}
            
            function changeRate(value) {{
                currentRate = parseFloat(value);
                document.getElementById('rate-value').textContent = currentRate;
                if (utterance) {{
                    utterance.rate = currentRate;
                }}
                // Update active preset
                document.querySelectorAll('.preset-btn').forEach(btn => {{
                    btn.classList.remove('active');
                }});
            }}
            
            function setRate(rate) {{
                currentRate = rate;
                document.getElementById('rate-slider').value = rate;
                document.getElementById('rate-value').textContent = rate;
                if (utterance) {{
                    utterance.rate = currentRate;
                }}
                // Update active preset
                document.querySelectorAll('.preset-btn').forEach(btn => {{
                    btn.classList.remove('active');
                    if (parseFloat(btn.textContent) === rate) {{
                        btn.classList.add('active');
                    }}
                }});
            }}
            
            // Keyboard shortcuts
            document.addEventListener('keydown', (e) => {{
                if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
                if (e.code === 'Space') {{
                    e.preventDefault();
                    togglePlay();
                }} else if (e.code === 'Escape') {{
                    stopSpeech();
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    components.html(html, height=400)

