from app.core.strategies.rsi_mean_reversion import RSIMeanReversion
from app.core.strategies.macd_bb_combo import MACDBBCombo

STRATEGY_REGISTRY = {
    "rsi_mean_reversion": RSIMeanReversion,
    "macd_bb_combo": MACDBBCombo,
}

def get_strategy_class(strategy_type: str):
    return STRATEGY_REGISTRY.get(strategy_type)
