
from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Path, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session
import os
import uuid
import json
from datetime import datetime, timedelta
import jinja2
from weasyprint import HTML
import difflib

from app.api.v1.deps import get_db, get_current_verified_user, log_user_activity
from app.crud.crud_report import report as crud_report
from app.crud.crud_patient import patient as crud_patient
from app.crud.crud_analysis import analysis as crud_analysis
from app.models.user import User
from app.models.activity_log import ActivityTypeEnum
from app.models.report import ReportStatusEnum, ReportFormatEnum
from app.schemas.report import Report, ReportCreate, ReportUpdate, ReportDetail, ReportFinalize, ReportHistoryEntry
from app.core.config import settings

router = APIRouter()

# Set up Jinja2 environment for HTML templates
template_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("app/templates")
)

def generate_report_pdf(report_id: str, db: Session) -> Optional[str]:
    """Generate PDF from a report"""
    report = crud_report.get(db, id=report_id)
    if not report:
        return None
    
    # Generate a unique filename
    filename = f"{uuid.uuid4()}.pdf"
    output_path = os.path.join(settings.UPLOAD_DIR, "reports", filename)
    
    try:
        # Create temporary HTML file
        temp_html_path = os.path.join("static/temp", f"{uuid.uuid4()}.html")
        
        # Get report data
        patient = report.patient
        doctor = report.doctor
        analysis = report.analysis
        
        # Prepare context for template
        context = {
            "report": report,
            "patient": {
                "name": f"{patient.first_name} {patient.last_name}",
                "id": patient.id,
                "mrn": patient.medical_record_number,
                "gender": patient.gender,
                "date_of_birth": patient.date_of_birth.strftime("%Y-%m-%d"),
                "age": (datetime.now().date() - patient.date_of_birth).days // 365,
            },
            "doctor": {
                "name": doctor.full_name,
                "id": doctor.id,
                "specialty": doctor.specialty,
            },
            "created_at": report.created_at.strftime("%Y-%m-%d %H:%M"),
            "updated_at": report.updated_at.strftime("%Y-%m-%d %H:%M") if report.updated_at else None,
            "finalized_at": report.finalized_at.strftime("%Y-%m-%d %H:%M") if report.finalized_at else None,
            "content": report.content,
            "title": report.title,
            "status": report.status,
        }
        
        if analysis:
            context["analysis"] = {
                "id": analysis.id,
                "ai_diagnosis": analysis.ai_diagnosis,
                "doctor_diagnosis": analysis.doctor_diagnosis,
                "confidence": f"{analysis.confidence*100:.1f}%" if analysis.confidence else None,
                "severity": analysis.severity,
                "created_at": analysis.created_at.strftime("%Y-%m-%d %H:%M"),
            }
        
        # Render template to HTML
        # Note: In a real app, you'd have an actual template file
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{report.title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                .header {{ border-bottom: 1px solid #ccc; padding-bottom: 10px; margin-bottom: 20px; }}
                .patient-info {{ margin-bottom: 20px; }}
                .report-content {{ margin-bottom: 30px; }}
                .footer {{ border-top: 1px solid #ccc; padding-top: 10px; font-size: 0.8em; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{report.title}</h1>
                <p>Report ID: {report.id}</p>
                <p>Status: {report.status}</p>
            </div>
            
            <div class="patient-info">
                <h2>Patient Information</h2>
                <table>
                    <tr><th>Name</th><td>{context['patient']['name']}</td></tr>
                    <tr><th>MRN</th><td>{context['patient']['mrn']}</td></tr>
                    <tr><th>Gender</th><td>{context['patient']['gender']}</td></tr>
                    <tr><th>Date of Birth</th><td>{context['patient']['date_of_birth']}</td></tr>
                    <tr><th>Age</th><td>{context['patient']['age']}</td></tr>
                </table>
            </div>
            
            <div class="report-content">
                <h2>Report Content</h2>
                {report.content}
            </div>
            
            {'<div class="analysis-info"><h2>Analysis Information</h2><table>' +
            '<tr><th>AI Diagnosis</th><td>' + context['analysis']['ai_diagnosis'] + '</td></tr>' +
            '<tr><th>Doctor Diagnosis</th><td>' + context['analysis']['doctor_diagnosis'] + '</td></tr>' +
            '<tr><th>Confidence</th><td>' + (context['analysis']['confidence'] or 'N/A') + '</td></tr>' +
            '<tr><th>Severity</th><td>' + (context['analysis']['severity'] or 'N/A') + '</td></tr>' +
            '</table></div>' if 'analysis' in context else ''}
            
            <div class="footer">
                <p>Generated by: {context['doctor']['name']}, {context['doctor']['specialty']}</p>
                <p>Created: {context['created_at']}</p>
                {'<p>Updated: ' + context['updated_at'] + '</p>' if context['updated_at'] else ''}
                {'<p>Finalized: ' + context['finalized_at'] + '</p>' if context['finalized_at'] else ''}
            </div>
        </body>
        </html>
        """
        
        with open(temp_html_path, "w") as f:
            f.write(html_content)
        
        # Convert HTML to PDF
        HTML(filename=temp_html_path).write_pdf(output_path)
        
        # Clean up temp file
        if os.path.exists(temp_html_path):
            os.remove(temp_html_path)
        
        # Update report with file path
        report.file_path = f"static/uploads/reports/{filename}"
        report.format = ReportFormatEnum.pdf
        db.add(report)
        db.commit()
        
        return report.file_path
        
    except Exception as e:
        # Handle errors
        print(f"Error generating PDF: {str(e)}")
        return None

def compute_diff(old_content: str, new_content: str) -> Dict:
    """Compute the difference between old and new content"""
    diff = difflib.ndiff(old_content.splitlines(), new_content.splitlines())
    changes = {
        "added": [],
        "removed": [],
        "modified": []
    }
    
    for line in diff:
        if line.startswith('+ '):
            changes["added"].append(line[2:])
        elif line.startswith('- '):
            changes["removed"].append(line[2:])
        elif line.startswith('? '):
            continue
        else:
            # Unchanged lines don't need to be tracked
            pass
    
    return changes

@router.get("", response_model=List[Report])
def read_reports(
    request: Request,
    db: Session = Depends(get_db),
    status: Optional[ReportStatusEnum] = Query(None, description="Filter by status"),
    patient_id: Optional[str] = Query(None, description="Filter by patient ID"),
    doctor_id: Optional[str] = Query(None, description="Filter by doctor ID"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Retrieve reports with optional filtering.
    """
    # If not specified, use current user as doctor filter
    if not doctor_id and not current_user.is_superuser:
        doctor_id = current_user.id
        
    reports = crud_report.get_filtered_reports(
        db, 
        status=status, 
        patient_id=patient_id, 
        doctor_id=doctor_id,
        start_date=start_date, 
        end_date=end_date, 
        skip=skip, 
        limit=limit
    )
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.view,
        description=f"User viewed reports list",
        resource_type="report"
    )
    
    return reports

@router.post("", response_model=Report)
def create_report(
    request: Request,
    *,
    db: Session = Depends(get_db),
    report_in: ReportCreate,
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Create a new report.
    """
    # Validate patient exists
    patient = crud_patient.get(db, id=report_in.patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
    
    # Validate analysis if provided
    if report_in.analysis_id:
        analysis = crud_analysis.get(db, id=report_in.analysis_id)
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found",
            )
    
    # Set the current user as doctor if not provided
    if not report_in.doctor_id:
        report_in.doctor_id = current_user.id
    
    # Only allow superusers to create reports for other doctors
    if report_in.doctor_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create reports for other doctors",
        )
    
    # Create report
    report = crud_report.create(db, obj_in=report_in)
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.create,
        description=f"User created report: {report.title}",
        resource_type="report",
        resource_id=report.id
    )
    
    return report

@router.get("/{report_id}", response_model=ReportDetail)
def read_report(
    request: Request,
    *,
    db: Session = Depends(get_db),
    report_id: str = Path(...),
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Get specific report by ID.
    """
    report = crud_report.get(db, id=report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    
    # Only allow access to own reports unless superuser
    if report.doctor_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this report",
        )
    
    # Get report history
    history = crud_report.get_report_history(db, report_id=report_id)
    
    # Create detailed response
    report_detail = ReportDetail.from_orm(report)
    
    # Add additional info
    if report.patient:
        report_detail.patient_name = f"{report.patient.first_name} {report.patient.last_name}"
    
    if report.doctor:
        report_detail.doctor_name = report.doctor.full_name
    
    # Add history
    report_detail.history = [ReportHistoryEntry.from_orm(h) for h in history]
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.view,
        description=f"User viewed report: {report.title}",
        resource_type="report",
        resource_id=report.id
    )
    
    return report_detail

@router.put("/{report_id}", response_model=Report)
def update_report(
    request: Request,
    *,
    db: Session = Depends(get_db),
    report_id: str = Path(...),
    report_in: ReportUpdate,
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Update a report.
    """
    report = crud_report.get(db, id=report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    
    # Only allow updates to own reports unless superuser
    if report.doctor_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this report",
        )
    
    # Only allow updates to draft reports
    if report.status != ReportStatusEnum.draft and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft reports can be updated",
        )
    
    # Store previous content for history
    previous_content = report.content
    
    # Update report
    report = crud_report.update(db, db_obj=report, obj_in=report_in)
    
    # Add to report history if content changed
    if report_in.content and report_in.content != previous_content:
        changes = compute_diff(previous_content, report.content)
        crud_report.add_report_history(
            db,
            report_id=report.id,
            user_id=current_user.id,
            changes=changes,
            previous_content=previous_content,
            notes="Report content updated"
        )
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.update,
        description=f"User updated report: {report.title}",
        resource_type="report",
        resource_id=report.id
    )
    
    return report

@router.post("/{report_id}/finalize", response_model=Report)
def finalize_report(
    request: Request,
    *,
    db: Session = Depends(get_db),
    report_id: str = Path(...),
    finalize_data: ReportFinalize,
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Finalize a report.
    """
    report = crud_report.get(db, id=report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    
    # Only allow finalizing own reports unless superuser
    if report.doctor_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to finalize this report",
        )
    
    # Only allow finalizing draft reports
    if report.status != ReportStatusEnum.draft:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft reports can be finalized",
        )
    
    # Finalize report
    report = crud_report.finalize_report(
        db,
        report_id=report.id,
        notes=finalize_data.notes
    )
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.update,
        description=f"User finalized report: {report.title}",
        resource_type="report",
        resource_id=report.id
    )
    
    return report

@router.post("/{report_id}/generate-pdf", response_model=Report)
def generate_pdf(
    request: Request,
    *,
    db: Session = Depends(get_db),
    report_id: str = Path(...),
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Generate PDF for a report.
    """
    report = crud_report.get(db, id=report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    
    # Only allow access to own reports unless superuser
    if report.doctor_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this report",
        )
    
    # Generate PDF in background
    pdf_path = generate_report_pdf(report_id, db)
    
    if not pdf_path:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate PDF",
        )
    
    # Update report with file path
    report.file_path = pdf_path
    report.format = ReportFormatEnum.pdf
    db.add(report)
    db.commit()
    db.refresh(report)
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.generate_report,
        description=f"User generated PDF for report: {report.title}",
        resource_type="report",
        resource_id=report.id
    )
    
    return report

@router.get("/{report_id}/download-pdf")
def download_pdf(
    request: Request,
    *,
    db: Session = Depends(get_db),
    report_id: str = Path(...),
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    Download PDF for a report.
    """
    report = crud_report.get(db, id=report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    
    # Only allow access to own reports unless superuser
    if report.doctor_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this report",
        )
    
    # Check if PDF exists
    if not report.file_path or report.format != ReportFormatEnum.pdf:
        # Generate PDF if it doesn't exist
        pdf_path = generate_report_pdf(report_id, db)
        if not pdf_path:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate PDF",
            )
    
    file_path = report.file_path
    if not os.path.isfile(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF file not found on server",
        )
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.download,
        description=f"User downloaded PDF for report: {report.title}",
        resource_type="report",
        resource_id=report.id
    )
    
    # Generate filename for download
    filename = f"Report_{report.id}.pdf"
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/pdf"
    )

@router.get("/{report_id}/html", response_class=HTMLResponse)
def view_report_html(
    request: Request,
    *,
    db: Session = Depends(get_db),
    report_id: str = Path(...),
    current_user: User = Depends(get_current_verified_user),
) -> Any:
    """
    View report as HTML.
    """
    report = crud_report.get(db, id=report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    
    # Only allow access to own reports unless superuser
    if report.doctor_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this report",
        )
    
    # Get report data
    patient = report.patient
    doctor = report.doctor
    analysis = report.analysis
    
    # Log the activity
    log_user_activity(
        request=request,
        db=db,
        user=current_user,
        activity_type=ActivityTypeEnum.view,
        description=f"User viewed HTML report: {report.title}",
        resource_type="report",
        resource_id=report.id
    )
    
    # Simple HTML template for demonstration
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{report.title}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
            .header {{ border-bottom: 1px solid #ccc; padding-bottom: 10px; margin-bottom: 20px; }}
            .patient-info {{ margin-bottom: 20px; }}
            .report-content {{ margin-bottom: 30px; }}
            .footer {{ border-top: 1px solid #ccc; padding-top: 10px; font-size: 0.8em; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{report.title}</h1>
            <p>Report ID: {report.id}</p>
            <p>Status: {report.status}</p>
        </div>
        
        <div class="patient-info">
            <h2>Patient Information</h2>
            <table>
                <tr><th>Name</th><td>{patient.first_name} {patient.last_name}</td></tr>
                <tr><th>MRN</th><td>{patient.medical_record_number}</td></tr>
                <tr><th>Gender</th><td>{patient.gender}</td></tr>
                <tr><th>Date of Birth</th><td>{patient.date_of_birth.strftime("%Y-%m-%d")}</td></tr>
                <tr><th>Age</th><td>{(datetime.now().date() - patient.date_of_birth).days // 365}</td></tr>
            </table>
        </div>
        
        <div class="report-content">
            <h2>Report Content</h2>
            {report.content}
        </div>
        
        {f'''
        <div class="analysis-info">
            <h2>Analysis Information</h2>
            <table>
                <tr><th>AI Diagnosis</th><td>{analysis.ai_diagnosis or 'N/A'}</td></tr>
                <tr><th>Doctor Diagnosis</th><td>{analysis.doctor_diagnosis or 'N/A'}</td></tr>
                <tr><th>Confidence</th><td>{f"{analysis.confidence*100:.1f}%" if analysis.confidence else 'N/A'}</td></tr>
                <tr><th>Severity</th><td>{analysis.severity or 'N/A'}</td></tr>
            </table>
        </div>
        ''' if analysis else ''}
        
        <div class="footer">
            <p>Generated by: {doctor.full_name}, {doctor.specialty or 'N/A'}</p>
            <p>Created: {report.created_at.strftime("%Y-%m-%d %H:%M")}</p>
            {f'<p>Updated: {report.updated_at.strftime("%Y-%m-%d %H:%M")}</p>' if report.updated_at else ''}
            {f'<p>Finalized: {report.finalized_at.strftime("%Y-%m-%d %H:%M")}</p>' if report.finalized_at else ''}
        </div>
        
        <div style="text-align: center; margin-top: 20px;">
            <a href="/api/v1/reports/{report.id}/download-pdf" style="padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 4px;">
                Download as PDF
            </a>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)
