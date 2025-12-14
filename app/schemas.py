from pydantic import BaseModel
from datetime import date
from typing import Optional

class StockDataSchema(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: float
    daily_return: Optional[float]
    ma_7: Optional[float]
    volatility: Optional[float]

    class Config:
        from_attributes = True
