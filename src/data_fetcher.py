import yfinance as yf


def get_stock_data(ticker: str) -> dict:
    stock = yf.Ticker(ticker)

    info = stock.info
    history = stock.history(period="6mo")

    latest_price = None
    if not history.empty:
        latest_price = round(float(history["Close"].iloc[-1]), 2)

    return {
        "ticker": ticker,
        "name": info.get("longName"),
        "currency": info.get("currency"),
        "latest_price": latest_price,
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "eps": info.get("trailingEps"),
        "dividend_yield": info.get("dividendYield"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
        "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
        "average_volume": info.get("averageVolume"),
    }