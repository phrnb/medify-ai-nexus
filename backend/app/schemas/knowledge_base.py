
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class KnowledgeBaseCategoryEnum(str, Enum):
    workflow = "workflow"
    medical = "medical"
    technical = "technical"
    faq = "faq"
    guidelines = "guidelines"

# Base KnowledgeBase schema
class KnowledgeBaseArticleBase(BaseModel):
    title: str
    content: str
    category: KnowledgeBaseCategoryEnum
    tags: List[str] = []
    is_published: bool = True

# Schema for creating a knowledge base article
class KnowledgeBaseArticleCreate(KnowledgeBaseArticleBase):
    pass

# Schema for updating a knowledge base article
class KnowledgeBaseArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[KnowledgeBaseCategoryEnum] = None
    tags: Optional[List[str]] = None
    is_published: Optional[bool] = None

# Schema for knowledge base article in DB
class KnowledgeBaseArticleInDBBase(KnowledgeBaseArticleBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: str
    updated_by: Optional[str] = None

    class Config:
        orm_mode = True

# Schema for returning knowledge base article
class KnowledgeBaseArticle(KnowledgeBaseArticleInDBBase):
    pass

# Schema for detailed knowledge base article view
class KnowledgeBaseArticleDetail(KnowledgeBaseArticle):
    created_by_name: Optional[str] = None
    updated_by_name: Optional[str] = None
