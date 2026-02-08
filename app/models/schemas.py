from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime, date
from app.models.enums import JobStatus, OptimizationType, Objective, Timeframe

# Request schemas
class StrategyDefinition(BaseModel):
    type: str = Field(..., description="Strategy type (e.g., 'rsi_mean_reversion' or 'custom')")
    entry_rule: Optional[str] = Field(None, description="Entry rule for custom strategy")
    exit_rule: Optional[str] = Field(None, description="Exit rule for custom strategy")

class ParameterRange(BaseModel):
    """For grid search - discrete values"""
    values: List[float] = Field(..., min_items=2, max_items=20)

class ParameterBounds(BaseModel):
    """For genetic/Bayesian - continuous ranges"""
    min: float
    max: float
    step: Optional[float] = None

class DataConfig(BaseModel):
    symbol: str = Field(..., example="BTC/USDT")
    start_date: date
    end_date: date
    timeframe: Timeframe = Timeframe.DAY_1

class OptimizationConfig(BaseModel):
    objective: Objective = Objective.SHARPE_RATIO
    constraints: Optional[str] = Field(None, description="e.g., 'rsi_buy < rsi_sell'")
    max_combinations: Optional[int] = Field(500, ge=1, le=10000)

class GridSearchRequest(BaseModel):
    strategy: StrategyDefinition
    parameters: Dict[str, ParameterRange]
    data: DataConfig
    optimization: OptimizationConfig = OptimizationConfig()
    capital: float = Field(10000, gt=0)
    commission: float = Field(0.001, ge=0, le=0.1)
    slippage: float = Field(0.0005, ge=0, le=0.1)

class GeneticConfig(BaseModel):
    population_size: int = Field(50, ge=10, le=200)
    generations: int = Field(20, ge=5, le=100)
    mutation_rate: float = Field(0.15, ge=0, le=1)
    crossover_rate: float = Field(0.7, ge=0, le=1)

class GeneticAlgorithmRequest(BaseModel):
    strategy: StrategyDefinition
    parameters: Dict[str, ParameterBounds]
    data: DataConfig
    genetic_config: GeneticConfig = GeneticConfig()
    optimization: OptimizationConfig = OptimizationConfig()
    capital: float = 10000
    commission: float = 0.001
    slippage: float = 0.0005

class WalkForwardConfig(BaseModel):
    training_period_months: int = Field(12, ge=3, le=60)
    validation_period_months: int = Field(3, ge=1, le=12)
    step_months: int = Field(3, ge=1, le=12)
    anchored: bool = Field(False, description="True=expanding window, False=rolling")

class WalkForwardRequest(BaseModel):
    strategy: StrategyDefinition
    parameters: Dict[str, ParameterRange]
    data: DataConfig
    walk_forward_config: WalkForwardConfig = WalkForwardConfig()
    optimization: OptimizationConfig = OptimizationConfig()
    capital: float = 10000
    commission: float = 0.001
    slippage: float = 0.0005

# Response schemas
class PerformanceMetrics(BaseModel):
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    avg_trade_duration_days: float
    calmar_ratio: Optional[float] = None
    sortino_ratio: Optional[float] = None

class OptimizationResultSchema(BaseModel):
    parameters: Dict[str, Any]
    performance: PerformanceMetrics
    equity_curve: Optional[List[Dict[str, Any]]] = None
    is_best: bool = False

class GridSearchResponse(BaseModel):
    job_id: str
    status: JobStatus
    best_parameters: Dict[str, Any]
    best_performance: PerformanceMetrics
    top_10_combinations: List[OptimizationResultSchema]
    total_combinations_tested: int
    computation_time_seconds: float

class WalkForwardPeriodResult(BaseModel):
    period_number: int
    training_start: date
    training_end: date
    validation_start: date
    validation_end: date
    best_parameters: Dict[str, Any]
    in_sample_sharpe: float
    out_sample_sharpe: float

class WalkForwardResponse(BaseModel):
    job_id: str
    status: JobStatus
    in_sample_performance: PerformanceMetrics
    out_of_sample_performance: PerformanceMetrics
    degradation_factor: float
    stability_score: float
    periods: List[WalkForwardPeriodResult]
    computation_time_seconds: float

# Job status response
class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    job_type: OptimizationType
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    progress_percent: Optional[int] = None
