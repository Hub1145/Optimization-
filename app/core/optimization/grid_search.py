import itertools
from typing import Dict, List, Any, Callable
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
from app.core.backtesting.engine import BacktestingEngine

class GridSearchOptimizer:
    """Grid search parameter optimization"""

    def __init__(self, data: pd.DataFrame, strategy_definition: Dict[str, str],
                 capital: float = 10000, commission: float = 0.001, slippage: float = 0.0005):
        self.data = data
        self.strategy_definition = strategy_definition
        self.capital = capital
        self.commission = commission
        self.slippage = slippage
        self.results = []

    def optimize(self, parameter_grid: Dict[str, List[Any]],
                 objective: str = 'sharpe_ratio',
                 constraints: str = None,
                 max_combinations: int = 500,
                 n_jobs: int = -1) -> Dict[str, Any]:
        """
        Perform grid search optimization

        Args:
            parameter_grid: Dict of parameter names to lists of values
            objective: Metric to optimize ('sharpe_ratio', 'total_return', etc.)
            constraints: String constraint (e.g., "param1 < param2")
            max_combinations: Max combinations to test
            n_jobs: Number of parallel jobs (-1 = all cores)

        Returns:
            Dict with best parameters and results
        """
        # Generate all combinations
        param_names = list(parameter_grid.keys())
        param_values = list(parameter_grid.values())
        all_combinations = list(itertools.product(*param_values))

        # Apply constraints
        if constraints:
            all_combinations = [
                combo for combo in all_combinations
                if self._check_constraint(dict(zip(param_names, combo)), constraints)
            ]

        # Limit combinations
        if len(all_combinations) > max_combinations:
            print(f"Warning: {len(all_combinations)} combinations exceed max of {max_combinations}")
            all_combinations = all_combinations[:max_combinations]

        print(f"Testing {len(all_combinations)} parameter combinations...")

        # Parallel backtesting
        if n_jobs == -1:
            n_jobs = None  # Use all cores

        results = []
        # ProcessPoolExecutor can be tricky in some environments, but let's stick with it.
        # Actually, for the sandbox, I might want to use ThreadPoolExecutor if ProcessPool has issues,
        # but backtesting is CPU bound.
        with ProcessPoolExecutor(max_workers=n_jobs) as executor:
            futures = {
                executor.submit(self._backtest_params, dict(zip(param_names, combo))): combo
                for combo in all_combinations
            }

            for future in tqdm(as_completed(futures), total=len(futures)):
                result = future.result()
                if result:
                    results.append(result)

        if not results:
            return {
                'best_parameters': {},
                'best_performance': {},
                'top_10_combinations': [],
                'total_combinations_tested': 0
            }

        # Sort by objective
        results.sort(key=lambda x: x['performance'].get(objective, 0), reverse=True)

        # Store results
        self.results = results

        return {
            'best_parameters': results[0]['parameters'],
            'best_performance': results[0]['performance'],
            'top_10_combinations': results[:10],
            'total_combinations_tested': len(results)
        }

    def _backtest_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Backtest a single parameter set"""
        try:
            engine = BacktestingEngine(
                self.data,
                capital=self.capital,
                commission=self.commission,
                slippage=self.slippage
            )

            strategy_class = engine.create_strategy_class(
                self.strategy_definition['entry_rule'],
                self.strategy_definition['exit_rule'],
                params
            )

            result = engine.run_backtest(strategy_class)

            return {
                'parameters': params,
                'performance': {
                    'total_return': result['total_return'],
                    'sharpe_ratio': result['sharpe_ratio'],
                    'max_drawdown': result['max_drawdown'],
                    'win_rate': result['win_rate'],
                    'profit_factor': result['profit_factor'],
                    'total_trades': result['total_trades'],
                    'avg_trade_duration_days': result['avg_trade_duration']
                },
                'equity_curve': result['equity_curve']
            }
        except Exception as e:
            print(f"Error backtesting params {params}: {e}")
            return None

    def _check_constraint(self, params: Dict[str, Any], constraint: str) -> bool:
        """Check if parameters satisfy constraint"""
        try:
            # Replace parameter names with values
            eval_str = constraint
            for name, value in params.items():
                eval_str = eval_str.replace(name, str(value))
            return eval(eval_str)
        except:
            return True  # If constraint can't be evaluated, accept params

    def get_heatmap_data(self, param1: str, param2: str, objective: str = 'sharpe_ratio') -> pd.DataFrame:
        """Generate heatmap data for sensitivity analysis"""
        if not self.results:
            raise ValueError("No results available. Run optimize() first.")

        # Extract data
        data = []
        for result in self.results:
            data.append({
                param1: result['parameters'][param1],
                param2: result['parameters'][param2],
                objective: result['performance'][objective]
            })

        df = pd.DataFrame(data)
        heatmap = df.pivot(index=param2, columns=param1, values=objective)
        return heatmap
