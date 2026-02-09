from app.workers.celery_app import celery_app
from app.core.optimizers.grid_search import GridSearchOptimizer
from app.core.optimizers.genetic import GeneticOptimizer
from app.core.optimizers.walk_forward import WalkForwardOptimizer
from app.core.strategies import get_strategy_class
from app.services.market_data import MarketDataService
from app.models.database import OptimizationJob, OptimizationResult, WalkForwardPeriod, EquityCurve
from app.models.enums import JobStatus
from app.dependencies import SessionLocal
from datetime import datetime
import asyncio
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def get_data_sync(data_config):
    market_data = MarketDataService()
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # This shouldn't happen in Celery worker but just in case
        import nest_asyncio
        nest_asyncio.apply()
        return loop.run_until_complete(market_data.get_data(
            data_config['symbol'],
            data_config['start_date'],
            data_config['end_date'],
            data_config['timeframe']
        ))
    else:
        return asyncio.run(market_data.get_data(
            data_config['symbol'],
            data_config['start_date'],
            data_config['end_date'],
            data_config['timeframe']
        ))

@celery_app.task(name="run_grid_search")
def run_grid_search(job_id, request_data):
    logger.info(f"Starting grid search for job {job_id}")
    db = SessionLocal()
    try:
        # Update job status
        job = db.query(OptimizationJob).filter(OptimizationJob.id == job_id).first()
        if job:
            job.status = JobStatus.RUNNING
            job.started_at = datetime.utcnow()
            db.commit()

        data_config = request_data['data']
        df = get_data_sync(data_config)

        if df.empty:
            raise ValueError("No data found")

        optimizer = GridSearchOptimizer(
            df,
            request_data['strategy'],
            capital=request_data['capital'],
            commission=request_data['commission'],
            slippage=request_data['slippage']
        )

        param_grid = {k: v['values'] for k, v in request_data['parameters'].items()}

        result = optimizer.optimize(
            param_grid,
            objective=request_data['optimization']['objective'],
            constraints=request_data['optimization']['constraints'],
            max_combinations=request_data['optimization']['max_combinations']
        )

        # Save results to DB
        for combo in result['top_10_combinations']:
            opt_result = OptimizationResult(
                job_id=job_id,
                parameters=combo['parameters'],
                total_return=combo['performance']['total_return'],
                sharpe_ratio=combo['performance']['sharpe_ratio'],
                max_drawdown=combo['performance']['max_drawdown'],
                win_rate=combo['performance']['win_rate'],
                profit_factor=combo['performance']['profit_factor'],
                total_trades=combo['performance']['total_trades'],
                avg_trade_duration_days=combo['performance']['avg_trade_duration_days'],
                is_best=(combo['parameters'] == result['best_parameters'])
            )
            db.add(opt_result)
            db.flush() # To get ID

            if combo.get('equity_curve'):
                curve = EquityCurve(
                    result_id=opt_result.id,
                    data=combo['equity_curve']
                )
                db.add(curve)

        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        db.commit()

        logger.info(f"Completed grid search for job {job_id}")
        return result
    except Exception as e:
        logger.error(f"Error in grid search: {e}")
        if job:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            db.commit()
        return {"error": str(e)}
    finally:
        db.close()

@celery_app.task(name="run_genetic_optimization")
def run_genetic_optimization(job_id, request_data):
    logger.info(f"Starting genetic optimization for job {job_id}")
    db = SessionLocal()
    try:
        # Update job status
        job = db.query(OptimizationJob).filter(OptimizationJob.id == job_id).first()
        if job:
            job.status = JobStatus.RUNNING
            job.started_at = datetime.utcnow()
            db.commit()

        data_config = request_data['data']
        df = get_data_sync(data_config)

        optimizer = GeneticOptimizer(
            df,
            request_data['strategy'],
            capital=request_data['capital'],
            commission=request_data['commission'],
            slippage=request_data['slippage']
        )

        result = optimizer.optimize(
            request_data['parameters'],
            population_size=request_data['genetic_config']['population_size'],
            generations=request_data['genetic_config']['generations'],
            mutation_rate=request_data['genetic_config']['mutation_rate'],
            crossover_rate=request_data['genetic_config']['crossover_rate'],
            objective=request_data['optimization']['objective']
        )

        # Save result to DB
        opt_result = OptimizationResult(
            job_id=job_id,
            parameters=result['best_parameters'],
            total_return=result['best_performance']['total_return'],
            sharpe_ratio=result['best_performance']['sharpe_ratio'],
            max_drawdown=result['best_performance']['max_drawdown'],
            win_rate=result['best_performance']['win_rate'],
            profit_factor=result['best_performance']['profit_factor'],
            total_trades=result['best_performance']['total_trades'],
            avg_trade_duration_days=result['best_performance']['avg_trade_duration_days'],
            is_best=True
        )
        db.add(opt_result)

        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        db.commit()

        return result
    except Exception as e:
        logger.error(f"Error in genetic optimization: {e}")
        if job:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            db.commit()
        return {"error": str(e)}
    finally:
        db.close()

@celery_app.task(name="run_walk_forward")
def run_walk_forward(job_id, request_data):
    logger.info(f"Starting walk-forward for job {job_id}")
    db = SessionLocal()
    try:
        # Update job status
        job = db.query(OptimizationJob).filter(OptimizationJob.id == job_id).first()
        if job:
            job.status = JobStatus.RUNNING
            job.started_at = datetime.utcnow()
            db.commit()

        data_config = request_data['data']
        df = get_data_sync(data_config)

        optimizer = WalkForwardOptimizer(
            df,
            request_data['strategy'],
            capital=request_data['capital'],
            commission=request_data['commission'],
            slippage=request_data['slippage']
        )

        param_grid = {k: v['values'] for k, v in request_data['parameters'].items()}

        result = optimizer.optimize(
            param_grid,
            training_period_months=request_data['walk_forward_config']['training_period_months'],
            validation_period_months=request_data['walk_forward_config']['validation_period_months'],
            step_months=request_data['walk_forward_config']['step_months'],
            anchored=request_data['walk_forward_config']['anchored'],
            objective=request_data['optimization']['objective']
        )

        # Save walk-forward periods
        for p in result['periods']:
            wf_period = WalkForwardPeriod(
                job_id=job_id,
                period_number=p['period_number'],
                training_start=p['training_start'],
                training_end=p['training_end'],
                validation_start=p['validation_start'],
                validation_end=p['validation_end'],
                best_parameters=p['best_parameters'],
                in_sample_sharpe=p['in_sample_sharpe'],
                out_sample_sharpe=p['out_sample_sharpe']
            )
            db.add(wf_period)

        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        db.commit()

        return result
    except Exception as e:
        logger.error(f"Error in walk-forward: {e}")
        if job:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            db.commit()
        return {"error": str(e)}
    finally:
        db.close()
