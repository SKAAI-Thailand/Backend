from typing import List
from pydantic import BaseModel

class PoseNode(BaseModel):
    x: float
    y: float
    z: float
    visibility: float


class HandNode(BaseModel):
    x: float
    y: float
    z: float


class PoseLandmarks(BaseModel):
    poseLandmarks: List[PoseNode]
    handLandmarks: List[List[HandNode]]

class DataTool:
    def Process(data: List[PoseLandmarks]):
        pass

class AITool:
    pass