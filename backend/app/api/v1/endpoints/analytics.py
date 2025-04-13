
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, cast, Date
import json
from datetime import datetime, timedelta

from app.api.v1.deps import get_db, get_current_verified_user, get_current_active_superuser, log_user_activity
from app.models.user import User
from app.models.activity_log import ActivityTypeEnum
from app.models.patient import Patient, GenderEnum
from app.models.analysis import Analysis, SeverityEnum
from app.models.image import Image, ImageTypeEnum
from app.models.model_version import ModelVersion

router = APIRouter()

@router.get("/patient-stats", response_model=Dict)
def get_patient_statistics(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Get patient statistics.
    """
    # Total patients
    total_patients = db.query(func.count(Patient.id)).scalar()
    
    # Active patients
    active_patients = db.query(func.count(Patient.id)).filter(Patient.is_active == True).scalar()
    
    # Gender distribution
    gender_distribution = (
        db.query(
            Patient.gender,
            func.count(Patient.id).label("count")
        )
        .group_by(Patient.gender)
        .all()
    )
    gender_stats = {gender: count for gender, count in gender_distribution}
    
    # Patients by age group
    current_date = datetime.now().date()
    patients_by_age = []
    
    age_ranges = [
        (0, 18, "0-18"),
        (19, 30, "19-30"),
        (31, 45, "31-45"),
        (46, 60, "46-60"),
        (61, 75, "61-75"),
        (76, 200, "76+")
    ]
    
    for min_age, max_age, label in age_ranges:
        min_date = current_date - timedelta(days=max_age*365)
        max_date = current_date - timedelta(days=min_age*365)
        
        count = (
            db.query(func.count(Patient.id))
            .filter(Patient.date_of_birth <= max_date, Patient.date_of_birth >= min_date)
            .scalar()
        )
        
        patients_by_age.append({
            "age_group": label,
            "count": count
        })
    
    # Recent patient registrations (by month for the last 6 months)
    six_months_ago = datetime.now() - timedelta(days=180)
    
    monthly_registrations = (
        db.query(
            func.date_trunc('month', Patient.created_at).label('month'),
            func.count(Patient.id).label('count')
        )
        .filter(Patient.created_at >= six_months_ago)
        .group_by('month')
        .order_by('month')
        .all()
    )
    
    registrations_by_month = [
        {"month": month.strftime("%Y-%m"), "count": count}
        for month, count in monthly_registrations
    ]
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.view,
        description=f"User viewed patient statistics",
        resource_type="analytics"
    )
    
    return {
        "total_patients": total_patients,
        "active_patients": active_patients,
        "inactive_patients": total_patients - active_patients,
        "gender_distribution": gender_stats,
        "patients_by_age": patients_by_age,
        "registrations_by_month": registrations_by_month
    }

@router.get("/analysis-stats", response_model=Dict)
def get_analysis_statistics(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Get analysis statistics.
    """
    # Total analyses
    total_analyses = db.query(func.count(Analysis.id)).scalar()
    
    # Analyses by status
    analyses_by_status = (
        db.query(
            Analysis.status,
            func.count(Analysis.id).label("count")
        )
        .group_by(Analysis.status)
        .all()
    )
    status_stats = {status.value: count for status, count in analyses_by_status}
    
    # Analyses by severity
    analyses_by_severity = (
        db.query(
            Analysis.severity,
            func.count(Analysis.id).label("count")
        )
        .filter(Analysis.severity.isnot(None))
        .group_by(Analysis.severity)
        .all()
    )
    severity_stats = {severity.value: count for severity, count in analyses_by_severity}
    
    # Analyses over time (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    daily_analyses = (
        db.query(
            cast(Analysis.created_at, Date).label('date'),
            func.count(Analysis.id).label('count')
        )
        .filter(Analysis.created_at >= thirty_days_ago)
        .group_by('date')
        .order_by('date')
        .all()
    )
    
    analyses_by_day = [
        {"date": date.strftime("%Y-%m-%d"), "count": count}
        for date, count in daily_analyses
    ]
    
    # Top diagnoses
    top_diagnoses = (
        db.query(
            Analysis.doctor_diagnosis,
            func.count(Analysis.id).label("count")
        )
        .filter(Analysis.doctor_diagnosis.isnot(None))
        .group_by(Analysis.doctor_diagnosis)
        .order_by(desc("count"))
        .limit(10)
        .all()
    )
    
    diagnoses_stats = [
        {"diagnosis": diagnosis, "count": count}
        for diagnosis, count in top_diagnoses
    ]
    
    # AI vs Doctor diagnosis agreement rate
    agreement_query = (
        db.query(
            func.count(Analysis.id).label("matching"),
            func.count().label("total")
        )
        .filter(
            Analysis.ai_diagnosis.isnot(None),
            Analysis.doctor_diagnosis.isnot(None)
        )
    )
    
    matching_diagnoses = (
        agreement_query
        .filter(func.lower(Analysis.ai_diagnosis) == func.lower(Analysis.doctor_diagnosis))
        .first()
    )
    
    total_paired_diagnoses = agreement_query.first()
    
    agreement_rate = 0
    if total_paired_diagnoses and total_paired_diagnoses.total > 0:
        agreement_rate = (matching_diagnoses.matching / total_paired_diagnoses.total) * 100
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.view,
        description=f"User viewed analysis statistics",
        resource_type="analytics"
    )
    
    return {
        "total_analyses": total_analyses,
        "analyses_by_status": status_stats,
        "analyses_by_severity": severity_stats,
        "analyses_by_day": analyses_by_day,
        "top_diagnoses": diagnoses_stats,
        "ai_doctor_agreement": {
            "agreement_rate": round(agreement_rate, 2),
            "total_paired_diagnoses": total_paired_diagnoses.total if total_paired_diagnoses else 0
        }
    }

@router.get("/image-stats", response_model=Dict)
def get_image_statistics(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Get image statistics.
    """
    # Total images
    total_images = db.query(func.count(Image.id)).scalar()
    
    # Images by type
    images_by_type = (
        db.query(
            Image.image_type,
            func.count(Image.id).label("count")
        )
        .group_by(Image.image_type)
        .all()
    )
    type_stats = {image_type.value: count for image_type, count in images_by_type}
    
    # Images by status
    images_by_status = (
        db.query(
            Image.status,
            func.count(Image.id).label("count")
        )
        .group_by(Image.status)
        .all()
    )
    status_stats = {status.value: count for status, count in images_by_status}
    
    # Images uploaded over time (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    daily_uploads = (
        db.query(
            cast(Image.created_at, Date).label('date'),
            func.count(Image.id).label('count')
        )
        .filter(Image.created_at >= thirty_days_ago)
        .group_by('date')
        .order_by('date')
        .all()
    )
    
    uploads_by_day = [
        {"date": date.strftime("%Y-%m-%d"), "count": count}
        for date, count in daily_uploads
    ]
    
    # Average file size
    avg_file_size = db.query(func.avg(Image.file_size)).scalar()
    avg_file_size_mb = round(avg_file_size / (1024 * 1024), 2) if avg_file_size else 0
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.view,
        description=f"User viewed image statistics",
        resource_type="analytics"
    )
    
    return {
        "total_images": total_images,
        "images_by_type": type_stats,
        "images_by_status": status_stats,
        "uploads_by_day": uploads_by_day,
        "average_file_size_mb": avg_file_size_mb
    }

@router.get("/user-stats", response_model=Dict)
def get_user_statistics(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Get user statistics (admin only).
    """
    # Total users
    total_users = db.query(func.count(User.id)).scalar()
    
    # Active users
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
    
    # Users by role
    users_by_role = (
        db.query(
            User.role,
            func.count(User.id).label("count")
        )
        .group_by(User.role)
        .all()
    )
    role_stats = {role: count for role, count in users_by_role}
    
    # New users over time (last 6 months)
    six_months_ago = datetime.now() - timedelta(days=180)
    
    monthly_registrations = (
        db.query(
            func.date_trunc('month', User.created_at).label('month'),
            func.count(User.id).label('count')
        )
        .filter(User.created_at >= six_months_ago)
        .group_by('month')
        .order_by('month')
        .all()
    )
    
    registrations_by_month = [
        {"month": month.strftime("%Y-%m"), "count": count}
        for month, count in monthly_registrations
    ]
    
    # User activity (last 30 days)
    from app.models.activity_log import ActivityLog
    
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    activity_by_type = (
        db.query(
            ActivityLog.activity_type,
            func.count(ActivityLog.id).label("count")
        )
        .filter(ActivityLog.created_at >= thirty_days_ago)
        .group_by(ActivityLog.activity_type)
        .all()
    )
    
    activity_stats = {activity_type.value: count for activity_type, count in activity_by_type}
    
    # Most active users
    most_active_users = (
        db.query(
            User.id,
            User.email,
            User.full_name,
            func.count(ActivityLog.id).label("activity_count")
        )
        .join(ActivityLog, User.id == ActivityLog.user_id)
        .filter(ActivityLog.created_at >= thirty_days_ago)
        .group_by(User.id, User.email, User.full_name)
        .order_by(desc("activity_count"))
        .limit(10)
        .all()
    )
    
    active_users_stats = [
        {"id": user_id, "email": email, "name": name, "activity_count": count}
        for user_id, email, name, count in most_active_users
    ]
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.view,
        description=f"Admin viewed user statistics",
        resource_type="analytics"
    )
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": total_users - active_users,
        "users_by_role": role_stats,
        "registrations_by_month": registrations_by_month,
        "activity_by_type": activity_stats,
        "most_active_users": active_users_stats
    }

@router.get("/ai-model-stats", response_model=Dict)
def get_ai_model_statistics(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Get AI model statistics.
    """
    # Model versions
    model_versions = (
        db.query(ModelVersion)
        .order_by(desc(ModelVersion.deployed_at))
        .all()
    )
    
    versions_data = [
        {
            "id": model.id,
            "version": model.version,
            "name": model.name,
            "accuracy": model.accuracy,
            "is_active": model.is_active,
            "deployed_at": model.deployed_at.strftime("%Y-%m-%d") if model.deployed_at else None
        }
        for model in model_versions
    ]
    
    # Performance by image type
    performance_by_type = []
    
    for image_type in ImageTypeEnum:
        # Get analyses for this image type with both AI and doctor diagnoses
        image_type_analyses = (
            db.query(
                func.count(Analysis.id).label("matching"),
                func.count().label("total")
            )
            .join(Image, Analysis.image_id == Image.id)
            .filter(
                Image.image_type == image_type,
                Analysis.ai_diagnosis.isnot(None),
                Analysis.doctor_diagnosis.isnot(None)
            )
        )
        
        # Count matches
        matching_diagnoses = (
            image_type_analyses
            .filter(func.lower(Analysis.ai_diagnosis) == func.lower(Analysis.doctor_diagnosis))
            .first()
        )
        
        total_analyses = image_type_analyses.first()
        
        accuracy = 0
        if total_analyses and total_analyses.total > 0:
            accuracy = (matching_diagnoses.matching / total_analyses.total) * 100
        
        # Only include if there's data
        if total_analyses and total_analyses.total > 0:
            performance_by_type.append({
                "image_type": image_type.value,
                "accuracy": round(accuracy, 2),
                "total_analyses": total_analyses.total
            })
    
    # Performance by severity
    performance_by_severity = []
    
    for severity in SeverityEnum:
        # Only analyze cases where AI returned this severity
        severity_analyses = (
            db.query(
                func.count(Analysis.id).label("matching"),
                func.count().label("total")
            )
            .filter(
                Analysis.severity == severity,
                Analysis.ai_diagnosis.isnot(None),
                Analysis.doctor_diagnosis.isnot(None)
            )
        )
        
        # Count matches
        matching_diagnoses = (
            severity_analyses
            .filter(func.lower(Analysis.ai_diagnosis) == func.lower(Analysis.doctor_diagnosis))
            .first()
        )
        
        total_analyses = severity_analyses.first()
        
        accuracy = 0
        if total_analyses and total_analyses.total > 0:
            accuracy = (matching_diagnoses.matching / total_analyses.total) * 100
        
        # Only include if there's data
        if total_analyses and total_analyses.total > 0:
            performance_by_severity.append({
                "severity": severity.value,
                "accuracy": round(accuracy, 2),
                "total_analyses": total_analyses.total
            })
    
    # AI confidence distribution
    confidence_ranges = [
        (0.0, 0.5, "0-50%"),
        (0.5, 0.7, "50-70%"),
        (0.7, 0.85, "70-85%"),
        (0.85, 0.95, "85-95%"),
        (0.95, 1.0, "95-100%")
    ]
    
    confidence_distribution = []
    
    for min_conf, max_conf, label in confidence_ranges:
        count = (
            db.query(func.count(Analysis.id))
            .filter(Analysis.confidence >= min_conf, Analysis.confidence <= max_conf)
            .scalar()
        )
        
        # Calculate accuracy for this range
        range_analyses = (
            db.query(
                func.count(Analysis.id).label("matching"),
                func.count().label("total")
            )
            .filter(
                Analysis.confidence >= min_conf, 
                Analysis.confidence <= max_conf,
                Analysis.ai_diagnosis.isnot(None),
                Analysis.doctor_diagnosis.isnot(None)
            )
        )
        
        matching = (
            range_analyses
            .filter(func.lower(Analysis.ai_diagnosis) == func.lower(Analysis.doctor_diagnosis))
            .first()
        )
        
        total = range_analyses.first()
        
        accuracy = 0
        if total and total.total > 0:
            accuracy = (matching.matching / total.total) * 100
        
        confidence_distribution.append({
            "range": label,
            "count": count,
            "accuracy": round(accuracy, 2)
        })
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.view,
        description=f"User viewed AI model statistics",
        resource_type="analytics"
    )
    
    return {
        "model_versions": versions_data,
        "performance_by_image_type": performance_by_type,
        "performance_by_severity": performance_by_severity,
        "confidence_distribution": confidence_distribution
    }
