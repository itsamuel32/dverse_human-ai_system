from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("Unreal Engine MCP Server")


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    print("ADD Called")
    print(f"A: {a}"), print(f"B: {b}")

    return a + b


@mcp.tool("get_scene_objects", "Use this tool when you need to know what scene objects "
                               "are currently available in Unreal Engine. It calls API"
                               "in Unreal Engine which returns the data.")
def get_scene_objects():
    """
    Use this tool when you need to know what scene objects
    are currently available in Unreal Engine. It calls API
    in Unreal Engine which returns the data.
    """
    try:
        print("UNREAL ENGINE CALLED")
        response = requests.get("http://localhost:8001/scene/objects")
        response.raise_for_status()
        print(response)

        return response.json()
    except Exception as e:
        return f"Error calling get_scene_objects: {str(e)}"


def main():
    mcp.run(transport='sse')


if __name__ == "__main__":
    main()
