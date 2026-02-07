import pandas as pd
import numpy as np
from app.core.backtesting.engine import BacktestingEngine
import talib

def test_backtesting_engine():
    # Create sample data
    dates = pd.date_range(start='2023-01-01', periods=100)
    data = pd.DataFrame({
        'Open': np.linspace(100, 110, 100),
        'High': np.linspace(101, 111, 100),
        'Low': np.linspace(99, 109, 100),
        'Close': np.linspace(100, 110, 100),
        'Volume': np.ones(100) * 1000
    }, index=dates)

    engine = BacktestingEngine(data)

    # Define a simple strategy
    entry_rule = "price > 105"
    exit_rule = "price > 108"
    parameters = {}

    strategy_class = engine.create_strategy_class(entry_rule, exit_rule, parameters)
    result = engine.run_backtest(strategy_class)

    assert 'total_return' in result
    assert 'sharpe_ratio' in result
    assert result['total_trades'] > 0
    print("Test passed!")

if __name__ == "__main__":
    test_backtesting_engine()
