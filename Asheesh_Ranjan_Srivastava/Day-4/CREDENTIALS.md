# Credentials Setup Guide

Complete guide for configuring all API credentials and OAuth connections needed for the LinkedIn job automation workflow.

---

## Overview

This workflow requires 4 main credential connections:
1. **Gmail OAuth2** - Read emails and mark as read
2. **OpenAI API** - AI text generation (extraction, rating, cover letters, video scripts)
3. **HeyGen API** - AI video generation (optional)
4. **Google Sheets OAuth2** - Save application data

---

## 1. Gmail OAuth2 Credentials

### Why Needed:
- Read LinkedIn job alert emails
- Extract full email content via Gmail API
- Mark emails as read after processing

### Setup Instructions:

#### A. Enable Gmail API in Google Cloud:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project:
   - Click "Select a project" → "New Project"
   - Name: "LinkedIn Job Automation" (or your choice)
   - Click "Create"

3. Enable Gmail API:
   - Navigate to "APIs & Services" → "Library"
   - Search for "Gmail API"
   - Click on it → Click "Enable"

4. Create OAuth 2.0 Credentials:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Configure consent screen if prompted:
     - User Type: External
     - App name: "LinkedIn Job Automation"
     - User support email: Your email
     - Developer contact: Your email
     - Save and Continue through all steps

5. Create OAuth Client:
   - Application type: **Web application**
   - Name: "n8n Gmail Integration"
   - Authorized redirect URIs: Add these URLs:
     ```
     https://app.n8n.cloud/rest/oauth2-credential/callback
     http://localhost:5678/rest/oauth2-credential/callback
     ```
     (Use first one for n8n Cloud, second for self-hosted)

6. **Save These Values:**
   - Client ID: `123456789.apps.googleusercontent.com`
   - Client Secret: `GOCSPX-abc123...`

#### B. Add to n8n:

1. In n8n, go to **Credentials** → **Add Credential**
2. Search and select **"Gmail OAuth2 API"**
3. Enter:
   - **Client ID:** [Your Client ID from step A6]
   - **Client Secret:** [Your Client Secret from step A6]
4. Click **"Sign in with Google"**
5. Select your Gmail account
6. Grant permissions:
   - ✅ Read emails
   - ✅ Modify emails
   - ✅ Manage labels
7. Click **"Save"**

#### C. Test Connection:

In n8n workflow:
1. Click "Get LinkedIn Email IDs" node
2. Select your Gmail credential from dropdown
3. Click "Execute Node"
4. Should show recent emails

---

## 2. OpenAI API Credentials

### Why Needed:
- **GPT-5:** Extract job details from HTML (high accuracy)
- **GPT-4o-latest:** Rate job fit + Generate cover letters (quality critical)
- **GPT-4o-mini:** Create video scripts (cost-optimized)

### Setup Instructions:

#### A. Get OpenAI API Key:

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to [API Keys](https://platform.openai.com/api-keys)
4. Click **"Create new secret key"**
5. Name: "n8n LinkedIn Automation"
6. **IMPORTANT:** Copy the key immediately (you won't see it again!)
   ```
   sk-proj-abc123xyz789...
   ```

#### B. Add Credits:

1. Go to [Billing](https://platform.openai.com/account/billing)
2. Add payment method
3. Set usage limits (recommended: $20-50/month for this workflow)
4. Monitor usage regularly

#### C. Add to n8n:

1. In n8n, go to **Credentials** → **Add Credential**
2. Select **"OpenAI API"**
3. Enter:
   - **API Key:** [Your sk-proj-... key from step A6]
4. Click **"Save"**

#### D. Test Connection:

In n8n workflow:
1. Click "Extract Job Data" node
2. Select your OpenAI credential
3. Click "Execute Node"
4. Should show successful completion

### Cost Monitoring:

Check usage at: https://platform.openai.com/usage

**Expected Costs (50 jobs/day):**
- GPT-5 extraction: ~$5-7/day
- GPT-4o-latest (rating + letters): ~$5-7/day
- GPT-4o-mini (video scripts): ~$0.50/day
- **Total:** ~$10-15/day

**Cost Optimization:**
- Process fewer jobs (adjust Gmail filter)
- Use GPT-4o-mini for more tasks (lower quality but cheaper)
- Implement HTML parsing (saves 99% extraction cost)

---

## 3. HeyGen API Credentials (Optional)

### Why Needed:
- Generate AI avatar videos for high-match jobs (rating ≥4)
- Creates 45-second personalized application videos

### Setup Instructions:

#### A. Get HeyGen API Key:

1. Go to [HeyGen](https://heygen.com/)
2. Sign up for account
3. Navigate to **Account** → **API**
4. Click **"Generate API Key"**
5. Copy the key:
   ```
   HG-abc123xyz789...
   ```

#### B. Add Credits/Plan:

HeyGen uses credits or subscription:
- Check pricing: https://heygen.com/pricing
- Videos cost ~$0.30-0.50 per minute
- 45-second videos = ~$0.25-0.35 each
- Expected: 20 videos/day = ~$5-7/day

#### C. Add to n8n:

HeyGen uses HTTP Header authentication:

1. In n8n, go to **Credentials** → **Add Credential**
2. Select **"HTTP Header Auth"** or **"Header Auth"**
3. Enter:
   - **Name:** `heygenApiKey` (exactly this name!)
   - **Header Name:** `X-Api-Key`
   - **Value:** [Your HeyGen API key]
4. Click **"Save"**

#### D. Configure in Workflow:

1. Click "Generate Video (HeyGen)" node
2. Under Authentication:
   - Type: Generic Credential Type
   - Credential Type: httpHeaderAuth
   - Select: Your "heygenApiKey" credential
3. Repeat for "Check Video Status" node

#### E. Test Connection:

1. Click "Generate Video (HeyGen)" node
2. Execute with test data
3. Should return video_id in response

### Optional: Skip Video Generation

Don't want to use HeyGen? You can disable video generation:

1. Delete "Generate Video (HeyGen)" node
2. Delete "Wait 30 Seconds" node
3. Delete "Check Video Status" node
4. Delete "IF Video Complete" node
5. Connect "Create Video Script" directly to "Save to Sheet"
6. Workflow will save video scripts but not create videos

---

## 4. Google Sheets OAuth2 Credentials

### Why Needed:
- Save all job application data
- Track applications over time
- Access cover letters and video scripts

### Setup Instructions:

#### A. Create Google Sheet:

1. Go to [Google Sheets](https://sheets.google.com/)
2. Create new spreadsheet
3. Name: "LinkedIn Job Applications Tracker"
4. Add columns (exact names):
   ```
   Title | Job Description | Link | Date | Rating | Company Name |
   Benefits | Location | Match Explanation | Cover Letter |
   Video Script | Video URL
   ```
5. Copy Sheet ID from URL:
   ```
   https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/edit
   Example: 1xMELeUYUcGrqctnCQSWOuB586k1NHth0mgLhUVRu6EI
   ```

#### B. Enable Google Sheets API:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Use same project as Gmail (or create new)
3. Enable Google Sheets API:
   - APIs & Services → Library
   - Search "Google Sheets API"
   - Click Enable

4. OAuth credentials:
   - If you already have OAuth from Gmail setup, you can reuse it
   - Otherwise, follow same steps as Gmail OAuth (section 1A)

#### C. Add to n8n:

1. In n8n, go to **Credentials** → **Add Credential**
2. Select **"Google Sheets OAuth2 API"**
3. Enter:
   - **Client ID:** [Same as Gmail, from Google Cloud]
   - **Client Secret:** [Same as Gmail]
4. Click **"Sign in with Google"**
5. Authorize access to Google Sheets
6. Click **"Save"**

#### D. Update Workflow:

1. Click "Save to Sheet (No Video)" node
2. Under "Document":
   - Click dropdown
   - Select "From list"
   - Choose your tracking sheet
   OR
   - Select "By ID"
   - Paste your Sheet ID: `1xMELeUYUcGrqctnCQSWOuB586k1NHth0mgLhUVRu6EI`

3. Under "Sheet":
   - Select the sheet name (default: "Sheet1")

4. Repeat for "Save to Google Sheet" node

#### E. Test Connection:

1. Execute workflow with test data
2. Check Google Sheet
3. Should see new row with job data

---

## Security Best Practices

### Protect Your Credentials:

❌ **NEVER DO THIS:**
- Commit API keys to git
- Share workflow JSON with credentials embedded
- Post API keys in public forums
- Use same API key across multiple projects
- Store keys in plain text files

✅ **ALWAYS DO THIS:**
- Use n8n's credential encryption
- Export workflows without credentials
- Rotate API keys every 3-6 months
- Monitor API usage for suspicious activity
- Set spending limits on OpenAI and HeyGen
- Use different credentials for dev/prod
- Review OAuth permissions regularly

### Data Privacy:

**What's Stored:**
- Your profile data (in workflow prompts)
- Job application details (in Google Sheet)
- Cover letters with personal info
- Video scripts with your name

**Privacy Considerations:**
- Google Sheet is private to your account
- n8n credentials are encrypted
- Email content is processed in real-time (not stored)
- API providers (OpenAI, HeyGen) process your data per their privacy policies

**Recommendations:**
- Review OpenAI privacy policy: https://openai.com/policies/privacy-policy
- Review HeyGen privacy policy: https://heygen.com/privacy
- Don't include sensitive personal data in profile (SSN, passport, etc.)
- Use separate Google Sheet for this workflow (not mixed with sensitive data)

---

## Credential Rotation Schedule

### Recommended Schedule:

| Credential | Rotation Frequency | Why |
|------------|-------------------|-----|
| OpenAI API Key | Every 6 months | Security best practice |
| HeyGen API Key | Every 6 months | Security best practice |
| Gmail OAuth | Yearly or if suspicious activity | OAuth tokens auto-refresh |
| Google Sheets OAuth | Yearly or if suspicious activity | OAuth tokens auto-refresh |

### How to Rotate:

1. **OpenAI/HeyGen:**
   - Generate new API key
   - Update in n8n credentials
   - Delete old key from provider dashboard
   - Test workflow works

2. **Gmail/Sheets OAuth:**
   - Revoke access in Google Account settings
   - Re-authorize in n8n
   - Test workflow works

---

## Troubleshooting

### Gmail OAuth Issues:

**Error: "Access denied" or "Invalid credentials"**
- Solution: Re-authorize Gmail connection in n8n
- Check: OAuth redirect URI matches exactly
- Verify: Gmail API is enabled in Google Cloud

**Error: "Token expired"**
- Solution: OAuth tokens auto-refresh, but may need re-auth
- Check: n8n has internet access to refresh tokens

### OpenAI API Issues:

**Error: "Incorrect API key"**
- Solution: Regenerate key and update in n8n
- Check: Key starts with `sk-proj-` (new format) or `sk-` (old format)

**Error: "Rate limit exceeded"**
- Solution: Wait 1 minute and retry
- Check: Your usage at https://platform.openai.com/usage
- Consider: Upgrading to higher tier if hitting limits regularly

**Error: "Insufficient credits"**
- Solution: Add credits in OpenAI billing
- Check: Usage limits and spending limits

### HeyGen API Issues:

**Error: "Invalid API key"**
- Solution: Verify key is correct and credential name is exactly `heygenApiKey`
- Check: Header Auth credential uses `X-Api-Key` header name

**Error: "Insufficient credits"**
- Solution: Add credits or upgrade plan
- Check: HeyGen account balance

### Google Sheets Issues:

**Error: "Sheet not found"**
- Solution: Verify Sheet ID is correct
- Check: Sheet is not deleted
- Ensure: OAuth has access to this sheet

**Error: "Column not found"**
- Solution: Ensure column names match exactly (case-sensitive)
- Check: No extra spaces in column names
- Verify: Sheet has all required columns

---

## Credential Summary

### Quick Reference:

```
Gmail OAuth2:
├── Purpose: Read emails, mark as read
├── Provider: Google Cloud Console
├── Type: OAuth 2.0
├── Scopes: Gmail read/modify
└── Cost: Free

OpenAI API:
├── Purpose: AI text generation
├── Provider: OpenAI Platform
├── Type: API Key
├── Models: GPT-5, GPT-4o-latest, GPT-4o-mini
└── Cost: ~$10-15/day (50 jobs)

HeyGen API:
├── Purpose: AI video generation
├── Provider: HeyGen
├── Type: API Key (Header Auth)
├── Feature: Avatar videos
└── Cost: ~$5-7/day (20 videos)

Google Sheets OAuth2:
├── Purpose: Save application data
├── Provider: Google Cloud Console
├── Type: OAuth 2.0
├── Access: Sheet read/write
└── Cost: Free
```

---

## Need Help?

### Resources:
- **n8n Credentials Docs:** https://docs.n8n.io/credentials/
- **Gmail API Docs:** https://developers.google.com/gmail/api
- **OpenAI API Docs:** https://platform.openai.com/docs
- **HeyGen API Docs:** https://docs.heygen.com/
- **Google Sheets API:** https://developers.google.com/sheets/api

### Support:
- **n8n Community:** https://community.n8n.io/
- **OpenAI Support:** https://help.openai.com/
- **HeyGen Support:** support@heygen.com

---

**Last Updated:** October 31, 2025
**Author:** Asheesh Ranjan Srivastava
**Project:** OutSkill AI Engineering Bootcamp 2025 - Day 4
