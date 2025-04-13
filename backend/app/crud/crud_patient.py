
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.crud.base import CRUDBase
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate

class CRUDPatient(CRUDBase[Patient, PatientCreate, PatientUpdate]):
    def get_by_medical_record_number(self, db: Session, *, mrn: str) -> Optional[Patient]:
        return db.query(Patient).filter(Patient.medical_record_number == mrn).first()
        
    def get_active_patients(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Patient]:
        return db.query(Patient).filter(Patient.is_active == True).offset(skip).limit(limit).all()
        
    def search_patients(
        self, 
        db: Session, 
        *, 
        search_term: str, 
        is_active: Optional[bool] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Patient]:
        query = db.query(Patient)
        
        if search_term:
            search = f"%{search_term}%"
            query = query.filter(
                or_(
                    Patient.first_name.ilike(search),
                    Patient.last_name.ilike(search),
                    Patient.medical_record_number.ilike(search),
                    Patient.email.ilike(search)
                )
            )
            
        if is_active is not None:
            query = query.filter(Patient.is_active == is_active)
            
        return query.offset(skip).limit(limit).all()
        
    def count_patients(
        self, 
        db: Session, 
        *, 
        search_term: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> int:
        query = db.query(Patient)
        
        if search_term:
            search = f"%{search_term}%"
            query = query.filter(
                or_(
                    Patient.first_name.ilike(search),
                    Patient.last_name.ilike(search),
                    Patient.medical_record_number.ilike(search),
                    Patient.email.ilike(search)
                )
            )
            
        if is_active is not None:
            query = query.filter(Patient.is_active == is_active)
            
        return query.count()
        
    def change_status(self, db: Session, *, patient_id: str, is_active: bool) -> Patient:
        patient = self.get(db, id=patient_id)
        if not patient:
            return None
            
        patient.is_active = is_active
        db.add(patient)
        db.commit()
        db.refresh(patient)
        return patient

patient = CRUDPatient(Patient)
