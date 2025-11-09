# SSE Implementation Details

## What is Used to Expose SSE

The code uses the following components to expose Server-Sent Events (SSE) for remote connections:

### 1. **MCP Framework's SseServerTransport**

**Location:** `mcp.server.sse.SseServerTransport`

**What it does:**
- Provides SSE transport layer for MCP protocol
- Handles SSE connection management
- Converts MCP protocol messages to/from SSE format

**Usage:**
```python
from mcp.server.sse import SseServerTransport

# Create SSE transport with endpoint
transport = SseServerTransport(endpoint="/sse")

# Connect SSE connection (ASGI interface)
streams = transport.connect_sse(scope, receive, send)
# Returns: (read_stream, write_stream)
```

### 2. **Starlette Framework**

**Location:** `starlette.applications.Starlette`

**What it does:**
- ASGI web framework (lightweight FastAPI alternative)
- Handles HTTP requests and routing
- Provides ASGI interface for SSE connections

**Usage:**
```python
from starlette.applications import Starlette
from starlette.routing import Route

# Create Starlette app with SSE route
app = Starlette(
    routes=[
        Route("/sse", sse_handler, methods=["GET", "POST"]),
    ]
)
```

### 3. **Uvicorn ASGI Server**

**Location:** `uvicorn`

**What it does:**
- ASGI HTTP server
- Runs the Starlette/FastAPI application
- Handles HTTP connections and serves SSE streams

**Usage:**
```python
import uvicorn

# Run server
config = uvicorn.Config(app, host="0.0.0.0", port=8000)
server = uvicorn.Server(config)
await server.serve()
```

## How It Works Together

```
Client Request (HTTP/SSE)
    ↓
Uvicorn (ASGI Server)
    ↓
Starlette (ASGI Framework)
    ↓
SseServerTransport (MCP SSE Transport)
    ↓
MCP Server (locationservice.py)
    ↓
Tool Handler (find_medical_providers)
    ↓
Response (JSON via SSE)
    ↓
Client
```

## Dependencies

### Required for SSE Support

1. **mcp** - MCP framework (includes `mcp.server.sse`)
2. **starlette** - ASGI web framework
3. **uvicorn** - ASGI HTTP server

### Installation

```bash
# Option 1: Install with MCP SSE extras
pip install 'mcp[sse]'

# Option 2: Install separately
pip install starlette uvicorn
```

## Architecture

### Local Mode (stdio)
- Uses: `mcp.server.stdio.stdio_server`
- Transport: Standard input/output
- Connection: Local process communication

### Remote Mode (HTTP/SSE)
- Uses: `mcp.server.sse.SseServerTransport`
- Transport: HTTP with Server-Sent Events
- Connection: HTTP/SSE over network
- Framework: Starlette (ASGI)
- Server: Uvicorn (ASGI server)

## Endpoint

When running in remote mode, the SSE endpoint is:

```
http://<host>:<port>/sse
```

Example:
```
http://localhost:8000/sse
```

## Configuration

Set environment variables to enable remote mode:

```bash
export MCP_SERVER_MODE=http
export MCP_SERVER_PORT=8000
export MCP_SERVER_HOST=0.0.0.0
```

## Summary

**SSE is exposed using:**
1. **SseServerTransport** (from `mcp.server.sse`) - MCP SSE transport layer
2. **Starlette** - ASGI web framework for HTTP routing
3. **Uvicorn** - ASGI HTTP server to run the application

These three components work together to expose the MCP server over HTTP/SSE for remote connections.

