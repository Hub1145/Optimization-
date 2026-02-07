from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.schemas import JobStatusResponse
from app.models.database import OptimizationJob, OptimizationResult
from app.models.enums import JobStatus, OptimizationType
from app.dependencies import get_db
from datetime import datetime

router = APIRouter()

@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(OptimizationJob).filter(OptimizationJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=str(job.id),
        status=job.status,
        job_type=job.job_type,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        error_message=job.error_message
    )

@router.get("/{job_id}/results")
def get_job_results(job_id: str, db: Session = Depends(get_db)):
    results = db.query(OptimizationResult).filter(OptimizationResult.job_id == job_id).all()
    return results
