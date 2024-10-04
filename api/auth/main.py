import datetime

from typing import Annotated

from fastapi import APIRouter, Response, Depends, status, HTTPException

from fastapi.security import OAuth2PasswordRequestForm

from database import get_db
from . import _jwt, _models

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

@auth_router.post("/signup")
async def create_user(request: _models.SignUpRequest, db=Depends(get_db)) -> Response:
    hashed_password=_jwt.pwd_context.hash(request.password)
    now = datetime.datetime.now(datetime.UTC)
    user = _models.UserInDB(
        username=request.username,
        email=request.email,
        hashed_password=hashed_password,

        is_active=True,
        is_verified=False,
        created_at=now,
        updated_at=now
    )

    db.users.insert_one(user.model_dump())
    return Response(content=user.model_dump_json(), media_type="application/json", status_code=status.HTTP_201_CREATED)

@auth_router.post("/token", response_model=_models.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db=Depends(get_db)
):
    user = _jwt.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = _jwt.create_access_token(
        data={"sub": user.username}
    )
    return _models.Token(access_token=access_token, token_type="bearer")