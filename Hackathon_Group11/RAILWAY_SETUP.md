# Railway Setup Guide - Step by Step

## Where to Configure Service Settings in Railway

### Step 1: Access Your Service

1. Go to https://railway.app
2. Sign in with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select your repository
5. Railway will automatically create a service

### Step 2: Configure Root Directory

**Location**: Service Settings → Source Section

1. **Click on your service** (the box that appeared after connecting GitHub)
2. Click the **"Settings"** tab (gear icon on the right sidebar)
3. Scroll down to **"Source"** section
4. Find **"Root Directory"** field
5. Enter: `backend`
6. Click **"Save"** (if button appears)

**Visual Path:**
```
Railway Dashboard
  └─ Your Project
      └─ Your Service (click it)
          └─ Settings Tab (gear icon)
              └─ Source Section
                  └─ Root Directory: `backend`
```

### Step 3: Configure Start Command (Optional)

**Location**: Service Settings → Deploy Section

1. In the same **Settings** tab
2. Scroll to **"Deploy"** section
3. Find **"Start Command"** field
4. Enter: `python main.py`
   - **Note**: Railway usually auto-detects this, so you might not need to set it
5. Click **"Save"** if you made changes

**Alternative**: Railway will use your `Procfile` if it exists in the root directory.

### Step 4: Set Environment Variables

**Location**: Service → Variables Tab

1. Click the **"Variables"** tab (next to Settings)
2. Click **"+ New Variable"** button
3. Add each variable one by one:

```
Name: OPEN_ROUTER_KEY
Value: sk-or-your-actual-key-here
```

```
Name: TAVILY_API_KEY
Value: your-tavily-key-here
```

```
Name: ENVIRONMENT
Value: production
```

```
Name: PORT
Value: 8000
```

4. After adding all variables, Railway will automatically redeploy

**Visual Path:**
```
Railway Dashboard
  └─ Your Project
      └─ Your Service
          └─ Variables Tab (click it)
              └─ + New Variable (button)
                  └─ Enter Name and Value
```

### Step 5: View Deployment

**Location**: Service → Deployments Tab

1. Click **"Deployments"** tab to see build progress
2. Click **"Logs"** tab to see real-time logs
3. Wait for deployment to complete (green checkmark)
4. Your service URL will appear at the top (e.g., `https://your-app.up.railway.app`)

---

## Quick Reference: Railway Dashboard Layout

```
┌─────────────────────────────────────┐
│  Railway Dashboard                   │
├─────────────────────────────────────┤
│  Projects                            │
│  ┌───────────────────────────────┐  │
│  │ Your Project                  │  │
│  │  ┌─────────────────────────┐ │  │
│  │  │ Your Service            │ │  │ ← Click here
│  │  │                         │ │  │
│  │  │ [Overview] [Variables]   │ │  │
│  │  │ [Settings] [Deployments]  │ │  │
│  │  │ [Logs] [Metrics]         │ │  │
│  │  └─────────────────────────┘ │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

---

## Troubleshooting

### Can't find Settings tab?

- Make sure you clicked on the **service** (not just the project)
- The service is the box that shows your GitHub repo name
- Settings tab is on the right sidebar when viewing the service

### Root Directory not saving?

- Make sure you're in the **Settings** tab
- Scroll down to **Source** section
- Type `backend` (lowercase, no quotes)
- Click **Save** if the button appears
- Railway will redeploy automatically

### Service not deploying?

1. Check **Logs** tab for errors
2. Verify **Root Directory** is set to `backend`
3. Check that `backend/main.py` exists in your repo
4. Verify `backend/requirements.txt` exists
5. Check **Variables** tab - make sure all required env vars are set

---

## Alternative: Using Procfile

If you have a `Procfile` in your root directory with:
```
web: cd backend && python main.py
```

Railway will automatically use it, and you might not need to set Root Directory or Start Command manually.

---

## Need Help?

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Check deployment logs in Railway dashboard

