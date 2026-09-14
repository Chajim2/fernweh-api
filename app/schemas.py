from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from uuid import UUID


### USER 

class UserBase(BaseModel):
    username : str

class UserCreate(UserBase):
    password : str

class UserPublic(UserBase):
    id : UUID


### FRIENDSHIPS

class FriendshipPublic(BaseModel):
    id : int
    created_at : datetime
    friend : UserPublic

### REQUESTS

class FriendRequestCreate(BaseModel):
    friend_id : UUID

class FriendRequestDecision(BaseModel):
    accepted : bool

class FriendRequestResponse(BaseModel):
    id : int
    user_id : UUID
    friend_id : UUID
    created_at : Optional[datetime]

class AcceptResponse(BaseModel):
    status : str
    friendship : FriendshipPublic

class DeclineResponse(BaseModel):
    status: str


### ENTRIES/COMMENTS

class EntryBase(BaseModel):
    text : str

class EntryCreate(EntryBase):
    title : str
    is_private : bool = False

class CommentInfo(BaseModel):
    text : str

class FeedItem(BaseModel):
    id : int
    text : str
    author_name : str
    authrod_id : UUID
    timestamp : datetime
    title : str | None
    parent_id : int | None
    is_private : bool = False
    type : str

class FeedResponse(BaseModel):
    fetched_so_far : int
    items : list[FeedItem]
    has_more : bool

class EntryResponse(EntryBase):
    id : int
    author_id : UUID
    title: str
    is_private: bool = False
    timestamp : datetime


### AUTH

class TokenBase(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Optional[str]

class RefreshResponse(BaseModel):
    refresh_token : str

class TokenData(BaseModel):
    id : Optional[str]

class LoginResponse(TokenBase):
    message : str = ""

class UserLogin(UserBase):
    password : str
