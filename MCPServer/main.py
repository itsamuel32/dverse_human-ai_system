from mcp.server.fastmcp import FastMCP
import json
import requests
import threading
import time

from vectordb.vector_db import VectorDB

# ────────────────────────── SETUP ───────────────────────────── #
mcp = FastMCP("Unreal Engine MCP Server")
vdb = VectorDB()


# ────────────────────────── Resources ───────────────────────── #

# @mcp.resource(uri="scene://description", name="Scene Description",
#               description="Static description of the Unreal Engine scene.")
# def scene_description() -> str:
#     return (
#         """The environment you are assisting with is an Art gallery -'Fontys Gallery' with famous paintings and statues.
#         Build in 2025, this is a first iteration of such 3D environment for Fontys, where LLM can interact together
#         with human to achieve human-ai collaboration. \n
#
#         In the scene it applies that: \n
#         X axis is forward-backward \n
#         Y axis is left-right \n
#         Z axis is up-down
#         """
#     )
#
#
# @mcp.resource("schema://scene_object_transform")
# def scene_object_transform_schema() -> str:
#     """Describes the expected fields for a scene object's transform."""
#     return (
#         """This is the schema for moving object by ID: \n
#        Body: { "ID": String, "Transform": { "LocationX": Float, "LocationY": Float, "LocationZ": Float,
#        "RotationPitch": Float, "RotationYaw": Float, "RotationRoll": Float, "ScaleX": Float, "ScaleY": Float,
#        "ScaleZ": Float } } \n
#        Only the fields from Transform you wish to change need to be specified; Unreal Engine
#        will keep default values for unspecified fields."""
#     )



# ────────────────────────── TOOLS ───────────────────────────── #

@mcp.tool(
    "query_scene_objects",
    """Search for scene objects using a semantic query. Returns a list of objects that may be relevant to the meaning of the query. 
    Each object includes a Name, Description, and Transform. Results may include tangential matches. 
    If multiple results are returned, analyze which object's Name or Description directly includes the query term.
    If no results match closely, you should apologize and say nothing was found."""
)
def query_scene_objects(query: str, nr_of_returned_objects: int):
    return vdb.search(query, nr_of_returned_objects)


@mcp.tool("move_scene_object",
          """Sends a PATCH request to Unreal Engine to move an object by ID with a full transform.
         
         1. First query from query_scene_objects to find the correct item/s by semantic query and its ID, and current transform.
         
         
         
              Input Body could look like this:

              { "ID": String, "Transform": { "LocationX": Float, "LocationY": Float, "LocationZ": Float,
                 "RotationPitch": Float, "RotationYaw": Float, "RotationRoll": Float, "ScaleX": Float, "ScaleY": Float,
                 "ScaleZ": Float } }

              Only specify the axes,rotations,and scale you want to change (Unreal keeps defaults for unspecified fields).

              """
          )
def move_scene_object(id: str, transform: dict) -> str:
    try:
        data = {
            "ID": id,
            "Transform": transform
        }

        response = requests.patch("http://localhost:8080/scene/objects/move", json=data)
        response.raise_for_status()
        return f"[OK] Object moved: {response.text}"

    except requests.RequestException as e:
        return f"[ERROR] Failed to move object: {e}"


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
