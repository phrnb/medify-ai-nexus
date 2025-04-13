
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Path
from sqlalchemy.orm import Session
from app.api.v1.deps import get_db, get_current_verified_user, log_user_activity
from app.crud.crud_patient import patient as crud_patient
from app.models.user import User
from app.models.activity_log import ActivityTypeEnum
from app.schemas.patient import Patient, PatientCreate, PatientUpdate, PatientDetail

router = APIRouter()

@router.get("", response_model=List[Patient])
def read_patients(
    request: Request,
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search by name or MRN"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Retrieve patients with optional filtering.
    """
    patients = crud_patient.search_patients(
        db, search_term=search, is_active=is_active, skip=skip, limit=limit
    )
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.view,
        description=f"User viewed patient list",
        resource_type="patient"
    )
    
    return patients

@router.post("", response_model=Patient)
def create_patient(
    request: Request,
    *,
    db: Session = Depends(get_db),
    patient_in: PatientCreate,
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Create new patient.
    """
    # Check if patient with this MRN already exists
    existing_patient = crud_patient.get_by_medical_record_number(
        db, mrn=patient_in.medical_record_number
    )
    if existing_patient:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A patient with this medical record number already exists",
        )
    
    # Create patient
    patient = crud_patient.create(db, obj_in=patient_in)
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.create,
        description=f"User created patient: {patient.first_name} {patient.last_name}",
        resource_type="patient",
        resource_id=patient.id
    )
    
    return patient

@router.get("/{patient_id}", response_model=PatientDetail)
def read_patient(
    request: Request,
    *,
    db: Session = Depends(get_db),
    patient_id: str = Path(...),
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Get specific patient by ID.
    """
    patient = crud_patient.get(db, id=patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.view,
        description=f"User viewed patient: {patient.first_name} {patient.last_name}",
        resource_type="patient",
        resource_id=patient.id
    )
    
    return patient

@router.put("/{patient_id}", response_model=Patient)
def update_patient(
    request: Request,
    *,
    db: Session = Depends(get_db),
    patient_id: str = Path(...),
    patient_in: PatientUpdate,
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Update a patient.
    """
    patient = crud_patient.get(db, id=patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
    
    # Update patient
    patient = crud_patient.update(db, db_obj=patient, obj_in=patient_in)
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.update,
        description=f"User updated patient: {patient.first_name} {patient.last_name}",
        resource_type="patient",
        resource_id=patient.id
    )
    
    return patient

@router.put("/{patient_id}/status", response_model=Patient)
def update_patient_status(
    request: Request,
    *,
    db: Session = Depends(get_db),
    patient_id: str = Path(...),
    is_active: bool,
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Update patient active status.
    """
    patient = crud_patient.get(db, id=patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
    
    # Change status
    patient = crud_patient.change_status(db, patient_id=patient_id, is_active=is_active)
    
    # Log the activity
    status_str = "active" if is_active else "inactive"
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.update,
        description=f"User changed patient status to {status_str}: {patient.first_name} {patient.last_name}",
        resource_type="patient",
        resource_id=patient.id
    )
    
    return patient
