from mcp.server.fastmcp import FastMCP

import requests
import threading
import time

from vectordb.vector_db import VectorDB

# ────────────────────────── SETUP ───────────────────────────── #
mcp = FastMCP("Unreal Engine MCP Server")
vdb = VectorDB()


# ────────────────────────── Resources ───────────────────────── #

@mcp.tool("get_scene_bounds")
def scene_description() -> str:
    """Returns  Walls and Floors of the gallery with their spacial data"""

    try:
        response = requests.get("http://localhost:8080/scene/bounds")
        response.raise_for_status()
        return f"Response from Server: {response.text}"

    except  requests.RequestException as e:
        return f"[ERROR] Failed to move object: {e}"


# ────────────────────────── TOOLS ───────────────────────────── #

@mcp.tool("query_scene_objects")
def query_scene_objects(query: str, nr_of_returned_objects: int):
    """
    Good for querying objects based on description or context.
    Search for scene objects using a semantic query. Returns a list of objects that may be relevant to the meaning of the query.
    Each object includes its ID, Name, Description, and Transform. Results may include tangential matches.
    If multiple results are returned, analyze which object's are closest to match for the prompt, some results may not match.
    If no results match closely, you should apologize and say nothing was found.
    """

    return vdb.search(query, nr_of_returned_objects)


# This could be None in the future and if the value is none, then It will not send it in the batch.
# Currently, if it changes one value but wants to keep the same, it should input the current transform values
# 0 also counts as location in case the object is location on X= 41, Y = 25, Z = 90 then 0 would position it to 0
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


# This could be None in the future and if the value is none, then It will not send it in the batch.
# Currently, if it changes one value but wants to keep the same, it should input the current transform values
# 0 also counts as rotation in case the object is rotated on X= 41, Y = 25, Z = 90 then 0 would rotate it :(
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


@mcp.tool("clear_trash_bins")
def clear_trash_bins():
    """
    This function clears the all trash bins in unreal engine scene.

    """
    try:

        response = requests.post("http://localhost:8080/scene/clear/trash")
        response.raise_for_status()
        return f"Response from Server: {response.text}"

    except requests.RequestException as e:
        return f"[ERROR] Failed to rotate object: {e}"


@mcp.tool("switch_lights")
def switch_lights(isOn: bool):
    """
    This function switches all the lights in the scene. if ture - lights on, if false - lights off.

    """
    try:

        body = {"isOn": isOn}

        response = requests.post("http://localhost:8080/scene/lights", json=body)
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
