# 🚀 Quick Deploy Guide (15 Minutes)

## Prerequisites
- ✅ Code pushed to GitHub
- ✅ Vercel account (free)
- ✅ Railway account (free)
- ✅ API keys ready

---

## Step 1: Deploy Backend to Railway (5 min)

1. **Go to Railway**: https://railway.app
2. **New Project** → **Deploy from GitHub repo**
3. **Select your repo**
4. **Configure Service**:
   - Root Directory: `backend`
   - Start Command: `python main.py`
5. **Set Environment Variables**:
   ```
   OPEN_ROUTER_KEY=sk-or-your-key
   TAVILY_API_KEY=your-key
   ENVIRONMENT=production
   PORT=8000
   ```
6. **Wait for deployment** → Copy Railway URL

---

## Step 2: Deploy Frontend to Vercel (5 min)

1. **Go to Vercel**: https://vercel.com
2. **Add New Project** → **Select GitHub repo**
3. **Configure**:
   - Framework: Vite
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
4. **Set Environment Variable**:
   ```
   VITE_API_URL=https://your-railway-url.up.railway.app
   ```
5. **Deploy** → Copy Vercel URL

---

## Step 3: Update CORS (2 min)

1. **Go back to Railway**
2. **Update Environment Variable**:
   ```
   ALLOWED_ORIGINS=https://your-vercel-url.vercel.app
   ```
3. **Railway auto-redeploys**

---

## Step 4: Test (3 min)

1. **Visit Vercel URL**
2. **Enter test query**
3. **Verify it works!**

---

## ✅ Done!

Your app is live:
- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://your-app.up.railway.app`

---

## 🆘 Troubleshooting

**Backend not starting?**
- Check Railway logs
- Verify `Procfile` exists: `web: cd backend && python main.py`

**CORS errors?**
- Verify `ALLOWED_ORIGINS` includes Vercel URL
- Check Railway logs

**Frontend can't connect?**
- Verify `VITE_API_URL` is set correctly
- Check browser DevTools → Network tab

---

**Full guide**: See `DEPLOYMENT.md` for detailed instructions.

