import yfinance as yf


def get_stock_data(ticker: str) -> dict:
    stock = yf.Ticker(ticker)

    info = stock.info
    history = stock.history(period="1y")  # 1 år for at få 200-dages gennemsnit

    latest_price = None
    if not history.empty:
        # Find seneste valid close price (dropna for at håndtere missing data)
        valid_closes = history["Close"].dropna()
        if not valid_closes.empty:
            latest_price = round(float(valid_closes.iloc[-1]), 2)

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
        "history": history,  # Tilføj historisk data for teknisk analyse
        # Expert ratings fra yfinance
        "recommendation_mean": info.get("recommendationMean"),
        "recommendation_key": info.get("recommendationKey"),
        "number_of_analysts": info.get("numberOfAnalystOpinions"),
        "target_mean_price": info.get("targetMeanPrice"),
        "target_median_price": info.get("targetMedianPrice"),
        "target_high_price": info.get("targetHighPrice"),
        "target_low_price": info.get("targetLowPrice"),
    }