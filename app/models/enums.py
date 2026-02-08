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
    MIN_3 = "3m"
    MIN_5 = "5m"
    MIN_15 = "15m"
    MIN_30 = "30m"
    HOUR_1 = "1h"
    HOUR_2 = "2h"
    HOUR_4 = "4h"
    HOUR_6 = "6h"
    HOUR_8 = "8h"
    HOUR_12 = "12h"
    DAY_1 = "1d"
    DAY_3 = "3d"
    WEEK_1 = "1w"
    MONTH_1 = "1M"
