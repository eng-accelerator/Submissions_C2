# Testing & Verification Guide

Complete testing checklist for the LinkedIn Job Automation workflow.

---

## Overview

This guide provides step-by-step instructions to test and verify all components of the workflow after setup.

**Recent Fix (October 31, 2025):**
- ✅ Fixed IF node "Check Extraction Status" condition
- Changed from `notEmpty` operation to `startsWith "https://"`
- This ensures valid LinkedIn URLs route to scraping, while error cases route to handling

---

## Pre-Testing Checklist

Before running tests, ensure:

- [ ] All credentials configured in n8n (Gmail, OpenAI, HeyGen, Google Sheets)
- [ ] Google Sheet created with correct column structure
- [ ] Sheet ID updated in workflow nodes
- [ ] Profile data customized in AI prompts
- [ ] Workflow imported and saved in n8n

---

## Test 1: Email Fetching

**Goal:** Verify Gmail integration works and fetches LinkedIn job alerts

### Steps:

1. Open n8n workflow
2. Click "Get LinkedIn Email IDs" node
3. Click "Execute Node" button
4. Expected output:
   ```json
   [
     {
       "id": "18f1234567890abcd",
       "threadId": "18f1234567890abcd"
     }
   ]
   ```

### Success Criteria:
- ✅ Returns list of email IDs
- ✅ No authentication errors
- ✅ Emails are from `jobs-listings@linkedin.com`

### Troubleshooting:
- **No emails found:** Check Gmail filters, ensure you have LinkedIn job alerts
- **Auth error:** Re-authorize Gmail OAuth in credentials
- **Rate limit:** Wait 1 minute and retry

---

## Test 2: Full Email Retrieval

**Goal:** Verify Gmail API returns complete email HTML

### Steps:

1. Click "Fetch Full Email via API" node
2. Click "Execute Node"
3. Check output has `payload.parts[0].body.data` field
4. Expected output structure:
   ```json
   {
     "payload": {
       "parts": [
         {
           "body": {
             "data": "PGh0bWw-..." // Base64 encoded HTML
           }
         }
       ]
     }
   }
   ```

### Success Criteria:
- ✅ Returns full email payload
- ✅ `payload.parts` array exists
- ✅ `body.data` contains base64-encoded content

### Troubleshooting:
- **Missing parts array:** Verify using HTTP Request node (not Gmail node)
- **Empty data:** Check Gmail credential has read permissions

---

## Test 3: URL Extraction ⚠️ CRITICAL

**Goal:** Verify LinkedIn job URLs are extracted from email HTML

### Steps:

1. Click "Extract Job URLs" node
2. Click "Execute Node"
3. Expected output (4-6 items):
   ```json
   [
     {
       "json": {
         "jobUrl": "https://www.linkedin.com/jobs/view/4318243991"
       }
     },
     {
       "json": {
         "jobUrl": "https://www.linkedin.com/jobs/view/4318567890"
       }
     }
   ]
   ```

### Success Criteria:
- ✅ Returns 4-6 unique job URLs per email
- ✅ URLs match pattern: `https://www.linkedin.com/jobs/view/{job_id}`
- ✅ No duplicate URLs

### Troubleshooting:
- **0 URLs found:** Email might be promotional, try another email
- **Returns status: 'no_urls':** This is correct behavior for emails without jobs
- **Duplicates:** Code should deduplicate, check Extract Job URLs code

---

## Test 4: IF Node Routing ⚠️ FIXED

**Goal:** Verify IF node correctly routes valid URLs to scraping

### Steps:

1. Click "Check Extraction Status" node
2. Click "Execute Node"
3. Check routing:
   - **True branch (green):** Items with valid `jobUrl` starting with "https://"
   - **False branch (red):** Items with `status: 'no_urls'`

### Success Criteria:
- ✅ Valid URLs go to True branch → "Scrape Job Page"
- ✅ Error objects go to False branch → "Handle No URLs"
- ✅ All 6 URLs (if extracted) route to True branch

### What Changed:
**Before (broken):**
```json
{
  "operation": "notEmpty",
  "rightValue": "true"  // Incorrect
}
```

**After (fixed):**
```json
{
  "operation": "startsWith",
  "rightValue": "https://"  // Correct
}
```

### Troubleshooting:
- **All items go to False:** Re-import updated workflow.json with fix
- **Mixed routing:** This is correct if some items have no URLs

---

## Test 5: Job Page Scraping

**Goal:** Verify LinkedIn job pages are scraped successfully

### Steps:

1. Click "Scrape Job Page" node
2. Click "Execute Node"
3. Expected output: Large HTML text (200-350 KB)
4. Check for LinkedIn page content

### Success Criteria:
- ✅ Returns HTML content (very large text)
- ✅ No 404 errors
- ✅ No rate limiting errors

### Troubleshooting:
- **404 Not Found:** Job posting may have been removed
- **403 Forbidden:** LinkedIn may be blocking requests (use VPN or wait)
- **Timeout:** Increase timeout in node settings (currently 30 seconds)

---

## Test 6: GPT Extraction

**Goal:** Verify GPT-5 extracts job details from HTML

### Steps:

1. Click "Extract Job Data" node
2. Click "Execute Node"
3. Expected output:
   ```json
   {
     "message": {
       "content": {
         "company_name": "TELUS Digital",
         "job_title": "AI Product Manager",
         "benefits": "401K, Medical, Remote work",
         "job_description": "Lead AI product development...",
         "location": "Remote",
         "salary_range": "$90,000 - $120,000"
       }
     }
   }
   ```

### Success Criteria:
- ✅ Returns structured JSON
- ✅ All fields populated (or empty string if not found)
- ✅ job_description is concise (200 chars or less)

### Troubleshooting:
- **OpenAI API error:** Check API key and credits
- **Empty fields:** Acceptable if job posting doesn't include that info
- **Rate limit:** Wait 60 seconds and retry

---

## Test 7: Job Rating

**Goal:** Verify GPT-4o-latest rates job fit (0-5 scale)

### Steps:

1. Click "Rate Job Match" node
2. Click "Execute Node"
3. Expected output:
   ```json
   {
     "message": {
       "content": {
         "rating": 4,
         "explanation": "Strong match due to AI/ML focus and remote option. Experience level aligns well with 6+ years background."
       }
     }
   }
   ```

### Success Criteria:
- ✅ Rating is number between 0-5
- ✅ Explanation provides clear reasoning
- ✅ Explanation mentions specific profile matches

### Troubleshooting:
- **Low ratings for good jobs:** Update candidate profile in prompt to be more accurate
- **High ratings for bad jobs:** Adjust scoring criteria in system prompt

---

## Test 8: Cover Letter Generation

**Goal:** Verify GPT-4o-latest creates personalized cover letters

### Steps:

1. Click "Generate Cover Letter" node
2. Click "Execute Node"
3. Expected output:
   ```json
   {
     "message": {
       "content": {
         "cover_letter": "Dear Hiring Manager,\n\nI was excited to discover..."
       }
     }
   }
   ```

### Success Criteria:
- ✅ Cover letter is 300-400 words
- ✅ Mentions specific company and role
- ✅ References Quest & Crossfire
- ✅ Professional but conversational tone
- ✅ Not generic (avoid "I am writing to apply")

### Troubleshooting:
- **Too generic:** Update system prompt with more specific instructions
- **Too long:** Adjust word count limit in prompt

---

## Test 9: Video Script Creation

**Goal:** Verify GPT-4o-mini creates 45-second video scripts

### Steps:

1. Click "Create Video Script" node
2. Click "Execute Node"
3. Expected output:
   ```json
   {
     "message": {
       "content": {
         "video_script": "Hi, I'm Asheesh. I noticed your AI Product Manager role..."
       }
     }
   }
   ```

### Success Criteria:
- ✅ Script is approximately 45 seconds when read aloud
- ✅ Sounds natural and conversational
- ✅ Includes hook, match, proof, CTA structure
- ✅ Mentions specific company/role

---

## Test 10: Rating-Based Video Generation ⚠️ OPTIONAL

**Goal:** Verify HeyGen generates videos only for rating ≥4

### Steps:

1. Ensure job has rating ≥4 from Test 7
2. Click "IF Rating >= 4" node
3. Check routing:
   - **True:** Rating is 4 or 5 → Goes to "Generate Video (HeyGen)"
   - **False:** Rating is 0-3 → Skips video generation

### Success Criteria:
- ✅ High-rated jobs (4-5) go to video generation
- ✅ Low-rated jobs (0-3) skip video generation
- ✅ Saves costs by not generating videos for poor matches

---

## Test 11: HeyGen Video Generation ⚠️ REQUIRES CREDITS

**Goal:** Verify HeyGen API creates AI avatar videos

### Prerequisites:
- HeyGen API key configured
- HeyGen account has sufficient credits (~$0.30 per video)
- Rating ≥4 job (from Test 10)

### Steps:

1. Click "Generate Video (HeyGen)" node
2. Click "Execute Node"
3. Expected output:
   ```json
   {
     "code": 100,
     "data": {
       "video_id": "abc123xyz789"
     }
   }
   ```

### Success Criteria:
- ✅ Returns video_id
- ✅ No authentication errors
- ✅ No insufficient credits error

### Troubleshooting:
- **Invalid API key:** Check credential name is exactly `heygenApiKey`
- **Insufficient credits:** Add credits to HeyGen account
- **Skip this test:** Delete video nodes if not using HeyGen

---

## Test 12: Video Status Check

**Goal:** Verify video generation completes successfully

### Steps:

1. Wait 30 seconds (automatic via "Wait 30 Seconds" node)
2. Click "Check Video Status" node
3. Expected output:
   ```json
   {
     "data": {
       "status": "completed",
       "video_url": "https://heygen-asset.s3.amazonaws.com/..."
     }
   }
   ```

### Success Criteria:
- ✅ Status is "completed"
- ✅ video_url is present
- ✅ Video URL is accessible

### Troubleshooting:
- **Status: "pending":** Video still processing, wait another 30 seconds
- **Status: "failed":** Check HeyGen dashboard for error details
- **No video_url:** Generation failed, check script content

---

## Test 13: Google Sheets Saving

**Goal:** Verify job data saves to Google Sheet

### Steps:

1. Click "Save to Sheet (No Video)" node (for jobs without videos)
2. OR click "Save to Google Sheet" node (for jobs with videos)
3. Click "Execute Node"
4. Open Google Sheet and verify new row appears

### Expected Sheet Row:
| Title | Job Description | Link | Date | Rating | Company Name | Benefits | Location | Match Explanation | Cover Letter | Video Script | Video URL |
|-------|----------------|------|------|--------|--------------|----------|----------|------------------|--------------|--------------|-----------|
| AI Product Manager | Lead AI... | https://... | [auto] | 4 | TELUS Digital | 401K, Medical | Remote | Strong match... | Dear Hiring... | Hi, I'm Asheesh... | [URL or empty] |

### Success Criteria:
- ✅ New row appears in sheet
- ✅ All fields populated correctly
- ✅ No duplicate rows (based on Title matching)
- ✅ Cover letter and video script are readable

### Troubleshooting:
- **Permission denied:** Re-authorize Google Sheets OAuth
- **Sheet not found:** Verify Sheet ID in node configuration
- **Column mismatch:** Ensure column names match exactly
- **Duplicates:** Check "Title" is set as matching column

---

## Test 14: Email Marking as Read

**Goal:** Verify Gmail email is marked as read after processing

### Steps:

1. Click "Mark Email as Read" node
2. Click "Execute Node"
3. Check Gmail inbox - email should be marked as read

### Success Criteria:
- ✅ Email shows as read in Gmail
- ✅ No errors

---

## Test 15: End-to-End Workflow Test ⚠️ COMPREHENSIVE

**Goal:** Run complete workflow from start to finish

### Steps:

1. Ensure you have 1-2 unread LinkedIn job alert emails in Gmail
2. Click workflow title at top
3. Click "Execute Workflow" button (NOT individual nodes)
4. Wait for all nodes to complete (3-5 minutes)
5. Check execution path:
   - Schedule → Get Emails → Fetch Full Email → Extract URLs → Check Status
   - → Scrape → Extract → Rate → Cover Letter → Video Script
   - → Save to Sheet → Mark as Read

### Success Criteria:
- ✅ All nodes execute without errors
- ✅ 4-6 jobs processed per email
- ✅ Google Sheet has new rows
- ✅ High-rated jobs (≥4) generate videos (if HeyGen enabled)
- ✅ Emails marked as read

### Execution Time:
- **Without videos:** ~2-3 minutes for 6 jobs
- **With videos:** ~5-7 minutes for 6 jobs

### Troubleshooting:
- **Stops at Extract URLs:** Check email has LinkedIn job postings
- **Stops at Scrape:** LinkedIn may be rate limiting, try VPN
- **Stops at Extract Job Data:** Check OpenAI API credits
- **Stops at video generation:** Check HeyGen credits
- **Sheet not updated:** Check Google Sheets credential

---

## Cost Monitoring

### Expected Costs (Per Run):

**OpenAI API (50 jobs):**
- GPT-5 extraction: $5-7/day
- GPT-4o-latest (rating + cover): $5-7/day
- GPT-4o-mini (video scripts): $0.50/day
- **Total:** ~$10-15/day

**HeyGen API (20 videos):**
- 45-second videos: $0.25-0.35 each
- **Total:** ~$5-7/day

**Total Daily Cost:** $15-22 for 50 jobs/day

### Monitor Usage:
- **OpenAI:** https://platform.openai.com/usage
- **HeyGen:** Check account dashboard
- **Gmail/Sheets:** Free (no cost)

---

## Production Readiness Checklist

Before enabling daily automation:

- [ ] All 15 tests passed successfully
- [ ] IF node routing works correctly (Test 4)
- [ ] Cost monitoring set up
- [ ] Google Sheet organized and accessible
- [ ] Profile data in prompts is accurate
- [ ] Spending limits set on OpenAI and HeyGen
- [ ] Workflow schedule set to appropriate time (3 AM default)
- [ ] Error handling tested (no emails, no URLs, failed scraping)

---

## Known Issues & Limitations

### Current Known Issues:
1. ✅ **IF node routing (FIXED):** Changed from `notEmpty` to `startsWith` operation
2. **LinkedIn rate limiting:** May occur with high volume, use VPN if needed
3. **Job post removal:** Some URLs may 404 if posting was removed

### Future Optimizations:
1. **HTML parsing:** Reduce GPT extraction cost by 99% (350KB → 2KB)
2. **Retry logic:** Auto-retry failed API calls
3. **Batch processing:** Process multiple emails in parallel

---

## Getting Help

### Resources:
- **Setup Issues:** See [SETUP.md](SETUP.md)
- **Credential Issues:** See [CREDENTIALS.md](CREDENTIALS.md)
- **Workflow Issues:** See [README.md](README.md) learning journey

### External Support:
- **n8n Community:** https://community.n8n.io/
- **OpenAI Support:** https://help.openai.com/
- **HeyGen Support:** support@heygen.com

---

## Test Results Template

Use this to track your testing progress:

```markdown
## Testing Session: [Date]

### Environment:
- n8n: [Cloud/Self-hosted]
- Test emails: [Number]
- OpenAI credits: $[Amount]
- HeyGen credits: $[Amount]

### Test Results:
- [ ] Test 1: Email Fetching - [Pass/Fail]
- [ ] Test 2: Full Email Retrieval - [Pass/Fail]
- [ ] Test 3: URL Extraction - [Pass/Fail]
- [ ] Test 4: IF Node Routing - [Pass/Fail] ← RECENTLY FIXED
- [ ] Test 5: Job Page Scraping - [Pass/Fail]
- [ ] Test 6: GPT Extraction - [Pass/Fail]
- [ ] Test 7: Job Rating - [Pass/Fail]
- [ ] Test 8: Cover Letter - [Pass/Fail]
- [ ] Test 9: Video Script - [Pass/Fail]
- [ ] Test 10: Rating IF Node - [Pass/Fail]
- [ ] Test 11: HeyGen Video - [Pass/Fail/Skipped]
- [ ] Test 12: Video Status - [Pass/Fail/Skipped]
- [ ] Test 13: Google Sheets - [Pass/Fail]
- [ ] Test 14: Mark as Read - [Pass/Fail]
- [ ] Test 15: End-to-End - [Pass/Fail]

### Issues Found:
[List any issues]

### Cost Incurred:
- OpenAI: $[Amount]
- HeyGen: $[Amount]

### Notes:
[Any additional observations]
```

---

**Last Updated:** October 31, 2025 (IF node fix applied)
**Author:** Asheesh Ranjan Srivastava
**Project:** OutSkill AI Engineering Bootcamp 2025 - Day 4
