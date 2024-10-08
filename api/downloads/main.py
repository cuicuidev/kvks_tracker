import os

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

WORKDIR = os.getcwd()
FILE_DIRECTORY = os.path.join(WORKDIR, "downloads/bin")
DESKTOP_CLIENT_VERSION = "0.0.6"

downloads_router = APIRouter(prefix="/download", tags=["Downloads"])

@downloads_router.get("/desktop_client.zip")
async def download_client():
    filename = "desktop_client.zip"
    file_path = os.path.join(FILE_DIRECTORY, filename)

    if os.path.exists(file_path):
        file_like = open(file_path, mode="rb")
        return StreamingResponse(file_like, media_type="application/octet-stream")
    else:
        return {"error": "File not found"}
    
@downloads_router.get("/kovaaks_tracker_setup.exe")
async def download_setup():
    filename = "kovaaks_tracker_setup.zip"
    file_path = os.path.join(FILE_DIRECTORY, filename)

    if os.path.exists(file_path):
        file_like = open(file_path, mode="rb")
        return StreamingResponse(file_like, media_type="application/octet-stream")
    else:
        return {"error": "File not found"}
    
@downloads_router.get("/latest")
async def latest_version():
    return {"desktop_client_version" : DESKTOP_CLIENT_VERSION}