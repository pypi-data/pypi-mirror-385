from pydantic import BaseModel, EmailStr

from .user import User


class EmailRequest(BaseModel):
    email: EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class SuccessResponse(BaseModel):
    message: str


# TODO not used i think
class JWTTokens(BaseModel):
    accessToken: str
    refreshToken: str
    refreshTokenJti: str | None = None


# Authentication Response
class SessionTokens(BaseModel):
    access: str
    refresh: str


class Verification(BaseModel):
    token: str
    link: str


class AuthResponse(BaseModel):
    user: User
    tokens: SessionTokens | None = None
    verification: Verification | None = None
