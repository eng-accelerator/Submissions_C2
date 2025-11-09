# Remote Server Support Guide

## Overview

The Medical MCP Server supports **both local (stdio) and remote (HTTP/SSE) connections**.

### Connection Modes

1. **stdio (Local)** - Default mode for local connections
2. **http (Remote)** - HTTP/SSE mode for remote connections

## Local Mode (stdio) - Default

### Usage

```bash
# Run in local mode (default)
python3 locationservice.py
```

Or explicitly:

```bash
MCP_SERVER_MODE=stdio python3 locationservice.py
```

### Configuration

No additional configuration needed. Works out of the box.

## Remote Mode (HTTP/SSE)

### Installation

For remote server support, install additional dependencies:

```bash
# Option 1: Install with MCP SSE support
pip install 'mcp[sse]'

# Option 2: Install separately
pip install fastapi uvicorn
```

### Usage

#### Start Remote Server

```bash
# Set environment variables
export MCP_SERVER_MODE=http
export MCP_SERVER_PORT=8000
export MCP_SERVER_HOST=0.0.0.0

# Start server
python3 locationservice.py
```

Or in one command:

```bash
MCP_SERVER_MODE=http MCP_SERVER_PORT=8000 python3 locationservice.py
```

#### Default Settings

- **Host**: `0.0.0.0` (all interfaces)
- **Port**: `8000`
- **Mode**: `stdio` (local)

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_SERVER_MODE` | `stdio` | Server mode: `stdio` (local) or `http` (remote) |
| `MCP_SERVER_PORT` | `8000` | Port for HTTP server (remote mode only) |
| `MCP_SERVER_HOST` | `0.0.0.0` | Host for HTTP server (remote mode only) |

### Accessing Remote Server

Once started, the server will be accessible at:

```
http://localhost:8000
```

Or from remote clients:

```
http://<server-ip>:8000
```

## MCP Client Configuration

### Local Mode (stdio)

```json
{
  "mcpServers": {
    "medical-service-finder": {
      "type": "stdio",
      "command": "python3",
      "args": [
        "/path/to/locationservice.py"
      ]
    }
  }
}
```

### Remote Mode (HTTP)

```json
{
  "mcpServers": {
    "medical-service-finder": {
      "type": "http",
      "url": "http://localhost:8000",
      "headers": {}
    }
  }
}
```

Or for remote server:

```json
{
  "mcpServers": {
    "medical-service-finder": {
      "type": "http",
      "url": "http://<server-ip>:8000",
      "headers": {
        "Authorization": "Bearer <token>"  // Optional
      }
    }
  }
}
```

## Deployment Options

### Option 1: Local Development

```bash
# Run locally
python3 locationservice.py
```

### Option 2: Remote Server

```bash
# On server
export MCP_SERVER_MODE=http
export MCP_SERVER_PORT=8000
python3 locationservice.py

# Server accessible at http://<server-ip>:8000
```

### Option 3: Docker Container

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY locationservice.py .

ENV MCP_SERVER_MODE=http
ENV MCP_SERVER_PORT=8000
ENV MCP_SERVER_HOST=0.0.0.0

EXPOSE 8000

CMD ["python3", "locationservice.py"]
```

### Option 4: Systemd Service

Create `/etc/systemd/system/medical-mcp.service`:

```ini
[Unit]
Description=Medical MCP Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/ailearn
Environment="MCP_SERVER_MODE=http"
Environment="MCP_SERVER_PORT=8000"
Environment="MCP_SERVER_HOST=0.0.0.0"
Environment="OPENAI_API_KEY=your-key"
Environment="PERPLEXITY_API_KEY=your-key"
ExecStart=/usr/bin/python3 /path/to/ailearn/locationservice.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Start service:

```bash
sudo systemctl enable medical-mcp
sudo systemctl start medical-mcp
```

## Security Considerations

### For Remote Servers

1. **Authentication**: Add authentication headers in MCP client config
2. **HTTPS**: Use reverse proxy (nginx, Caddy) with SSL/TLS
3. **Firewall**: Restrict access to specific IPs
4. **API Keys**: Never expose API keys in environment variables on remote servers

### Example with Nginx Reverse Proxy

```nginx
server {
    listen 443 ssl;
    server_name mcp.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## Testing Remote Server

### Test Local Connection

```bash
# Start server
MCP_SERVER_MODE=http python3 locationservice.py

# In another terminal, test connection
curl http://localhost:8000/health
```

### Test Remote Connection

```bash
# On server
MCP_SERVER_MODE=http MCP_SERVER_HOST=0.0.0.0 python3 locationservice.py

# From client
curl http://<server-ip>:8000/health
```

## Troubleshooting

### Issue: HTTP/SSE transport not available

**Solution:**
```bash
pip install 'mcp[sse]'
# or
pip install fastapi uvicorn
```

### Issue: Port already in use

**Solution:**
```bash
# Use different port
MCP_SERVER_PORT=8001 python3 locationservice.py
```

### Issue: Connection refused

**Solution:**
1. Check firewall settings
2. Verify server is running
3. Check host/port configuration
4. Verify network connectivity

### Issue: Fallback to stdio mode

**Solution:**
1. Install HTTP/SSE dependencies
2. Check error messages
3. Verify environment variables

## Summary

✅ **Local Mode (stdio)**: Default, works out of the box
✅ **Remote Mode (http)**: Requires `mcp[sse]` or `fastapi uvicorn`
✅ **Configurable**: Via environment variables
✅ **Flexible**: Supports both local and remote deployments

The server automatically detects the mode and falls back to stdio if HTTP/SSE is not available.

