
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base_class import Base

class ReportHistory(Base):
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = Column(String, ForeignKey("report.id"), nullable=False)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    previous_content = Column(Text, nullable=True)  # The content before the change
    changes = Column(JSON, nullable=False)  # What was changed
    notes = Column(Text, nullable=True)  # Notes about the change
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    report = relationship("Report", back_populates="history")
    user = relationship("User")
