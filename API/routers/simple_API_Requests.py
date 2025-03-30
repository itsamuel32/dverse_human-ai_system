import random
from typing import List

from fastapi import APIRouter

from DTOs.environment_object import EnvironmentObject, Transform, Location, Rotation
from enums.obj_enum import ObjType


class SimpleRouter:

    def __init__(self):
        self.router = APIRouter(
            prefix="/simple",
            tags=["Simple Requests"]
        )

    def get_all_routes(self) -> APIRouter:
        @self.router.get("/environment/details")
        async def get_all() -> List[EnvironmentObject]:

            def generate_random_transform():
                location = Location(X=random.uniform(-5000.01, 8000.01),
                                    Y=random.uniform(-5000.01, 8000.01),
                                    Z=random.uniform(-5000.01, 8000.01))

                rotation = Rotation(Roll=random.uniform(0.00, 360.0),
                                    Pitch=random.uniform(0.00, 360.0),
                                    Yaw=random.uniform(0.00, 360.0))

                return Transform(Location=location, Rotation=rotation)

            objects_in_UE: List[EnvironmentObject] = [
                EnvironmentObject(Id="1", Name="My favourite item", Tag="Some Tag", Type=ObjType.OTHER,
                                  Transform=generate_random_transform()),
                EnvironmentObject(Id="2", Name="This is a beautiful plant", Tag="Cool Plant", Type=ObjType.PLANT,
                                  Transform=generate_random_transform()),
                EnvironmentObject(Id="3", Name="This plant is very colourful", Tag="Cool Plant", Type=ObjType.PLANT,
                                  Transform=generate_random_transform()),
                EnvironmentObject(Id="4", Name="A red cup, good for tea. It belongs to my mom", Tag="Utensils", Type=ObjType.OTHER,
                                  Transform=generate_random_transform()),
                EnvironmentObject(Id="5", Name="A chair, where my father sits while watching TV", Tag="Some Tag", Type=ObjType.OTHER,
                                  Transform=generate_random_transform()),
                EnvironmentObject(Id="6", Name="A coffee table", Tag="Some Tag", Type=ObjType.OTHER,
                                  Transform=generate_random_transform()),
                EnvironmentObject(Id="7", Name="Roses on the coffee table, my mom got them for her birthday that was yesterday", Tag="Mom's Rose", Type=ObjType.PLANT,
                                  Transform=generate_random_transform()),
                EnvironmentObject(Id="8", Name="A Television, BBC new are on", Tag="Living Room TV", Type=ObjType.APPLIANCE,
                                  Transform=generate_random_transform())]

            print("GET operation executed")

            return objects_in_UE

        return self.router
