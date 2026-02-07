import pandas as pd
import numpy as np
from app.core.optimization.grid_search import GridSearchOptimizer

def test_grid_search():
    dates = pd.date_range(start='2023-01-01', periods=100)
    data = pd.DataFrame({
        'Open': np.random.randn(100).cumsum() + 100,
        'High': np.random.randn(100).cumsum() + 102,
        'Low': np.random.randn(100).cumsum() + 98,
        'Close': np.random.randn(100).cumsum() + 100,
        'Volume': np.ones(100) * 1000
    }, index=dates)

    strategy_definition = {
        'entry_rule': "RSI < rsi_oversold",
        'exit_rule': "RSI > rsi_overbought"
    }

    optimizer = GridSearchOptimizer(data, strategy_definition)

    parameter_grid = {
        'rsi_period': [14, 21],
        'rsi_oversold': [30, 40],
        'rsi_overbought': [60, 70]
    }

    # Use n_jobs=1 to avoid issues in some environments
    result = optimizer.optimize(parameter_grid, n_jobs=1)

    assert 'best_parameters' in result
    assert len(result['top_10_combinations']) > 0
    print("Grid search test passed!")

if __name__ == "__main__":
    test_grid_search()
