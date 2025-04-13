
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime
from app.crud.base import CRUDBase
from app.models.report import Report, ReportStatusEnum, ReportFormatEnum
from app.models.report_history import ReportHistory
from app.schemas.report import ReportCreate, ReportUpdate

class CRUDReport(CRUDBase[Report, ReportCreate, ReportUpdate]):
    def get_reports_by_patient(
        self,
        db: Session,
        *,
        patient_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Report]:
        return (
            db.query(Report)
            .filter(Report.patient_id == patient_id)
            .order_by(desc(Report.updated_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
        
    def get_reports_by_doctor(
        self,
        db: Session,
        *,
        doctor_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Report]:
        return (
            db.query(Report)
            .filter(Report.doctor_id == doctor_id)
            .order_by(desc(Report.updated_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
        
    def get_filtered_reports(
        self,
        db: Session,
        *,
        status: Optional[ReportStatusEnum] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        patient_id: Optional[str] = None,
        doctor_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Report]:
        query = db.query(Report)
        
        if status:
            query = query.filter(Report.status == status)
            
        if start_date:
            query = query.filter(Report.created_at >= start_date)
            
        if end_date:
            query = query.filter(Report.created_at <= end_date)
            
        if patient_id:
            query = query.filter(Report.patient_id == patient_id)
            
        if doctor_id:
            query = query.filter(Report.doctor_id == doctor_id)
            
        return query.order_by(desc(Report.updated_at)).offset(skip).limit(limit).all()
        
    def count_reports(
        self,
        db: Session,
        *,
        status: Optional[ReportStatusEnum] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        patient_id: Optional[str] = None,
        doctor_id: Optional[str] = None
    ) -> int:
        query = db.query(Report)
        
        if status:
            query = query.filter(Report.status == status)
            
        if start_date:
            query = query.filter(Report.created_at >= start_date)
            
        if end_date:
            query = query.filter(Report.created_at <= end_date)
            
        if patient_id:
            query = query.filter(Report.patient_id == patient_id)
            
        if doctor_id:
            query = query.filter(Report.doctor_id == doctor_id)
            
        return query.count()
        
    def finalize_report(
        self,
        db: Session,
        *,
        report_id: str,
        notes: Optional[str] = None
    ) -> Report:
        report = self.get(db, id=report_id)
        if not report:
            return None
            
        # Change status to final
        report.status = ReportStatusEnum.final
        report.finalized_at = datetime.now()
        
        db.add(report)
        db.commit()
        db.refresh(report)
        return report
        
    def add_report_history(
        self,
        db: Session,
        *,
        report_id: str,
        user_id: str,
        changes: Dict,
        previous_content: Optional[str] = None,
        notes: Optional[str] = None
    ) -> ReportHistory:
        history_entry = ReportHistory(
            report_id=report_id,
            user_id=user_id,
            changes=changes,
            previous_content=previous_content,
            notes=notes
        )
        
        db.add(history_entry)
        db.commit()
        db.refresh(history_entry)
        return history_entry
        
    def get_report_history(
        self,
        db: Session,
        *,
        report_id: str
    ) -> List[ReportHistory]:
        return (
            db.query(ReportHistory)
            .filter(ReportHistory.report_id == report_id)
            .order_by(desc(ReportHistory.created_at))
            .all()
        )

report = CRUDReport(Report)
