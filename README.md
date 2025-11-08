# Medical Service Provider Finder MCP Server

A Model Context Protocol (MCP) server that finds real medical service providers using Perplexity API as the primary search engine. Implements progressive radius search (10→25→50→100 miles) and urgency-based recommendations.

## Features

✅ **Perplexity API Integration** - Primary search engine for real-time, accurate results  
✅ **Real Addresses Only** - No hallucination, only verifiable addresses  
✅ **Progressive Radius Search** - 10 → 25 → 50 → 100 miles  
✅ **Urgency-Based Recommendations** - High/Medium/Low urgency logic  
✅ **Distance & Travel Time** - Calculated for each provider  
✅ **Rating Extraction** - 1-5 scale ratings from search results  
✅ **Skills Matching** - Extracts available services/skills  

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your-openai-api-key-here
PERPLEXITY_API_KEY=your-perplexity-api-key-here
```

Or set environment variables:

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
export PERPLEXITY_API_KEY="your-perplexity-api-key-here"
```

### 3. Run the MCP Server

```bash
python3 locationservice.py
```

## MCP Client Configuration

Add to your MCP client configuration (e.g., `.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "medical-service-finder": {
      "type": "stdio",
      "command": "python3",
      "args": [
        "/path/to/locationservice.py"
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

- **patient_address** (required): Full address of the patient
- **service_type** (required): Type of medical service needed (e.g., "Cardiology", "Emergency Care", "Hospitals")
- **urgency** (required): Urgency level - "high", "medium", or "low"

### Output Format

Returns JSON with:
- 5 providers with name, address, distance, travel time, rating, and skills
- 1 recommendation based on urgency level
- Metadata including search radius used

## Testing

```bash
# Test the MCP server
python3 test_mcp_server.py

# Test Perplexity search directly
python3 test_perplexity_search.py
```

## Documentation

- [MCP Server Setup Guide](MCP_SERVER_SETUP.md) - Detailed setup instructions
- [Testing Guide](TESTING_GUIDE.md) - How to test the system
- [Dependencies Status](DEPENDENCIES_STATUS.md) - Package information

## Project Structure

```
.
├── locationservice.py          # Main MCP server
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
├── README.md                   # This file
├── MCP_SERVER_SETUP.md         # Setup guide
├── test_mcp_server.py          # MCP server test
├── test_perplexity_search.py   # Perplexity search test
└── mcp_config_example.json     # MCP client config example
```

## License

[Add your license here]

## Support

For issues or questions, check the documentation or contact the team.

