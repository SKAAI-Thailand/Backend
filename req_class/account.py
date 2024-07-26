from pydantic import BaseModel

class RegisterData(BaseModel):
    name: str
    password: str
    email: str


class RegisterReq(BaseModel):
    version: str
    data: RegisterData


class ResetPassData(BaseModel):
    email: str


class ResetPassReq(BaseModel):
    version: str
    data: ResetPassData


class NewPassData(BaseModel):
    token: str
    password: str


class NewPassReq(BaseModel):
    version: str
    data: NewPassData
