from fastapi.security import OAuth2PasswordRequestForm
from app.schemas import UserLogin, LoginResponse, RefreshResponse, UserPublic
from sqlmodel import select, Session
from fastapi import Depends, FastAPI, HTTPException, Response, status, APIRouter, status
import app.utils as utils, app.models as models
from app.database import get_session
import app.oauth2 as oauth2

router = APIRouter(tags = ['auth'], prefix='/auth')

@router.post('/login', response_model=LoginResponse)
def login(loginInfo : OAuth2PasswordRequestForm = Depends(), db : Session = Depends(get_session)):
    statement = select(models.User).where(models.User.username == loginInfo.username)
    user = db.exec(statement).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect user credentials")
    
    if not utils.verify(loginInfo.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect user credentials")
    
    access_token = oauth2.create_access_token(data = {"user_id" : str(user.id)}) 
    refresh_token = oauth2.create_refresh_token(data = {"user_id" : str(user.id)}) 

    return {
        "access_token" : access_token,
        "refresh_token" : refresh_token,
        "token_type" : "bearer"
        }

@router.post('/register', status_code=status.HTTP_201_CREATED)
def register(loginInfo : UserLogin, db : Session = Depends(get_session)):
    loginInfo.password = utils.hash(loginInfo.password)
    new_user = models.User(**loginInfo.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserPublic(username=new_user.username, id=new_user.id)
 
@router.post("/refresh")
def validate_refresh_token(refresh_info : RefreshResponse):
    user_data = oauth2.verify_access_token(refresh_info.refresh_token, HTTPException(
        status.HTTP_401_UNAUTHORIZED, detail="Invalid  or outdated refresh token"))
    
    return RefreshResponse( 
        refresh_token=oauth2.create_access_token(data = {"user_id" : str(user_data.id)})
    )
    
    