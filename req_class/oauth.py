from pydantic import BaseModel

class OAuthData(BaseModel):
    email: str
    password: str

class OAuthReq(BaseModel):
    version: str
    data: OAuthData

class GoogleOAuthCodeData(BaseModel):
    code: str


class GoogleOAuthCodeReq(BaseModel):
    version: str
    data: GoogleOAuthCodeData


class GoogleOAuthData(BaseModel):
    token: str


class GoogleOAuthReq(BaseModel):
    version: str
    data: GoogleOAuthData