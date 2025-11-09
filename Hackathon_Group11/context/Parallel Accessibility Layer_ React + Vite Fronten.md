<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Parallel Accessibility Layer: React + Vite Frontend with Streamlit Backend

You're thinking strategically—this is **exactly what impresses judges**. But let me be honest about the 12-hour constraint: adding React + Vite as a *parallel* frontend is a **trade-off**, not a free upgrade.

## The Case for This Hybrid Architecture

**Why judges love it:**

- **Showcases full-stack thinking** — Backend (LangGraph/Streamlit) + Frontend (React/Vite)
- **Accessibility credentials** — WCAG compliance, keyboard navigation, screen reader support
- **Production-ready perception** — React signals "this could scale beyond a hackathon"
- **Team synergy** — One person builds Python backend, another builds React frontend in parallel

**When it's viable in 12 hours:**

- You have 2+ people
- You're comfortable with React boilerplate
- You're building a lightweight API, not complex interactions

***

## Architecture: Clean Separation

```
multi-agent-researcher/
├── backend/                    # Python backend (hours 0-6)
│   ├── agents/
│   ├── orchestration/
│   ├── main.py                # FastAPI server (NOT Streamlit)
│   └── requirements.txt
├── frontend/                   # React frontend (hours 0-6, parallel)
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── App.tsx
│   │   └── accessibility.css   # WCAG compliance
│   ├── vite.config.ts
│   └── package.json
└── docker-compose.yml          # Optional: local dev
```

**Critical: Switch from Streamlit to FastAPI backend.** Why?


| Aspect | Streamlit | FastAPI |
| :-- | :-- | :-- |
| **Built for** | Data apps | APIs |
| **CORS support** | Complex | Native |
| **Concurrent requests** | Slow | Fast |
| **Accessibility** | Limited | Full control |
| **Hackathon time** | 30 min to build UI | 30 min to build API |


***

## Phase 0: Decision Gate (30 minutes)

**Before you start, answer this:**

1. **Do you have 2 people?** (or are you confident coding both Python + React rapidly?)
2. **Do you know React?** (If not, this adds 2+ hours of learning)
3. **Are you willing to drop Streamlit entirely?** (Yes, for this to work in time)
4. **What's your priority?**
    - Pure demo wow-factor? → React + Vite
    - Safe bet that works? → Stick with Streamlit

**If 2/4 answers are "no," skip this approach.** Streamlit MVP is smarter.

***

## Scenario: You Have a Team (2 People, 12 Hours)

### Person A: Python Backend (FastAPI) - 6 Hours

**Hour 0-1: FastAPI skeleton**

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ResearchRequest(BaseModel):
    query: str

class ResearchResponse(BaseModel):
    sources: dict
    analysis: dict
    insights: list
    report: str
    status: str

@app.post("/api/research")
async def research(req: ResearchRequest):
    """Endpoint for research requests"""
    # Will integrate orchestration here
    pass

@app.get("/api/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Hour 1-3: Integrate orchestration (same agents as before)**

```python
# backend/main.py - continued
from orchestration.coordinator import workflow

@app.post("/api/research")
async def research(req: ResearchRequest):
    try:
        result = workflow.invoke({"query": req.query})
        return ResearchResponse(
            sources=result["sources"],
            analysis=result["analysis"],
            insights=result["insights"],
            report=result["report"],
            status="success"
        )
    except Exception as e:
        return ResearchResponse(
            sources={},
            analysis={},
            insights=[],
            report=f"Error: {str(e)}",
            status="error"
        )

@app.get("/api/demo-queries")
async def demo_queries():
    """Return pre-cached demo queries"""
    return [
        "AI safety concerns in large language models",
        "Recent breakthroughs in drug discovery using AI",
        "Enterprise adoption of generative AI in 2025"
    ]
```

**Hour 3-6: Streaming endpoint + error handling**

For a polished feel, add streaming (show agent progress in real-time):

```python
# backend/main.py - streaming
from fastapi.responses import StreamingResponse
import json
import asyncio

@app.post("/api/research-stream")
async def research_stream(req: ResearchRequest):
    """Streaming endpoint for real-time progress"""
    
    async def event_generator():
        try:
            # Retrieval
            yield f"data: {json.dumps({'stage': 'retrieval', 'message': '🔍 Retrieving sources...'})}\n\n"
            retriever_result = await asyncio.to_thread(
                lambda: workflow.invoke({"query": req.query, "stage": "retrieval"})
            )
            
            # Analysis
            yield f"data: {json.dumps({'stage': 'analysis', 'message': '📊 Analyzing findings...'})}\n\n"
            await asyncio.sleep(0.1)  # Simulate work
            
            # Insights
            yield f"data: {json.dumps({'stage': 'insights', 'message': '💡 Generating insights...'})}\n\n"
            
            # Report
            yield f"data: {json.dumps({'stage': 'report', 'message': '📄 Compiling report...'})}\n\n"
            
            # Final result
            yield f"data: {json.dumps({'stage': 'complete', 'data': retriever_result})}\n\n"
        
        except Exception as e:
            yield f"data: {json.dumps({'stage': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

**Deployment note:** Run locally with:

```bash
pip install fastapi uvicorn
python backend/main.py
# Runs on http://localhost:8000
```


***

### Person B: React + Vite Frontend - 6 Hours

**Hour 0-0.5: Project scaffold**

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install axios zustand
```

**Hour 0.5-1: Core component structure**

```typescript
// frontend/src/App.tsx
import React, { useState } from 'react'
import { ResearchForm } from './components/ResearchForm'
import { ResearchResults } from './components/ResearchResults'
import './App.css'
import './accessibility.css'

export const App: React.FC = () => {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)

  const handleResearch = async (q: string) => {
    setQuery(q)
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q })
      })
      const data = await response.json()
      setResults(data)
    } catch (error) {
      console.error('Research failed:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container" role="main">
      <header className="app-header" role="banner">
        <h1>🤖 Multi-Agent Deep Researcher</h1>
        <p>Accessible research powered by specialized AI agents</p>
      </header>

      <main className="app-main">
        <ResearchForm onSubmit={handleResearch} loading={loading} />
        {results && <ResearchResults data={results} />}
      </main>
    </div>
  )
}
```

**Hour 1-2: Accessible form component**

```typescript
// frontend/src/components/ResearchForm.tsx
import React, { useState } from 'react'

interface Props {
  onSubmit: (query: string) => void
  loading: boolean
}

export const ResearchForm: React.FC<Props> = ({ onSubmit, loading }) => {
  const [query, setQuery] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      onSubmit(query)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="research-form" role="search">
      <label htmlFor="query-input" className="form-label">
        What would you like to research?
      </label>
      
      <input
        id="query-input"
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="e.g., AI safety concerns in LLMs"
        disabled={loading}
        aria-busy={loading}
        aria-describedby="query-hint"
        className="query-input"
      />
      
      <p id="query-hint" className="form-hint">
        Enter your research topic. Results will appear below.
      </p>

      <button
        type="submit"
        disabled={loading || !query.trim()}
        aria-label={loading ? 'Research in progress' : 'Start research'}
        className="submit-button"
      >
        {loading ? '⏳ Researching...' : '🔍 Start Research'}
      </button>
    </form>
  )
}
```

**Hour 2-3: Results display with accessibility**

```typescript
// frontend/src/components/ResearchResults.tsx
import React from 'react'
import { Markdown } from './Markdown'

interface Props {
  data: {
    sources: Record<string, any>
    analysis: Record<string, any>
    insights: string[]
    report: string
    status: string
  }
}

export const ResearchResults: React.FC<Props> = ({ data }) => {
  return (
    <section className="results" role="region" aria-label="Research results">
      {data.status === 'error' ? (
        <div className="error-box" role="alert" aria-live="assertive">
          <h2>Research Failed</h2>
          <p>{data.report}</p>
        </div>
      ) : (
        <>
          <div className="results-grid">
            <div className="sources-card" role="region" aria-label="Sources retrieved">
              <h2>📚 Sources Retrieved</h2>
              <p className="stat">{Object.keys(data.sources).length} sources</p>
            </div>

            <div className="analysis-card" role="region" aria-label="Analysis findings">
              <h2>📊 Analysis</h2>
              <p className="stat">{Object.keys(data.analysis).length} findings</p>
            </div>

            <div className="insights-card" role="region" aria-label="Generated insights">
              <h2>💡 Insights</h2>
              <p className="stat">{data.insights.length} trends identified</p>
            </div>
          </div>

          <div className="report-section" role="region" aria-label="Full research report">
            <h2>📄 Full Report</h2>
            <Markdown content={data.report} />
            <button 
              onClick={() => downloadReport(data.report)}
              className="download-button"
              aria-label="Download report as markdown file"
            >
              📥 Download Report
            </button>
          </div>
        </>
      )}
    </section>
  )
}

const downloadReport = (content: string) => {
  const element = document.createElement('a')
  element.setAttribute('href', 'data:text/markdown;charset=utf-8,' + encodeURIComponent(content))
  element.setAttribute('download', 'research_report.md')
  element.style.display = 'none'
  document.body.appendChild(element)
  element.click()
  document.body.removeChild(element)
}
```

**Hour 3-4: Accessibility CSS (WCAG compliance)**

```css
/* frontend/src/accessibility.css */

/* Color contrast - WCAG AA compliant */
:root {
  --text-primary: #1a1a1a;
  --text-secondary: #4a4a4a;
  --bg-primary: #ffffff;
  --bg-secondary: #f5f5f5;
  --accent: #0066cc;
  --focus-outline: 3px solid #4d90fe;
}

/* Focus visible for keyboard navigation */
*:focus-visible {
  outline: var(--focus-outline);
  outline-offset: 2px;
}

/* Skip to main content link */
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: var(--accent);
  color: white;
  padding: 8px;
  z-index: 100;
}

.skip-link:focus {
  top: 0;
}

/* Form labels always visible */
.form-label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-primary);
}

/* Input fields - sufficient padding and size */
input[type="text"],
textarea {
  font-size: 16px; /* Prevents zoom on iOS */
  padding: 12px;
  border: 2px solid var(--text-secondary);
  border-radius: 4px;
  min-height: 44px; /* Touch target size */
}

input[type="text"]:focus {
  border-color: var(--accent);
}

/* Buttons - min 44x44px for touch */
button {
  min-height: 44px;
  min-width: 44px;
  padding: 12px 20px;
  font-size: 16px;
  cursor: pointer;
  border-radius: 4px;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* High contrast mode support */
@media (prefers-contrast: more) {
  :root {
    --text-primary: #000000;
    --bg-primary: #ffffff;
  }
  
  button {
    border: 2px solid currentColor;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  * {
    animation: none !important;
    transition: none !important;
  }
}

/* Screen reader only content */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
```

**Hour 4-5: Loading states + streaming**

```typescript
// frontend/src/hooks/useResearchStream.ts
import { useEffect, useState } from 'react'

export const useResearchStream = (query: string) => {
  const [stages, setStages] = useState<Array<{stage: string; message: string}>>([])
  const [data, setData] = useState(null)

  useEffect(() => {
    if (!query) return

    const eventSource = new EventSource(
      `http://localhost:8000/api/research-stream?query=${encodeURIComponent(query)}`
    )

    eventSource.onmessage = (event) => {
      const message = JSON.parse(event.data)
      
      if (message.stage === 'complete') {
        setData(message.data)
        eventSource.close()
      } else {
        setStages(prev => [...prev, message])
      }
    }

    return () => eventSource.close()
  }, [query])

  return { stages, data }
}
```

**Hour 5-6: Testing + polish**

- Lighthouse audit (DevTools → Lighthouse)
- Test with screen reader (NVDA on Windows, VoiceOver on Mac)
- Keyboard-only navigation (Tab through entire app)
- Mobile responsiveness

```bash
npm run build
npm run preview
```


***

## Parallel Execution Timeline (12 Hours, 2 People)

| Time | Person A (Backend) | Person B (Frontend) | Sync Points |
| :-- | :-- | :-- | :-- |
| 0-0.5h | FastAPI skeleton | Vite setup | Split team |
| 0.5-1h | CORS + endpoints | React structure | - |
| 1-3h | Orchestration integration | Form component | **Sync:** API contract defined |
| 3-4h | Streaming setup | Results display | **Sync:** Test API calls |
| 4-5h | Error handling | Accessibility CSS | **Sync:** Complete pipeline |
| 5-6h | Local testing | Loading states | **Sync:** E2E testing |
| 6-8h | Demo caching + fallback | Mobile polish + a11y tests | **Sync:** Final UI/UX review |
| 8-10h | Backend optimization | React build optimization | **Sync:** Performance check |
| 10-12h | Buffer/debugging | Deploy prep + buffer | **Final:** Rehearsal |


***

## API Contract (Define This First!)

**Person A \& B must agree on this in Hour 0.5:**

```typescript
// Shared interface
interface ResearchRequest {
  query: string
}

interface ResearchResponse {
  sources: {
    web?: string[]
    papers?: string[]
    news?: string[]
  }
  analysis: {
    summary: string[]
    contradictions: string[]
    credibility: string
  }
  insights: string[]
  report: string
  status: 'success' | 'error'
}
```

**Person A builds to this. Person B consumes this. Both move fast.**

***

## Deployment (Optional, but Judges Love It)

**Docker Compose for local demo:**

```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      OPENAI_API_KEY: ${OPENAI_API_KEY}
  
  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    depends_on:
      - backend
```

Run: `docker-compose up`

***

## The Trade-Off Analysis

### Option 1: Streamlit Only (Safe)

- ✅ Everything in Python, easier team sync
- ✅ Built for data viz, native widgets
- ✅ Slower to build (~4 hours total)
- ❌ Limited accessibility out-of-box
- ❌ Doesn't scale to production
- ⏱ **12 hours: Comfortable**


### Option 2: React + Vite + FastAPI (Impressive)

- ✅ Full-stack, production-ready architecture
- ✅ WCAG-compliant, accessible UI
- ✅ Streaming, real-time progress
- ✅ Separates concerns cleanly
- ❌ Requires 2 people or significant time pressure
- ❌ More to debug if things break
- ⏱ **12 hours: Aggressive, but doable**


### Option 3: Hybrid (Smart Middle Ground)

- ✅ Streamlit for backend UI
- ✅ React component library for accessibility layer
- ❌ Complexity without real benefit
- ⏱ **12 hours: Not recommended, overcomplicated**

***

## My Recommendation

**Go React + Vite + FastAPI IF:**

- You have a dedicated frontend person comfortable with React
- You've done this before or are confident with TypeScript
- You want to stand out from other hackathon projects
- Your team is strong and likes parallel work

**Stick with Streamlit IF:**

- You're flying solo
- You prioritize speed over architectural elegance
- You want minimal debugging surface area
- You're not sure about React/TypeScript

**For a 12-hour hackathon with accessibility as a requirement, React + Vite is actually the smarter choice.** Streamlit's accessibility is an afterthought; React with proper ARIA/semantic HTML is native to the framework.

***

## Judgment Perspective

**What judges see in React + Vite + FastAPI:**
> "These engineers understand separation of concerns. They built a production-grade backend API, then wrapped it in an accessible frontend. They could scale this to thousands of users without major refactoring. They also prioritized accessibility from day one—WCAG compliance isn't an afterthought."

**What judges see in Streamlit:**
> "Solid proof-of-concept. All logic is clean. They focused on agent architecture, not UI polish. Good for a research tool."

Both are valid. React + Vite is just *more impressive* for this specific project.

