from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import StrategyDefinition, DataConfig, PerformanceMetrics
from app.services.market_data import MarketDataService
from app.core.backtesting.engine import BacktestingEngine
from app.core.strategies import get_strategy_class
from app.utils.validators import validate_date_range
from app.config import settings
import pandas as pd

router = APIRouter()

@router.post("/", response_model=PerformanceMetrics)
async def run_single_backtest(
    strategy: StrategyDefinition,
    data_config: DataConfig,
    parameters: dict,
    capital: float = 10000,
    commission: float = 0.001,
    slippage: float = 0.0005
):
    # Early validation
    try:
        validate_date_range(data_config.start_date, data_config.end_date, settings.MAX_DATA_DAYS)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    market_data = MarketDataService()
    df = await market_data.get_data(
        data_config.symbol,
        str(data_config.start_date),
        str(data_config.end_date),
        data_config.timeframe
    )

    if df.empty:
        raise HTTPException(status_code=404, detail="No data found for symbol")

    engine = BacktestingEngine(df, capital, commission, slippage)

    strategy_class = engine.create_strategy_class(
        strategy.type,
        strategy.entry_rule,
        strategy.exit_rule,
        parameters
    )

    result = engine.run_backtest(strategy_class)

    return PerformanceMetrics(
        total_return=result['total_return'],
        sharpe_ratio=result['sharpe_ratio'],
        max_drawdown=result['max_drawdown'],
        win_rate=result['win_rate'],
        profit_factor=result['profit_factor'],
        total_trades=result['total_trades'],
        avg_trade_duration_days=result['avg_trade_duration']
    )
