from typing import List, Union
from pydantic import BaseModel

from req_class import oauth

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


class PoseAccuracyData(BaseModel):
    pose: List[PoseLandmarks]
    auth: Union[oauth.OAuthData, oauth.GoogleOAuthData, None]


class PoseAccuracyReq(BaseModel):
    version: str
    data: PoseAccuracyData