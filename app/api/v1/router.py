from fastapi import APIRouter
from app.api.v1.endpoints import optimize, backtest, strategies, results, health

api_router = APIRouter()
api_router.include_router(optimize.router, prefix="/optimize", tags=["optimize"])
api_router.include_router(backtest.router, prefix="/backtest", tags=["backtest"])
api_router.include_router(strategies.router, prefix="/strategies", tags=["strategies"])
api_router.include_router(results.router, prefix="/results", tags=["results"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
