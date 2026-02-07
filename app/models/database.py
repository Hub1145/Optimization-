from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, ARRAY, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    tier = Column(String(50), default="free")
    api_key = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    jobs = relationship("OptimizationJob", back_populates="user", cascade="all, delete-orphan")
    usage = relationship("APIUsage", back_populates="user", cascade="all, delete-orphan")

class OptimizationJob(Base):
    __tablename__ = "optimization_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(String(50), default="pending", index=True)
    job_type = Column(String(50), nullable=False)
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)

    # Relationships
    user = relationship("User", back_populates="jobs")
    config = relationship("StrategyConfig", back_populates="job", uselist=False, cascade="all, delete-orphan")
    results = relationship("OptimizationResult", back_populates="job", cascade="all, delete-orphan")
    walk_forward_periods = relationship("WalkForwardPeriod", back_populates="job", cascade="all, delete-orphan")

class StrategyConfig(Base):
    __tablename__ = "strategy_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("optimization_jobs.id"), nullable=False)
    strategy_type = Column(String(100), nullable=False)
    entry_rule = Column(Text, nullable=False)
    exit_rule = Column(Text, nullable=False)
    parameters = Column(JSON, nullable=False)
    data_config = Column(JSON, nullable=False)
    optimization_config = Column(JSON, nullable=False)
    capital = Column(Float, default=10000)
    commission = Column(Float, default=0.001)
    slippage = Column(Float, default=0.0005)

    # Relationships
    job = relationship("OptimizationJob", back_populates="config")

class OptimizationResult(Base):
    __tablename__ = "optimization_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("optimization_jobs.id"), nullable=False, index=True)
    parameters = Column(JSON, nullable=False)
    total_return = Column(Float)
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)
    win_rate = Column(Float)
    profit_factor = Column(Float)
    total_trades = Column(Integer)
    avg_trade_duration_days = Column(Float)
    is_best = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    job = relationship("OptimizationJob", back_populates="results")
    equity_curve = relationship("EquityCurve", back_populates="result", uselist=False, cascade="all, delete-orphan")

class EquityCurve(Base):
    __tablename__ = "equity_curves"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    result_id = Column(UUID(as_uuid=True), ForeignKey("optimization_results.id"), nullable=False)
    data = Column(JSON, nullable=False)
    file_url = Column(String(500))

    # Relationships
    result = relationship("OptimizationResult", back_populates="equity_curve")

class WalkForwardPeriod(Base):
    __tablename__ = "walk_forward_periods"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("optimization_jobs.id"), nullable=False)
    period_number = Column(Integer, nullable=False)
    training_start = Column(DateTime, nullable=False)
    training_end = Column(DateTime, nullable=False)
    validation_start = Column(DateTime, nullable=False)
    validation_end = Column(DateTime, nullable=False)
    best_parameters = Column(JSON, nullable=False)
    in_sample_sharpe = Column(Float)
    out_sample_sharpe = Column(Float)
    degradation_factor = Column(Float)

    # Relationships
    job = relationship("OptimizationJob", back_populates="walk_forward_periods")

class PrebuiltStrategy(Base):
    __tablename__ = "prebuilt_strategies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    strategy_type = Column(String(100), nullable=False)
    parameters = Column(JSON, nullable=False)
    recommended_symbols = Column(ARRAY(String))
    recommended_timeframe = Column(String(10))
    backtest_period = Column(String(50))
    sharpe_ratio = Column(Float)
    total_return = Column(Float)
    max_drawdown = Column(Float)
    tier_required = Column(String(50), default="free")
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class APIUsage(Base):
    __tablename__ = "api_usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    endpoint = Column(String(200), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    response_time_ms = Column(Integer)
    status_code = Column(Integer)

    # Relationships
    user = relationship("User", back_populates="usage")
