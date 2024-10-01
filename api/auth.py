import datetime

from typing import Annotated

from fastapi import APIRouter, Response, Depends, status, HTTPException

from pydantic import BaseModel, EmailStr

from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt

import bson

from database import get_db


auth_router = APIRouter(prefix="/auth", tags=["Auth"])

SECRET_KEY="b8f3d7a90c4e5f1b2a8d3e6c91f4b2c0e7d5a6f91c4b3e2f5d7c9e1f2a4b3d6"
ALGORITHM="HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

class CreateUserRequest(BaseModel):
    email: EmailStr
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    email: str
    hashed_password: str

@auth_router.post("/signup")
async def create_user(request: CreateUserRequest, db=Depends(get_db)) -> Response:
    hashed_password=bcrypt_context.hash(request.password)
    user = User(
        username=request.username,
        email=request.email,
        hashed_password=hashed_password
    )
    users = db["users"]
    users.insert_one(user.model_dump())
    return Response(content=user.model_dump_json(), media_type="application/json", status_code=status.HTTP_201_CREATED)

def authenticate_user(username: str, password: str, db):
    users = db.users
    user = users.find_one({"username" : username})
    if not user:
        return status.HTTP_404_NOT_FOUND
    if not bcrypt_context.verify(password, user["hashed_password"]):
        return status.HTTP_401_UNAUTHORIZED
    return user

def create_access_token(username: str, id: bson.ObjectId, dt: datetime.timedelta) -> Token:
    encode = {"sub" : username, "id" : str(id)}
    expires = datetime.datetime.now(datetime.UTC) + dt
    encode.update({"exp" : expires})
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    return Token(access_token=token, token_type="Bearer")

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: str = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")
        return {"username" : username, "id" : bson.ObjectId(user_id)}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")

@auth_router.post("/token")
async def access_token(request: Annotated[OAuth2PasswordRequestForm, Depends()], db=Depends(get_db)) -> Token:
    user = authenticate_user(request.username, request.password, db)
    if user == status.HTTP_404_NOT_FOUND:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with the username {request.username} not found in the database.")
    if user == status.HTTP_401_UNAUTHORIZED:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Wrong credentials.")
    token = create_access_token(user["username"], user["_id"], datetime.timedelta(days=30))

    return token