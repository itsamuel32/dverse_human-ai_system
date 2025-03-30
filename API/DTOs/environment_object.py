from typing import Optional

from pydantic import BaseModel

from enums.obj_enum import ObjType


class Location(BaseModel):
    X: float
    Y: float
    Z: float


class Rotation(BaseModel):
    Roll: float
    Pitch: float
    Yaw: float


class Transform(BaseModel):
    Location: Location
    Rotation: Rotation


class EnvironmentObject(BaseModel):
    Id: str
    Tag: Optional[str]
    Name: str
    Type: ObjType
    Transform: Transform
