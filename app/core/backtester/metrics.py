import pandas as pd
import numpy as np
from typing import Dict, List, Any

def score_strategy_ml(results_df: pd.DataFrame, weights: Dict[str, float] = None) -> Dict:
    """
    ML-inspired scoring based on multiple performance metrics.
    Normalizes metrics and applies weights.
    """
    if results_df.empty:
        return None

    if weights is None:
        weights = {
            'net_profit': 0.35,
            'win_rate': 0.25,
            'profit_factor': 0.25,
            'loss_streak': 0.15
        }

    df = results_df.copy()

    # Absolute values for normalization
    max_profit = df['total_return'].max()
    max_win_rate = df['win_rate'].max()
    max_profit_factor = df['profit_factor'].max()
    max_loss_streak = df['max_loss_streak'].max()

    # Normalize (handling division by zero)
    df['norm_profit'] = (df['total_return'] / max_profit) if max_profit > 0 else 0
    df['norm_win_rate'] = (df['win_rate'] / max_win_rate) if max_win_rate > 0 else 0
    df['norm_profit_factor'] = (df['profit_factor'] / max_profit_factor) if max_profit_factor > 0 else 0
    df['norm_loss_streak_desire'] = 1 - (df['max_loss_streak'] / max_loss_streak) if max_loss_streak > 0 else 1

    # Calculate ML score
    df['ml_score'] = (
        weights.get('net_profit', 0) * df['norm_profit'] +
        weights.get('win_rate', 0) * df['norm_win_rate'] +
        weights.get('profit_factor', 0) * df['norm_profit_factor'] +
        weights.get('loss_streak', 0) * df['norm_loss_streak_desire']
    )

    return df.sort_values(by='ml_score', ascending=False).iloc[0].to_dict()

def calculate_risk_metrics(returns: pd.Series) -> Dict[str, float]:
    """Calculate risk metrics like VaR and CVaR"""
    if returns.empty:
        return {}

    var_95 = np.percentile(returns, 5)
    cvar_95 = returns[returns <= var_95].mean()

    return {
        'value_at_risk_95': abs(var_95),
        'conditional_var_95': abs(cvar_95) if not np.isnan(cvar_95) else 0
    }
