from mcp.server.fastmcp import FastMCP

import requests
import threading
import time

from vectordb.vector_db import VectorDB

# ────────────────────────── SETUP ───────────────────────────── #
mcp = FastMCP("Unreal Engine MCP Server")
vdb = VectorDB()


# ────────────────────────── Resources ───────────────────────── #

@mcp.resource("resource://scene_data")
def scene_description() -> str:
    return (
        """The environment you are assisting with is an Art gallery -'Fontys Gallery' with famous paintings and statues.
        Build in 2025, this is a first iteration of such 3D environment for Fontys, where LLM can interact together
        with human to achieve human-ai collaboration.

        In the scene it applies that: 
        X axis is forward-backward
        Y axis is left-right 
        Z axis is up-down
        
        Roll = rotation on X axis
        Pitch = rotation on Y axis
        Yaw = rotation on Z axis
        
        Objects in the scene:
        [id: 1, Mona Lisa]
        [id: 2, Woman in the Sun]
        [id: 3, The Starry Night]
        """
    )


# ────────────────────────── TOOLS ───────────────────────────── #

@mcp.tool("query_scene_objects")
def query_scene_objects(query: str, nr_of_returned_objects: int):
    """Search for scene objects using a semantic query. Returns a list of objects that may be relevant to the meaning of the query.
        Each object includes its ID, Name, Description, and Transform. Results may include tangential matches.
        If multiple results are returned, analyze which object's are closest to match for the prompt, some results may not match.
        If no results match closely, you should apologize and say nothing was found.
    """

    return vdb.search(query, nr_of_returned_objects)


@mcp.tool("move_scene_object")
def move_scene_object(id: str, locationX: float, locationY: float, locationZ: float) -> str:
    """
    Sends a PATCH request to Unreal Engine to move an object by ID with a location transform.
    1. First query from query_scene_objects to find the correct item/s by semantic query and its ID, and current transform.
    2. The axis that does not need to be changed requires the original transform value to be inserted.
    """
    try:
        data = {
            "ID": id,
            "Transform": {"LocationX": locationX, "LocationY": locationY, "LocationZ": locationZ}

        }

        response = requests.patch("http://localhost:8080/scene/objects/move", json=data)
        response.raise_for_status()
        return f"Response from Server: {response.text}"

    except requests.RequestException as e:
        return f"[ERROR] Failed to move object: {e}"


@mcp.tool("rotate_scene_object")
def rotate_scene_object(id: str, rotation_roll: float, rotation_pitch: float, rotation_yaw: float) -> str:
    """
    Sends a PATCH request to Unreal Engine to rotate an object by ID with a rotation transform.
    1. [Recommended step] First query from query_scene_objects to find the correct item/s by semantic query and its ID, and current transform.
    2. The axis that does not need to be changed requires the original transform value to be inserted.
    """
    try:
        data = {
            "ID": id,
            "Transform": {"RotationRoll": rotation_roll, "RotationPitch": rotation_pitch, "RotationYaw": rotation_yaw}

        }

        response = requests.patch("http://localhost:8080/scene/objects/rotate", json=data)
        response.raise_for_status()
        return f"Response from Server: {response.text}"

    except requests.RequestException as e:
        return f"[ERROR] Failed to rotate object: {e}"


# ────────────────────── BACKGROUND UPDATER ──────────────────── #
def background_updater():
    while True:
        count = vdb.update_from_unreal()
        print(f"[Updater] Updated {count} objects.")
        time.sleep(360)


def start_updater():
    thread = threading.Thread(target=background_updater, daemon=True)
    thread.start()


# ────────────────────────── MAIN ────────────────────────────── #
def main():
    start_updater()
    mcp.run(transport='sse')


if __name__ == "__main__":
    main()
