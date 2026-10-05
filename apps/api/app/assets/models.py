from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base, JSONType, UTCDateTime, utcnow


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(
        String(40), primary_key=True
    )  # "asset_<12 hex>", used in documents
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), index=True
    )
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    storage_key: Mapped[str] = mapped_column(String(200), unique=True)  # unguessable path
    thumb_key: Mapped[str] = mapped_column(String(200))
    original_filename: Mapped[str] = mapped_column(String(300))
    mime: Mapped[str] = mapped_column(String(100))
    size_bytes: Mapped[int] = mapped_column(Integer)
    width: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)
    sha256: Mapped[str] = mapped_column(String(64))
    alt_default: Mapped[str] = mapped_column(String(300), default="")
    # smaller copies for srcset: [{"width": 640, "key": "p1/token/name-640.webp"}, ...]
    variants: Mapped[list] = mapped_column(JSONType, default=list)
    color: Mapped[str] = mapped_column(String(9), default="")  # average colour placeholder
    credit: Mapped[str] = mapped_column(String(300), default="")  # e.g. "Photo by X on Pexels"
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)
