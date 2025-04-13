
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.crud.base import CRUDBase
from app.models.image import Image, ImageStatusEnum, ImageTypeEnum
from app.schemas.image import ImageCreate, ImageUpdate

class CRUDImage(CRUDBase[Image, ImageCreate, ImageUpdate]):
    def get_images_by_patient(
        self, 
        db: Session, 
        *, 
        patient_id: str,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Image]:
        return (
            db.query(Image)
            .filter(Image.patient_id == patient_id)
            .order_by(Image.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
    def get_filtered_images(
        self,
        db: Session,
        *,
        patient_id: Optional[str] = None,
        image_type: Optional[ImageTypeEnum] = None,
        status: Optional[ImageStatusEnum] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Image]:
        query = db.query(Image)
        
        if patient_id:
            query = query.filter(Image.patient_id == patient_id)
            
        if image_type:
            query = query.filter(Image.image_type == image_type)
            
        if status:
            query = query.filter(Image.status == status)
            
        return query.order_by(Image.created_at.desc()).offset(skip).limit(limit).all()
        
    def count_images(
        self,
        db: Session,
        *,
        patient_id: Optional[str] = None,
        image_type: Optional[ImageTypeEnum] = None,
        status: Optional[ImageStatusEnum] = None
    ) -> int:
        query = db.query(Image)
        
        if patient_id:
            query = query.filter(Image.patient_id == patient_id)
            
        if image_type:
            query = query.filter(Image.image_type == image_type)
            
        if status:
            query = query.filter(Image.status == status)
            
        return query.count()
        
    def update_status(
        self,
        db: Session,
        *,
        image_id: str,
        status: ImageStatusEnum
    ) -> Image:
        image = self.get(db, id=image_id)
        if not image:
            return None
            
        image.status = status
        db.add(image)
        db.commit()
        db.refresh(image)
        return image

image = CRUDImage(Image)
