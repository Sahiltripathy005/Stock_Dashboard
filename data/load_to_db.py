import pandas as pd
from app.database import SessionLocal, engine
from app.models import StockData
from app.database import Base

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
            daily_return=row["Daily_Return"],
            ma_7=row["MA_7"],
            high_52w=row["High_52W"],
            low_52w=row["Low_52W"],
            volatility=row["Volatility"]
        )
        db.add(record)

    db.commit()
    db.close()
    print("Data loaded into database successfully.")

if __name__ == "__main__":
    main()
