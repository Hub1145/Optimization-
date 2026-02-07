from typing import Any, Dict
import pandas as pd

def format_performance_metrics(stats: Dict[str, Any]) -> Dict[str, float]:
    """Format raw backtest stats into performance metrics schema"""
    return {
        'total_return': round(stats.get('total_return', 0), 4),
        'sharpe_ratio': round(stats.get('sharpe_ratio', 0), 4),
        'max_drawdown': round(stats.get('max_drawdown', 0), 4),
        'win_rate': round(stats.get('win_rate', 0), 4),
        'profit_factor': round(stats.get('profit_factor', 0), 4),
        'total_trades': int(stats.get('total_trades', 0)),
        'avg_trade_duration_days': round(stats.get('avg_trade_duration_days', 0), 2)
    }

def format_equity_curve(curve_df: pd.DataFrame) -> list:
    """Format equity curve for API response"""
    if isinstance(curve_df, pd.DataFrame):
        return curve_df.reset_index().to_dict('records')
    return []
