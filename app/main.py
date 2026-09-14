import uuid
from fastapi import Body, Depends, FastAPI, Response, status
from contextlib import asynccontextmanager
import time
from uuid import UUID
from sqlalchemy.orm import Session

from app.database import create_db_and_tables, get_session
import app.utils as utils, app.models as models
import app.routers.auth as auth
import app.routers.friend_requests as friend_requests
import app.routers.friendships as friendships
import app.routers.entries as entries
import app.routers.ai as ai
import app.routers.comments as comments
from app.oauth2 import get_current_user
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app : FastAPI):
    await create_db_and_tables()
    yield
    print("it was a good run")

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost",  # For local development
    "http://localhost:3000",
    "https://fernweh-flutter.onrender.com" # Your Flutter app's domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)
"""while True:
    try:
        conn = psycopg2.connect(host="localhost", database="fernweh_backend", user='postgres', password='132465', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("connected to db")
        break
    except Exception as e:
        print("sad day for connecting to db", e)
        time.sleep(3)
"""     
@app.get('/')
def nothing():
    return {"data" : "Nun to see her my friend"} 

app.include_router(auth.router)
app.include_router(friend_requests.router)
app.include_router(friendships.router)
app.include_router(entries.router)
app.include_router(comments.router)
app.include_router(ai.router)
