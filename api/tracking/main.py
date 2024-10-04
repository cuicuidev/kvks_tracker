import datetime

from typing import Union, Optional

from pydantic import BaseModel

from fastapi import APIRouter, Response, Depends, Query, status

import bson
from pymongo.database import Database

from database import get_db
from auth import get_current_active_user
from auth import User

tracking_router = APIRouter(prefix="/tracking", tags=["Tracking", "Data"])

Number = Union[float, int]

class BenchmarkResults(BaseModel):
    scenarios: list[Number]

class Scenario(BaseModel):
    name: str
    creator: Optional[str]

class Score(BaseModel):
    scenario: Scenario
    score: Number
    hit_count: int
    miss_count: int
    submitted_at: datetime.datetime
    raw_csv: str

@tracking_router.post("/score")
async def post_score(
        score: Score,
        current_user: User = Depends(get_current_active_user),
        db: Database = Depends(get_db)
        ) -> Response:
    user_id = current_user.user_id
    score = score.model_dump()
    score["user_id"] = bson.ObjectId(user_id)

    result = db.scores.insert_one(score)
    return Response(content=str(result), media_type="application/json", status_code=status.HTTP_201_CREATED)

def get_scenario_query(
        name: str = Query(...),
        creator: str = Query(...)
        ) -> Scenario:
    return Scenario(name=name, creator=creator)

@tracking_router.get("/scores")
async def get_scores(
        scenario: Scenario = Depends(get_scenario_query),
        current_user: User = Depends(get_current_active_user),
        db: Database = Depends(get_db)
        ) -> Response:
    
    # cursor = db.scores.find({"$and" : [
    #     {"scenario.name" : scenario.name},
    #     {"scenario.creator" : scenario.creator}
    # ]})

    return Response()