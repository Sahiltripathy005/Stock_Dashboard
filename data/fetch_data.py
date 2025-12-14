import pandas as pd

VALID_SYMBOLS = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]

def main():
    df = pd.read_csv("data/csv/all_stocks_5yr.csv")

    df.columns = [c.capitalize() for c in df.columns]

    df.rename(columns={
        "Date": "Date",
        "Open": "Open",
        "High": "High",
        "Low": "Low",
        "Close": "Close",
        "Volume": "Volume",
        "Name": "Symbol"
    }, inplace=True)

    df = df[df["Symbol"].isin(VALID_SYMBOLS)]

    df["Date"] = pd.to_datetime(df["Date"])

    df.to_csv("data/stocks_raw.csv", index=False)
    print("✅ CSV loaded → stocks_raw.csv")
    print("Symbols:", df["Symbol"].unique())

if __name__ == "__main__":
    main()
