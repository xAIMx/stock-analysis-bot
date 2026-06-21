import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


def get_stock_data(ticker: str, period: str = "2y") -> dict:
    """Henter omfattende aktiedata fra yfinance"""
    stock = yf.Ticker(ticker)
    info = stock.info
    history = stock.history(period=period)

    latest_price = None
    if not history.empty:
        latest_price = round(float(history["Close"].iloc[-1]), 2)

    # Beregn yderligere metriker
    data = {
        "ticker": ticker,
        "name": info.get("longName"),
        "currency": info.get("currency"),
        "latest_price": latest_price,
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "eps": info.get("trailingEps"),
        "forward_eps": info.get("epsTrailingTwelveMonths"),
        "dividend_yield": info.get("dividendYield"),
        "payout_ratio": info.get("payoutRatio"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
        "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
        "average_volume": info.get("averageVolume"),
        "beta": info.get("beta"),
        "pb_ratio": info.get("priceToBook"),
        "ps_ratio": info.get("priceToSalesTrailing12Months"),
        "peg_ratio": info.get("pegRatio"),
        "ev_ebitda": info.get("enterpriseToEbitda"),
        "debt_to_equity": info.get("debtToEquity"),
        "current_ratio": info.get("currentRatio"),
        "quick_ratio": info.get("quickRatio"),
        "return_on_equity": info.get("returnOnEquity"),
        "return_on_assets": info.get("returnOnAssets"),
        "profit_margins": info.get("profitMargins"),
        "operating_margin": info.get("operatingMargins"),
        "net_margin": info.get("netIncomeToCommon"),
        "revenue": info.get("totalRevenue"),
        "revenue_growth": info.get("revenueGrowth"),
        "earnings_growth": info.get("earningsGrowth"),
        "fcf_yield": info.get("freeCashflow"),
        "total_debt": info.get("totalDebt"),
        "total_cash": info.get("totalCash"),
        "current_assets": info.get("currentAssets"),
        "current_liabilities": info.get("currentLiabilities"),
        "interest_expense": info.get("interestExpense"),
        "ebitda": info.get("ebitda"),
        "rd_expense": info.get("researchDevelopment"),
        "shares_outstanding": info.get("sharesOutstanding"),
        "book_value": info.get("bookValue"),
    }

    # Beregn afledt data
    if history is not None and not history.empty and len(history) > 0:
        # Volatilitet (30-dages)
        returns = history["Close"].pct_change()
        volatility_30d = returns.tail(30).std() if len(history) >= 30 else returns.std()
        data["volatility"] = volatility_30d

        # Max Drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        data["max_drawdown"] = max_drawdown

        # Sharpe Ratio (årlig risikofri rente ~4%)
        annual_return = returns.mean() * 252
        annual_volatility = returns.std() * np.sqrt(252)
        risk_free_rate = 0.04
        if annual_volatility > 0:
            sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility
        else:
            sharpe_ratio = 0
        data["sharpe_ratio"] = sharpe_ratio

    # Beregn yderligere finansielle nøgletal
    if data["total_debt"] and data["total_cash"] and data["market_cap"]:
        net_debt = data["total_debt"] - data["total_cash"]
        data["net_debt"] = net_debt
        if data["ebitda"] and data["ebitda"] > 0:
            data["debt_to_ebitda"] = net_debt / data["ebitda"]
        if data["ebitda"] and data["interest_expense"] and data["interest_expense"] > 0:
            data["interest_coverage_ratio"] = data["ebitda"] / data["interest_expense"]

    if data["revenue"] and data["shares_outstanding"]:
        revenue_per_share = data["revenue"] / data["shares_outstanding"]
        data["revenue_per_share"] = revenue_per_share

    # FCF Yield
    free_cash_flow = info.get("freeCashflow")
    if free_cash_flow and data["market_cap"] and data["market_cap"] > 0:
        data["fcf_yield"] = free_cash_flow / data["market_cap"]

    # ROE, ROA beregninger hvis data tilgængelig
    if data["book_value"] and data["latest_price"]:
        data["return_on_equity"] = info.get("returnOnEquity")
        data["return_on_assets"] = info.get("returnOnAssets")

    # ROIC (Return on Invested Capital)
    if data["ebitda"] and data["total_debt"] and data["book_value"]:
        nopat = data["ebitda"] * 0.75  # Antag 25% skattesats
        invested_capital = data["total_debt"] + data["book_value"]
        if invested_capital > 0:
            data["return_on_invested_capital"] = nopat / invested_capital

    # Asset Turnover
    if data["revenue"] and data["book_value"]:
        data["asset_turnover"] = data["revenue"] / data["book_value"]

    # EPS Growth og Revenue Growth
    data["eps_growth"] = info.get("epsTrailingTwelveMonths")

    # Forward estimates
    target_mean_price = info.get("targetMeanPrice")
    if target_mean_price and latest_price:
        expected_return = (target_mean_price - latest_price) / latest_price
        data["next_year_growth_estimate"] = expected_return

    return data