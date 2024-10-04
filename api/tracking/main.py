from typing import Union

from pydantic import BaseModel

from fastapi import APIRouter, Response, Depends, status

from auth import get_current_active_user
from auth import User

Number = Union[float, int]

tracking_router = APIRouter(prefix="/tracking", tags=["Tracking", "Data"])

class BenchmarkResults(BaseModel):
    scenarios: list[Number]

@tracking_router.get("/latest")
async def get_latest(
        current_user: User = Depends(get_current_active_user)
        ) -> Response:
    results = BenchmarkResults(scenarios=[200,900])
    return Response(content=results.model_dump_json(), media_type="application/json", status_code=status.HTTP_200_OK)