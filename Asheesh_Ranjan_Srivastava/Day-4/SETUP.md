# Setup Guide: LinkedIn Job Automation Workflow

Complete step-by-step guide to set up and run the automated LinkedIn job application system.

---

## Prerequisites

### Required Accounts:
1. **n8n** (Cloud or Self-hosted)
   - Cloud: https://n8n.io/cloud (recommended for beginners)
   - Self-hosted: https://docs.n8n.io/hosting/

2. **Gmail Account**
   - Enable LinkedIn job alerts emails
   - Configure Gmail API access (see below)

3. **OpenAI Account**
   - Sign up: https://platform.openai.com/
   - API key with credits
   - Models needed: GPT-5, GPT-4o-latest, GPT-4o-mini

4. **HeyGen Account** (Optional for video generation)
   - Sign up: https://heygen.com/
   - API access required

5. **Google Sheets**
   - Google account with Sheets access
   - Create a tracking sheet (see below)

---

## Step 1: Set Up n8n

### Option A: n8n Cloud (Easiest)
1. Go to https://n8n.io/cloud
2. Sign up for an account
3. Create a new workspace
4. Note your workspace URL

### Option B: Self-Hosted (Advanced)
```bash
# Using Docker
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# Or using npm
npm install n8n -g
n8n start
```

---

## Step 2: Configure Gmail API

### Enable Gmail API:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API:
   - APIs & Services → Library
   - Search "Gmail API"
   - Click Enable

4. Create OAuth 2.0 Credentials:
   - APIs & Services → Credentials
   - Create Credentials → OAuth 2.0 Client ID
   - Application type: Web application
   - Add redirect URI: `https://YOUR_N8N_URL/rest/oauth2-credential/callback`

5. Note your Client ID and Client Secret

### Connect to n8n:
1. In n8n: Credentials → Add Credential
2. Select "Gmail OAuth2 API"
3. Enter Client ID and Client Secret
4. Click "Connect my account"
5. Authorize access

---

## Step 3: Configure OpenAI API

1. Get API Key:
   - Go to https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Copy the key (you won't see it again!)

2. Add to n8n:
   - Credentials → Add Credential
   - Select "OpenAI API"
   - Paste API key
   - Save

3. Verify Access:
   - Ensure you have credits
   - Check rate limits: https://platform.openai.com/account/limits

---

## Step 4: Configure HeyGen API (Optional)

1. Get API Key:
   - Sign up at https://heygen.com/
   - Go to Account → API
   - Generate API key

2. Add to n8n:
   - Credentials → Add Credential
   - Select "HTTP Header Auth"
   - Header Name: `X-Api-Key`
   - Value: Your HeyGen API key
   - Save as "heygenApiKey"

**Note:** Video generation is optional. Workflow will work without HeyGen, just won't generate videos.

---

## Step 5: Set Up Google Sheets

### Create Tracking Sheet:
1. Go to [Google Sheets](https://sheets.google.com/)
2. Create new spreadsheet
3. Name it: "LinkedIn Job Applications Tracker"
4. Create columns (exact names):
   - Title
   - Job Description
   - Link
   - Date
   - Rating
   - Company Name
   - Benefits
   - Location
   - Match Explanation
   - Cover Letter
   - Video Script
   - Video URL

5. Copy the Sheet ID from URL:
   ```
   https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/edit
   ```

### Connect to n8n:
1. Credentials → Add Credential
2. Select "Google Sheets OAuth2 API"
3. Follow OAuth flow to authorize
4. Save

---

## Step 6: Import Workflow

1. **Download workflow.json** from this repository
2. In n8n:
   - Click "+" → Import from File
   - Select `workflow.json`
   - Click Import

3. **Update Credentials:**
   - Click each node that needs credentials
   - Select your configured credentials from dropdown
   - Nodes needing credentials:
     - "Get LinkedIn Email IDs" → Gmail OAuth2
     - "Fetch Full Email via API" → Gmail OAuth2
     - "Extract Job Data" → OpenAI API
     - "Rate Job Match" → OpenAI API
     - "Generate Cover Letter" → OpenAI API
     - "Create Video Script" → OpenAI API
     - "Generate Video (HeyGen)" → HeyGen API (optional)
     - "Check Video Status" → HeyGen API (optional)
     - "Save to Google Sheet" → Google Sheets OAuth2
     - "Save to Sheet (No Video)" → Google Sheets OAuth2
     - "Mark Email as Read" → Gmail OAuth2

---

## Step 7: Customize Profile Data

**IMPORTANT:** The workflow includes MY profile data. You MUST update it with YOUR information.

### Edit "Rate Job Match" Node:
1. Click on "Rate Job Match" node
2. Find the "Candidate Profile" section in the prompt
3. Replace with YOUR:
   - Name
   - Skills (technical and soft skills)
   - Experience level
   - Target roles
   - Salary expectations
   - Location preferences
   - Recent projects
   - Education
   - Preferences (remote/hybrid, company types, etc.)

### Edit "Generate Cover Letter" Node:
1. Click on "Generate Cover Letter" node
2. Update candidate information in prompt
3. Update recent achievements and projects

### Edit "Create Video Script" Node:
1. Click on "Create Video Script" node
2. Update candidate name and key achievements

---

## Step 8: Update Google Sheet ID

1. Open "Save to Sheet (No Video)" node
2. Click on "Document ID" field
3. Replace with YOUR Google Sheet ID
4. Save

Repeat for "Save to Google Sheet" node if used.

---

## Step 9: Configure Gmail Filter

### Update Email Query:
1. Click "Get LinkedIn Email IDs" node
2. Update filters:
   - `sender`: Keep as `jobs-listings@linkedin.com`
   - `receivedAfter`: Change to your desired start date

### Enable LinkedIn Job Alerts:
1. Go to LinkedIn → Jobs
2. Set up job alerts for roles you want
3. Configure to email you daily/weekly
4. Alerts will come from `jobs-listings@linkedin.com`

---

## Step 10: Test the Workflow

### Test with 1 Email First:

1. **Manual Test:**
   - Click "Execute workflow" button
   - Check each node output
   - Verify data is correct

2. **Check Results:**
   - Look at Google Sheet - data should appear
   - Verify cover letter quality
   - Check if rating makes sense

3. **Debug Issues:**
   - Click on any red node to see error
   - Check credentials are connected
   - Verify API keys have credits
   - Check Sheet ID is correct

### Common Issues:

**No URLs Found:**
- Check Gmail query is correct
- Verify LinkedIn sends job alerts to this email
- Check emails have `/comm/jobs/view/` links

**Extraction Fails:**
- Verify OpenAI API key has credits
- Check rate limits not exceeded
- Ensure GPT models are accessible

**Sheet Write Fails:**
- Verify Sheet ID is correct
- Check column names match exactly
- Ensure Google Sheets credentials authorized

---

## Step 11: Activate Automation

### Set Schedule:
1. Click "Schedule (Daily 3 AM)" node
2. Adjust cron expression if needed:
   - Current: `0 3 * * *` (3 AM daily)
   - Change time if desired (e.g., `0 9 * * *` for 9 AM)

### Activate Workflow:
1. Click "Active" toggle (top right)
2. Workflow will now run automatically
3. Check execution history to monitor runs

---

## Step 12: Monitor and Optimize

### Check Daily:
- Review execution log
- Check Google Sheet for new entries
- Verify cover letters are high quality
- Adjust profile data if matches are poor

### Optimize Over Time:
1. **Adjust Rating Criteria:**
   - If too many low ratings: Make criteria more lenient
   - If too many high ratings: Make criteria stricter

2. **Refine Prompts:**
   - Improve cover letter quality
   - Adjust video script tone
   - Tune job description extraction

3. **Add HTML Parsing:** (Future optimization)
   - Reduces costs by 99%
   - See README.md for details

---

## Cost Estimation

### Daily Costs (50 jobs):
- **OpenAI GPT-5:** ~$5-7 (extraction)
- **OpenAI GPT-4o-latest:** ~$5-7 (rating + cover letters)
- **OpenAI GPT-4o-mini:** ~$0.50 (video scripts)
- **HeyGen Videos:** ~$3-6 (20 videos at ≥4 rating)
- **Total:** ~$13-20/day

### Cost Optimization:
- **Free tier:** Use OpenAI free credits initially
- **Reduce jobs:** Filter emails more strictly
- **Skip videos:** Disable HeyGen for now
- **HTML parsing:** Implement to save 99% extraction cost

---

## Troubleshooting

### Workflow Not Running:
- [ ] Check "Active" toggle is ON
- [ ] Verify schedule trigger is configured
- [ ] Check n8n has internet access
- [ ] Review execution log for errors

### No Emails Processed:
- [ ] Confirm LinkedIn sends alerts to Gmail
- [ ] Check Gmail query filters
- [ ] Verify OAuth not expired
- [ ] Check email date range

### Extraction Errors:
- [ ] Verify OpenAI API key valid
- [ ] Check API credits remain
- [ ] Ensure rate limits not hit
- [ ] Review error messages in node output

### Sheet Write Errors:
- [ ] Verify Sheet ID correct
- [ ] Check column names exact match
- [ ] Ensure OAuth authorized
- [ ] Check sheet not protected/locked

---

## Security Best Practices

### Protect Your Credentials:
- ❌ Never commit API keys to git
- ❌ Never share workflow with credentials
- ✅ Use n8n's credential encryption
- ✅ Export workflow without credentials
- ✅ Rotate API keys periodically

### Data Privacy:
- Your profile data is in the workflow
- Cover letters contain personal information
- Google Sheet has application history
- Consider privacy when sharing

---

## Next Steps

1. ✅ Complete all setup steps above
2. ✅ Test with 1-2 emails first
3. ✅ Customize profile data thoroughly
4. ✅ Review and adjust rating criteria
5. ✅ Activate workflow for daily automation
6. 📈 Monitor results and optimize over time

---

## Getting Help

### Resources:
- **n8n Docs:** https://docs.n8n.io/
- **n8n Community:** https://community.n8n.io/
- **OpenAI Docs:** https://platform.openai.com/docs
- **Gmail API Docs:** https://developers.google.com/gmail/api

### Common Questions:
See [CREDENTIALS.md](CREDENTIALS.md) for detailed credential setup.
See [README.md](README.md) for project overview and learning journey.

---

**Setup completed?** You should now have a fully functional automated job application system!

**Need help?** Check the troubleshooting section above or refer to n8n community forums.

---

**Last Updated:** October 31, 2025
**Author:** Asheesh Ranjan Srivastava
**Project:** OutSkill AI Engineering Bootcamp 2025 - Day 4
