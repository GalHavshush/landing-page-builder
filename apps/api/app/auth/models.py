from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base, UTCDateTime, utcnow


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(200), default="")
    # editor preferences, independent of any site's language
    ui_language: Mapped[str] = mapped_column(String(8), default="he", server_default="en")
    ui_theme: Mapped[str] = mapped_column(String(8), default="system", server_default="system")
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)


class UserSession(Base):
    """Server-side login session. Only a hash of the cookie token is stored, so a database
    leak does not hand out working sessions."""

    __tablename__ = "sessions"

    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    expires_at: Mapped[datetime] = mapped_column(UTCDateTime)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)
