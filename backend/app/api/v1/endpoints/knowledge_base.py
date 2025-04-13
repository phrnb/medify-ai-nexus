
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Request
from sqlalchemy.orm import Session
from app.api.v1.deps import get_db, get_current_verified_user, log_user_activity
from app.models.user import User
from app.models.activity_log import ActivityTypeEnum
from app.schemas.knowledge_base import (
    KnowledgeBaseArticle,
    KnowledgeBaseArticleCreate,
    KnowledgeBaseArticleUpdate,
    KnowledgeBaseArticleDetail,
    KnowledgeBaseCategoryEnum,
)
from app.crud.crud_knowledge_base import knowledge_base_article

router = APIRouter()

@router.get("", response_model=List[KnowledgeBaseArticle])
def read_knowledge_base_articles(
    request: Request,
    db: Session = Depends(get_db),
    category: Optional[KnowledgeBaseCategoryEnum] = Query(None, description="Filter by category"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    search: Optional[str] = Query(None, description="Search in title and content"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Retrieve knowledge base articles with optional filtering.
    """
    articles = knowledge_base_article.get_filtered_articles(
        db, category=category, tag=tag, search_term=search, skip=skip, limit=limit
    )
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.view,
        description=f"User viewed knowledge base articles list",
        resource_type="knowledge_base_article"
    )
    
    return articles

@router.post("", response_model=KnowledgeBaseArticle)
def create_knowledge_base_article(
    request: Request,
    *,
    db: Session = Depends(get_db),
    article_in: KnowledgeBaseArticleCreate,
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Create new knowledge base article.
    """
    article = knowledge_base_article.create_with_user(
        db, obj_in=article_in, created_by=current_user.id
    )
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.create,
        description=f"User created knowledge base article: {article.title}",
        resource_type="knowledge_base_article",
        resource_id=article.id
    )
    
    return article

@router.get("/{article_id}", response_model=KnowledgeBaseArticleDetail)
def read_knowledge_base_article(
    request: Request,
    *,
    db: Session = Depends(get_db),
    article_id: str = Path(...),
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Get specific knowledge base article by ID.
    """
    article = knowledge_base_article.get(db, id=article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base article not found",
        )
    
    # Create detailed response
    article_detail = KnowledgeBaseArticleDetail.from_orm(article)
    
    # Add additional info
    if article.creator:
        article_detail.created_by_name = article.creator.full_name
    if article.updater:
        article_detail.updated_by_name = article.updater.full_name
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.view,
        description=f"User viewed knowledge base article: {article.title}",
        resource_type="knowledge_base_article",
        resource_id=article.id
    )
    
    return article_detail

@router.put("/{article_id}", response_model=KnowledgeBaseArticle)
def update_knowledge_base_article(
    request: Request,
    *,
    db: Session = Depends(get_db),
    article_id: str = Path(...),
    article_in: KnowledgeBaseArticleUpdate,
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Update a knowledge base article.
    """
    article = knowledge_base_article.get(db, id=article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base article not found",
        )
    
    # Update with the current user as updater
    article_in_dict = article_in.dict(exclude_unset=True)
    article_in_dict["updated_by"] = current_user.id
    
    article = knowledge_base_article.update(db, db_obj=article, obj_in=article_in_dict)
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.update,
        description=f"User updated knowledge base article: {article.title}",
        resource_type="knowledge_base_article",
        resource_id=article.id
    )
    
    return article

@router.delete("/{article_id}", response_model=KnowledgeBaseArticle)
def delete_knowledge_base_article(
    request: Request,
    *,
    db: Session = Depends(get_db),
    article_id: str = Path(...),
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Delete a knowledge base article.
    """
    article = knowledge_base_article.get(db, id=article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base article not found",
        )
    
    # Check if user has permission to delete articles (admins only)
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete knowledge base articles",
        )
    
    article = knowledge_base_article.remove(db, id=article_id)
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.delete,
        description=f"User deleted knowledge base article: {article.title}",
        resource_type="knowledge_base_article",
        resource_id=article.id
    )
    
    return article
