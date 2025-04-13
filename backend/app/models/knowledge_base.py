
from sqlalchemy import Boolean, Column, String, DateTime, ForeignKey, Text, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.db.base_class import Base

class KnowledgeBaseCategoryEnum(str, enum.Enum):
    workflow = "workflow"
    medical = "medical"
    technical = "technical"
    faq = "faq"
    guidelines = "guidelines"

class KnowledgeBaseArticle(Base):
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    tags = Column(ARRAY(String), nullable=True)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String, ForeignKey("user.id"), nullable=False)
    updated_by = Column(String, ForeignKey("user.id"), nullable=True)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
