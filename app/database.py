from typing import Annotated
import os
from dotenv import load_dotenv

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

from sqlmodel.ext.asyncio.session import AsyncSession  # <-- CORRECT AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = "sqlite:///./fernweh.db"
ASYNC_DATABASE_URL = "sqlite+aiosqlite:///./fernweh.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)


async def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    print("created all tables")


def get_session():
    with Session(engine) as session:
        yield session


async def get_async_session():
    async with AsyncSession(async_engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
