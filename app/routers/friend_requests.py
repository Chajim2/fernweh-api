from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlmodel import Session, select, or_, and_
from app.oauth2 import get_current_user
from app.database import get_session 
from app.models import FriendRequest, User, Friendship
from app.schemas import FriendRequestResponse, \
                        AcceptResponse, FriendshipPublic, UserPublic
from app.routers.friendships import friendship_exists

router = APIRouter(tags=["friend_requests"], prefix="/friend_requests")

def friend_request_exists(friend_request : FriendRequest, user : User, db : Session):
    statement = select(FriendRequest).where(or_(
                                                and_(FriendRequest.user_id == user.id, FriendRequest.friend_id == friend_request.friend_id),
                                                and_(FriendRequest.user_id == friend_request.friend_id, FriendRequest.friend_id == user.id)
                                            )
                                        )
    return db.exec(statement).first() is not None

   
@router.post("/{friend_id}") 
def accept_friend_request(friend_id : UUID, db : Session = Depends(get_session),
                          current_user : User = Depends(get_current_user)) -> AcceptResponse:

    statement = select(FriendRequest).where(FriendRequest.friend_id == current_user.id, FriendRequest.user_id == friend_id)
    friendrequest = db.exec(statement).first()
    
    if friendrequest:
        db.delete(friendrequest)
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        
    statement = select(User).where(User.id == friend_id)
    friend = db.exec(statement).first()

    if friend is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    friendship = Friendship(user_id = current_user.id, friend_id = friend_id) 
    friendship_reversed = Friendship(user_id=friend_id, friend_id=current_user.id)

    db.add(friendship)
    db.add(friendship_reversed)

    db.commit()
    db.refresh(friendship) 

    return AcceptResponse(
        friendship=FriendshipPublic(
            created_at=friendship.created_at,
            user= UserPublic(
                username=friend.username,
                id=friend.id
            )
        )
    )

@router.delete("/{friend_id}", status_code=status.HTTP_204_NO_CONTENT) 
def decline_friend_request(friend_id : UUID, db : Session = Depends(get_session),
                           current_user : User = Depends(get_current_user)) -> None:

    statement = select(FriendRequest).where(FriendRequest.friend_id == current_user.id, FriendRequest.user_id == friend_id)
    friendrequest = db.exec(statement).first()
    
    if friendrequest:
        db.delete(friendrequest)
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
 


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_friend_request(friend_request : FriendRequest, db : Session = Depends(get_session), current_user :
                           User = Depends(get_current_user)) -> FriendRequestResponse:
    new_friend_request = FriendRequest(user_id = current_user.id, friend_id = friend_request.friend_id)
    if friend_request_exists(new_friend_request, current_user, db):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Friend request already exists between these two users")
    
    if friendship_exists(new_friend_request, current_user, db):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="These two users are already friends")
    
    db.add(new_friend_request)
    db.commit()
    db.refresh(new_friend_request)
    
    return new_friend_request # same format as FriendRequestResponse

@router.get("/")
def get_all_friend_requests(db : Session = Depends(get_session), current_user : User = Depends(get_current_user)) \
                            -> list[FriendRequestResponse]:
    statement = select(FriendRequest).where(FriendRequest.friend_id == current_user.id)
    return db.exec(statement).all()
