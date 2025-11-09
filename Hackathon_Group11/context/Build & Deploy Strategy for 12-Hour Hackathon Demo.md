<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Build \& Deploy Strategy for 12-Hour Hackathon Demo

You're in the **final stretch**—you've architected the system, optimized models, now you need to **ship it working**. This is where most hackathons fail: great code that doesn't deploy. Let me give you a bulletproof strategy.

***

## Deployment Architecture Decision

**For a 12-hour hackathon, you have 3 options:**


| Option | Setup Time | Demo Safety | Production Ready | Recommend? |
| :-- | :-- | :-- | :-- | :-- |
| **Local + USB backup** | 0 min | Medium | No | ❌ Risky |
| **Vercel + Railway** | 15 min | High | Yes | ✅ **BEST** |
| **Docker Compose locally** | 30 min | Medium | Maybe | ⚠️ If paranoid |

**Go with Vercel (React) + Railway (FastAPI).** This is **battle-tested, free, and judges love it** because it shows you can ship real software.

***

## Phase 1: Pre-Deployment Checklist (Hour 10-11)

### Backend (FastAPI) Pre-Flight

**Test locally first:**

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Test API
python main.py
# Should output: "Uvicorn running on http://0.0.0.0:8000"

# Test endpoint
curl -X POST http://localhost:8000/api/research \
  -H "Content-Type: application/json" \
  -d '{"query": "multi-agent AI"}'

# Should return: JSON with sources, analysis, insights, report
```

**Create `requirements.txt`:**

```
fastapi==0.104.1
uvicorn==0.24.0
langchain==0.1.5
langchain-openai==0.0.6
langchain-anthropic==0.1.5
langchain-community==0.0.10
python-dotenv==1.0.0
tavily-python==0.1.0
duckduckgo-search==3.9.10
pydantic==2.5.0
requests==2.31.0
```

**Create `backend/main.py` (production-ready):**

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import agents
from orchestration.coordinator import workflow

app = FastAPI(title="Multi-Agent Researcher", version="1.0.0")

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev
        "https://yourdomain.vercel.app",  # Vercel production
        "*"  # Open for demo (close in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ResearchRequest(BaseModel):
    query: str

class ResearchResponse(BaseModel):
    sources: dict
    analysis: dict
    insights: list
    report: str
    status: str

# Routes
@app.get("/health")
async def health():
    """Health check for deployment monitoring"""
    return {
        "status": "ok",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.post("/api/research")
async def research(req: ResearchRequest):
    """Main research endpoint"""
    logger.info(f"Research query: {req.query}")
    
    try:
        result = workflow.invoke({"query": req.query})
        
        return ResearchResponse(
            sources=result.get("sources", {}),
            analysis=result.get("analysis", {}),
            insights=result.get("insights", []),
            report=result.get("report", ""),
            status="success"
        )
    except Exception as e:
        logger.error(f"Research failed: {str(e)}")
        return ResearchResponse(
            sources={},
            analysis={},
            insights=[],
            report=f"Error: {str(e)}",
            status="error"
        )

@app.get("/api/demo-queries")
async def demo_queries():
    """Pre-cached demo queries"""
    return {
        "queries": [
            "AI safety concerns in large language models",
            "Recent breakthroughs in drug discovery using AI",
            "Enterprise adoption of generative AI in 2025"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

**Create `backend/.env`:**

```
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
ENVIRONMENT=development
```

**Create `backend/.env.production` (for Railway):**

```
OPENAI_API_KEY=${OPENAI_API_KEY}  # Set in Railway dashboard
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
TAVILY_API_KEY=${TAVILY_API_KEY}
ENVIRONMENT=production
```


***

### Frontend (React + Vite) Pre-Flight

**Test locally:**

```bash
cd frontend

# Install dependencies
npm install

# Test dev server
npm run dev
# Should output: "Local: http://localhost:5173"

# Verify it connects to backend
# Open browser, enter query, should return results
```

**Create `frontend/vite.config.ts`:**

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false,  // Smaller builds
  }
})
```

**Create `frontend/package.json`:**

```json
{
  "name": "multi-agent-researcher-frontend",
  "type": "module",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.0.0",
    "typescript": "^5.0.0",
    "vite": "^5.0.0"
  }
}
```

**Create `frontend/.env.production`:**

```
VITE_API_URL=https://your-railway-backend.up.railway.app
```


***

## Phase 2: Deploy Backend to Railway (10 minutes)

**Why Railway?**

- Free tier supports FastAPI perfectly
- Auto-deploys from GitHub
- Easy environment variables
- Production-grade uptime


### Step 1: Prepare GitHub repo

```bash
# From project root
git init
git add .
git commit -m "Initial multi-agent researcher commit"
git remote add origin https://github.com/YOUR_USERNAME/multi-agent-researcher.git
git push -u origin main
```

**Create `.gitignore`:**

```
__pycache__/
*.py[cod]
*$py.class
.env
.env.local
node_modules/
dist/
.DS_Store
```


### Step 2: Connect to Railway

1. Go to https://railway.app
2. Sign up (GitHub login easiest)
3. Click "New Project" → "Deploy from GitHub"
4. Select your repo
5. Railway auto-detects Python project

### Step 3: Configure environment

In Railway dashboard:

- Go to "Variables"
- Add:

```
OPENAI_API_KEY = your_key
ANTHROPIC_API_KEY = your_key
TAVILY_API_KEY = your_key
ENVIRONMENT = production
PORT = 8000
```


### Step 4: Create `Procfile` (tells Railway how to run)

```
web: cd backend && python main.py
```

**That's it.** Railway auto-deploys and gives you a URL like:

```
https://multi-agent-researcher-production.up.railway.app
```


***

## Phase 3: Deploy Frontend to Vercel (5 minutes)

**Why Vercel?**

- Optimized for React/Next.js/Vite
- Instant global CDN
- One-click deployment
- Free tier perfect for hackathons


### Step 1: Push to GitHub (already done above)

### Step 2: Connect to Vercel

1. Go to https://vercel.com
2. Sign up (GitHub login)
3. Click "Add New Project" → Select your GitHub repo
4. Vercel auto-detects Vite project

### Step 3: Configure environment variables

- Environment: `Production`
- Add:

```
VITE_API_URL = https://multi-agent-researcher-production.up.railway.app
```


### Step 4: Override build settings

- Build Command: `npm run build`
- Output Directory: `frontend/dist`
- Framework: Vite

**Deploy.** Vercel gives you:

```
https://multi-agent-researcher.vercel.app
```


***

## Phase 4: Create Deployment Checklist (Hour 11-11.5)

**Before you present, verify:**

```bash
# Backend health check
curl https://multi-agent-researcher-production.up.railway.app/health
# Should return: {"status": "ok", "environment": "production"}

# Frontend loads
# Visit https://multi-agent-researcher.vercel.app
# Should load without errors

# End-to-end test
# Enter demo query in frontend
# Should return results from backend
# Check network tab: API calls should succeed

# Test demo queries
# Click each pre-cached query
# Should return instantly from cache
```


***

## Phase 5: Fallback Strategy (Hour 11.5-12)

**What if deployment fails?** Have a backup.

### Fallback 1: Local Demo with USB

```bash
# Create demo script
cat > demo.sh << 'EOF'
#!/bin/bash

# Start backend
cd backend && python main.py &
BACKEND_PID=$!

# Start frontend
cd ../frontend && npm run dev &
FRONTEND_PID=$!

# Keep running
wait

# Cleanup
kill $BACKEND_PID $FRONTEND_PID
EOF

chmod +x demo.sh
```

**Run during presentation:**

```bash
./demo.sh
# Opens at http://localhost:5173
```


### Fallback 2: Docker locally

**Create `docker-compose.yml`:**

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      TAVILY_API_KEY: ${TAVILY_API_KEY}
      ENVIRONMENT: production
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 5

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    environment:
      VITE_API_URL: http://backend:8000
    depends_on:
      backend:
        condition: service_healthy
```

**Create `backend/Dockerfile`:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
```

**Create `frontend/Dockerfile`:**

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

RUN npm run build

EXPOSE 5173

CMD ["npm", "run", "preview"]
```

**Run locally:**

```bash
docker-compose up
# Runs on http://localhost:5173
```


***

## Complete Deployment Timeline (Hours 10-12)

| Time | Task | Outcome |
| :-- | :-- | :-- |
| 10:00-10:15 | Test backend locally, create requirements.txt | `uvicorn running` ✓ |
| 10:15-10:30 | Test frontend locally, create vite.config.ts | `npm run dev` ✓ |
| 10:30-10:40 | Push to GitHub | Repo ready |
| 10:40-10:50 | Deploy backend to Railway | `railway.app URL` ✓ |
| 10:50-11:00 | Deploy frontend to Vercel | `vercel.app URL` ✓ |
| 11:00-11:15 | End-to-end test (cloud) | API + UI working ✓ |
| 11:15-11:30 | Create local fallback (demo.sh) | Backup ready ✓ |
| 11:30-11:45 | Cache demo queries (in case API slow) | Cache.json ready |
| 11:45-12:00 | Rehearse presentation + final checks | **DEMO READY** |


***

## Presentation Setup (Last 30 Minutes)

**Have 3 scenarios prepared:**

### Scenario A: Cloud Works (Best Case)

```
1. Show deployed URLs
2. Click "Start Research"
3. Get results
4. Download report
TALKING POINT: "This is deployed on production infrastructure..."
```


### Scenario B: Cloud Slow (Fallback)

```
1. Say "Let me show you the pre-cached results"
2. Switch to local instance with cached responses
3. Same demo, instant results
TALKING POINT: "For scalability, we cache common queries..."
```


### Scenario C: Internet Down (Paranoia)

```
1. Have screenshots of working app
2. Show GitHub repo
3. Explain architecture + show code
4. Demo locally with Docker
TALKING POINT: "The system is designed to degrade gracefully..."
```


***

## Production URL Structure

After deployment, you'll have:

```
Frontend:  https://multi-agent-researcher.vercel.app
Backend:   https://multi-agent-researcher-production.up.railway.app

API Endpoints:
  /health              → Backend health check
  /api/research        → Main research endpoint
  /api/demo-queries    → List of demo queries
```


***

## Monitoring During Demo

**Open these during presentation:**

1. **Vercel Analytics:** https://vercel.com/dashboard
    - See: Real-time requests, errors, performance
2. **Railway Dashboard:** https://railway.app/dashboard
    - See: Backend logs, CPU usage, request count
3. **Browser DevTools:** F12
    - Network tab: See all API calls
    - Console: Catch any JavaScript errors

***

## Quick Reference: Deploy Commands

```bash
# Frontend deploy
cd frontend
npm run build
vercel deploy --prod

# Backend deploy (via Railway UI, or CLI)
railway up

# Local fallback
./demo.sh

# Docker fallback
docker-compose up
```


***

## Final Checklist Before Presentation

```
✅ Backend deployed to Railway
   - Health check returns 200
   - Environment variables set
   - Logs show no errors

✅ Frontend deployed to Vercel
   - Page loads without 404s
   - API_URL environment variable set
   - Builds successfully

✅ Local fallback ready
   - demo.sh executable
   - docker-compose.yml tested
   - Cache.json has 3 demo queries

✅ Demo scenario tested
   - 1 cloud demo (if working)
   - 1 cached result demo (if slow)
   - 1 local demo (if internet fails)

✅ Slides ready
   - Show architecture diagram
   - Have GitHub repo link
   - Have deployed URLs

✅ Presentation flow
   - Demo (2 min)
   - Architecture explanation (1 min)
   - Code walkthrough (2 min)
   - Q&A (1 min)
```


***

## Why This Strategy Wins

| Aspect | This Approach | Benefits |
| :-- | :-- | :-- |
| **Deployment time** | 15 minutes | More time for polish |
| **Reliability** | 3 fallbacks | Presenter never panics |
| **Production ready** | Yes | Judges impressed |
| **Cost** | Free tier | \$0 spend |
| **Scalability** | Cloud-native | "Scales to thousands" |
| **Showcase factor** | Full-stack deploy | Shows real engineering |

**You're not just building a demo, you're shipping a product.** Judges see this difference immediately.

