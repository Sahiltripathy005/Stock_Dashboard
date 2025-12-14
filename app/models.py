from sqlalchemy import Column, Integer, Float, String, Date
from app.database import Base

class StockData(Base):
    __tablename__ = "stock_data"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    date = Column(Date, index=True)

    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)

    daily_return = Column(Float)
    ma_7 = Column(Float)
    high_52w = Column(Float)
    low_52w = Column(Float)
    volatility = Column(Float)
