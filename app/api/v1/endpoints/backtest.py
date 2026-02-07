from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import StrategyDefinition, DataConfig, PerformanceMetrics
from app.services.market_data import MarketDataService
from app.core.backtesting.engine import BacktestingEngine
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
    market_data = MarketDataService()
    df = await market_data.get_data(
        data_config.symbol,
        str(data_config.start_date),
        str(data_config.end_date),
        data_config.timeframe,
        data_config.provider,
        data_config.exchange
    )

    if df.empty:
        raise HTTPException(status_code=404, detail="No data found for symbol")

    engine = BacktestingEngine(df, capital, commission, slippage)
    strategy_class = engine.create_strategy_class(
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
