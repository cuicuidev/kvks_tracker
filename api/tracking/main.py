import datetime

from typing import Union, Optional

import bson.json_util
from pydantic import BaseModel

from fastapi import APIRouter, Response, Depends, Query, HTTPException, status

import bson
from pymongo.database import Database

from database import get_db
from auth import get_current_active_user
from auth import User

tracking_router = APIRouter(prefix="/tracking", tags=["Tracking", "Data"])

Number = Union[float, int]

class Kill(BaseModel):
    kill_n: int
    timestamp: datetime.datetime
    bot: str
    weapon: str
    ttk: float
    shots: int
    hits: int
    accuracy: float
    damage_done: float
    damage_possible: float
    efficiency: float
    cheated: bool
    overshots: float


class KovaaksScore(BaseModel):
    kills: list[Kill]

    n_kills: int
    deaths: int
    fight_time: float
    time_remaining: float
    avg_ttk: float
    damage_done: float
    damage_possible: Optional[float]
    total_overshots: int
    damage_taken: float
    hit_count: int
    miss_count: int
    midairs: int
    midaired: int
    directs: int
    directed: int
    reloads: int
    distance_traveled: float
    mbs_points: float
    score: float
    scenario: str
    hash: str
    game_version: str
    challenge_start: datetime.datetime
    pause_count: int
    pause_duration: float

    input_lag: float
    max_fps_config: float
    sens_scale: str
    sens_increment: float
    horiz_sens: float
    vert_sens: float
    dpi: int
    fov: int
    fovscale: str
    hide_gun: bool
    crosshair: str
    crosshair_scale: float
    crosshair_color: str
    resolution: str
    avg_fps: float
    resolution_scale: float

@tracking_router.post("/score")
async def post_score(
        score: KovaaksScore,
        current_user: User = Depends(get_current_active_user),
        db: Database = Depends(get_db)
        ) -> Response:
    user_id = current_user.user_id
    score = score.model_dump()
    score["user_id"] = bson.ObjectId(user_id)
    score["created_at"] = datetime.datetime.now(datetime.UTC)

    result = db.scores.insert_one(score)
    return Response(content=str(result), media_type="application/json", status_code=status.HTTP_201_CREATED)

@tracking_router.get("/latest")
async def latest_score(
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends(get_db)
) -> Response:
    user_id = current_user.user_id

    result = db.scores.find_one(
        {"user_id": user_id},
        sort=[("created_at", -1)]
    )

    if not result:
        raise HTTPException(status_code=404, detail="No scores found for the user.")

    return Response(content=bson.json_util.dumps(result), media_type="application/json")

# def get_scenario_query(
#         name: str = Query(...),
#         creator: str = Query(...)
#         ) -> Scenario:
#     return Scenario(name=name, creator=creator)

# @tracking_router.get("/scores")
# async def get_scores(
#         scenario: Scenario = Depends(get_scenario_query),
#         current_user: User = Depends(get_current_active_user),
#         db: Database = Depends(get_db)
#         ) -> Response:
    
#     # cursor = db.scores.find({"$and" : [
#     #     {"scenario.name" : scenario.name},
#     #     {"scenario.creator" : scenario.creator}
#     # ]})

#     return Response()