from langchain.tools import tool
import requests


@tool
def get_environment() -> str:
    """Gets environment data from the local API in JSON. This API call returns the up-to-date data from the environment

    This is example of the data
     [
  {
    "Id": "1",
    "Tag": "Some Tag",
    "Name": "Item Name",
    "Type": "Some Type",
    "Transform": {
      "Location": {"X": 0, "Y": 0, "Z": 0},
      "Rotation": {"Roll": 0, "Pitch": 0, "Yaw": 0}
    }
  },
  ...
]"""
    print("[TOOL] get_environment was called.")
    try:
        res = requests.get("http://localhost:8080/simple/environment/details")
        print(res)
        return res.text
    except Exception as e:
        return str(e)


@tool
def move_object(input: str) -> str:
    """Moves an object to a target location."""
    # res = requests.post("http://localhost:8080/move-object", json={
    #     "name": name,
    #     "color": color,
    #     "target": target
    # })

    # return res.text
    return "Nothing"
