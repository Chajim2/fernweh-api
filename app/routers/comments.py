from fastapi import APIRouter, Depends, status, HTTPException
from typing import cast
from sqlalchemy import ColumnElement 
from sqlalchemy.future import select as asyncselect
from sqlmodel import Session, select, desc
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database import get_session, get_async_session
from app.oauth2 import get_current_user
import app.models as models
from app.routers.friendships import get_all_friends
import app.schemas as schemas

router = APIRouter(
    prefix="/comments",
    tags=["comments"]
)

@router.post("/{entry_id}")
def post_comments(entry_id : int, comment : schemas.CommentInfo, db: Session = Depends(get_session), current_user : models.User = Depends(get_current_user)):
    new_comment = models.Comment(author_id = current_user.id, parent_id=entry_id, text = comment.text)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment

async def get_friends_comments(user_id, db: AsyncSession):
    '''
    takes in the id of a user and an async db session
    return a list of all comments, ade by the user's friends (without his own)
    THIS DOESNT WORK, IT ALSO RETURNS THE COMMENTS UNDER OTHER USERS' POSTS AAAAAAAAAAAAHHHHAHAHAH 
    '''
    friends = await get_all_friends(user_id, db)
    friend_ids = [friend.id for friend in friends]
    
    if not friend_ids:
        return []
    
    stmt = (
        select(models.Comment, models.User.username)
        .join(models.User, cast(ColumnElement[bool], models.Comment.author_id == models.User.id))
        .where(cast(ColumnElement, models.User.id).in_(friend_ids))
        .order_by(desc(models.Comment.timestamp))
    )
    
    result = await db.exec(stmt)
    comments_with_user = []
    for comment, username in result.all():
        comments_with_user.append({
            "comment": comment,
            "username": username
        })
    
    return comments_with_user