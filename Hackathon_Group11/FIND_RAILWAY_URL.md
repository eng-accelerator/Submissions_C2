# How to Find Your Railway URL

## Where to Find Your Railway Deployment URL

After Railway deploys your service, you need to find the public URL. Here's where to look:

---

## Method 1: Service Overview (Easiest)

1. **Click on your service** in the Railway dashboard
2. Look at the **top of the service page**
3. You'll see a section showing:
   - **"Public Domain"** or
   - **"Domain"** or
   - **"URL"**
4. The URL will look like: `https://your-app-name.up.railway.app`
5. **Click the copy icon** (📋) next to the URL to copy it

**Visual Location:**
```
┌─────────────────────────────────────┐
│  Your Service Name                  │
│  ┌───────────────────────────────┐ │
│  │ 🌐 Public Domain              │ │ ← Look here!
│  │ https://your-app.up.railway.app │ │
│  │ [📋 Copy]                     │ │
│  └───────────────────────────────┘ │
│                                     │
│  [Overview] [Variables] [Settings]│
└─────────────────────────────────────┘
```

---

## Method 2: Settings → Networking

If you don't see a domain automatically:

1. **Click on your service**
2. Click **"Settings"** tab (gear icon)
3. Scroll to **"Networking"** section
4. Click **"Generate Domain"** button
5. Railway will create a public URL
6. Copy the URL that appears

**Path:**
```
Service → Settings Tab → Networking Section → Generate Domain
```

---

## Method 3: Service Settings → Domains

1. **Click on your service**
2. Click **"Settings"** tab
3. Look for **"Domains"** section
4. You'll see your Railway domain listed
5. Copy the URL

---

## What the URL Looks Like

Railway URLs typically look like:
```
https://your-service-name-production.up.railway.app
```

Or:
```
https://your-app-name.up.railway.app
```

---

## If You Don't See a URL

### Option 1: Generate Domain

1. Go to **Settings** → **Networking**
2. Click **"Generate Domain"**
3. Railway will create a public URL

### Option 2: Check Deployment Status

1. Click **"Deployments"** tab
2. Make sure deployment shows **"Active"** (green checkmark)
3. If deployment failed, check **"Logs"** tab for errors

### Option 3: Check Service Status

1. Look at the service overview
2. Make sure it shows **"Active"** or **"Running"**
3. If it shows **"Failed"**, check logs

---

## Quick Checklist

- [ ] Service is deployed (green checkmark in Deployments tab)
- [ ] Service status shows "Active" or "Running"
- [ ] Public domain is visible in service overview
- [ ] URL starts with `https://` and ends with `.up.railway.app`
- [ ] URL is copied and ready to use

---

## Using the URL

Once you have your Railway URL:

1. **Test it**: Open in browser: `https://your-app.up.railway.app/api/health`
   - Should return: `{"status": "ok", "message": "API is running"}`

2. **Use in Vercel**: Set `VITE_API_URL` environment variable to your Railway URL

3. **Update CORS**: In Railway Variables, set `ALLOWED_ORIGINS` to include your Vercel URL

---

## Example

After deployment, you might see:

```
Service: multi-agent-researcher
Status: Active ✅
Public Domain: https://multi-agent-researcher-production.up.railway.app
```

**Copy this URL** - you'll need it for:
- Setting `VITE_API_URL` in Vercel
- Testing your API
- Updating CORS settings

---

## Troubleshooting

**No URL visible?**
- Make sure deployment completed successfully
- Check Deployments tab for errors
- Try generating domain in Settings → Networking

**URL not working?**
- Check service logs for errors
- Verify environment variables are set
- Make sure `PORT` environment variable is set to `8000`

**Can't find the service?**
- Make sure you're in the correct project
- Check that the service was created after connecting GitHub repo

---

## Need Help?

- Railway Docs: https://docs.railway.app/deploy/configuring
- Railway Discord: https://discord.gg/railway
- Check Railway dashboard → Service → Logs for errors

