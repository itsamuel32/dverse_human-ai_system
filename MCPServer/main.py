from mcp.server.fastmcp import FastMCP

import requests
import threading
import time

from vectordb.vector_db import VectorDB

# ────────────────────────── SETUP ─────────────────────────────
mcp = FastMCP("Unreal Engine MCP Server")
vdb = VectorDB()


# ────────────────────────── TOOLS ─────────────────────────────

@mcp.tool(
    "search_scene_objects",
    "Search for scene objects using a semantic query. Returns a list of objects that may be relevant to the meaning of the query. "
    "Each object includes a Name, Description, and Transform. Results may include tangential matches. "
    "If multiple results are returned, analyze which object's Name or Description directly includes the query term. "
    "If no results match closely, you should apologize and say nothing was found."
)
def search_scene_objects(query: str, nr_of_returned_objects: int):
    return vdb.search(query, nr_of_returned_objects)


# ────────────────────── BACKGROUND UPDATER ────────────────────
def background_updater():
    while True:
        count = vdb.update_from_unreal()
        print(f"[Updater] Updated {count} objects.")
        time.sleep(60)


def start_updater():
    thread = threading.Thread(target=background_updater, daemon=True)
    thread.start()


# ────────────────────────── MAIN ──────────────────────────────
def main():
    start_updater()
    mcp.run(transport='sse')


if __name__ == "__main__":
    main()
