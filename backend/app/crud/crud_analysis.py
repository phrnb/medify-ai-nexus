
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime
from app.crud.base import CRUDBase
from app.models.analysis import Analysis, AnalysisStatusEnum, SeverityEnum
from app.schemas.analysis import AnalysisCreate, AnalysisUpdate

class CRUDAnalysis(CRUDBase[Analysis, AnalysisCreate, AnalysisUpdate]):
    def get_by_image_id(self, db: Session, *, image_id: str) -> Optional[Analysis]:
        return (
            db.query(Analysis)
            .filter(Analysis.image_id == image_id)
            .order_by(Analysis.created_at.desc())
            .first()
        )
        
    def get_analyses_by_patient(
        self,
        db: Session,
        *,
        patient_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Analysis]:
        return (
            db.query(Analysis)
            .join(Analysis.image)
            .filter(Analysis.image.patient_id == patient_id)
            .order_by(Analysis.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
    def get_filtered_analyses(
        self,
        db: Session,
        *,
        status: Optional[AnalysisStatusEnum] = None,
        severity: Optional[SeverityEnum] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Analysis]:
        query = db.query(Analysis)
        
        if status:
            query = query.filter(Analysis.status == status)
            
        if severity:
            query = query.filter(Analysis.severity == severity)
            
        if start_date:
            query = query.filter(Analysis.created_at >= start_date)
            
        if end_date:
            query = query.filter(Analysis.created_at <= end_date)
            
        return query.order_by(desc(Analysis.created_at)).offset(skip).limit(limit).all()
        
    def count_analyses(
        self,
        db: Session,
        *,
        status: Optional[AnalysisStatusEnum] = None,
        severity: Optional[SeverityEnum] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        query = db.query(Analysis)
        
        if status:
            query = query.filter(Analysis.status == status)
            
        if severity:
            query = query.filter(Analysis.severity == severity)
            
        if start_date:
            query = query.filter(Analysis.created_at >= start_date)
            
        if end_date:
            query = query.filter(Analysis.created_at <= end_date)
            
        return query.count()
        
    def verify_analysis(
        self,
        db: Session,
        *,
        analysis_id: str,
        doctor_diagnosis: str,
        severity: SeverityEnum,
        notes: Optional[str] = None,
        verified_by_id: str
    ) -> Analysis:
        analysis = self.get(db, id=analysis_id)
        if not analysis:
            return None
            
        analysis.doctor_diagnosis = doctor_diagnosis
        analysis.severity = severity
        analysis.notes = notes
        analysis.verified_by_id = verified_by_id
        analysis.verified_at = datetime.now()
        
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        return analysis

analysis = CRUDAnalysis(Analysis)
