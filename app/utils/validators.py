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
