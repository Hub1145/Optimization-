import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from backtesting import Backtest, Strategy
import talib

class BacktestingEngine:
    """Core backtesting engine using backtesting.py library"""

    def __init__(self, data: pd.DataFrame, capital: float = 10000,
                 commission: float = 0.001, slippage: float = 0.0005):
        """
        Args:
            data: DataFrame with OHLCV columns
            capital: Starting capital
            commission: Commission as decimal (0.001 = 0.1%)
            slippage: Slippage as decimal
        """
        self.data = self._validate_data(data)
        self.capital = capital
        self.commission = commission
        self.slippage = slippage

    def _validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure data has required columns and is sorted"""
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in df.columns for col in required_cols):
            # Try case-insensitive match
            df.columns = [col.capitalize() for col in df.columns]
            if not all(col in df.columns for col in required_cols):
                raise ValueError(f"Data must contain: {required_cols}")

        # Ensure datetime index
        if not isinstance(df.index, pd.DatetimeIndex):
            if 'Date' in df.columns:
                df = df.set_index('Date')
            elif 'date' in df.columns:
                df = df.set_index('date')
            df.index = pd.to_datetime(df.index)

        # Sort by date
        df = df.sort_index()

        # Remove NaN values
        df = df.dropna()

        return df

    def create_strategy_class(self, strategy_type: str, entry_rule: str, exit_rule: str,
                             parameters: Dict[str, Any]) -> type:
        """
        Dynamically create or retrieve a Strategy class from rules and parameters

        Args:
            strategy_type: Name of pre-built strategy or 'custom'
            entry_rule: Entry condition (e.g., "RSI < {rsi_threshold}")
            exit_rule: Exit condition
            parameters: Dict of parameter values

        Returns:
            Strategy class
        """
        from app.core.strategies import get_strategy_class
        prebuilt_class = get_strategy_class(strategy_type)

        if prebuilt_class:
            class WrappedStrategy(prebuilt_class):
                pass
            for k, v in parameters.items():
                setattr(WrappedStrategy, k, v)
            return WrappedStrategy

        class DynamicStrategy(Strategy):
            # Inject parameters as class attributes
            params = parameters

            def init(self):
                # Calculate indicators based on parameters
                close = self.data.Close

                # RSI
                if 'rsi_period' in self.params:
                    self.rsi = self.I(talib.RSI, close, self.params['rsi_period'])

                # EMA
                if 'ema_period' in self.params:
                    self.ema = self.I(talib.EMA, close, self.params['ema_period'])

                # MACD
                if 'macd_fast' in self.params:
                    macd, signal, hist = self.I(
                        talib.MACD, close,
                        self.params.get('macd_fast', 12),
                        self.params.get('macd_slow', 26),
                        self.params.get('macd_signal', 9)
                    )
                    self.macd = macd
                    self.macd_signal = signal

                # Bollinger Bands
                if 'bb_period' in self.params:
                    upper, middle, lower = self.I(
                        talib.BBANDS, close,
                        self.params['bb_period'],
                        self.params.get('bb_std', 2),
                        self.params.get('bb_std', 2)
                    )
                    self.bb_upper = upper
                    self.bb_middle = middle
                    self.bb_lower = lower

            def next(self):
                # Evaluate entry rule
                if not self.position:
                    entry_condition = self._eval_condition(entry_rule)
                    if entry_condition:
                        self.buy()

                # Evaluate exit rule
                else:
                    exit_condition = self._eval_condition(exit_rule)
                    if exit_condition:
                        self.position.close()

            def _eval_condition(self, rule: str) -> bool:
                """Safely evaluate a trading rule"""
                try:
                    # Context for evaluation
                    context = {
                        'price': self.data.Close[-1],
                    }

                    # Add indicators
                    if hasattr(self, 'rsi'):
                        context['RSI'] = self.rsi[-1]
                    if hasattr(self, 'ema'):
                        context['EMA'] = self.ema[-1]
                    if hasattr(self, 'macd'):
                        context['MACD'] = self.macd[-1]
                        context['MACD_SIGNAL'] = self.macd_signal[-1]

                    # Add parameters
                    context.update(self.params)

                    # Restricted evaluation
                    return eval(rule, {"__builtins__": {}}, context)
                except Exception as e:
                    return False

        return DynamicStrategy

    def run_backtest(self, strategy_class: type) -> Dict[str, Any]:
        """
        Run backtest and return results

        Returns:
            Dict with performance metrics
        """
        bt = Backtest(
            self.data,
            strategy_class,
            cash=self.capital,
            commission=self.commission,
            exclusive_orders=True
        )

        stats = bt.run()

        # Extract key metrics
        avg_trade_duration = stats.get('Avg. Trade Duration')
        if isinstance(avg_trade_duration, pd.Timedelta):
            avg_trade_duration_days = avg_trade_duration.total_seconds() / 86400
        else:
            avg_trade_duration_days = 0.0

        results = {
            'total_return': (stats['Return [%]'] / 100),
            'sharpe_ratio': stats.get('Sharpe Ratio', 0) if not pd.isna(stats.get('Sharpe Ratio')) else 0,
            'max_drawdown': abs(stats['Max. Drawdown [%]'] / 100),
            'win_rate': (stats.get('Win Rate [%]', 0) / 100) if not pd.isna(stats.get('Win Rate [%]')) else 0,
            'profit_factor': stats.get('Profit Factor', 0) if not pd.isna(stats.get('Profit Factor')) else 0,
            'total_trades': stats['# Trades'],
            'avg_trade_duration': avg_trade_duration_days,
            'equity_curve': stats._equity_curve.to_dict('records'),
            'trades': stats._trades.to_dict('records') if hasattr(stats, '_trades') else []
        }

        return results

    def calculate_metrics(self, returns: pd.Series) -> Dict[str, float]:
        """Calculate performance metrics from return series"""
        total_return = (returns + 1).prod() - 1

        # Sharpe ratio (annualized, assuming daily data)
        if len(returns) > 0 and returns.std() > 0:
            sharpe = (returns.mean() / returns.std()) * np.sqrt(252)
        else:
            sharpe = 0

        # Max drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = abs(drawdown.min())

        # Sortino ratio (downside deviation)
        downside_returns = returns[returns < 0]
        if len(downside_returns) > 0 and downside_returns.std() > 0:
            sortino = (returns.mean() / downside_returns.std()) * np.sqrt(252)
        else:
            sortino = 0

        # Calmar ratio
        if max_drawdown > 0:
            calmar = total_return / max_drawdown
        else:
            calmar = 0

        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'max_drawdown': max_drawdown,
            'calmar_ratio': calmar
        }
