from langchain.tools import tool
import requests



@tool
def get_environment(input:str) -> str:
    """Gets environment data from the local API object list)."""
    res = requests.get("http://localhost:8080/simple/environment/details")
    print(res)
    return res.text



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
