from typing import Annotated, Dict

import bson
from pymongo.database import Database

from fastapi import APIRouter, Response, Depends, HTTPException, status

from database import get_db
from auth import get_current_user

users_router = APIRouter(prefix="/users", tags=["Users"])

db_dependency = Annotated[Database, Depends(get_db)]
user_dependency = Annotated[Dict, Depends(get_current_user)]

@users_router.get("/user/{id}")
async def get_user(id: str, db=db_dependency, user=user_dependency) -> Response:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed.")
    id_bson = bson.ObjectId(id)
    users = db["users"]
    user = users.find_one({"_id" : id_bson})
    return user