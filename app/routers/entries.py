from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy import ColumnElement
from sqlmodel import Session, select, desc
from typing import cast
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import null, union_all, false, literal

from app.database import get_async_session, get_session
from app.oauth2 import get_current_user
from app.models import Entry, User, Comment
from app.schemas import EntryCreate, FeedResponse, EntryResponse

router = APIRouter(prefix="/entries", tags=["entries"])


@router.get("/")  # currently not in use, might delete later
def get_all_entries(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    statement = (
        select(Entry)
        .join(User, cast(ColumnElement[bool], Entry.author_id == User.id))
        .where(Entry.author_id == current_user.id)
    )

    return db.exec(statement).all()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=EntryResponse)
def post_entry(
    entry_info: EntryCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> EntryResponse:

    new_entry = Entry(
        author_id=current_user.id,
        title=entry_info.title,
        text=entry_info.text,
        is_private=entry_info.is_private,
    )

    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)

    return new_entry


@router.get("/feed", response_model=FeedResponse)
async def get_all_relevant_entries(
    fetched_so_far: int,
    fetch_count: int = 20,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    Return a list of all entries and comments that should be displayed to the user on their feed;
    That is:
        a) entries by them and their friends
        b) comments from their friends (or themselves) under their own posts
        c) their comments under friends posts

    start fetching at pos fetched_so far for scrolling logic;
    """

    # fetch all relevant posts
    entries_stmt = select(
        literal("entry").label("type"),
        Entry.id.label("id"),
        Entry.author_id.label("author_id"),
        Entry.timestamp.label("timestamp"),
        Entry.text.label("text"),
        Entry.title.label("title"),
        Entry.is_private.label("is_private"),
        null().label("parent_id"),
        User.username.label("author_name"),
    ).join(User, Entry.author_id == User.id)

    comments_stmt = select(
        literal("comment").label("type"),
        Comment.id.label("id"),
        Comment.author_id.label("author_id"),
        Comment.timestamp.label("timestamp"),
        Comment.text.label("text"),
        null().label("title"),
        false().label("is_private"),
        Comment.parent_id.label("parent_id"),
        User.username.label("author_name"),
    ).join(User, Comment.author_id == User.id)

    union_stmt = (
        union_all(entries_stmt, comments_stmt)
        .order_by(desc("timestamp"), desc("id"), "type")
        .offset(fetched_so_far)
        .limit(fetch_count + 1)
    )

    print("\n--- DB DIAGNOSTICS ---")
    users = (await db.execute(select(User))).scalars().all()
    print("ALL USERS:", [(u.id, u.username) for u in users])

    entries = (await db.execute(select(Entry))).scalars().all()
    print(
        "ALL ENTRIES:",
        [(e.id, getattr(e, "author_id", "MISSING_AUTHOR")) for e in entries],
    )
    print("----------------------\n")

    res = await db.execute(union_stmt)
    rows = res.mappings().all()

    print("haesrhbia", rows)

    has_more = len(rows) > fetch_count

    if has_more:  # remove the extra item that served as has_more check
        rows.pop()

    return FeedResponse(
        fetched_so_far=fetched_so_far + len(rows), items=rows, has_more=has_more
    )


@router.get("/{id}")
def get_entry_with_comments(
    id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Return the post of with the given id, all comments under it and the title emotions
    """
    # add check whether post author is current user or their friend !!
    statement = select(Entry).where(Entry.id == id)
    entry = db.exec(statement).first()

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entry with id {id} not found",
        )

    statement = select(Comment).where(Comment.parent_id == id)
    comments = db.exec(statement).all()

    return {"entry": entry, "comments": comments}
