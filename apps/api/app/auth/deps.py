from datetime import timedelta

from fastapi import Depends, HTTPException, Request, Response
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.auth.models import User, UserSession
from app.auth.security import hash_token, new_token
from app.config import get_settings
from app.db import get_db, utcnow

COOKIE = "session"


def start_session(db: Session, user: User, response: Response) -> None:
    settings = get_settings()
    token = new_token()
    db.add(
        UserSession(
            token_hash=hash_token(token),
            user_id=user.id,
            expires_at=utcnow() + timedelta(days=settings.session_days),
        )
    )
    response.set_cookie(
        COOKIE,
        token,
        max_age=settings.session_days * 86400,
        httponly=True,  # not readable from JavaScript
        samesite="lax",
        secure=settings.cookie_secure,
        path="/",
    )


def end_session(db: Session, request: Request, response: Response) -> None:
    token = request.cookies.get(COOKIE)
    if token:
        db.execute(delete(UserSession).where(UserSession.token_hash == hash_token(token)))
    response.delete_cookie(COOKIE, path="/")


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get(COOKIE)
    if token:
        row = db.get(UserSession, hash_token(token))
        if row and row.expires_at > utcnow():
            user = db.get(User, row.user_id)
            if user:
                return user
    raise HTTPException(status_code=401, detail="Not authenticated")
