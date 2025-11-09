# How to Change Git Branch in Vercel

## Changing the Deployment Branch

Vercel allows you to deploy from different Git branches. Here's how to change it:

---

## Method 1: Project Settings (Recommended)

### Step 1: Access Project Settings

1. Go to https://vercel.com
2. Sign in to your account
3. Click on your **project** (the one you want to configure)
4. Click **"Settings"** tab (gear icon at the top)

### Step 2: Configure Git Branch

1. In Settings, scroll to **"Git"** section
2. Find **"Production Branch"** setting
3. Click the dropdown or input field
4. Select or type your branch name (e.g., `main`, `master`, `feature/ui-integration`)
5. Click **"Save"** button

**Visual Path:**
```
Vercel Dashboard
  └─ Your Project (click it)
      └─ Settings Tab (gear icon)
          └─ Git Section
              └─ Production Branch (dropdown)
                  └─ Select your branch
                      └─ Save
```

---

## Method 2: During Project Creation

If you're creating a new project:

1. **Add New Project** → Select your GitHub repo
2. In the configuration screen, look for **"Git Branch"** or **"Production Branch"**
3. Select your branch from the dropdown
4. Continue with deployment

---

## Branch Configuration Options

### Production Branch

- **Location**: Settings → Git → Production Branch
- **Purpose**: Branch used for production deployments
- **Default**: Usually `main` or `master`
- **Change**: Select any branch from your repo

### Preview Branches

- **Location**: Settings → Git → Preview Branches
- **Purpose**: Automatically create preview deployments for other branches
- **Default**: All branches (creates preview for every push)
- **Options**: 
  - All branches
  - Only specific branches
  - Ignore certain branches

---

## Step-by-Step: Change to Feature Branch

### Example: Deploy from `feature/ui-integration` branch

1. **Go to Vercel**: https://vercel.com
2. **Click your project**
3. **Click "Settings"** tab
4. **Scroll to "Git" section**
5. **Find "Production Branch"**
6. **Click the dropdown** → Select `feature/ui-integration`
7. **Click "Save"**
8. **Vercel will automatically redeploy** from the new branch

---

## Branch Selection Options

### Option 1: Deploy Specific Branch

1. Settings → Git → Production Branch
2. Select branch from dropdown
3. Save

### Option 2: Deploy All Branches (Preview)

1. Settings → Git → Preview Branches
2. Enable "All branches"
3. Each branch gets its own preview URL

### Option 3: Ignore Branches

1. Settings → Git → Ignored Build Step
2. Add branch names to ignore
3. Vercel won't deploy these branches

---

## Common Branch Names

- `main` - Default main branch
- `master` - Legacy main branch
- `develop` - Development branch
- `feature/*` - Feature branches
- `release/*` - Release branches
- `hotfix/*` - Hotfix branches

---

## After Changing Branch

1. **Vercel automatically redeploys** from the new branch
2. **Check "Deployments" tab** to see the new deployment
3. **Wait for build to complete** (green checkmark)
4. **Your production URL** will now reflect the new branch

---

## Troubleshooting

### Branch Not Showing in Dropdown?

**Problem**: Your branch doesn't appear in the dropdown

**Solution**:
1. Make sure the branch exists in your GitHub repo
2. Push the branch to GitHub: `git push origin your-branch-name`
3. Refresh Vercel settings page
4. The branch should now appear

### Deployment Fails After Branch Change?

**Problem**: Build fails after switching branches

**Solution**:
1. Check **"Deployments"** tab → Click failed deployment → **"Logs"**
2. Verify the branch has all necessary files:
   - `frontend/package.json`
   - `frontend/vite.config.ts`
   - `vercel.json` (if exists)
3. Check that build command works for that branch
4. Verify environment variables are set correctly

### Want to Deploy Multiple Branches?

**Solution**: Use Preview Deployments
1. Settings → Git → Preview Branches
2. Enable "All branches"
3. Each branch gets its own preview URL
4. Production still uses your Production Branch

---

## Quick Reference

### Change Production Branch

```
Vercel Dashboard
  → Your Project
    → Settings Tab
      → Git Section
        → Production Branch
          → Select Branch
            → Save
```

### View Current Branch

```
Vercel Dashboard
  → Your Project
    → Deployments Tab
      → Latest Deployment
        → See "Branch" column
```

### Deploy Specific Branch Manually

```
Vercel Dashboard
  → Your Project
    → Deployments Tab
      → "Create Deployment" button
        → Select Branch
          → Deploy
```

---

## Best Practices

1. **Production Branch**: Use `main` or `master` for production
2. **Feature Branches**: Use Preview Deployments for testing
3. **Branch Protection**: Configure in GitHub to prevent direct pushes to main
4. **Environment Variables**: Set per branch if needed (Settings → Environment Variables)

---

## Example Workflow

### Scenario: Deploy from `feature/ui-integration` branch

1. **Push branch to GitHub**:
   ```bash
   git push origin feature/ui-integration
   ```

2. **Change Vercel Production Branch**:
   - Settings → Git → Production Branch → `feature/ui-integration`
   - Save

3. **Vercel automatically deploys**:
   - Check Deployments tab
   - Wait for build to complete
   - Production URL now uses this branch

4. **When ready for production**:
   - Merge `feature/ui-integration` → `main`
   - Change Production Branch back to `main`
   - Or just merge and Vercel will auto-deploy from `main`

---

## Need Help?

- Vercel Docs: https://vercel.com/docs/concepts/git
- Vercel Dashboard: https://vercel.com/dashboard
- Check deployment logs in Vercel dashboard

