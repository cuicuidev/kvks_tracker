from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI

from auth import auth_router
from users import users_router
from tracking import tracking_router
from downloads import downloads_router
from analytics import analytics_router
    

app = FastAPI()
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tracking_router)
app.include_router(downloads_router)
app.include_router(analytics_router)