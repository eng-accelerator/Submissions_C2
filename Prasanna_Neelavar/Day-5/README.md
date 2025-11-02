# Day 5 - LinkedIn Post Generator with n8n and Angular

This project combines n8n workflow automation with an Angular frontend to create a sophisticated LinkedIn post generation and publishing system.

## Project Overview

A web application that helps users generate and publish viral LinkedIn posts based on various parameters. The system uses:
- n8n for backend workflow automation
- Angular with Tailwind CSS for the frontend
- OpenRouter AI for content generation
- LinkedIn API for post publishing

## Components

### 1. n8n Workflow (`n8n_Viral_LinkedinPost_Creator.json`)

The backend workflow consists of:

- **Generate Post Webhook**: Receives post parameters and generates content
  - Accepts: theme, category, tone, and length parameters
  - Uses OpenRouter AI (gpt-oss-20b) for content generation
  - Returns formatted LinkedIn post content

- **Publish Post Webhook**: Handles post publication to LinkedIn
  - Accepts: final post content
  - Authenticates with LinkedIn
  - Publishes content to user's LinkedIn profile

### 2. Angular Frontend

Generated using Gemini CLI with the provided prompt (`gemini_angular_app_prompt.json`), the frontend features:

**Form Fields:**
- Theme/Idea (text input)
- Post Type/Category (dropdown)
- Length (dropdown)
- Tone (dropdown)

**Actions:**
- Generate Post button
- Edit capability
- Publish to LinkedIn button

## Important Note ⚠️

The webhook URLs in the prompt file are for demonstration only. Users need to:
1. Import the n8n workflow
2. Set up their own n8n instance
3. Configure their own webhook URLs
4. Update the Angular environment configuration with their webhook URLs

## Setup Instructions

### n8n Workflow Setup:
1. Import `n8n_Viral_LinkedinPost_Creator.json` into your n8n instance
2. Configure credentials:
   - LinkedIn OAuth2 credentials
   - OpenRouter API credentials
3. Note down your new webhook URLs for:
   - Generate Post webhook
   - Publish Post webhook

### Frontend Setup:
1. Generate the Angular application using Gemini CLI:
   ```bash
   # Install Gemini CLI if not already installed
   npm install -g @gemini-ai/cli

   # Create a new directory for your project
   mkdir viral-linkedin-post-generator
   cd viral-linkedin-post-generator

   # Initialize a new Angular project using the prompt
   gemini init angular-app --prompt-file ../gemini_angular_app_prompt.json

   # Alternative: Use direct prompt command
   gemini prompt angular-app --input-file ../gemini_angular_app_prompt.json --output ./src
   ```

2. Review and update the generated code:
   - Check the generated component structure
   - Verify the form implementations
   - Review the service integrations

3. Update webhook URLs in environment.ts:
   ```typescript
   export const environment = {
     production: false,
     generatePostWebhook: 'your-n8n-generate-webhook-url',
     publishPostWebhook: 'your-n8n-publish-webhook-url'
   };
   ```

4. Install dependencies:
   ```bash
   npm install
   ```

5. Run the application:
   ```bash
   ng serve
   ```

   Access the application at http://localhost:4200

## Security Considerations

1. Never commit or share webhook URLs
2. Keep API credentials secure
3. Use environment variables for sensitive data
4. Implement proper error handling

## Workflow Features

1. **Content Generation:**
   - AI-powered post generation
   - Professional formatting
   - LinkedIn-optimized content

2. **Publishing:**
   - Direct LinkedIn integration
   - Post preview
   - Edit capability before publishing

3. **User Experience:**
   - Responsive design
   - Form validation
   - Real-time feedback

## Technical Implementation

### n8n Workflow:
- Webhook triggers
- OpenRouter AI integration
- LinkedIn API connection
- Error handling
- Response formatting

### Angular Frontend:
- Reactive Forms
- HTTP Client integration
- Tailwind CSS styling
- Component-based architecture
- Responsive design

## Future Enhancements

1. Multiple social media platform support
2. Content scheduling
3. Analytics integration
4. Template management
5. Post history tracking

## Troubleshooting

1. **Webhook Issues:**
   - Verify n8n instance is running
   - Check webhook URLs
   - Confirm API credentials

2. **LinkedIn Integration:**
   - Verify OAuth configuration
   - Check token expiration
   - Confirm posting permissions

3. **Content Generation:**
   - Monitor AI service status
   - Check prompt formatting
   - Verify API quotas
