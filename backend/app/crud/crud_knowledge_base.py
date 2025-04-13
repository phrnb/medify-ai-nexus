
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.crud.base import CRUDBase
from app.models.knowledge_base import KnowledgeBaseArticle, KnowledgeBaseCategoryEnum
from app.schemas.knowledge_base import KnowledgeBaseArticleCreate, KnowledgeBaseArticleUpdate

class CRUDKnowledgeBaseArticle(CRUDBase[KnowledgeBaseArticle, KnowledgeBaseArticleCreate, KnowledgeBaseArticleUpdate]):
    def create_with_user(
        self, db: Session, *, obj_in: KnowledgeBaseArticleCreate, created_by: str
    ) -> KnowledgeBaseArticle:
        """Create a new article with user as creator"""
        obj_in_data = obj_in.dict()
        obj_in_data["created_by"] = created_by
        db_obj = KnowledgeBaseArticle(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
        
    def get_filtered_articles(
        self,
        db: Session,
        *,
        category: Optional[KnowledgeBaseCategoryEnum] = None,
        tag: Optional[str] = None,
        search_term: Optional[str] = None,
        published_only: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[KnowledgeBaseArticle]:
        query = db.query(KnowledgeBaseArticle)
        
        if published_only:
            query = query.filter(KnowledgeBaseArticle.is_published == True)
            
        if category:
            query = query.filter(KnowledgeBaseArticle.category == category)
            
        if tag:
            query = query.filter(KnowledgeBaseArticle.tags.any(tag))
            
        if search_term:
            search = f"%{search_term}%"
            query = query.filter(
                or_(
                    KnowledgeBaseArticle.title.ilike(search),
                    KnowledgeBaseArticle.content.ilike(search)
                )
            )
            
        return query.order_by(KnowledgeBaseArticle.updated_at.desc()).offset(skip).limit(limit).all()
        
    def count_articles(
        self,
        db: Session,
        *,
        category: Optional[KnowledgeBaseCategoryEnum] = None,
        tag: Optional[str] = None,
        search_term: Optional[str] = None,
        published_only: bool = True
    ) -> int:
        query = db.query(KnowledgeBaseArticle)
        
        if published_only:
            query = query.filter(KnowledgeBaseArticle.is_published == True)
            
        if category:
            query = query.filter(KnowledgeBaseArticle.category == category)
            
        if tag:
            query = query.filter(KnowledgeBaseArticle.tags.any(tag))
            
        if search_term:
            search = f"%{search_term}%"
            query = query.filter(
                or_(
                    KnowledgeBaseArticle.title.ilike(search),
                    KnowledgeBaseArticle.content.ilike(search)
                )
            )
            
        return query.count()

knowledge_base_article = CRUDKnowledgeBaseArticle(KnowledgeBaseArticle)
