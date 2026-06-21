import pandas as pd
import numpy as np


def calculate_rsi(prices, period=14):
    """
    Beregner Relative Strength Index (RSI).
    RSI måler momentum: værdi mellem 0-100.
    Over 70 = overbought, under 30 = oversold.
    """
    if len(prices) < period:
        return None

    deltas = np.diff(prices)
    seed = deltas[:period + 1]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi = 100 - (100 / (1 + rs))

    for i in range(period + 1, len(deltas)):
        delta = deltas[i]
        if delta > 0:
            upval = delta
            downval = 0
        else:
            upval = 0
            downval = -delta

        up = (up * (period - 1) + upval) / period
        down = (down * (period - 1) + downval) / period

        rs = up / down if down != 0 else 0
        rsi = 100 - (100 / (1 + rs))

    return round(rsi, 2)


def calculate_momentum(prices, period=10):
    """
    Beregner Momentum - forholdet mellem nuværende pris og pris N perioder tilbage.
    Positive værdi = optrend, negativ = nedtrend.
    """
    if len(prices) < period:
        return None

    momentum = ((prices[-1] - prices[-period - 1]) / prices[-period - 1]) * 100
    return round(momentum, 2)


def calculate_macd(prices, fast=12, slow=26, signal=9):
    """
    Beregner MACD (Moving Average Convergence Divergence)
    Returnerer dict med macd, signal og histogram
    """
    if len(prices) < slow:
        return None

    ema_fast = pd.Series(prices).ewm(span=fast).mean().values
    ema_slow = pd.Series(prices).ewm(span=slow).mean().values
    
    macd_line = ema_fast - ema_slow
    signal_line = pd.Series(macd_line).ewm(span=signal).mean().values
    histogram = macd_line - signal_line

    return {
        "macd": round(float(macd_line[-1]), 4),
        "signal": round(float(signal_line[-1]), 4),
        "histogram": round(float(histogram[-1]), 4),
    }


def calculate_bollinger_bands(prices, period=20, std_dev=2):
    """
    Beregner Bollinger Bands
    Returnerer øvre band, midterlinje (SMA) og nedre band
    """
    if len(prices) < period:
        return None

    sma = prices[-period:].mean()
    std = prices[-period:].std()
    
    upper_band = sma + (std_dev * std)
    lower_band = sma - (std_dev * std)

    return {
        "upper": round(upper_band, 2),
        "middle": round(sma, 2),
        "lower": round(lower_band, 2),
    }


def calculate_price_changes(history_df):
    """
    Beregner prisændringer over forskellige perioder
    """
    if history_df is None or len(history_df) == 0:
        return {}

    valid_closes = history_df["Close"].dropna()
    if len(valid_closes) == 0:
        return {}

    prices = valid_closes.values
    current_price = prices[-1]
    
    changes = {}

    # 1 måned (cirka 21-22 handelsdage)
    if len(prices) >= 22:
        price_1m_ago = prices[-22]
        changes["price_change_1m"] = (current_price - price_1m_ago) / price_1m_ago

    # 3 måneder (cirka 63-65 handelsdage)
    if len(prices) >= 65:
        price_3m_ago = prices[-65]
        changes["price_change_3m"] = (current_price - price_3m_ago) / price_3m_ago

    # 6 måneder (cirka 130-132 handelsdage)
    if len(prices) >= 132:
        price_6m_ago = prices[-132]
        changes["price_change_6m"] = (current_price - price_6m_ago) / price_6m_ago

    # 1 år (cirka 252 handelsdage)
    if len(prices) >= 252:
        price_1y_ago = prices[-252]
        changes["price_change_1y"] = (current_price - price_1y_ago) / price_1y_ago

    return changes


def calculate_technical_indicators(history_df):
    """
    Beregner alle tekniske indikatorer fra historiske prisdata.
    Returnerer dict med alle indikatorer.
    """
    if history_df is None or len(history_df) == 0:
        return None

    # Fjern NaN værdier for at få valid prices
    valid_closes = history_df["Close"].dropna()
    if len(valid_closes) == 0:
        return None
    
    prices = valid_closes.values
    current_price = prices[-1]

    # Beregn glidende gennemsnit
    sma50 = prices[-50:].mean() if len(prices) >= 50 else None
    sma200 = prices[-200:].mean() if len(prices) >= 200 else None
    ema12 = pd.Series(prices).ewm(span=12).mean().values[-1] if len(prices) >= 12 else None

    # Beregn RSI
    rsi = calculate_rsi(prices, period=14)

    # Beregn Momentum
    momentum = calculate_momentum(prices, period=10)

    # Beregn MACD
    macd = calculate_macd(prices)

    # Beregn Bollinger Bands
    bollinger = calculate_bollinger_bands(prices, period=20, std_dev=2)

    # Beregn prisændringer
    price_changes = calculate_price_changes(history_df)

    indicators = {
        "current_price": round(current_price, 2),
        "sma50": round(sma50, 2) if sma50 else None,
        "sma200": round(sma200, 2) if sma200 else None,
        "ema12": round(ema12, 2) if ema12 else None,
        "rsi": rsi,
        "momentum": momentum,
        "macd": macd,
    }

    if bollinger:
        indicators["bollinger_upper"] = bollinger["upper"]
        indicators["bollinger_middle"] = bollinger["middle"]
        indicators["bollinger_lower"] = bollinger["lower"]

    indicators.update(price_changes)

    return indicators


def calculate_technical_score(indicators: dict) -> int:
    """
    Beregner Technical Score (0-100) baseret på:
    - Pris i forhold til SMA50 (25 point)
    - Pris i forhold til SMA200 (25 point)
    - RSI niveau (25 point)
    - Momentum retning (25 point)
    """
    if indicators is None:
        return 0

    score = 0
    current_price = indicators.get("current_price", 0)
    sma50 = indicators.get("sma50")
    sma200 = indicators.get("sma200")
    rsi = indicators.get("rsi")
    momentum = indicators.get("momentum")

    # SMA50: Hvis pris over SMA50 = bullish kortsigtet (25 point)
    if sma50 and current_price > sma50:
        score += 25
    elif sma50 and current_price > sma50 * 0.95:
        score += 12

    # SMA200: Hvis pris over SMA200 = bullish langsigtet (25 point)
    if sma200 and current_price > sma200:
        score += 25
    elif sma200 and current_price > sma200 * 0.95:
        score += 12

    # RSI: Ikke overbought/oversold (25 point)
    # Ideelt 30-70, godt 40-60
    if rsi:
        if 40 <= rsi <= 60:
            score += 25
        elif 30 <= rsi <= 70:
            score += 15
        elif 20 <= rsi <= 80:
            score += 8

    # Momentum: Positiv trend (25 point)
    if momentum:
        if momentum > 0:
            score += 25
        elif momentum > -5:
            score += 12

    return min(score, 100)


def get_technical_insights(indicators: dict, score: int) -> list:
    """
    Genererer tekstuelle insights baseret på tekniske indikatorer.
    """
    insights = []

    if indicators is None:
        return insights

    current_price = indicators.get("current_price", 0)
    sma50 = indicators.get("sma50")
    sma200 = indicators.get("sma200")
    rsi = indicators.get("rsi")
    momentum = indicators.get("momentum")

    # SMA50 insights
    if sma50:
        if current_price > sma50:
            pct_above = ((current_price - sma50) / sma50) * 100
            insights.append(f"✓ Pris handler {pct_above:.1f}% over 50-dages gennemsnit (bullish kortsigtet)")
        else:
            pct_below = ((sma50 - current_price) / sma50) * 100
            insights.append(f"✗ Pris handler {pct_below:.1f}% under 50-dages gennemsnit (bearish kortsigtet)")

    # SMA200 insights
    if sma200:
        if current_price > sma200:
            pct_above = ((current_price - sma200) / sma200) * 100
            insights.append(f"✓ Pris handler {pct_above:.1f}% over 200-dages gennemsnit (bullish langsigtet)")
        else:
            pct_below = ((sma200 - current_price) / sma200) * 100
            insights.append(f"✗ Pris handler {pct_below:.1f}% under 200-dages gennemsnit (bearish langsigtet)")

    # RSI insights
    if rsi:
        if rsi > 70:
            insights.append(f"⚠ RSI på {rsi} (overbought - mulig tilbagetrækning)")
        elif rsi < 30:
            insights.append(f"⚠ RSI på {rsi} (oversold - mulig bounce)")
        elif rsi > 50:
            insights.append(f"✓ RSI på {rsi} (moderat bullish momentum)")
        else:
            insights.append(f"• RSI på {rsi} (neutral momentum)")

    # Momentum insights
    if momentum:
        if momentum > 5:
            insights.append(f"✓ Momentum positiv: {momentum:.1f}% (stigning)")
        elif momentum < -5:
            insights.append(f"✗ Momentum negativ: {momentum:.1f}% (fald)")
        else:
            insights.append(f"• Momentum svagt: {momentum:.1f}% (sidelæns)")

    return insights
