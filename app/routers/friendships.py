from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from sqlmodel import select, Session
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from app.oauth2 import get_current_user
from app.database import get_session, get_async_session
from app.schemas import UserPublic
from app.models import Friendship, User, FriendRequest

router = APIRouter(tags=["friendships"], prefix="/friendships")

async def get_all_friends(user_id: UUID, db: AsyncSession) -> List[UserPublic]:
    statement = select(Friendship).where(Friendship.user_id == user_id)

    results = await db.exec(statement)
    friendships = results.all()
    friends = []

    for friendship in friendships: # assuming updated friendship table with reverse friendships added
        friend_stmt = select(User).where(User.id == friendship.friend_id)
        result = await db.exec(friend_stmt)
        friend_info = result.first()

        if friend_info:
            friend = UserPublic(id=friend_info.id, username=friend_info.username)
            friends.append(friend)

    return friends

def friendship_exists(friend_request : FriendRequest, user : User, db : Session) -> bool:
    statement = select(Friendship).where(
        Friendship.user_id == user.id,
        Friendship.friend_id == friend_request.friend_id
    )

    return db.exec(statement).first() is not None

@router.get("/")
async def get_all_friends_endpoint( current_user : User = Depends(get_current_user),
                              db : AsyncSession = Depends(get_async_session)) -> List[UserPublic]:
    """Returns all friends of the current user - returns id, name for each friend"""
    return get_all_friends(current_user.id, db)

@router.delete("/{friend_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_friendship(friend_id : UUID, current_user : User = Depends(get_current_user),
                      db : Session = Depends(get_session)) -> None:
    
    stmt1 = db.delete(Friendship).where(Friendship.user_id == current_user.id,
                                        Friendship.friend_id == friend_id)

    stmt2 = db.delete(Friendship).where(Friendship.user_id == friend_id,
                                        Friendship.friend_id == current_user.id)


    friendship1 = db.exec(stmt1).first()
    friendship2 = db.exec(stmt2).first()

    if not friendship1 and not friendship2:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Friendship does not exist")

    if friendship1:
        db.delete(friendship1)
    if friendship2:
        db.delete(friendship2)

    db.commit()
