# StrategyOptimizer API

A professional, high-performance trading strategy optimization service.

## 📁 Project Architecture

```
optimization-api/
├── app/
│   ├── api/                   # FastAPI endpoints (REST + WebSocket)
│   ├── core/
│   │   ├── backtester/        # Engine & performance metrics
│   │   ├── optimizers/        # Grid Search, Genetic, Walk-Forward, Monte Carlo
│   │   ├── strategies/        # Pre-built & Custom templates
│   │   └── data/              # Market data fetchers (CCXT, yfinance)
│   ├── models/                # DB & Pydantic schemas
│   ├── services/              # Redis, Celery, Storage
│   └── workers/               # Async task processing
```

## 🚀 Key Features

### 1. Multiple Optimization Methods
- **Grid Search**: Exhaustive parameter sweep.
- **Genetic Algorithm**: Evolutionary optimization for large parameter spaces.
- **Walk-Forward Analysis**: Robustness validation using rolling windows to prevent overfitting.
- **Monte Carlo Simulation**: Stress testing by trade order randomization.

### 2. Comprehensive Metrics
The API calculates and returns professional-grade metrics:
- **Performance**: Total Return, Sharpe Ratio, Sortino Ratio, Calmar Ratio, Profit Factor, Win Rate.
- **Trade Statistics**: Total Trades, Winning/Losing counts, Avg Win/Loss, Max Win/Loss Streaks, Avg Duration.
- **Risk Metrics**: Value at Risk (VaR 95%), Conditional VaR (CVaR).

### 3. ML-Powered Strategy Selection
Utilizes a weighted normalization model to score strategies:
`Score = (Profit * 0.35) + (WinRate * 0.25) + (ProfitFactor * 0.25) - (LossStreak * 0.15)`

### 4. Real-time Monitoring
WebSocket support for streaming job progress and status updates:
`ws://[host]/api/v1/optimization/{job_id}/stream`

## 🛠️ Tech Stack
- **FastAPI**: Modern, async web framework.
- **Celery + Redis**: Background task queue.
- **PostgreSQL**: Result persistence.
- **backtesting.py**: Core execution engine.
- **TA-Lib**: Technical indicator library.

## 🚦 Getting Started

1. **Configuration**: Edit `config.json` with your credentials.
2. **Run with Docker**:
```bash
docker-compose up --build
```

## 📖 API Usage Guide

### Submit Optimization Job
`POST /api/v1/optimization/start`
```json
{
  "strategy": { "type": "rsi_mean_reversion" },
  "parameters": {
    "rsi_period": { "values": [14, 21] },
    "rsi_oversold": { "values": [30, 40] }
  },
  "data": {
    "symbol": "BTC/USDT",
    "start_date": "2023-01-01",
    "end_date": "2023-12-31"
  },
  "optimization": { "objective": "sharpe_ratio" }
}
```

### Get Results
`GET /api/v1/optimization/{job_id}/results`

## 💼 User Tiers & Business Model
- **Free**: 10 optimizations/mo, Grid Search only, 1yr data.
- **Pro**: 100 optimizations/mo, All methods, 5yr data, Walk-Forward/Monte Carlo.
- **Enterprise**: Unlimited, Custom data, Dedicated workers.
