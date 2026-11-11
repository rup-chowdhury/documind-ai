import uuid

from sqlalchemy import Column, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..main import Base


class Citation(Base):
    __tablename__ = "citations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    message_id = Column(
        UUID(as_uuid=True),
        ForeignKey("messages.id"),
        nullable=False,
        index=True,
    )

    chunk_id = Column(
        UUID(as_uuid=True),
        ForeignKey("document_chunks.id"),
        nullable=False,
        index=True,
    )

    relevance_score = Column(Float, nullable=True)

    message = relationship("Message", back_populates="citations")
    chunk = relationship("DocumentChunk", back_populates="citations")