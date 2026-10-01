from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AdminResponse(BaseModel):
    id: int
    username: str

    model_config = {"from_attributes": True}
