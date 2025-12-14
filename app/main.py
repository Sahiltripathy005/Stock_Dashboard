from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from app.database import SessionLocal, engine
from app import models
import os



app = FastAPI(title="Stock Data Intelligence API")
models.Base.metadata.create_all(bind=engine)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def load_data_on_startup():
    db = SessionLocal()

    existing = db.query(models.StockData).first()
    if existing:
        db.close()
        print("Database already initialized")
        return

    print("Initializing database from CSV...")

    csv_path = "data/csv/all_stocks_5yr.csv"
    if not os.path.exists(csv_path):
        print("CSV not found, skipping initialization")
        db.close()
        return

    df = pd.read_csv(csv_path)

    df.columns = [c.capitalize() for c in df.columns]
    df.rename(columns={"Name": "Symbol"}, inplace=True)

    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
    df = df[df["Symbol"].isin(symbols)]

    df["Date"] = pd.to_datetime(df["Date"])

    for _, row in df.iterrows():
        record = models.StockData(
            symbol=row["Symbol"],
            date=row["Date"].date(),
            open=row["Open"],
            high=row["High"],
            low=row["Low"],
            close=row["Close"],
            volume=row["Volume"]
        )
        db.add(record)

    db.commit()
    db.close()
    print("Database initialized successfully")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Stock Data API is running"}

@app.get("/companies")
def get_companies(db: Session = Depends(get_db)):
    result = db.query(models.StockData.symbol).distinct().all()
    return [row[0] for row in result]

@app.get("/data/{symbol}")
def get_stock_data(symbol: str, db: Session = Depends(get_db)):
    records = (
        db.query(models.StockData)
        .filter(models.StockData.symbol == symbol.strip().upper())
        .order_by(models.StockData.date.asc())   
        .limit(60)                              
        .all()
    )

    if not records:
        return {"error": "Symbol not found"}

    records = records[-30:]

    return [
        {
            "date": r.date.isoformat(),
            "open": r.open,
            "high": r.high,
            "low": r.low,
            "close": r.close,
            "volume": r.volume,
            "daily_return": r.daily_return,
            "ma_7": r.ma_7,
            "volatility": r.volatility,
        }
        for r in records
    ]



@app.get("/summary/{symbol}")
def get_summary(symbol: str, db: Session = Depends(get_db)):
    data = (
        db.query(models.StockData.close)
        .filter(models.StockData.symbol == symbol.strip().upper())
        .all()
    )

    if not data:
        return {"error": "Symbol not found"}

    closes = [row[0] for row in data]

    return {
        "symbol": symbol.upper(),
        "52_week_high": max(closes),
        "52_week_low": min(closes),
        "average_close": sum(closes) / len(closes)
    }


@app.get("/compare")
def compare_stocks(symbol1: str, symbol2: str, db: Session = Depends(get_db)):
    def get_closes(symbol: str):
        rows = (
            db.query(models.StockData.close)
            .filter(
                models.StockData.symbol == symbol.strip().upper(),
                models.StockData.close.isnot(None)
            )
            .order_by(models.StockData.date)
            .all()
        )
        return [row[0] for row in rows if row[0] is not None]

    s1_vals = get_closes(symbol1)
    s2_vals = get_closes(symbol2)

    if len(s1_vals) < 2 or len(s2_vals) < 2:
        return {
            "error": "Insufficient historical data for comparison",
            "symbol1_points": len(s1_vals),
            "symbol2_points": len(s2_vals)
        }

    return {
        "comparison_window": "Full available overlapping history",
        symbol1.upper(): {
            "start_close": s1_vals[0],
            "end_close": s1_vals[-1],
            "return": (s1_vals[-1] - s1_vals[0]) / s1_vals[0]
        },
        symbol2.upper(): {
            "start_close": s2_vals[0],
            "end_close": s2_vals[-1],
            "return": (s2_vals[-1] - s2_vals[0]) / s2_vals[0]
        }
    }


@app.get("/debug/symbols")
def debug_symbols(db: Session = Depends(get_db)):
    rows = db.query(models.StockData.symbol).limit(20).all()
    return [row[0] for row in rows]

@app.get("/debug/db_summary")
def db_summary(db: Session = Depends(get_db)):
    rows = (
        db.query(models.StockData.symbol, models.StockData.date)
        .order_by(models.StockData.symbol)
        .limit(20)
        .all()
    )

    return [
        {
            "symbol": r[0],
            "date": r[1].isoformat() if r[1] else None
        }
        for r in rows
    ]
