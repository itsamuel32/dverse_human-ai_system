import requests

from main import mcp


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
        response = requests.get("http://localhost:8001/scene/objects")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return f"Error calling get_scene_objects: {str(e)}"
