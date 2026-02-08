from typing import Dict, List, Any
import pandas as pd
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from app.core.optimization.grid_search import GridSearchOptimizer
from app.core.backtesting.engine import BacktestingEngine

class WalkForwardOptimizer:
    """Walk-forward optimization to prevent overfitting"""

    def __init__(self, data: pd.DataFrame, strategy_definition: Dict[str, str],
                 capital: float = 10000, commission: float = 0.001, slippage: float = 0.0005):
        self.data = data
        self.strategy_definition = strategy_definition
        self.capital = capital
        self.commission = commission
        self.slippage = slippage

    def optimize(self, parameter_grid: Dict[str, List[Any]],
                 training_period_months: int = 12,
                 validation_period_months: int = 3,
                 step_months: int = 3,
                 anchored: bool = False,
                 objective: str = 'sharpe_ratio') -> Dict[str, Any]:
        """
        Perform walk-forward optimization

        Args:
            parameter_grid: Parameter grid for optimization
            training_period_months: Training window size
            validation_period_months: Validation window size
            step_months: How many months to step forward
            anchored: If True, use expanding window. If False, rolling window
            objective: Metric to optimize

        Returns:
            Walk-forward results with in-sample and out-of-sample performance
        """
        periods = self._generate_periods(
            training_period_months,
            validation_period_months,
            step_months,
            anchored
        )

        print(f"Generated {len(periods)} walk-forward periods")

        in_sample_results = []
        out_sample_results = []
        period_details = []

        for i, period in enumerate(periods):
            # Split data
            train_data = self.data[period['train_start']:period['train_end']]
            val_data = self.data[period['val_start']:period['val_end']]

            if len(train_data) < 50:
                continue

            if len(val_data) < 10:
                continue

            # Optimize on training data
            optimizer = GridSearchOptimizer(
                train_data,
                self.strategy_definition,
                self.capital,
                self.commission,
                self.slippage
            )

            train_result = optimizer.optimize(parameter_grid, objective)
            best_params = train_result['best_parameters']

            if not best_params:
                continue

            # Test on validation data
            val_engine = BacktestingEngine(val_data, self.capital, self.commission, self.slippage)
            strategy_class = val_engine.create_strategy_class(
                self.strategy_definition.get('type', 'custom'),
                self.strategy_definition.get('entry_rule'),
                self.strategy_definition.get('exit_rule'),
                best_params
            )
            val_result = val_engine.run_backtest(strategy_class)

            # Store results
            in_sample_results.append(train_result['best_performance'])
            out_sample_results.append({
                'total_return': val_result['total_return'],
                'sharpe_ratio': val_result['sharpe_ratio'],
                'max_drawdown': val_result['max_drawdown'],
                'win_rate': val_result['win_rate'],
                'profit_factor': val_result['profit_factor'],
                'total_trades': val_result['total_trades'],
                'avg_trade_duration_days': val_result['avg_trade_duration']
            })

            period_details.append({
                'period_number': i + 1,
                'training_start': period['train_start'],
                'training_end': period['train_end'],
                'validation_start': period['val_start'],
                'validation_end': period['val_end'],
                'best_parameters': best_params,
                'in_sample_sharpe': train_result['best_performance'].get('sharpe_ratio', 0),
                'out_sample_sharpe': val_result.get('sharpe_ratio', 0)
            })

        # Aggregate performance
        avg_in_sample = self._average_performance(in_sample_results)
        avg_out_sample = self._average_performance(out_sample_results)

        # Degradation factor
        if avg_in_sample.get('sharpe_ratio', 0) > 0:
            degradation = avg_out_sample.get('sharpe_ratio', 0) / avg_in_sample['sharpe_ratio']
        else:
            degradation = 0

        # Stability score (consistency of out-sample Sharpe)
        out_sharpes = [p['out_sample_sharpe'] for p in period_details]
        if len(out_sharpes) > 1:
            stability = 1 - (pd.Series(out_sharpes).std() / (pd.Series(out_sharpes).mean() + 1e-9))
        else:
            stability = 0

        return {
            'in_sample_performance': avg_in_sample,
            'out_of_sample_performance': avg_out_sample,
            'degradation_factor': degradation,
            'stability_score': stability,
            'periods': period_details
        }

    def _generate_periods(self, train_months: int, val_months: int,
                         step_months: int, anchored: bool) -> List[Dict]:
        """Generate walk-forward period windows"""
        periods = []

        start_date = self.data.index[0]
        end_date = self.data.index[-1]

        current_train_start = start_date

        while True:
            # Training period
            train_end = current_train_start + relativedelta(months=train_months)

            # Validation period
            val_start = train_end
            val_end = val_start + relativedelta(months=val_months)

            # Check if we've exceeded data range
            if val_end > end_date:
                break

            periods.append({
                'train_start': current_train_start,
                'train_end': train_end,
                'val_start': val_start,
                'val_end': val_end
            })

            # Move forward
            if anchored:
                # Anchored: training start stays same, validation slides
                current_train_start = current_train_start
            else:
                # Rolling: both windows slide forward
                current_train_start = current_train_start + relativedelta(months=step_months)

        return periods

    def _average_performance(self, results: List[Dict]) -> Dict:
        """Average performance across periods"""
        if not results:
            return {k: 0 for k in ['total_return', 'sharpe_ratio', 'max_drawdown',
                                   'win_rate', 'profit_factor', 'total_trades', 'avg_trade_duration_days']}

        df = pd.DataFrame(results)
        return df.mean().to_dict()
