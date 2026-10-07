from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import deps
from app.auth.models import User
from app.auth.schemas import Credentials, PreferencesIn, RegisterRequest, UserOut
from app.auth.security import hash_password, verify_password
from app.config import get_settings
from app.db import get_db
from app.ratelimit import limit_login, limit_register

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserOut, status_code=201, dependencies=[Depends(limit_register)]
)
def register(body: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    if not get_settings().allow_registration:
        raise HTTPException(403, "Registration is closed")
    if db.scalar(select(User).where(User.email == body.email)):
        raise HTTPException(409, "An account with this email already exists")
    user = User(email=body.email, name=body.name, password_hash=hash_password(body.password))
    db.add(user)
    db.flush()
    deps.start_session(db, user, response)
    return user


@router.post("/login", response_model=UserOut, dependencies=[Depends(limit_login)])
def login(body: Credentials, response: Response, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == body.email))
    if not verify_password(user.password_hash if user else None, body.password):
        raise HTTPException(401, "Invalid email or password")
    deps.start_session(db, user, response)
    return user


@router.post("/logout", status_code=204)
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    deps.end_session(db, request, response)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(deps.get_current_user)):
    return user


@router.patch("/me", response_model=UserOut)
def update_preferences(body: PreferencesIn, user: User = Depends(deps.get_current_user)):
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(user, field, value)
    return user
