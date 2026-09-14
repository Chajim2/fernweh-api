from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy import Column, Integer, String
import uuid
from sqlmodel import SQLModel, Field, Relationship

class User(SQLModel, table = True):
    id : UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username : str = Field(unique=True, index=True)
    password : str
    class Config:
        arbitrary_types_allowed = True
    
    entries_posted : "Entry" = Relationship(back_populates="author")
    comments_posted: "Comment" = Relationship(back_populates="author")

class Entry(SQLModel, table = True):
    id : Optional[int] = Field(default = None, primary_key= True)
    title : str
    text : str
    timestamp : Optional[datetime] = Field(default_factory= lambda : datetime.now(timezone.utc))
    author_id : UUID = Field(foreign_key="user.id")
    is_private : Optional[bool] = Field(default=False)

    author : "User" = Relationship(back_populates="entries_posted")

class Comment(SQLModel, table = True):
    id : Optional[int] = Field(default = None, primary_key= True)
    author_id : UUID = Field(foreign_key="user.id")
    parent_id : int = Field(foreign_key="entry.id")
    text : str
    timestamp : Optional[datetime] = Field(default_factory= lambda : datetime.now(timezone.utc))
    author : "User" = Relationship(back_populates="comments_posted")


class Friendship(SQLModel, table = True):
    id : Optional[int] = Field(default = None, primary_key= True)
    user_id : UUID  = Field(foreign_key="user.id")
    friend_id : UUID = Field(foreign_key="user.id")
    created_at : Optional[datetime] = Field(default_factory= lambda : datetime.now(timezone.utc))
  
class FriendRequest(SQLModel, table = True):
    id : Optional[int] = Field(default = None, primary_key= True)
    user_id : UUID  = Field(foreign_key="user.id")
    friend_id : UUID = Field(foreign_key="user.id") 
    created_at : Optional[datetime] = Field(default_factory= lambda : datetime.now(timezone.utc))
