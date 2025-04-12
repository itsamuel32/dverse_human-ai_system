# mcp_main.py

from fastapi import FastAPI
from fastmcp import FastMCP

# Create FastAPI MCP server
app = FastAPI()
mcp = FastMCP(app=app)



@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b



if __name__ == "__main__":
    #uvicorn.run(app, port=8001)
    mcp.run()