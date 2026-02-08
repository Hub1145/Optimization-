import numpy as np
import pandas as pd
from typing import List, Dict, Any

class MonteCarloSimulator:
    """
    Robustness testing by trade order randomization.
    """

    def __init__(self, trades: List[Dict[str, Any]], start_balance: float = 10000):
        self.trades_df = pd.DataFrame(trades)
        self.start_balance = start_balance

    def run(self, n_simulations: int = 1000) -> Dict[str, Any]:
        if self.trades_df.empty:
            return {}

        pnls = self.trades_df['PnL'].values
        all_final_balances = []
        all_max_drawdowns = []

        for _ in range(n_simulations):
            # Shuffle trades
            shuffled_pnls = np.random.permutation(pnls)

            # Calculate equity curve
            equity = self.start_balance + np.cumsum(shuffled_pnls)
            equity = np.insert(equity, 0, self.start_balance)

            # Final balance
            all_final_balances.append(equity[-1])

            # Max Drawdown
            rolling_max = np.maximum.accumulate(equity)
            drawdowns = (equity - rolling_max) / rolling_max
            all_max_drawdowns.append(abs(np.min(drawdowns)))

        return {
            'mean_final_balance': float(np.mean(all_final_balances)),
            'median_final_balance': float(np.median(all_final_balances)),
            'std_final_balance': float(np.std(all_final_balances)),
            'worst_case_final_balance': float(np.min(all_final_balances)),
            'best_case_final_balance': float(np.max(all_final_balances)),
            'mean_max_drawdown': float(np.mean(all_max_drawdowns)),
            'max_max_drawdown': float(np.max(all_max_drawdowns)),
            'probability_profitable': float(sum(b > self.start_balance for b in all_final_balances) / n_simulations),
            'var_95_final_balance': float(np.percentile(all_final_balances, 5))
        }
