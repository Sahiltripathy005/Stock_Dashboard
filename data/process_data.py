import pandas as pd
import numpy as np

def clean_data(df):
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    df["Symbol"] = df["Symbol"].astype(str).str.strip().str.upper()

    numeric_cols = ["Open", "High", "Low", "Close", "Volume"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values(by=["Symbol", "Date"])

    df[numeric_cols] = (
        df.groupby("Symbol")[numeric_cols]
        .apply(lambda x: x.ffill().bfill())
        .reset_index(level=0, drop=True)
    )

    df = df.dropna(subset=["Date"])

    return df




def add_metrics(df):
    # Always sort before rolling 
    df = df.sort_values(["Symbol", "Date"])

    # Daily Return
    df["daily_return"] = (df["Close"] - df["Open"]) / df["Open"]

    # 7-day Moving Average
    df["ma_7"] = df.groupby("Symbol")["Close"].transform(
        lambda x: x.rolling(window=7, min_periods=7).mean()
    )

    # 52-week High / Low 
    df["high_52w"] = df.groupby("Symbol")["High"].transform("max")
    df["low_52w"] = df.groupby("Symbol")["Low"].transform("min")

    # Volatility = rolling std dev of daily returns (7-day window)
    df["volatility"] = df.groupby("Symbol")["daily_return"].transform(
        lambda x: x.rolling(window=7, min_periods=7).std()
    )

    return df


def main():
    df = pd.read_csv("data/stocks_raw.csv")
    df = clean_data(df)
    df = add_metrics(df)

    df.to_csv("data/stocks_processed.csv", index=False)
    print("Processed data saved to data/stocks_processed.csv")

if __name__ == "__main__":
    main()
