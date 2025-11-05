# Day 4 - n8n Workflow Automation

> **Note:** These workflows were created as part of the AI Mastermind Course class work, demonstrating practical applications of n8n automation with various APIs and services.

This directory contains three n8n workflows that demonstrate the integration of various APIs, services, and AI capabilities to automate different business processes.

## Overview

n8n is a workflow automation tool that allows you to connect different services and build automated workflows. These workflows demonstrate the integration of services like OpenAI, HeyGen, RSS feeds, Google Sheets, and more.

## n8n Workflows

### 1. LinkedIn Job Automation (`linkedin-job-automation.json`)

An automated job application assistant that:
- Reads job listings from an RSS feed
- Processes job descriptions using OpenAI
- Analyzes job details and generates:
  - Company information extraction
  - Benefits analysis
  - Job description summary
  - Application rating
  - Customized cover letters
- Stores results in Google Sheets for tracking
- Features automated scheduling for regular checks

**Key Components:**
- RSS Feed Reader for job listings
- OpenAI integration for content analysis
- Google Sheets integration for data storage
- Automated scheduling system

### 2. Personalized Newsletter with Web Search (`Personalised_Newsletter_Tavily API Web search.json`)

A smart newsletter system that:
- Uses Tavily API for web searching
- Processes search results with AI
- Generates personalized newsletters
- Sends formatted content via Gmail

**Key Components:**
- Chat trigger for interactive control
- Tavily API integration for web search
- OpenAI GPT-4 for content processing
- Gmail integration for delivery
- Memory buffer for context retention

### 3. Video Resume & Cover Letter Generator (`Video_Resume_Coverletter.json`)

An automated system for creating video presentations that:
- Monitors Google Sheets for new entries
- Generates video scripts using AI
- Creates video presentations using HeyGen
- Updates status and manages workflow states

**Key Components:**
- Google Sheets integration for input/output
- OpenAI for script generation
- HeyGen API for video creation
- Status tracking and error handling
- Wait nodes for API processing

## Technical Implementation Details

### Common Features Across Workflows:
1. **API Integrations:**
   - OpenAI API for content generation
   - Third-party APIs (HeyGen, Tavily)
   - Google Workspace (Sheets, Gmail)

2. **Data Processing:**
   - JSON handling
   - Content transformation
   - Error handling

3. **Workflow Control:**
   - Conditional execution
   - Status tracking
   - Automated scheduling
   - Wait states for API processing

### Security Considerations:
- API credentials management
- OAuth2 authentication for Google services
- Secure data handling

## Usage Notes

1. **Importing Workflows:**
   - Open n8n in your browser (typically http://localhost:5678)
   - Click on "Workflows" in the left sidebar
   - Click the "Import from File" button (or press `Ctrl/Cmd + I`)
   - Select the desired `.json` workflow file
   - Review and configure credentials for each service
   - Save the workflow

2. **Setup Requirements:**
   - n8n installation
   - Required API credentials
   - Google Workspace access
   - OpenAI API key

2. **Configuration:**
   - Update API credentials
   - Configure Google Workspace connections
   - Adjust scheduling as needed
   - Modify wait times based on API response times

3. **Monitoring:**
   - Check execution logs
   - Monitor API usage
   - Review output in Google Sheets
   - Verify email deliveries

## Best Practices Demonstrated

1. **Workflow Design:**
   - Modular node structure
   - Error handling implementation
   - Status tracking
   - Clear data flow

2. **Integration Patterns:**
   - API rate limiting consideration
   - Batch processing
   - Asynchronous operations
   - State management

3. **Data Management:**
   - Structured data storage
   - Version tracking
   - Status updates
   - Audit trail maintenance
