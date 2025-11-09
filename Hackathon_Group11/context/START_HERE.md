# 🚀 Quick Start Guide - React + FastAPI Architecture

## Architecture Overview

This project now uses a **full-stack architecture**:
- **Backend**: FastAPI (Python) - `http://localhost:8000`
- **Frontend**: React + Vite (TypeScript) - `http://localhost:5173`

## Setup Instructions

### Step 1: Backend Setup

1. **Create virtual environment:**
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

3. **Configure API key:**
   ```bash
   cp env.example .env
   # Edit .env and add your OPEN_ROUTER_KEY
   ```

4. **Start backend:**
   ```bash
   python backend/main.py
   ```
   
   Backend will run on `http://localhost:8000`

### Step 2: Frontend Setup

1. **Navigate to frontend:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start frontend:**
   ```bash
   npm run dev
   ```
   
   Frontend will run on `http://localhost:5173`

### Step 3: Access Application

Open your browser and go to: `http://localhost:5173`

## Development Workflow

### Running Both Services

**Terminal 1 (Backend):**
```bash
# Activate venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Start backend
python backend/main.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

### Testing

**Backend API:**
- Health check: `http://localhost:8000/api/health`
- API docs: `http://localhost:8000/docs`

**Frontend:**
- Open `http://localhost:5173` in browser
- Enter a research query
- Watch real-time progress updates

## Project Structure

```
hackathon/
├── backend/
│   ├── main.py              # FastAPI server
│   └── requirements.txt     # Backend deps
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── App.tsx
│   │   └── ...
│   ├── package.json
│   └── vite.config.ts
├── agents/                  # Agent implementations
├── orchestration/           # LangGraph workflow
├── utils/                   # Utilities
└── requirements.txt         # Main Python deps
```

## Key Features

✅ **Accessible UI** - WCAG AA compliant React frontend
✅ **Real-time Progress** - Streaming updates via Server-Sent Events
✅ **Production Ready** - FastAPI backend with proper CORS
✅ **Type Safe** - TypeScript frontend
✅ **Modern Stack** - React 18 + Vite 5 + FastAPI

## Troubleshooting

**Backend not starting?**
- Check Python version: `python --version` (needs 3.8+)
- Verify virtual environment is activated
- Check `.env` file has `OPEN_ROUTER_KEY`

**Frontend not connecting?**
- Ensure backend is running on port 8000
- Check CORS configuration in `backend/main.py`
- Verify frontend is on port 5173

**CORS errors?**
- Backend must be running before frontend
- Check browser console for specific errors
- Verify URLs match in CORS config

## Next Steps

- Read `README_BACKEND.md` for backend details
- Read `README_FRONTEND.md` for frontend details
- Check `QUICK_START.md` for original Streamlit setup (legacy)

---

**Ready to build!** 🎉

