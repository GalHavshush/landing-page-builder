from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base, JSONType, UTCDateTime, utcnow


class SiteExport(Base):
    """One built version of a site: the ZIP is kept in storage. This is the artifact that
    "publish" will deploy later (ADR 004), and the source for "download an earlier version"."""

    __tablename__ = "exports"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), index=True
    )
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    doc_revision: Mapped[int] = mapped_column(Integer)
    artifact_key: Mapped[str] = mapped_column(String(200))
    size_bytes: Mapped[int] = mapped_column(Integer)
    file_count: Mapped[int] = mapped_column(Integer)
    issues: Mapped[list] = mapped_column(JSONType, default=list)  # build warnings at the time
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)
