"""
Figma Integration using LangChain MCP Adapters
Uses LangChain's official MCP support for cleaner integration
"""
import os
import asyncio
from typing import List, Optional
from agents.state import AnalysisState
from langchain_mcp_adapters.client import MultiServerMCPClient


async def fetch_figma_images_async(figma_url: str, figma_token: str) -> List[str]:
    """
    Fetch images from Figma using LangChain MCP adapters
    
    Args:
        figma_url: Figma file URL
        figma_token: User's Figma personal access token
    
    Returns:
        List of local file paths to downloaded images
    """
    print(f"[FIGMA MCP] Fetching images using LangChain MCP adapters")
    print(f"[FIGMA MCP] URL: {figma_url}")
    
    # Configure Figma MCP server using LangChain adapters
    client = MultiServerMCPClient(
        {
            "figma": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-figma"],
                "transport": "stdio",
                "env": {
                    "FIGMA_ACCESS_TOKEN": figma_token
                }
            }
        }
    )
    
    try:
        # Get all available tools from Figma MCP server
        tools = await client.get_tools()
        print(f"[FIGMA MCP] Loaded {len(tools)} tools from Figma MCP server")
        
        # Find the export_images tool
        export_tool = None
        for tool in tools:
            if "export" in tool.name.lower() or "image" in tool.name.lower():
                export_tool = tool
                print(f"[FIGMA MCP] Found export tool: {tool.name}")
                break
        
        if not export_tool:
            # If no specific export tool, use the first available tool
            export_tool = tools[0] if tools else None
            print(f"[FIGMA MCP] Using tool: {export_tool.name if export_tool else 'None'}")
        
        if not export_tool:
            raise ValueError("No tools available from Figma MCP server")
        
        # Invoke the tool to export images
        result = await export_tool.ainvoke({
            "file_url": figma_url,
            "format": "png",
            "scale": 2,
            "output_dir": "storage"
        })
        
        # Extract file paths from result
        if isinstance(result, tuple):
            # LangChain tools return (content, error)
            content, error = result
            if error:
                raise ValueError(f"Tool execution error: {error}")
            
            # Parse file paths from content
            if isinstance(content, list):
                file_paths = content
            elif isinstance(content, str):
                # Try to parse as JSON or newline-separated paths
                import json
                try:
                    parsed = json.loads(content)
                    file_paths = parsed if isinstance(parsed, list) else [content]
                except:
                    file_paths = [line.strip() for line in content.split('\n') if line.strip()]
            else:
                file_paths = [str(content)]
        else:
            file_paths = [str(result)]
        
        print(f"[FIGMA MCP] Successfully exported {len(file_paths)} images")
        return file_paths
    
    except Exception as e:
        print(f"[FIGMA MCP ERROR] Failed to fetch images: {str(e)}")
        raise
    
    finally:
        # Clean up client resources
        await client.cleanup()


def process_figma_url(figma_url: str, figma_token: str) -> List[str]:
    """
    Synchronous wrapper for async Figma image fetching
    
    Args:
        figma_url: Figma file URL
        figma_token: User's Figma access token
    
    Returns:
        List of local file paths to downloaded images
    """
    print(f"[FIGMA MCP] Processing Figma URL with LangChain MCP")
    
    # Run async function in event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        file_paths = loop.run_until_complete(
            fetch_figma_images_async(figma_url, figma_token)
        )
        return file_paths
    finally:
        loop.close()


def figma_mcp_fetch_node(state: AnalysisState) -> dict:
    """
    LangGraph node for fetching Figma images using LangChain MCP.
    Only runs if figma_url is present in state.
    
    Returns a partial state dict with only the keys this node updates.
    """
    figma_url = state.get("figma_url")
    figma_token = state.get("figma_token")
    
    if not figma_url:
        print("[FIGMA MCP] No Figma URL provided, skipping")
        return {}
    
    if not figma_token:
        error_msg = "Figma token required but not provided"
        print(f"[FIGMA MCP ERROR] {error_msg}")
        return {"errors": [error_msg]}
    
    try:
        print("[FIGMA MCP] Starting Figma fetch node (LangChain MCP)")
        file_paths = process_figma_url(figma_url, figma_token)
        
        print(f"[FIGMA MCP] Fetch node complete: {len(file_paths)} files")
        
        # Return only the keys this node updates
        return {
            "file_paths": file_paths,
            "source_type": "figma"
        }
        
    except Exception as e:
        error_msg = f"Figma MCP fetch error: {str(e)}"
        print(f"[FIGMA MCP ERROR] {error_msg}")
        return {"errors": [error_msg]}
