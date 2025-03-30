from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI

from enums.obj_color import Color
from routers.simple_API_Requests import SimpleRouter


def include_routes():
    simple_router = SimpleRouter()
    app.include_router(simple_router.get_all_routes())


@asynccontextmanager
async def lifespan(app: FastAPI):
    include_routes()
    yield


app = FastAPI(title="Simple API", lifespan=lifespan)


@app.get("/")
def index():
    response = {"Message: ": "This API should suit as a "}
    return response


def main():
    uvicorn.run("main:app", host="localhost", port=8080, reload=True)


if __name__ == "__main__":

    main()
