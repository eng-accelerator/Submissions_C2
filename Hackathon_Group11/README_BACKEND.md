# FastAPI Backend Setup 

## Quick Start

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)
- OpenRouter API key

### Installation

1. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   # Create .env file
   cp env.example .env
   # Edit .env and add your OPEN_ROUTER_KEY
   ```

4. **Run the server:**
   ```bash
   # From project root
   python backend/main.py
   
   # Or using uvicorn directly
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **API will be available at:**
   - API: `http://localhost:8000`
   - Docs: `http://localhost:8000/docs`
   - Health: `http://localhost:8000/api/health`

## API Endpoints

### POST /api/research
Main research endpoint - processes query through multi-agent workflow.

**Request:**
```json
{
  "query": "Latest developments in quantum computing 2024"
}
```

**Response:**
```json
{
  "sources": {...},
  "analysis": {...},
  "insights": {...},
  "report": "...",
  "status": "success",
  "error": null
}
```

### POST /api/research-stream
Streaming endpoint with real-time progress updates (Server-Sent Events).

**Request:**
```json
{
  "query": "Latest developments in quantum computing 2024"
}
```

**Response:** Server-Sent Events stream with progress updates.

### GET /api/health
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "message": "API is running"
}
```

### GET /api/demo-queries
Get pre-configured demo queries.

**Response:**
```json
{
  "queries": [
    "Latest developments in quantum computing 2024",
    "Current state of AI safety research and regulations",
    "Emerging climate technology solutions 2024"
  ]
}
```

## Architecture

```
backend/
├── main.py              # FastAPI server
└── requirements.txt     # Backend dependencies

# Uses agents and orchestration from root directory
agents/
orchestration/
utils/
```

## CORS Configuration

The backend is configured to allow requests from:
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (Alternative React dev server)
- `http://127.0.0.1:5173`
- `http://127.0.0.1:3000`

To add more origins, edit `backend/main.py`:
```python
allow_origins=[
    "http://localhost:5173",
    "http://your-frontend-url:port"
]
```

## Development

### Auto-reload
The server runs with `--reload` flag for automatic restart on code changes.

### API Documentation
FastAPI automatically generates interactive API docs:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Production Deployment

### Using Uvicorn
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Gunicorn
```bash
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Environment Variables
- `OPEN_ROUTER_KEY` - Required for LLM operations
- `PORT` - Optional, defaults to 8000

## Troubleshooting

**Port already in use?**
- Change port in `backend/main.py`:
  ```python
  uvicorn.run(app, host="0.0.0.0", port=8001)
  ```

**Import errors?**
- Ensure you're running from project root
- Check that all dependencies are installed
- Verify virtual environment is activated

**CORS errors?**
- Check frontend URL is in `allow_origins` list
- Verify backend is running before starting frontend

---

**For frontend setup, see README_FRONTEND.md**

