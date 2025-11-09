# Deployment Guide: Vercel + Railway

This guide walks you through deploying the Multi-Agent AI Deep Researcher to production using **Vercel** (frontend) and **Railway** (backend).

## 🎯 Quick Overview

- **Frontend (React + Vite)**: Deploy to Vercel
- **Backend (FastAPI)**: Deploy to Railway
- **Time**: ~15 minutes
- **Cost**: Free tier (both platforms)

---

## 📋 Prerequisites

1. **GitHub Account**: Your code should be in a GitHub repository
2. **Vercel Account**: Sign up at https://vercel.com (free)
3. **Railway Account**: Sign up at https://railway.app (free)
4. **API Keys Ready**:
   - OpenRouter API key
   - Tavily API key (optional)

---

## 🚀 Phase 1: Deploy Backend to Railway

### Step 1: Prepare Your Repository

Ensure your code is pushed to GitHub:

```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### Step 2: Connect Railway to GitHub

1. Go to https://railway.app
2. Sign up/login (GitHub login recommended)
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select your repository
5. Railway will auto-detect it's a Python project

### Step 3: Configure Railway Service

1. Railway will create a service automatically
2. Click on the service to configure it

**Set Root Directory:**
- In the service settings, set **Root Directory** to: `backend`

**Configure Start Command:**
- Railway should auto-detect, but verify it's: `python main.py`

### Step 4: Set Environment Variables

In Railway dashboard → **Variables** tab, add:

```bash
OPEN_ROUTER_KEY=sk-or-your-key-here
TAVILY_API_KEY=your-tavily-key-here
ENVIRONMENT=production
PORT=8000
ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:5173
```

**Important**: Replace `your-app.vercel.app` with your actual Vercel URL (you'll get this after deploying frontend).

### Step 5: Deploy

Railway will automatically deploy when you:
1. Push to GitHub (if connected)
2. Or click **"Deploy"** in the dashboard

**Wait for deployment** - Railway will give you a URL like:
```
https://multi-agent-researcher-production.up.railway.app
```

### Step 6: Test Backend

```bash
# Health check
curl https://your-railway-url.up.railway.app/api/health

# Should return: {"status": "ok", "message": "API is running"}
```

**Save this Railway URL** - you'll need it for the frontend!

---

## 🎨 Phase 2: Deploy Frontend to Vercel

### Step 1: Connect Vercel to GitHub

1. Go to https://vercel.com
2. Sign up/login (GitHub login recommended)
3. Click **"Add New Project"**
4. Select your GitHub repository
5. Vercel will auto-detect it's a Vite project

### Step 2: Configure Build Settings

In the project configuration:

**Framework Preset**: Vite

**Root Directory**: `frontend`

**Build Command**: `npm run build`

**Output Directory**: `dist`

**Install Command**: `npm install`

### Step 3: Set Environment Variables

In **Environment Variables** section, add:

```bash
VITE_API_URL=https://your-railway-url.up.railway.app
```

**Important**: Replace `your-railway-url.up.railway.app` with your actual Railway URL from Phase 1!

### Step 4: Deploy

Click **"Deploy"**

Vercel will:
1. Install dependencies
2. Build your app
3. Deploy to production

**Wait for deployment** - Vercel will give you a URL like:
```
https://multi-agent-researcher.vercel.app
```

### Step 5: Update Railway CORS

Go back to Railway and update the `ALLOWED_ORIGINS` variable:

```bash
ALLOWED_ORIGINS=https://multi-agent-researcher.vercel.app,http://localhost:5173
```

Railway will automatically redeploy with the new CORS settings.

---

## ✅ Phase 3: Verify Deployment

### Test Frontend

1. Visit your Vercel URL: `https://your-app.vercel.app`
2. The app should load without errors
3. Open browser DevTools (F12) → Network tab
4. Enter a research query
5. Check that API calls go to your Railway backend

### Test Backend

```bash
# Health check
curl https://your-railway-url.up.railway.app/api/health

# Test research endpoint
curl -X POST https://your-railway-url.up.railway.app/api/research \
  -H "Content-Type: application/json" \
  -d '{"query": "test query"}'
```

### End-to-End Test

1. Open your Vercel frontend
2. Enter a demo query (e.g., "Latest developments in quantum computing 2024")
3. Click "Start Research"
4. Should see progress indicators
5. Should receive results from backend

---

## 🔧 Troubleshooting

### Backend Issues

**Problem**: Backend not starting
- Check Railway logs: Dashboard → Service → Logs
- Verify `Procfile` exists in root: `web: cd backend && python main.py`
- Check environment variables are set correctly

**Problem**: CORS errors
- Verify `ALLOWED_ORIGINS` includes your Vercel URL
- Check Railway logs for CORS-related errors
- Ensure `VERCEL_URL` environment variable is set (if using)

**Problem**: API key errors
- Verify `OPEN_ROUTER_KEY` is set in Railway
- Check key format (should start with `sk-or-`)
- Test API key locally first

### Frontend Issues

**Problem**: Frontend can't connect to backend
- Verify `VITE_API_URL` is set in Vercel environment variables
- Check that Railway backend URL is correct
- Open browser DevTools → Network tab to see actual API calls

**Problem**: Build fails
- Check Vercel build logs
- Verify `package.json` has all dependencies
- Ensure TypeScript compiles without errors

**Problem**: 404 errors on routes
- Verify `vercel.json` exists with proper rewrites
- Check that `outputDirectory` is set to `frontend/dist`

---

## 📝 Environment Variables Reference

### Railway (Backend)

| Variable | Description | Example |
|----------|-------------|---------|
| `OPEN_ROUTER_KEY` | OpenRouter API key | `sk-or-...` |
| `TAVILY_API_KEY` | Tavily search API key | `tvly-...` |
| `ENVIRONMENT` | Environment name | `production` |
| `PORT` | Server port | `8000` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `https://app.vercel.app` |

### Vercel (Frontend)

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `https://app.up.railway.app` |

---

## 🔄 Updating Deployments

### Update Backend

1. Make changes to backend code
2. Commit and push to GitHub
3. Railway automatically redeploys

### Update Frontend

1. Make changes to frontend code
2. Commit and push to GitHub
3. Vercel automatically redeploys

---

## 🎯 Production URLs

After deployment, you'll have:

```
Frontend:  https://your-app.vercel.app
Backend:   https://your-app.up.railway.app

API Endpoints:
  /api/health          → Health check
  /api/research        → Main research endpoint
  /api/research-stream → Streaming research endpoint
  /api/demo-queries    → Demo queries list
```

---

## 📊 Monitoring

### Railway Dashboard

- View logs in real-time
- Monitor CPU/memory usage
- See request metrics

### Vercel Dashboard

- View deployment history
- See build logs
- Monitor performance
- View analytics

---

## 🚨 Fallback Strategy

If cloud deployment fails during demo:

1. **Local Fallback**: Run `./run_backend.sh` and `cd frontend && npm run dev`
2. **Docker Fallback**: Use `docker-compose up` (if configured)
3. **Screenshots**: Have screenshots ready as backup

---

## ✅ Deployment Checklist

Before presenting:

- [ ] Backend deployed to Railway
- [ ] Backend health check returns 200
- [ ] Frontend deployed to Vercel
- [ ] Frontend loads without errors
- [ ] Environment variables set correctly
- [ ] CORS configured properly
- [ ] End-to-end test passes
- [ ] Demo queries work
- [ ] Local fallback ready (just in case)

---

## 🎉 You're Done!

Your Multi-Agent AI Deep Researcher is now live in production!

**Next Steps:**
- Share your Vercel URL with judges
- Monitor both dashboards during demo
- Have Railway/Vercel dashboards open to show deployment

**Pro Tip**: Keep both dashboards open during presentation to show real-time monitoring!

