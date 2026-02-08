from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.models.schemas import GridSearchRequest, GeneticAlgorithmRequest, WalkForwardRequest, JobStatusResponse
from app.models.database import OptimizationJob, StrategyConfig, User
from app.workers.tasks import run_grid_search, run_genetic_optimization, run_walk_forward
from app.models.enums import JobStatus, OptimizationType
from app.dependencies import get_db
from app.utils.validators import validate_date_range
from app.config import settings
from datetime import datetime
import uuid

router = APIRouter()

def get_or_create_default_user(db: Session):
    user = db.query(User).first()
    if not user:
        user = User(email="admin@example.com", hashed_password="hashed_password")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

@router.post("/start", response_model=JobStatusResponse)
def start_optimization(request: GridSearchRequest, db: Session = Depends(get_db)):
    try:
        validate_date_range(request.data.start_date, request.data.end_date, settings.MAX_DATA_DAYS)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    user = get_or_create_default_user(db)
    job = OptimizationJob(
        id=uuid.uuid4(),
        user_id=user.id,
        status=JobStatus.PENDING,
        job_type=OptimizationType.GRID_SEARCH
    )
    db.add(job)

    config = StrategyConfig(
        job_id=job.id,
        strategy_type=request.strategy.type,
        entry_rule=request.strategy.entry_rule,
        exit_rule=request.strategy.exit_rule,
        parameters={k: v.model_dump() for k, v in request.parameters.items()},
        data_config=request.data.model_dump(),
        optimization_config=request.optimization.model_dump(),
        capital=request.capital,
        commission=request.commission,
        slippage=request.slippage
    )
    db.add(config)
    db.commit()

    run_grid_search.delay(str(job.id), request.model_dump())

    return JobStatusResponse(
        job_id=str(job.id),
        status=JobStatus.PENDING,
        job_type=OptimizationType.GRID_SEARCH,
        created_at=job.created_at
    )

@router.post("/genetic/start", response_model=JobStatusResponse)
def start_genetic_optimization(request: GeneticAlgorithmRequest, db: Session = Depends(get_db)):
    try:
        validate_date_range(request.data.start_date, request.data.end_date, settings.MAX_DATA_DAYS)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    user = get_or_create_default_user(db)
    job = OptimizationJob(
        id=uuid.uuid4(),
        user_id=user.id,
        status=JobStatus.PENDING,
        job_type=OptimizationType.GENETIC
    )
    db.add(job)
    db.commit()

    run_genetic_optimization.delay(str(job.id), request.model_dump())

    return JobStatusResponse(
        job_id=str(job.id),
        status=JobStatus.PENDING,
        job_type=OptimizationType.GENETIC,
        created_at=job.created_at
    )

@router.post("/walk-forward/start", response_model=JobStatusResponse)
def start_walk_forward_optimization(request: WalkForwardRequest, db: Session = Depends(get_db)):
    try:
        validate_date_range(request.data.start_date, request.data.end_date, settings.MAX_DATA_DAYS)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    user = get_or_create_default_user(db)
    job = OptimizationJob(
        id=uuid.uuid4(),
        user_id=user.id,
        status=JobStatus.PENDING,
        job_type=OptimizationType.WALK_FORWARD
    )
    db.add(job)
    db.commit()

    run_walk_forward.delay(str(job.id), request.model_dump())

    return JobStatusResponse(
        job_id=str(job.id),
        status=JobStatus.PENDING,
        job_type=OptimizationType.WALK_FORWARD,
        created_at=job.created_at
    )

@router.get("/{job_id}/status", response_model=JobStatusResponse)
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

@router.delete("/{job_id}/cancel")
def cancel_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(OptimizationJob).filter(OptimizationJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Logic to revoke task
    from app.workers.celery_app import celery_app
    # We need the task ID which we should have stored
    # For now mock success
    job.status = JobStatus.FAILED
    job.error_message = "Cancelled by user"
    db.commit()
    return {"message": "Job cancelled"}

@router.websocket("/{job_id}/stream")
async def stream_job_status(websocket: WebSocket, job_id: str, db: Session = Depends(get_db)):
    await websocket.accept()
    try:
        import asyncio
        while True:
            job = db.query(OptimizationJob).filter(OptimizationJob.id == job_id).first()
            if not job:
                await websocket.send_json({"error": "Job not found"})
                break

            await websocket.send_json({
                "job_id": str(job.id),
                "status": job.status,
                "progress": 0, # Mock progress
                "completed_at": job.completed_at.isoformat() if job.completed_at else None
            })

            if job.status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                break

            await asyncio.sleep(2)
    except WebSocketDisconnect:
        pass
