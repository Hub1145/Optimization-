import pandas as pd
import numpy as np
from app.core.optimization.genetic import GeneticOptimizer

def test_genetic_optimization():
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

    optimizer = GeneticOptimizer(data, strategy_definition)

    parameter_bounds = {
        'rsi_period': {'min': 10, 'max': 30},
        'rsi_oversold': {'min': 20, 'max': 45},
        'rsi_overbought': {'min': 55, 'max': 80}
    }

    result = optimizer.optimize(
        parameter_bounds,
        population_size=10,
        generations=2
    )

    assert 'best_parameters' in result
    assert 'best_performance' in result
    print("Genetic optimization test passed!")

if __name__ == "__main__":
    test_genetic_optimization()
