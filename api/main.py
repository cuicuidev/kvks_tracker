from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI

from auth import auth_router
from users import users_router
    

app = FastAPI()
app.include_router(auth_router)
app.include_router(users_router)