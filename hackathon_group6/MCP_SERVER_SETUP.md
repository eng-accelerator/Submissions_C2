# Medical MCP Server Setup Guide

## Overview

The Medical Service Provider Finder MCP Server uses **Perplexity API** as the primary search engine to find real medical providers with verified addresses. It implements progressive radius search (10→25→50→100 miles) and urgency-based recommendations.

## Features

✅ **Perplexity API Integration** - Primary search engine for real-time, accurate results
✅ **Real Addresses Only** - No hallucination, only verifiable addresses
✅ **Progressive Radius Search** - 10 → 25 → 50 → 100 miles
✅ **Urgency-Based Recommendations** - High/Medium/Low urgency logic
✅ **Distance & Travel Time** - Calculated for each provider
✅ **Rating Extraction** - 1-5 scale ratings from search results
✅ **Skills Matching** - Extracts available services/skills

## Installation

### 1. Install Dependencies

```bash
pip install mcp duckduckgo-search geopy openai python-dotenv
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Location: /Users/muralis/AIML/ailearn/.env

OPENAI_API_KEY=your-openai-api-key-here
PERPLEXITY_API_KEY=your-perplexity-api-key-here
```

Or set environment variables:

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
export PERPLEXITY_API_KEY="your-perplexity-api-key-here"
```

### 3. Verify Configuration

```bash
python3 -c "from locationservice import openai_client, perplexity_client; print('OpenAI:', '✅' if openai_client else '❌'); print('Perplexity:', '✅' if perplexity_client else '❌')"
```

## Running the MCP Server

### Standalone Mode

```bash
python3 locationservice.py
```

The server will run in stdio mode, ready to accept MCP protocol messages.

### With MCP Client

Add to your MCP client configuration (e.g., `.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "medical-service-finder": {
      "type": "stdio",
      "command": "python3",
      "args": [
        "/Users/muralis/AIML/ailearn/locationservice.py"
      ],
      "env": {
        "OPENAI_API_KEY": "your-openai-api-key",
        "PERPLEXITY_API_KEY": "your-perplexity-api-key"
      }
    }
  }
}
```

## Tool: `find_medical_providers`

### Input Parameters

1. **patient_address** (required): Full address of the patient
   - Example: `"123 Main Street, Denver, CO 80202"`

2. **service_type** (required): Type of medical service needed
   - Examples: `"Cardiology"`, `"Emergency Care"`, `"Hospitals"`, `"Pediatrics"`

3. **urgency** (required): Urgency level
   - Options: `"high"`, `"urgent"`, `"emergency"`, `"critical"`, `"medium"`, `"moderate"`, `"low"`, `"routine"`

### Output Format

```json
{
  "providers": [
    {
      "name": "<provider name>",
      "address": "<provider address>",
      "distance": "<distance in miles>",
      "travelTime": "<travel time in minutes>",
      "Rating": <rating 1-5>,
      "Skills": ["skill1", "skill2", ...]
    },
    ... (exactly 5 providers)
  ],
  "recommendation": {
    "name": "<recommended provider>",
    "address": "<address>",
    "distance": "<distance>",
    "travelTime": "<travel time>",
    "Rating": <rating>,
    "Skills": ["skills"]
  },
  "metadata": {
    "urgency": "<urgency level>",
    "patient_address": "<patient address>",
    "service_type": "<service type>",
    "total_found": <number>,
    "search_radius_used": "<10/25/50/100 miles>",
    "max_distance": "<max distance>"
  }
}
```

## How It Works

### 1. Search Priority

1. **Perplexity API** (if `PERPLEXITY_API_KEY` is set)
   - Real-time search with structured results
   - Better accuracy and real addresses

2. **DuckDuckGo + OpenAI Parsing** (fallback)
   - Web search with LLM parsing
   - Extracts structured data from search results

3. **DuckDuckGo Basic** (last resort)
   - Basic regex extraction
   - Less accurate

### 2. Progressive Radius Search

The system searches in expanding radius circles:

1. **10 miles** → If < 5 providers found, expand
2. **25 miles** → If < 5 providers found, expand
3. **50 miles** → If < 5 providers found, expand
4. **100 miles** → If < 5 providers found, return all found

### 3. Urgency-Based Recommendations

- **High/Urgent/Emergency/Critical**: Recommends **closest provider** (prioritizes distance)
- **Medium/Moderate**: Recommends **balanced provider** (distance + rating)
- **Low/Routine**: Recommends **highest rated provider** (prioritizes quality)

## Testing

### Test the MCP Server

```bash
python3 test_mcp_server.py
```

### Test Perplexity Search Directly

```bash
python3 test_perplexity_search.py
```

## Example Usage

### Input

```json
{
  "patient_address": "123 Main Street, Denver, CO 80202",
  "service_type": "Cardiology",
  "urgency": "high"
}
```

### Output

```json
{
  "providers": [
    {
      "name": "Aurora Denver Cardiology Associates",
      "address": "1675 Larimer St Suite 675, Denver, CO 80202",
      "distance": "0.5 miles",
      "travelTime": "1 minutes",
      "Rating": 4.7,
      "Skills": ["Cardiology", "Primary Care", "Emergency Care"]
    },
    ... (4 more providers)
  ],
  "recommendation": {
    "name": "Aurora Denver Cardiology Associates",
    "address": "1675 Larimer St Suite 675, Denver, CO 80202",
    "distance": "0.5 miles",
    "travelTime": "1 minutes",
    "Rating": 4.7,
    "Skills": ["Cardiology", "Primary Care", "Emergency Care"]
  },
  "metadata": {
    "urgency": "high",
    "patient_address": "123 Main Street, Denver, CO 80202",
    "service_type": "Cardiology",
    "total_found": 5,
    "search_radius_used": "10 miles",
    "max_distance": "8.50 miles"
  }
}
```

## Troubleshooting

### Issue: No providers found

**Possible causes:**
- Perplexity API key not set or invalid
- OpenAI API key not set or invalid
- Network connectivity issues
- Address geocoding failed

**Solutions:**
1. Verify API keys in `.env` file
2. Check network connection
3. Try a different address format
4. Check API rate limits

### Issue: Addresses are "Address not found"

**Possible causes:**
- Search results don't contain full addresses
- Address extraction failed

**Solutions:**
1. Perplexity API usually provides better addresses
2. Check if service type is too specific
3. Try expanding search radius

### Issue: MCP server not responding

**Possible causes:**
- Server not running
- Incorrect configuration
- API keys not loaded

**Solutions:**
1. Verify server is running: `python3 locationservice.py`
2. Check MCP client configuration
3. Verify environment variables are loaded

## Resources

The MCP server also exposes resources:

- `medical://service_types` - List of common medical service types

## Notes

- **Perplexity API** is recommended** for best results
- The system automatically falls back to DuckDuckGo if Perplexity is unavailable
- All addresses are verified from search results (no hallucination)
- Progressive radius search ensures efficient provider discovery

## Support

For issues or questions:
1. Check the logs for error messages
2. Verify API keys are correct
3. Test with `test_mcp_server.py`
4. Check Perplexity API status

