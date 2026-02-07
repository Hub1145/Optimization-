import numpy as np
import pandas as pd
from typing import Dict

def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    if len(returns) < 2:
        return 0.0
    excess_returns = returns - risk_free_rate / 252 # Daily
    if excess_returns.std() == 0:
        return 0.0
    return (excess_returns.mean() / excess_returns.std()) * np.sqrt(252)

def calculate_max_drawdown(equity_curve: pd.Series) -> float:
    if len(equity_curve) < 1:
        return 0.0
    rolling_max = equity_curve.cummax()
    drawdowns = (equity_curve - rolling_max) / rolling_max
    return abs(drawdowns.min())

def calculate_strategy_score(metrics: Dict[str, float]) -> float:
    """
    ML-like scoring based on multiple metrics
    Score = (Total Return * 0.4) + (Sharpe * 0.3) + (Win Rate * 0.2) - (Max DD * 0.1)
    """
    total_return = metrics.get('total_return', 0)
    sharpe = metrics.get('sharpe_ratio', 0)
    win_rate = metrics.get('win_rate', 0)
    max_dd = metrics.get('max_drawdown', 0)

    # Normalize metrics or just weight them
    score = (total_return * 0.4) + (sharpe * 0.3) + (win_rate * 0.2) - (max_dd * 0.1)
    return score
