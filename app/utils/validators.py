from typing import Any, Dict
import pandas as pd

def validate_ohlcv_data(df: pd.DataFrame):
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    if df.isnull().values.any():
        # Log warning or handle
        pass

    return True

def validate_strategy_params(params: Dict[str, Any], schema: Dict[str, Any]):
    # Basic validation logic
    for key, value in schema.items():
        if key not in params:
            raise ValueError(f"Missing parameter: {key}")
    return True

def validate_date_range(start_date, end_date, max_days: int):
    from datetime import datetime, date

    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    elif isinstance(start_date, datetime):
        start_date = start_date.date()

    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    elif isinstance(end_date, datetime):
        end_date = end_date.date()

    delta = end_date - start_date
    if delta.days > max_days:
        raise ValueError(f"Requested data range ({delta.days} days) exceeds maximum allowed limit of {max_days} days.")
    if delta.days < 0:
        raise ValueError("End date must be after start date.")
    return True
