# Troubleshooting: Unable to Change Branch in Vercel

## Common Issues and Solutions

---

## Issue 1: Branch Not Showing in Dropdown

### Problem
The branch you want doesn't appear in the Production Branch dropdown.

### Solutions

**Solution A: Push Branch to GitHub**
```bash
# Make sure your branch is pushed to GitHub
git push origin your-branch-name

# Example:
git push origin feature/ui-integration
```

**Solution B: Refresh Vercel**
1. Go to Vercel Dashboard
2. Click your project
3. Go to Settings → Git
4. Click "Disconnect" (temporarily)
5. Click "Connect Git Repository" again
6. Select your repo
7. Now all branches should appear

**Solution C: Check Branch Exists**
1. Go to your GitHub repo
2. Click "Branches" dropdown
3. Verify your branch exists
4. If not, push it: `git push origin branch-name`

---

## Issue 2: Dropdown is Disabled/Grayed Out

### Problem
The Production Branch dropdown is disabled and you can't select anything.

### Solutions

**Solution A: Check Repository Connection**
1. Settings → Git
2. Verify repository is connected
3. If not connected, click "Connect Git Repository"
4. Reconnect your GitHub repo

**Solution B: Check Permissions**
1. Make sure you have admin access to the Vercel project
2. If you're a collaborator, ask project owner for admin access
3. Only admins can change production branch

**Solution C: Disconnect and Reconnect**
1. Settings → Git → "Disconnect Repository"
2. Click "Connect Git Repository" again
3. Select your repo
4. Now you should be able to change branch

---

## Issue 3: Changes Not Saving

### Problem
You select a branch but it doesn't save or reverts back.

### Solutions

**Solution A: Check Network**
1. Refresh the page
2. Try again
3. Make sure you have internet connection

**Solution B: Clear Browser Cache**
1. Hard refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
2. Or clear browser cache
3. Try again

**Solution C: Try Different Browser**
1. Try Chrome, Firefox, or Edge
2. Sometimes browser extensions interfere

---

## Issue 4: Branch Changed But Not Deploying

### Problem
You changed the branch but Vercel isn't deploying from it.

### Solutions

**Solution A: Trigger Manual Deployment**
1. Go to Deployments tab
2. Click "Create Deployment" button
3. Select your branch
4. Click "Deploy"

**Solution B: Push to Branch**
```bash
# Make a small change and push
git checkout your-branch-name
# Make a small change (add a comment, etc.)
git add .
git commit -m "Trigger Vercel deployment"
git push origin your-branch-name
```

**Solution C: Check Branch Protection**
1. Go to GitHub → Settings → Branches
2. Check if branch has protection rules
3. Vercel might need permissions to deploy

---

## Issue 5: Can't Find Settings Tab

### Problem
You can't find where to change the branch.

### Solutions

**Solution A: Check Project Access**
1. Make sure you're viewing the correct project
2. Click on project name in dashboard
3. Settings tab should be at the top

**Solution B: Use Direct URL**
1. Go to: `https://vercel.com/your-username/your-project/settings/git`
2. Replace with your actual username and project name
3. This takes you directly to Git settings

**Solution C: Alternative Method**
1. Go to Deployments tab
2. Click "Create Deployment"
3. Select branch from there
4. This creates a one-time deployment

---

## Step-by-Step: Force Branch Change

### Method 1: Disconnect and Reconnect

1. **Go to Vercel**: https://vercel.com
2. **Click your project**
3. **Settings** → **Git** section
4. **Click "Disconnect Repository"** (at bottom)
5. **Confirm disconnect**
6. **Click "Connect Git Repository"**
7. **Select your GitHub repo**
8. **During setup, select your branch**
9. **Complete setup**

### Method 2: Manual Deployment

1. **Go to Deployments tab**
2. **Click "Create Deployment"** button (top right)
3. **Select "GitHub"** as source
4. **Select your repository**
5. **Select your branch** from dropdown
6. **Click "Deploy"**
7. **After deployment, go to Settings → Git**
8. **Set this as Production Branch**

### Method 3: Use Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Link project
vercel link

# Deploy from specific branch
vercel --prod --branch=your-branch-name
```

---

## Verify Branch is Available

### Check in GitHub

1. Go to your GitHub repo
2. Click "Branches" dropdown (top left)
3. Verify your branch is listed
4. If not, push it:
   ```bash
   git push origin your-branch-name
   ```

### Check in Vercel

1. Go to Vercel Dashboard
2. Your Project → Deployments
3. Click "Create Deployment"
4. Check if your branch appears in dropdown
5. If not, it's not pushed to GitHub

---

## Alternative: Deploy Specific Branch Manually

If you can't change the production branch:

1. **Go to Deployments tab**
2. **Click "Create Deployment"**
3. **Select your branch**
4. **Deploy**
5. **This creates a preview deployment**
6. **You can promote it to production later**

---

## Still Not Working?

### Contact Vercel Support

1. Go to: https://vercel.com/support
2. Click "Contact Support"
3. Explain the issue:
   - What branch you're trying to use
   - What error you see
   - Screenshot of the issue

### Check Vercel Status

1. Go to: https://vercel-status.com
2. Check if there are any outages
3. Sometimes Vercel has temporary issues

---

## Quick Checklist

Before trying to change branch:

- [ ] Branch exists in GitHub
- [ ] Branch is pushed to GitHub (`git push origin branch-name`)
- [ ] You have admin access to Vercel project
- [ ] Repository is connected in Vercel
- [ ] You're in the correct project
- [ ] Browser is up to date
- [ ] No browser extensions blocking

---

## Common Mistakes

1. **Not pushing branch to GitHub** - Vercel can only see branches in GitHub
2. **Wrong repository** - Make sure you're in the right project
3. **No admin access** - Only admins can change production branch
4. **Branch name typo** - Check exact branch name in GitHub
5. **Cached page** - Hard refresh the page

---

## Need More Help?

- Vercel Docs: https://vercel.com/docs/concepts/git
- Vercel Discord: https://vercel.com/discord
- GitHub: Check your branch exists and is pushed

