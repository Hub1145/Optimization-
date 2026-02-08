# StrategyOptimizer API

A high-performance, cloud-ready API for trading strategy backtesting and optimization. Built with FastAPI, Celery, PostgreSQL, and Redis.

## 🚀 Features

- **Backtesting Engine**: Fast and accurate backtesting using `backtesting.py`.
- **Optimization Algorithms**:
  - **Grid Search**: Exhaustive search over a parameter space.
  - **Genetic Algorithms**: Evolutionary optimization for complex parameter spaces.
  - **Walk-Forward Analysis**: Validation technique to prevent overfitting by using rolling windows.
- **Strategy Management**:
  - **Pre-built Strategies**: RSI Mean Reversion, MACD + Bollinger Bands Combo.
  - **Custom Rules**: Input custom entry/exit logic via API strings.
- **Market Data Integration**: CCXT (Crypto) and yfinance (Stocks/Forex).
- **Asynchronous Execution**: Long-running jobs are handled by Celery workers.
- **Persistence**: Save and retrieve optimization results from PostgreSQL.

## 🛠️ Architecture

The system consists of several components:
1. **FastAPI Web Server**: Handles requests, job submission, and result retrieval.
2. **Celery Worker**: Executes the actual backtesting and optimization tasks.
3. **Redis**: Message broker for Celery and caching.
4. **PostgreSQL**: Stores job metadata, strategy configurations, and performance results.

## ⚙️ Configuration

The application uses `config.json` for configuration (overridable by environment variables).

```json
{
  "PROJECT_NAME": "StrategyOptimizer API",
  "API_V1_STR": "/api/v1",
  "POSTGRES_SERVER": "db",
  "POSTGRES_USER": "postgres",
  "POSTGRES_PASSWORD": "postgres",
  "POSTGRES_DB": "strategy_optimizer",
  "REDIS_URL": "redis://redis:6379/0",
  "CELERY_BROKER_URL": "redis://redis:6379/0",
  "CELERY_RESULT_BACKEND": "redis://redis:6379/0",
  "SECRET_KEY": "yoursecretkey"
}
```

## 📈 How It Works

### 1. Strategy Selection & Input

Users can interact with strategies in two ways:

- **Pre-built Strategies**: Select a pre-defined strategy by its ID (e.g., `rsi_mean_reversion`, `macd_bb_combo`).
- **Custom Strategies**: Input custom entry and exit rules as Python-style boolean expressions.
  - Example: `entry_rule: "RSI < rsi_oversold and price > EMA"`
  - The engine automatically resolves variables like `price`, `RSI`, `EMA`, `MACD`, etc.

### 2. Performing Optimization

Optimization is performed by sending a POST request to the relevant endpoint (`/optimize/grid-search`, `/optimize/genetic`, or `/optimize/walk-forward`).

- **Grid Search**: You provide a list of values for each parameter.
- **Genetic**: You provide min/max bounds for each parameter.
- **Walk-Forward**: You provide training/validation window sizes and step periods.

### 3. Optimization Criteria ("Best" Result)

The "best" strategy is determined by the `objective` parameter in your request. Supported objectives include:
- `sharpe_ratio` (Annualized risk-adjusted return)
- `total_return` (Absolute return percentage)
- `win_rate` (Percentage of winning trades)
- `profit_factor` (Gross Profit / Gross Loss)
- `max_drawdown` (The engine automatically tries to *minimize* this if selected)

## 🚦 Getting Started

### Using Docker (Recommended)

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`. You can access the interactive Swagger documentation at `http://localhost:8000/docs`.

## 📖 API Usage Example

**Submit a Grid Search Job:**

```json
POST /api/v1/optimize/grid-search
{
  "strategy": {
    "type": "rsi_mean_reversion"
  },
  "parameters": {
    "rsi_period": {"values": [10, 14, 21]},
    "rsi_oversold": {"values": [25, 30, 35]},
    "rsi_overbought": {"values": [65, 70, 75]}
  },
  "data": {
    "symbol": "BTC/USDT",
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "timeframe": "1d",
    "provider": "crypto"
  },
  "optimization": {
    "objective": "sharpe_ratio"
  }
}
```

**Get Results:**

```bash
GET /api/v1/results/{job_id}
GET /api/v1/results/{job_id}/results
```

## ⚠️ Security Note

This API uses a restricted `eval()` environment for custom rules. While limited, it is designed for trusted users. Always ensure your deployment environment is secured.

## 📄 License

MIT
