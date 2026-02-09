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

### 2. Crypto Focus & Flexible Timeframes
The API currently focuses on **Crypto data** fetched from **Binance** via CCXT. It supports a wide range of timeframes:
- **Minutes**: `1m`, `3m`, `5m`, `15m`, `30m`
- **Hours**: `1h`, `2h`, `4h`, `6h`, `8h`, `12h`
- **Days**: `1d`, `3d`
- **Weeks/Months**: `1w`, `1M`

### 3. Data Usage Limits
To ensure high performance and prevent long optimization times, the API enforces historical data limits:
- **Maximum Data Range**: 365 days (configurable in `config.json` via `MAX_DATA_DAYS`).
- This limit applies to both single backtests and all optimization methods.

### 3. Comprehensive Metrics
The API calculates and returns professional-grade metrics:
- **Performance**: Total Return, Sharpe Ratio, Sortino Ratio, Calmar Ratio, Profit Factor, Win Rate.
- **Trade Statistics**: Total Trades, Winning/Losing counts, Avg Win/Loss, Max Win/Loss Streaks, Avg Duration.
- **Risk Metrics**: Value at Risk (VaR 95%), Conditional VaR (CVaR).

### 4. ML-Powered Strategy Selection
Utilizes a weighted normalization model to score strategies:
`Score = (Profit * 0.35) + (WinRate * 0.25) + (ProfitFactor * 0.25) - (LossStreak * 0.15)`

### 5. Real-time Monitoring
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
3. **Run Manually**:
```bash
pip install -r requirements.txt
python main.py
```

The API will be available at `http://localhost:5000`. You can access the interactive Swagger documentation at `http://localhost:5000/docs`.

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
