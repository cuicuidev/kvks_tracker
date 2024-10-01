import os

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

def get_db():
    url = os.getenv("MONGODB_URL")
    client = MongoClient(url, server_api=ServerApi('1'))
    return client["main"]