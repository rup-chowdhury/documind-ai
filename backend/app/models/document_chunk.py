import uuid

from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..main import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id"),
        nullable=False,
        index=True,
    )

    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)

    document = relationship("Document", back_populates="chunks")
    citations = relationship("Citation", back_populates="chunk")
