from fastapi import APIRouter, Response, Depends, HTTPException, status

from auth import get_current_active_user
from auth import User

users_router = APIRouter(prefix="/users", tags=["Users"])

@users_router.get("/me", response_model=User)
async def get_user(
        current_user : User = Depends(get_current_active_user),
        ) -> Response:
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed.")
    return Response(content=current_user.model_dump_json(), media_type="application/json", status_code=status.HTTP_200_OK)