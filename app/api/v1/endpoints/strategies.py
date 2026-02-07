from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.models.database import PrebuiltStrategy
from app.dependencies import get_db

router = APIRouter()

class StrategyInfo(BaseModel):
    id: str
    name: str
    description: str
    type: str

@router.get("/", response_model=List[StrategyInfo])
def list_strategies(db: Session = Depends(get_db)):
    strategies = db.query(PrebuiltStrategy).all()
    if not strategies:
        # Fallback to defaults if DB is empty
        return [
            StrategyInfo(id="1", name="RSI Mean Reversion", description="Buy when RSI is oversold, sell when overbought", type="rsi_mean_reversion"),
            StrategyInfo(id="2", name="EMA Crossover", description="Golden cross / Death cross", type="ema_crossover"),
            StrategyInfo(id="3", name="Bollinger Breakout", description="Trade breakouts of Bollinger Bands", type="bollinger_breakout"),
            StrategyInfo(id="4", name="MACD Divergence", description="Trade MACD divergences", type="macd_divergence")
        ]

    return [
        StrategyInfo(
            id=str(s.id),
            name=s.name,
            description=s.description,
            type=s.strategy_type
        ) for s in strategies
    ]
