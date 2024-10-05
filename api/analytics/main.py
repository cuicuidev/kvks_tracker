from typing import Literal, Optional

from fastapi import APIRouter, Response, Depends, status
from pydantic import BaseModel

import bson
from pymongo.database import Database

from database import get_db
from auth import User, get_current_active_user

analytics_router = APIRouter(prefix="/analytics", tags=["Analytics", "Data"])

class ErrorLogs(BaseModel):
    type: Literal["kvks_tracker", "setup", "config"]
    error: str
    logs: Optional[str]

@analytics_router.post("/errors")
async def post_errors(
        request: ErrorLogs,
        current_user: User = Depends(get_current_active_user),
        db: Database = Depends(get_db)
        ) -> Response:
    log = request.model_dump()
    log["user_id"] = bson.ObjectId(current_user.user_id)
    result = db.errors.insert_one(log)
    return Response(content=str(result.inserted_id), media_type="application/json", status_code=status.HTTP_201_CREATED)
