from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

import app.models as models
import app.schemas as schemas
from app.oauth2 import get_current_user
from app.database import get_session, get_async_session
from app.ai.llm_caller import llmcaller

router = APIRouter(prefix = "/ai", tags=['ai'])


@router.post("/get_emotions")
def get_emotions_in_text(to_analyze : schemas.EntryBase, user : models.User = Depends(get_current_user)):
    emotions = llmcaller.get_emotions(to_analyze.text)
    return {'emotions' : emotions}
