from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.schemas import GridSearchRequest, GeneticAlgorithmRequest, WalkForwardRequest, JobStatusResponse
from app.models.database import OptimizationJob, StrategyConfig, User
from app.workers.tasks import run_grid_search, run_genetic_optimization, run_walk_forward
from app.models.enums import JobStatus, OptimizationType
from app.dependencies import get_db
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

@router.post("/grid-search", response_model=JobStatusResponse)
def optimize_grid_search(request: GridSearchRequest, db: Session = Depends(get_db)):
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

@router.post("/genetic", response_model=JobStatusResponse)
def optimize_genetic(request: GeneticAlgorithmRequest, db: Session = Depends(get_db)):
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

@router.post("/walk-forward", response_model=JobStatusResponse)
def optimize_walk_forward(request: WalkForwardRequest, db: Session = Depends(get_db)):
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
