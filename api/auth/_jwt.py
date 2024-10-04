import datetime

from typing import Annotated, Optional


from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt

from pymongo.database import Database

from . import _models
import database

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db: Database, username: str):
    user = db.users.find_one({"username": username})
    if user:
        user["user_id"] = str(user["_id"])
        del user["_id"]
        return _models.UserInDB(**user)
    return None

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: datetime.timedelta = datetime.timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)):
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.UTC) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = _models.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(database.get_db(), username=token_data.username)
    if user is None:
        raise credentials_exception
    user.hashed_password = "REDACTED"
    return user

async def get_current_active_user(
    current_user: Annotated[_models.User, Depends(get_current_user)],
):
    if current_user.is_active:
        return current_user
    raise HTTPException(status_code=400, detail="Inactive user")