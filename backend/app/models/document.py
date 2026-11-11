from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

import uuid
from ..main import Base

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False)
    filename = Column(String, nullable=False)
    storage_key = Column(String, nullable=False)
    status = Column(String, default="pending") # pending, ready, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document")
    processing_jobs = relationship(
        "ProcessingJob",
        back_populates="document",
    )

