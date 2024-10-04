import datetime

from pymongo import ReturnDocument
from pymongo.database import Database

from fastapi import APIRouter, Response, Depends, HTTPException, status

from database import get_db
from auth import get_current_active_user
from auth import User

from . import _models

users_router = APIRouter(prefix="/users", tags=["Users"])

@users_router.get("/me")
async def get_me(
        current_user: User = Depends(get_current_active_user),
        ) -> Response:
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed.")
    return Response(content=current_user.model_dump_json(), media_type="application/json", status_code=status.HTTP_200_OK)

@users_router.put("/me")
async def update_me(
        update_profile_form: _models.UpdateProfileForm,
        current_user: User = Depends(get_current_active_user),
        db: Database = Depends(get_db)
        ) -> Response:
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed.")
    
    conflicts = db.users.count_documents({"username" : update_profile_form.username})
    if conflicts > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already in use.")
    
    update_dict = update_profile_form.model_dump()
    update_dict = {k:v for k, v in update_dict.items() if v is not None}

    if len(update_dict) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields were specified.")
    
    update_dict["updated_at"] = datetime.datetime.now(datetime.UTC)
    new_user = db.users.find_one_and_update(
        {"username" : current_user.username},
        {"$set" : update_dict},
        return_document=ReturnDocument.AFTER
        )
    
    return Response(content=User(**new_user).model_dump_json(), media_type="application/json", status_code=status.HTTP_201_CREATED)

@users_router.delete("/me")
async def deactivate_me(
        current_user: User = Depends(get_current_active_user),
        db: Database = Depends(get_db)
        ) -> Response:
    
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed.")
    
    update_dict = {"is_active" : False}
    
    update_dict["updated_at"] = datetime.datetime.now(datetime.UTC)
    new_user = db.users.find_one_and_update(
        {"username" : current_user.username},
        {"$set" : update_dict},
        return_document=ReturnDocument.AFTER
        )
    
    return Response(content=User(**new_user).model_dump_json(), media_type="application/json", status_code=status.HTTP_200_OK)

@users_router.delete("/me/hard")
async def delete_me(
        current_user: User = Depends(get_current_active_user),
        db: Database = Depends(get_db)
        ) -> Response:
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed.")
    
    deleted_user = db.users.find_one_and_delete(
        {"username": current_user.username}
    )
    
    return Response(content=User(**deleted_user).model_dump_json(), media_type="application/json", status_code=status.HTTP_200_OK)