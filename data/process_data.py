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
    df["Daily_Return"] = (df["Close"] - df["Open"]) / df["Open"]

    df["MA_7"] = df.groupby("Symbol")["Close"].transform(
        lambda x: x.rolling(window=7).mean()
    )

    df["High_52W"] = df.groupby("Symbol")["High"].transform("max")
    df["Low_52W"] = df.groupby("Symbol")["Low"].transform("min")

    df["Volatility"] = df.groupby("Symbol")["Daily_Return"].transform(
        lambda x: x.rolling(window=30).std()
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
