import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..main import Base


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id"),
        nullable=False,
        index=True,
    )

    status = Column(String, nullable=False, default="queued")
    attempts = Column(Integer, nullable=False, default=0)
    error_code = Column(String, nullable=True)

    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    document = relationship("Document", back_populates="processing_jobs")

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )