from datetime import datetime, timezone
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

def now_utc(): return datetime.now(timezone.utc)

class Submission(Base):
    __tablename__ = "submissions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    student_id: Mapped[str] = mapped_column(String(128), index=True)
    course_id: Mapped[str] = mapped_column(String(128), index=True)
    assignment_id: Mapped[str] = mapped_column(String(128), index=True)
    title: Mapped[str] = mapped_column(String(240))
    content: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), default="CREATED", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

class Rubric(Base):
    __tablename__ = "rubrics"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(240))
    version: Mapped[int] = mapped_column(Integer, default=1)
    criteria_json: Mapped[str] = mapped_column(Text)
    active: Mapped[int] = mapped_column(Integer, default=1)

class Evaluation(Base):
    __tablename__ = "evaluations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    submission_id: Mapped[str] = mapped_column(ForeignKey("submissions.id"), index=True)
    rubric_id: Mapped[str] = mapped_column(ForeignKey("rubrics.id"))
    idempotency_key: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(32), default="QUEUED", index=True)
    attempt: Mapped[int] = mapped_column(Integer, default=0)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    result_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
    __table_args__ = (UniqueConstraint("submission_id", "idempotency_key", name="uq_eval_idempotency"),)

class Review(Base):
    __tablename__ = "reviews"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    evaluation_id: Mapped[str] = mapped_column(ForeignKey("evaluations.id"), index=True)
    reviewer_id: Mapped[str] = mapped_column(String(128))
    decision: Mapped[str] = mapped_column(String(24))
    comment: Mapped[str] = mapped_column(Text, default="")
