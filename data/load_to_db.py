import pandas as pd
from app.database import SessionLocal, engine, Base
from app.models import StockData

# Create tables
Base.metadata.create_all(bind=engine)

def main():
    df = pd.read_csv("data/stocks_processed.csv")

    db = SessionLocal()

    for _, row in df.iterrows():
        record = StockData(
            symbol=row["Symbol"],
            date=pd.to_datetime(row["Date"]).date(),
            open=row["Open"],
            high=row["High"],
            low=row["Low"],
            close=row["Close"],
            volume=row["Volume"],
            daily_return=row["daily_return"],
            ma_7=row["ma_7"],
            high_52w=row["high_52w"],
            low_52w=row["low_52w"],
            volatility=row["volatility"]
        )
        db.add(record)

    db.commit()
    db.close()
    print("✅ Data loaded into database successfully.")

if __name__ == "__main__":
    main()
