from enum import Enum

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class OptimizationType(str, Enum):
    GRID_SEARCH = "grid_search"
    GENETIC = "genetic"
    WALK_FORWARD = "walk_forward"
    MONTE_CARLO = "monte_carlo"
    SENSITIVITY = "sensitivity"

class Objective(str, Enum):
    SHARPE_RATIO = "sharpe_ratio"
    TOTAL_RETURN = "total_return"
    WIN_RATE = "win_rate"
    PROFIT_FACTOR = "profit_factor"
    CALMAR_RATIO = "calmar_ratio"

class Timeframe(str, Enum):
    MIN_1 = "1m"
    MIN_5 = "5m"
    MIN_15 = "15m"
    MIN_30 = "30m"
    HOUR_1 = "1h"
    HOUR_4 = "4h"
    DAY_1 = "1d"
