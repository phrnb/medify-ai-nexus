
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Path, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import uuid
from PIL import Image as PILImage
import shutil
from datetime import datetime

from app.api.v1.deps import get_db, get_current_verified_user, log_user_activity
from app.crud.crud_image import image as crud_image
from app.crud.crud_patient import patient as crud_patient
from app.models.user import User
from app.models.activity_log import ActivityTypeEnum
from app.models.image import ImageTypeEnum, ImageStatusEnum
from app.schemas.image import Image, ImageCreate, ImageUpdate, ImageDetail
from app.core.config import settings

router = APIRouter()

def validate_image(file: UploadFile) -> tuple:
    """Validate uploaded image file"""
    # Check file size
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > settings.MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_IMAGE_SIZE_MB}MB"
        )
    
    # Check file type
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_IMAGE_TYPES)}"
        )
    
    # Get image dimensions if it's a standard image format
    width = None
    height = None
    if file.content_type in ["image/jpeg", "image/png"]:
        try:
            img = PILImage.open(file.file)
            width, height = img.size
            file.file.seek(0)  # Reset file pointer after reading
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image file: {str(e)}"
            )
    
    return file_size, width, height

def create_thumbnail(source_path: str, thumbnail_path: str, size=(200, 200)):
    """Create a thumbnail for an image"""
    try:
        img = PILImage.open(source_path)
        img.thumbnail(size)
        img.save(thumbnail_path)
        return True
    except Exception:
        return False

@router.get("", response_model=List[Image])
def read_images(
    request: Request,
    db: Session = Depends(get_db),
    patient_id: Optional[str] = Query(None, description="Filter by patient ID"),
    image_type: Optional[ImageTypeEnum] = Query(None, description="Filter by image type"),
    status: Optional[ImageStatusEnum] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Retrieve images with optional filtering.
    """
    images = crud_image.get_filtered_images(
        db, 
        patient_id=patient_id, 
        image_type=image_type, 
        status=status, 
        skip=skip, 
        limit=limit
    )
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.view,
        description=f"User viewed image list",
        resource_type="image"
    )
    
    return images

@router.post("", response_model=Image)
def upload_image(
    request: Request,
    *,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    patient_id: str = Form(...),
    image_type: ImageTypeEnum = Form(...),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Upload a new image for a patient.
    """
    # Check if patient exists
    patient = crud_patient.get(db, id=patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
    
    # Validate image
    file_size, width, height = validate_image(file)
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    
    # Set up file paths
    file_path = os.path.join(settings.UPLOAD_DIR, "images", unique_filename)
    thumbnail_path = os.path.join(settings.UPLOAD_DIR, "images", f"thumb_{unique_filename}")
    
    # Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create thumbnail if it's a standard image
    thumbnail_relative_path = None
    if file.content_type in ["image/jpeg", "image/png"]:
        if create_thumbnail(file_path, thumbnail_path):
            thumbnail_relative_path = f"static/uploads/images/thumb_{unique_filename}"
    
    # Create image record
    image_in = ImageCreate(
        patient_id=patient_id,
        image_type=image_type,
        description=description,
        original_filename=file.filename,
        file_size=file_size,
        mime_type=file.content_type,
        width=width,
        height=height,
    )
    
    image = crud_image.create(
        db, 
        obj_in=image_in
    )
    
    # Update the file path
    image.file_path = f"static/uploads/images/{unique_filename}"
    if thumbnail_relative_path:
        image.thumbnail_path = thumbnail_relative_path
    image.uploaded_by = current_user.id
    
    db.add(image)
    db.commit()
    db.refresh(image)
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.create,
        description=f"User uploaded image: {file.filename}",
        resource_type="image",
        resource_id=image.id
    )
    
    return image

@router.get("/{image_id}", response_model=ImageDetail)
def read_image(
    request: Request,
    *,
    db: Session = Depends(get_db),
    image_id: str = Path(...),
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Get specific image by ID.
    """
    image = crud_image.get(db, id=image_id)
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found",
        )
    
    # Get patient name and uploader name
    image_detail = ImageDetail.from_orm(image)
    if image.patient:
        image_detail.patient_name = f"{image.patient.first_name} {image.patient.last_name}"
    if image.uploader:
        image_detail.uploaded_by_name = image.uploader.full_name
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.view,
        description=f"User viewed image details: {image.original_filename}",
        resource_type="image",
        resource_id=image.id
    )
    
    return image_detail

@router.put("/{image_id}", response_model=Image)
def update_image(
    request: Request,
    *,
    db: Session = Depends(get_db),
    image_id: str = Path(...),
    image_in: ImageUpdate,
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Update image metadata.
    """
    image = crud_image.get(db, id=image_id)
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found",
        )
    
    # Update image
    image = crud_image.update(db, db_obj=image, obj_in=image_in)
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.update,
        description=f"User updated image metadata: {image.original_filename}",
        resource_type="image",
        resource_id=image.id
    )
    
    return image

@router.get("/{image_id}/file")
def get_image_file(
    request: Request,
    *,
    db: Session = Depends(get_db),
    image_id: str = Path(...),
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Get the image file.
    """
    image = crud_image.get(db, id=image_id)
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found",
        )
    
    file_path = image.file_path
    if not os.path.isfile(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image file not found on server",
        )
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.download,
        description=f"User downloaded image file: {image.original_filename}",
        resource_type="image",
        resource_id=image.id
    )
    
    return FileResponse(file_path, filename=image.original_filename)

@router.get("/{image_id}/thumbnail")
def get_image_thumbnail(
    *,
    db: Session = Depends(get_db),
    image_id: str = Path(...),
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Get the image thumbnail.
    """
    image = crud_image.get(db, id=image_id)
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found",
        )
    
    if not image.thumbnail_path:
        # If no thumbnail, return the original image
        file_path = image.file_path
        if not os.path.isfile(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image file not found on server",
            )
        return FileResponse(file_path)
    
    file_path = image.thumbnail_path
    if not os.path.isfile(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thumbnail file not found on server",
        )
    
    return FileResponse(file_path)
