"""
FastAPI Backend Server
Multi-Agent AI Deep Researcher API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import sys
import os
import json
import asyncio
import logging
from contextlib import asynccontextmanager

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestration.coordinator import ResearchWorkflow

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup
    logger.info("FastAPI app starting up...")
    logger.info("App is ready to accept requests")
    # Don't initialize workflow here - let it initialize lazily on first use
    yield
    # Shutdown (if needed)
    logger.info("FastAPI app shutting down...")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Multi-Agent AI Deep Researcher API",
    description="API for multi-agent research system",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for React frontend
# Get allowed origins from environment or use defaults
allowed_origins_str = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"
)
# Split and strip whitespace and trailing slashes from each origin
allowed_origins = [origin.strip().rstrip('/') for origin in allowed_origins_str.split(",") if origin.strip()]

# Add Vercel production URL if provided
vercel_url = os.getenv("VERCEL_URL")
if vercel_url:
    vercel_url = vercel_url.strip()
    allowed_origins.append(f"https://{vercel_url}")
    allowed_origins.append(f"http://{vercel_url}")

# Log allowed origins for debugging
logger.info(f"CORS allowed origins: {allowed_origins}")

# Configure CORS middleware
# Use allow_origin_regex to handle all Vercel preview and production deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",  # Matches all Vercel deployments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Initialize workflow lazily to prevent crashes on startup
# Workflow will be initialized on first use
_workflow_instance = None

def get_workflow():
    """Get or create workflow instance (lazy initialization)."""
    global _workflow_instance
    if _workflow_instance is None:
        try:
            _workflow_instance = ResearchWorkflow()
        except Exception as e:
            logger.error(f"Failed to initialize workflow: {e}")
            raise
    return _workflow_instance

# Request/Response models
class ResearchRequest(BaseModel):
    query: str

class ResearchResponse(BaseModel):
    sources: Dict[str, Any]
    analysis: Dict[str, Any]
    insights: Dict[str, Any]
    report: str
    status: str
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    message: str

# Health check endpoint
@app.get("/api/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(status="ok", message="API is running")

# Demo queries endpoint
@app.get("/api/demo-queries")
async def demo_queries():
    """Return pre-cached demo queries"""
    return {
        "queries": [
            "Latest developments in quantum computing 2024",
            "Current state of AI safety research and regulations",
            "Emerging climate technology solutions 2024"
        ]
    }

# Main research endpoint
@app.post("/api/research", response_model=ResearchResponse)
async def research(req: ResearchRequest):
    """
    Main research endpoint - processes query through multi-agent workflow
    """
    logger.info(f"Research request received: {req.query}")
    
    try:
        # Run workflow (lazy initialization)
        result = get_workflow().run(req.query)
        
        # Format response
        return ResearchResponse(
            sources=result.get("sources", {}),
            analysis=result.get("analysis", {}),
            insights=result.get("insights", {}),
            report=result.get("report", ""),
            status="success" if not result.get("error") else "error",
            error=result.get("error", "")
        )
    
    except Exception as e:
        logger.error(f"Research failed: {e}")
        return ResearchResponse(
            sources={},
            analysis={},
            insights={},
            report=f"Error: {str(e)}",
            status="error",
            error=str(e)
        )

# Streaming endpoint for real-time progress
@app.post("/api/research-stream")
async def research_stream(req: ResearchRequest):
    """
    Streaming endpoint for real-time progress updates
    Uses Server-Sent Events (SSE)
    """
    logger.info(f"Streaming research request: {req.query}")
    
    async def event_generator():
        try:
            # Stage 1: Retrieval
            yield f"data: {json.dumps({'stage': 'retrieval', 'message': '🔍 Retrieving sources from web, papers, and news...', 'progress': 20})}\n\n"
            await asyncio.sleep(0.5)
            
            # Stage 2: Enrichment
            yield f"data: {json.dumps({'stage': 'enrichment', 'message': '📊 Enriching sources with metadata and sentiment...', 'progress': 40})}\n\n"
            await asyncio.sleep(0.3)
            
            # Run full workflow in background
            # We'll simulate stages but run the full workflow
            full_result = await asyncio.to_thread(
                lambda: get_workflow().run(req.query)
            )
            
            # Extract results
            retrieval_result = full_result.get("sources", {})
            analysis_result = full_result.get("analysis", {})
            insights_result = full_result.get("insights", {})
            report_result = full_result.get("report", "")
            
            # Final result
            final_result = {
                "sources": retrieval_result,
                "analysis": analysis_result,
                "insights": insights_result,
                "report": report_result,
                "status": "success"
            }
            
            yield f"data: {json.dumps({'stage': 'complete', 'message': '✅ Research complete!', 'progress': 100, 'data': final_result})}\n\n"
        
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: {json.dumps({'stage': 'error', 'message': f'Error: {str(e)}', 'progress': 0})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# Voice input endpoint (for future Wispr Flow integration)
@app.post("/api/research-voice")
async def research_voice(audio_data: bytes = None):
    """
    Accept voice input and convert to text query.
    Currently a placeholder for future Wispr Flow integration.
    
    In production, this would:
    1. Accept audio data from frontend
    2. Use Wispr Flow API or Web Speech API to convert to text
    3. Return the transcribed query
    """
    logger.info("Voice endpoint called (placeholder)")
    return {
        "message": "Voice endpoint ready for Wispr Flow integration",
        "status": "success",
        "note": "Currently using Web Speech API in frontend. Backend integration pending."
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Multi-Agent AI Deep Researcher API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "research": "/api/research",
            "research_stream": "/api/research-stream",
            "research_voice": "/api/research-voice",
            "demo_queries": "/api/demo-queries"
        }
    }

# Removed if __name__ == "__main__" block
# Railway should use Procfile: uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
# This prevents Railway from using python main.py which causes the uvicorn warning

