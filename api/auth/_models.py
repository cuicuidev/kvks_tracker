import datetime

from typing import Optional

from pydantic import BaseModel, EmailStr

class SignUpRequest(BaseModel):
    email: EmailStr
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str
    email: EmailStr

    created_at: datetime.datetime
    updated_at: datetime.datetime
    is_verified: bool
    is_active: bool

class UserInDB(User):
    _id: Optional[str] = None
    hashed_password: str