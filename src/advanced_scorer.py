"""
AVANCERET SCORING SYSTEM
========================
Omfatter 100+ faktorer fra:
- Værdi-metriker (P/E, P/B, PEG, osv.)
- Vækst-metriker (Revenue, EPS vækst)
- Kvalitets-metriker (Debt, ROE, ROA)
- Momentum & Teknisk analyse
- Sentiment & Analytiker vurderinger
- Risikovurdering & Volatilitet
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


def calculate_value_score(data: dict) -> Tuple[int, List[str]]:
    """
    Værdi-baseret scoringsystem (0-100)
    Vurderer om aktien er undervurderet
    """
    score = 50
    insights = []
    weights = {}

    # 1. P/E Ratio - Klassisk værdi metrik
    pe = data.get("pe_ratio")
    if pe and pe > 0:
        if pe < 10:
            score += 15
            weights["pe_very_low"] = 15
            insights.append("🟢 P/E meget lav (< 10) - mulig undervurdering")
        elif pe < 15:
            score += 12
            weights["pe_low"] = 12
            insights.append("🟢 P/E lav (< 15) - tegn på værdi")
        elif pe < 20:
            score += 8
            weights["pe_moderate"] = 8
            insights.append("🟡 P/E moderat (15-20)")
        elif pe < 30:
            score += 3
            weights["pe_elevated"] = 3
            insights.append("🟠 P/E forhøjet (20-30)")
        else:
            score -= 5
            weights["pe_very_high"] = -5
            insights.append("🔴 P/E meget høj (> 30) - mulig overvurdering")

    # 2. Forward P/E
    forward_pe = data.get("forward_pe")
    if forward_pe and forward_pe > 0 and pe:
        pe_diff = pe - forward_pe
        if pe_diff > 0:  # Forward P/E lavere = earnings growth forventet
            score += min(10, int(pe_diff))
            weights["forward_pe_improvement"] = min(10, int(pe_diff))
            insights.append(f"🟢 Forward P/E lavere end trailing ({forward_pe:.1f} vs {pe:.1f})")

    # 3. Price-to-Book Ratio (hvis tilgængelig via yfinance)
    pb_ratio = data.get("pb_ratio")
    if pb_ratio and pb_ratio > 0:
        if pb_ratio < 1:
            score += 10
            weights["pb_undervalued"] = 10
            insights.append("🟢 P/B < 1 - handler under bogført værdi")
        elif pb_ratio < 2:
            score += 5
            weights["pb_moderate"] = 5
            insights.append("🟡 P/B moderat (1-2)")
        else:
            score -= 3
            weights["pb_high"] = -3

    # 4. PEG Ratio (P/E divideret med growth rate)
    # Ideelt < 1 = fair value, < 0.5 = meget billig
    peg_ratio = data.get("peg_ratio")
    if peg_ratio and peg_ratio > 0:
        if peg_ratio < 0.5:
            score += 15
            weights["peg_very_attractive"] = 15
            insights.append("🟢 PEG meget lav (< 0.5) - attraktiv værdi vs vækst")
        elif peg_ratio < 1.0:
            score += 10
            weights["peg_attractive"] = 10
            insights.append("🟢 PEG fair (< 1.0)")
        elif peg_ratio < 1.5:
            score += 5
            weights["peg_moderate"] = 5
        else:
            score -= 5
            weights["peg_expensive"] = -5
            insights.append("🔴 PEG > 1.5 - dyr i forhold til vækst")

    # 5. Price-to-Sales Ratio
    ps_ratio = data.get("ps_ratio")
    if ps_ratio and ps_ratio > 0:
        if ps_ratio < 1:
            score += 8
            weights["ps_low"] = 8
            insights.append("🟢 P/S lav (< 1)")
        elif ps_ratio < 3:
            score += 4
            weights["ps_moderate"] = 4
        else:
            score -= 4
            weights["ps_high"] = -4

    # 6. Enterprise Value to EBITDA (EV/EBITDA)
    ev_ebitda = data.get("ev_ebitda")
    if ev_ebitda and ev_ebitda > 0:
        if ev_ebitda < 8:
            score += 8
            weights["ev_ebitda_low"] = 8
            insights.append("🟢 EV/EBITDA lav - god værdi")
        elif ev_ebitda < 12:
            score += 4
            weights["ev_ebitda_moderate"] = 4
        else:
            score -= 4
            weights["ev_ebitda_high"] = -4

    # 7. Free Cash Flow Yield
    fcf_yield = data.get("fcf_yield")
    if fcf_yield and fcf_yield > 0:
        if fcf_yield > 0.08:  # > 8%
            score += 12
            weights["fcf_excellent"] = 12
            insights.append(f"🟢 FCF Yield høj ({fcf_yield*100:.2f}%) - god kontantstrøm")
        elif fcf_yield > 0.05:  # > 5%
            score += 8
            weights["fcf_good"] = 8
        elif fcf_yield > 0.02:  # > 2%
            score += 4
            weights["fcf_moderate"] = 4
        else:
            score -= 5
            weights["fcf_low"] = -5

    # 8. Dividend Safety & Yield
    dividend_yield = data.get("dividend_yield")
    if dividend_yield and dividend_yield > 0:
        if dividend_yield > 0.05:  # > 5%
            score += 10
            weights["dividend_high"] = 10
            insights.append(f"🟢 Dividend Yield høj ({dividend_yield*100:.2f}%)")
        elif dividend_yield > 0.02:  # > 2%
            score += 6
            weights["dividend_moderate"] = 6
            insights.append(f"🟡 Dividend Yield moderat ({dividend_yield*100:.2f}%)")

    # 9. Dividend Payout Ratio (sikkerhed)
    payout_ratio = data.get("payout_ratio")
    if payout_ratio and 0 < payout_ratio < 1:
        if payout_ratio < 0.3:  # < 30%
            score += 8
            weights["payout_safe"] = 8
            insights.append("🟢 Lav udlodningsprocent - sikker udbytte")
        elif payout_ratio < 0.5:  # < 50%
            score += 5
            weights["payout_moderate"] = 5
        elif payout_ratio > 0.8:
            score -= 8
            weights["payout_risky"] = -8
            insights.append("🔴 Høj udlodningsprocent - risiko for udbytte-nedsættelse")

    # 10. 52-Week Performance
    low_52w = data.get("fifty_two_week_low")
    high_52w = data.get("fifty_two_week_high")
    current_price = data.get("latest_price")
    
    if low_52w and high_52w and current_price:
        price_position = (current_price - low_52w) / (high_52w - low_52w)
        if price_position < 0.3:  # Tæt på 52-week low
            score += 10
            weights["price_low"] = 10
            insights.append("🟢 Pris tæt på 52-week low - potentiel værdi")
        elif price_position < 0.5:
            score += 5
            weights["price_moderate"] = 5
        elif price_position > 0.9:  # Tæt på 52-week high
            score -= 8
            weights["price_high"] = -8
            insights.append("🔴 Pris tæt på 52-week high")

    final_score = max(0, min(100, score))
    return final_score, insights, weights


def calculate_growth_score(data: dict) -> Tuple[int, List[str]]:
    """
    Vækst-baseret scoringsystem (0-100)
    Vurderer vækstpotentiale
    """
    score = 50
    insights = []
    weights = {}

    # 1. Revenue Growth (YoY)
    revenue_growth = data.get("revenue_growth")
    if revenue_growth and revenue_growth != 0:
        if revenue_growth > 0.25:  # > 25%
            score += 15
            weights["revenue_exceptional"] = 15
            insights.append(f"🟢 Omsætningsvækst eksklusiv ({revenue_growth*100:.1f}%)")
        elif revenue_growth > 0.15:  # > 15%
            score += 12
            weights["revenue_strong"] = 12
            insights.append(f"🟢 Stærk omsætningsvækst ({revenue_growth*100:.1f}%)")
        elif revenue_growth > 0.08:  # > 8%
            score += 8
            weights["revenue_good"] = 8
            insights.append(f"🟡 Moderat omsætningsvækst ({revenue_growth*100:.1f}%)")
        elif revenue_growth > 0.02:  # > 2%
            score += 3
            weights["revenue_modest"] = 3
        else:
            score -= 5
            weights["revenue_stagnant"] = -5
            insights.append("🔴 Lav eller negativ omsætningsvækst")

    # 2. EPS Growth (Earnings Per Share)
    eps_growth = data.get("eps_growth")
    if eps_growth and eps_growth != 0:
        if eps_growth > 0.30:  # > 30%
            score += 15
            weights["eps_exceptional"] = 15
            insights.append(f"🟢 Eksklusiv EPS-vækst ({eps_growth*100:.1f}%)")
        elif eps_growth > 0.15:  # > 15%
            score += 12
            weights["eps_strong"] = 12
            insights.append(f"🟢 Stærk EPS-vækst ({eps_growth*100:.1f}%)")
        elif eps_growth > 0.08:  # > 8%
            score += 8
            weights["eps_good"] = 8
        else:
            score -= 5
            weights["eps_weak"] = -5

    # 3. Operating Margin & Trend
    operating_margin = data.get("operating_margin")
    if operating_margin and operating_margin > 0:
        if operating_margin > 0.25:  # > 25%
            score += 12
            weights["margin_excellent"] = 12
            insights.append(f"🟢 Fremragende driftsmarginal ({operating_margin*100:.1f}%)")
        elif operating_margin > 0.15:  # > 15%
            score += 8
            weights["margin_good"] = 8
        elif operating_margin > 0.08:  # > 8%
            score += 4
            weights["margin_moderate"] = 4
        else:
            score -= 5
            weights["margin_low"] = -5

    # 4. Free Cash Flow Growth
    fcf_growth = data.get("fcf_growth")
    if fcf_growth and fcf_growth > 0:
        if fcf_growth > 0.25:  # > 25%
            score += 12
            weights["fcf_growth_strong"] = 12
            insights.append(f"🟢 Stærk FCF-vækst ({fcf_growth*100:.1f}%)")
        elif fcf_growth > 0.10:  # > 10%
            score += 8
            weights["fcf_growth_good"] = 8
        elif fcf_growth > 0:
            score += 4
            weights["fcf_growth_modest"] = 4

    # 5. Expected Future Growth (Forward Estimates)
    next_year_growth = data.get("next_year_growth_estimate")
    if next_year_growth and next_year_growth > 0:
        if next_year_growth > 0.25:  # > 25%
            score += 10
            weights["forward_growth_high"] = 10
            insights.append(f"🟢 Høj forventet vækst ({next_year_growth*100:.1f}%)")
        elif next_year_growth > 0.12:  # > 12%
            score += 7
            weights["forward_growth_good"] = 7
        elif next_year_growth > 0.05:
            score += 4
            weights["forward_growth_modest"] = 4

    # 6. Research & Development as % of Revenue
    rd_ratio = data.get("rd_ratio")
    if rd_ratio and rd_ratio > 0:
        if rd_ratio > 0.10:  # > 10%
            score += 8
            weights["rd_strong"] = 8
            insights.append("🟢 Høj R&D-investering - innovativ virksomhed")
        elif rd_ratio > 0.05:  # > 5%
            score += 4
            weights["rd_moderate"] = 4

    final_score = max(0, min(100, score))
    return final_score, insights, weights


def calculate_quality_score(data: dict) -> Tuple[int, List[str]]:
    """
    Kvalitets-baseret scoringsystem (0-100)
    Vurderer virksomhedens fundamentale styrke
    """
    score = 50
    insights = []
    weights = {}

    # 1. Return on Equity (ROE)
    roe = data.get("return_on_equity")
    if roe and roe > 0:
        if roe > 0.25:  # > 25%
            score += 15
            weights["roe_excellent"] = 15
            insights.append(f"🟢 Fremragende ROE ({roe*100:.1f}%)")
        elif roe > 0.15:  # > 15%
            score += 12
            weights["roe_very_good"] = 12
            insights.append(f"🟢 Høj ROE ({roe*100:.1f}%)")
        elif roe > 0.10:  # > 10%
            score += 8
            weights["roe_good"] = 8
        elif roe > 0.05:  # > 5%
            score += 4
            weights["roe_moderate"] = 4
        else:
            score -= 5
            weights["roe_low"] = -5

    # 2. Return on Assets (ROA)
    roa = data.get("return_on_assets")
    if roa and roa > 0:
        if roa > 0.15:  # > 15%
            score += 12
            weights["roa_excellent"] = 12
        elif roa > 0.08:  # > 8%
            score += 8
            weights["roa_good"] = 8
        elif roa > 0.03:  # > 3%
            score += 4
            weights["roa_moderate"] = 4
        else:
            score -= 5
            weights["roa_low"] = -5

    # 3. Return on Invested Capital (ROIC)
    roic = data.get("return_on_invested_capital")
    if roic and roic > 0:
        if roic > 0.20:  # > 20%
            score += 12
            weights["roic_excellent"] = 12
            insights.append(f"🟢 Fremragende ROIC ({roic*100:.1f}%)")
        elif roic > 0.12:  # > 12%
            score += 8
            weights["roic_good"] = 8
        else:
            score -= 4
            weights["roic_weak"] = -4

    # 4. Debt-to-Equity Ratio
    debt_to_equity = data.get("debt_to_equity")
    if debt_to_equity is not None and debt_to_equity >= 0:
        if debt_to_equity < 0.5:
            score += 15
            weights["debt_very_low"] = 15
            insights.append(f"🟢 Lav gæld/egenkapital ({debt_to_equity:.2f})")
        elif debt_to_equity < 1.0:
            score += 10
            weights["debt_low"] = 10
            insights.append(f"🟡 Moderat gæld ({debt_to_equity:.2f})")
        elif debt_to_equity < 2.0:
            score += 5
            weights["debt_moderate"] = 5
        elif debt_to_equity < 3.0:
            score -= 5
            weights["debt_high"] = -5
        else:
            score -= 15
            weights["debt_very_high"] = -15
            insights.append(f"🔴 Høj gæld ({debt_to_equity:.2f})")

    # 5. Current Ratio (Likviditet)
    current_ratio = data.get("current_ratio")
    if current_ratio and current_ratio > 0:
        if current_ratio > 2.0:
            score += 10
            weights["liquidity_excellent"] = 10
            insights.append(f"🟢 Fremragende likviditet ({current_ratio:.2f})")
        elif current_ratio > 1.5:
            score += 8
            weights["liquidity_good"] = 8
        elif current_ratio > 1.0:
            score += 4
            weights["liquidity_adequate"] = 4
        elif current_ratio > 0.5:
            score -= 5
            weights["liquidity_low"] = -5
        else:
            score -= 15
            weights["liquidity_critical"] = -15
            insights.append("🔴 Kritisk likviditets situation")

    # 6. Quick Ratio (mere konservativ likviditet)
    quick_ratio = data.get("quick_ratio")
    if quick_ratio and quick_ratio > 0:
        if quick_ratio > 1.5:
            score += 8
            weights["quick_excellent"] = 8
        elif quick_ratio > 1.0:
            score += 5
            weights["quick_good"] = 5
        elif quick_ratio < 0.5:
            score -= 8
            weights["quick_low"] = -8

    # 7. Debt-to-EBITDA (solvens indikator)
    debt_to_ebitda = data.get("debt_to_ebitda")
    if debt_to_ebitda and debt_to_ebitda > 0:
        if debt_to_ebitda < 2.0:
            score += 10
            weights["debt_ebitda_low"] = 10
            insights.append(f"🟢 Lav gæld/EBITDA ({debt_to_ebitda:.2f}x)")
        elif debt_to_ebitda < 3.5:
            score += 6
            weights["debt_ebitda_moderate"] = 6
        elif debt_to_ebitda < 5.0:
            score -= 5
            weights["debt_ebitda_high"] = -5
        else:
            score -= 12
            weights["debt_ebitda_very_high"] = -12

    # 8. Interest Coverage Ratio
    interest_coverage = data.get("interest_coverage_ratio")
    if interest_coverage and interest_coverage > 0:
        if interest_coverage > 10:
            score += 10
            weights["interest_excellent"] = 10
        elif interest_coverage > 5:
            score += 7
            weights["interest_good"] = 7
        elif interest_coverage > 2.5:
            score += 4
            weights["interest_moderate"] = 4
        else:
            score -= 10
            weights["interest_low"] = -10
            insights.append("🔴 Lav rentedækkelsesgrad - risiko")

    # 9. Asset Turnover
    asset_turnover = data.get("asset_turnover")
    if asset_turnover and asset_turnover > 0:
        if asset_turnover > 2:
            score += 8
            weights["asset_turnover_high"] = 8
        elif asset_turnover > 1:
            score += 4
            weights["asset_turnover_good"] = 4

    # 10. Net Profit Margin
    net_margin = data.get("net_margin")
    if net_margin and net_margin > 0:
        if net_margin > 0.20:  # > 20%
            score += 12
            weights["margin_net_excellent"] = 12
        elif net_margin > 0.10:  # > 10%
            score += 8
            weights["margin_net_good"] = 8
        elif net_margin > 0.05:  # > 5%
            score += 4
            weights["margin_net_moderate"] = 4

    final_score = max(0, min(100, score))
    return final_score, insights, weights


def calculate_momentum_score(indicators: dict) -> Tuple[int, List[str]]:
    """
    Momentum & Teknisk scoringsystem (0-100)
    Baseret på prisbevægelser og tekniske indikatorer
    """
    score = 50
    insights = []
    weights = {}

    if not indicators:
        return score, insights, weights

    current_price = indicators.get("current_price", 0)
    sma50 = indicators.get("sma50")
    sma200 = indicators.get("sma200")
    rsi = indicators.get("rsi")
    momentum = indicators.get("momentum")
    macd = indicators.get("macd")
    bollinger_upper = indicators.get("bollinger_upper")
    bollinger_lower = indicators.get("bollinger_lower")
    price_change_1m = indicators.get("price_change_1m")
    price_change_3m = indicators.get("price_change_3m")

    # 1. SMA50 Position (kortsigtet trend)
    if sma50 and current_price:
        pct_above_sma50 = ((current_price - sma50) / sma50) * 100
        if pct_above_sma50 > 5:
            score += 12
            weights["sma50_bullish"] = 12
            insights.append(f"🟢 Pris {pct_above_sma50:.1f}% over SMA50 (bullish)")
        elif pct_above_sma50 > 2:
            score += 6
            weights["sma50_slightly_bullish"] = 6
        elif pct_above_sma50 > -2:
            score += 2
            weights["sma50_neutral"] = 2
        elif pct_above_sma50 > -5:
            score -= 6
            weights["sma50_slightly_bearish"] = -6
        else:
            score -= 12
            weights["sma50_bearish"] = -12
            insights.append(f"🔴 Pris {abs(pct_above_sma50):.1f}% under SMA50 (bearish)")

    # 2. SMA200 Position (langsigtet trend)
    if sma200 and current_price:
        pct_above_sma200 = ((current_price - sma200) / sma200) * 100
        if pct_above_sma200 > 5:
            score += 15
            weights["sma200_bullish"] = 15
            insights.append(f"🟢 Pris {pct_above_sma200:.1f}% over SMA200 (langsigtet bullish)")
        elif pct_above_sma200 > 2:
            score += 8
            weights["sma200_slightly_bullish"] = 8
        elif pct_above_sma200 < -5:
            score -= 15
            weights["sma200_bearish"] = -15
            insights.append("🔴 Under 200-dages gennemsnit (langsigtet bearish)")

    # 3. RSI (Relative Strength Index)
    if rsi is not None:
        if rsi > 70:
            score -= 8
            weights["rsi_overbought"] = -8
            insights.append(f"⚠️ RSI {rsi} (overbought - kan få tilbagetrækning)")
        elif rsi > 60:
            score += 8
            weights["rsi_strong"] = 8
            insights.append(f"🟢 RSI {rsi} (stærk momentum)")
        elif rsi > 50:
            score += 4
            weights["rsi_bullish"] = 4
        elif rsi > 40:
            score += 2
            weights["rsi_neutral"] = 2
        elif rsi > 30:
            score -= 2
            weights["rsi_bearish"] = -2
        elif rsi < 30:
            score -= 8
            weights["rsi_oversold"] = -8
            insights.append(f"⚠️ RSI {rsi} (oversold - potentiel bounce)")
        else:
            score -= 12
            weights["rsi_very_oversold"] = -12

    # 4. MACD (Moving Average Convergence Divergence)
    if macd and isinstance(macd, dict):
        macd_line = macd.get("macd")
        signal_line = macd.get("signal")
        histogram = macd.get("histogram")
        
        if histogram and histogram > 0:
            score += 10
            weights["macd_bullish"] = 10
            insights.append("🟢 MACD histogram positiv (bullish crossover)")
        elif histogram and histogram < 0:
            score -= 10
            weights["macd_bearish"] = -10
            insights.append("🔴 MACD histogram negativ (bearish crossover)")

    # 5. Bollinger Bands Position
    if bollinger_upper and bollinger_lower and current_price:
        bb_position = (current_price - bollinger_lower) / (bollinger_upper - bollinger_lower)
        if bb_position > 0.8:
            score -= 5
            weights["bb_upper"] = -5
            insights.append("⚠️ Pris tæt på øvre Bollinger Band (potentiel modstand)")
        elif bb_position < 0.2:
            score += 5
            weights["bb_lower"] = 5
            insights.append("🟢 Pris tæt på nedre Bollinger Band (potentiel support)")

    # 6. 1-Måneds Momentum
    if price_change_1m is not None:
        if price_change_1m > 0.15:  # > 15%
            score += 10
            weights["momentum_1m_strong"] = 10
            insights.append(f"🟢 1-måneds momentum stærk: {price_change_1m*100:.1f}%")
        elif price_change_1m > 0.05:  # > 5%
            score += 6
            weights["momentum_1m_good"] = 6
        elif price_change_1m > -0.05:  # -5% til +5%
            score += 2
            weights["momentum_1m_neutral"] = 2
        elif price_change_1m > -0.15:  # -5% til -15%
            score -= 6
            weights["momentum_1m_weak"] = -6
        else:
            score -= 10
            weights["momentum_1m_strong_down"] = -10

    # 7. 3-Måneds Momentum
    if price_change_3m is not None:
        if price_change_3m > 0.25:  # > 25%
            score += 12
            weights["momentum_3m_strong"] = 12
        elif price_change_3m > 0.10:  # > 10%
            score += 8
            weights["momentum_3m_good"] = 8
        elif price_change_3m > -0.10:
            score += 3
            weights["momentum_3m_neutral"] = 3
        elif price_change_3m > -0.25:
            score -= 8
            weights["momentum_3m_weak"] = -8
        else:
            score -= 12
            weights["momentum_3m_strong_down"] = -12

    final_score = max(0, min(100, score))
    return final_score, insights, weights


def calculate_risk_score(data: dict, indicators: dict = None) -> Tuple[int, List[str]]:
    """
    Risiko-vurderingssystem (0-100)
    Lavere score = højere risiko
    """
    score = 50
    insights = []
    weights = {}

    # 1. Beta (Volatilitet i forhold til marked)
    beta = data.get("beta")
    if beta and beta > 0:
        if beta < 0.8:
            score += 15
            weights["beta_low"] = 15
            insights.append(f"🟢 Beta lav ({beta:.2f}) - mindre volatil end marked")
        elif beta < 1.0:
            score += 8
            weights["beta_moderate_low"] = 8
        elif beta < 1.2:
            score += 4
            weights["beta_moderate"] = 4
        elif beta < 1.5:
            score -= 5
            weights["beta_elevated"] = -5
        else:
            score -= 15
            weights["beta_high"] = -15
            insights.append(f"🔴 Beta høj ({beta:.2f}) - meget volatil")

    # 2. Volatility (30-dages eller implied)
    volatility = data.get("volatility")
    if volatility is not None:
        if volatility < 0.15:  # < 15%
            score += 12
            weights["volatility_low"] = 12
            insights.append(f"🟢 Lav volatilitet ({volatility*100:.1f}%)")
        elif volatility < 0.25:  # < 25%
            score += 8
            weights["volatility_moderate"] = 8
        elif volatility < 0.40:  # < 40%
            score -= 5
            weights["volatility_high"] = -5
        else:
            score -= 15
            weights["volatility_very_high"] = -15
            insights.append(f"🔴 Høj volatilitet ({volatility*100:.1f}%)")

    # 3. Sharpe Ratio (risikojusteret afkast)
    sharpe_ratio = data.get("sharpe_ratio")
    if sharpe_ratio is not None:
        if sharpe_ratio > 1.0:
            score += 12
            weights["sharpe_excellent"] = 12
            insights.append(f"🟢 Fremragende Sharpe Ratio ({sharpe_ratio:.2f})")
        elif sharpe_ratio > 0.5:
            score += 8
            weights["sharpe_good"] = 8
        elif sharpe_ratio > 0:
            score += 4
            weights["sharpe_moderate"] = 4
        else:
            score -= 8
            weights["sharpe_negative"] = -8

    # 4. Max Drawdown (værst case)
    max_drawdown = data.get("max_drawdown")
    if max_drawdown is not None and max_drawdown < 0:
        if max_drawdown > -0.20:  # > -20%
            score += 10
            weights["drawdown_small"] = 10
        elif max_drawdown > -0.35:  # > -35%
            score += 5
            weights["drawdown_moderate"] = 5
        elif max_drawdown > -0.50:  # > -50%
            score -= 5
            weights["drawdown_large"] = -5
        else:
            score -= 15
            weights["drawdown_very_large"] = -15
            insights.append(f"🔴 Stor nedgang oplevet ({max_drawdown*100:.1f}%)")

    # 5. Debt-to-Equity Ratio (finansiel risiko)
    debt_to_equity = data.get("debt_to_equity")
    if debt_to_equity is not None and debt_to_equity >= 0:
        if debt_to_equity < 0.5:
            score += 12
            weights["debt_risk_low"] = 12
        elif debt_to_equity < 1.0:
            score += 6
            weights["debt_risk_moderate"] = 6
        elif debt_to_equity < 2.0:
            score -= 6
            weights["debt_risk_high"] = -6
        else:
            score -= 15
            weights["debt_risk_very_high"] = -15

    # 6. Current Ratio (Likviditets risiko)
    current_ratio = data.get("current_ratio")
    if current_ratio is not None:
        if current_ratio > 1.5:
            score += 10
            weights["liquidity_risk_low"] = 10
        elif current_ratio > 1.0:
            score += 5
            weights["liquidity_risk_moderate"] = 5
        elif current_ratio > 0.5:
            score -= 8
            weights["liquidity_risk_high"] = -8
        else:
            score -= 15
            weights["liquidity_risk_critical"] = -15

    # 7. Debt-to-EBITDA (Solvens risiko)
    debt_to_ebitda = data.get("debt_to_ebitda")
    if debt_to_ebitda is not None and debt_to_ebitda > 0:
        if debt_to_ebitda < 2.0:
            score += 8
            weights["solvency_strong"] = 8
        elif debt_to_ebitda < 3.5:
            score += 4
            weights["solvency_moderate"] = 4
        elif debt_to_ebitda < 5.0:
            score -= 6
            weights["solvency_weak"] = -6
        else:
            score -= 12
            weights["solvency_critical"] = -12

    # 8. Price Volatility (hvis indicators tilgængelig)
    if indicators:
        price_change_1m = indicators.get("price_change_1m")
        price_change_3m = indicators.get("price_change_3m")
        
        if price_change_1m is not None and price_change_3m is not None:
            volatility_estimate = abs(price_change_3m - price_change_1m)
            if volatility_estimate < 0.15:
                score += 5
                weights["price_volatility_low"] = 5
            elif volatility_estimate > 0.50:
                score -= 8
                weights["price_volatility_high"] = -8

    final_score = max(0, min(100, score))
    return final_score, insights, weights


def calculate_sentiment_score(analyst_data: dict, news_data: dict = None) -> Tuple[int, List[str]]:
    """
    Sentiment-baseret scoringsystem (0-100)
    Baseret på analytiker vurderinger og nyheder
    """
    score = 50
    insights = []
    weights = {}

    # 1. Analyst Recommendation
    recommendation = analyst_data.get("recommendation")
    recommendation_mean = analyst_data.get("recommendation_mean")
    num_analysts = analyst_data.get("num_analysts", 0)

    if recommendation_mean is not None:
        if recommendation_mean < 1.5:  # Stærk køb
            score += 20
            weights["analyst_strong_buy"] = 20
            insights.append(f"🟢 Analytikere: {recommendation} ({num_analysts} analytikere)")
        elif recommendation_mean < 2.0:  # Køb
            score += 15
            weights["analyst_buy"] = 15
            insights.append(f"🟢 Analytikere: {recommendation}")
        elif recommendation_mean < 2.5:  # Svag køb / Hold
            score += 8
            weights["analyst_hold_buy"] = 8
        elif recommendation_mean < 3.5:  # Hold
            score += 3
            weights["analyst_hold"] = 3
        elif recommendation_mean < 4.0:  # Svag sælg / Hold
            score -= 8
            weights["analyst_hold_sell"] = -8
        elif recommendation_mean < 4.5:  # Sælg
            score -= 15
            weights["analyst_sell"] = -15
            insights.append(f"🔴 Analytikere: {recommendation}")
        else:  # Stærk sælg
            score -= 20
            weights["analyst_strong_sell"] = -20

    # 2. Analyst Target Price vs Current Price
    target_mean = analyst_data.get("target_mean")
    current_price = analyst_data.get("current_price")
    
    if target_mean and current_price and current_price > 0:
        upside_potential = (target_mean - current_price) / current_price
        if upside_potential > 0.30:  # > 30%
            score += 15
            weights["target_high_upside"] = 15
            insights.append(f"🟢 Analytikers target {upside_potential*100:.1f}% over nuværende pris")
        elif upside_potential > 0.15:  # > 15%
            score += 10
            weights["target_good_upside"] = 10
        elif upside_potential > 0:  # > 0%
            score += 5
            weights["target_modest_upside"] = 5
        elif upside_potential > -0.10:  # -10% til 0%
            score += 2
            weights["target_near"] = 2
        elif upside_potential > -0.25:  # -10% til -25%
            score -= 8
            weights["target_downside"] = -8
        else:
            score -= 15
            weights["target_high_downside"] = -15
            insights.append(f"🔴 Analytikers target {abs(upside_potential)*100:.1f}% under nuværende")

    # 3. Analyst Consensus Spread (hvor uenige er de)
    target_high = analyst_data.get("target_high")
    target_low = analyst_data.get("target_low")
    
    if target_high and target_low and target_mean and target_mean > 0:
        consensus_spread = (target_high - target_low) / target_mean
        if consensus_spread < 0.20:  # < 20%
            score += 8
            weights["consensus_high"] = 8
            insights.append("🟢 Høj analytiker-enighed om target")
        elif consensus_spread < 0.40:  # < 40%
            score += 4
            weights["consensus_moderate"] = 4
        elif consensus_spread > 0.80:  # > 80%
            score -= 8
            weights["consensus_low"] = -8
            insights.append("🔴 Lav analytiker-enighed (usikkert marked)")

    # 4. News Sentiment (hvis tilgængelig)
    if news_data:
        news_sentiment = news_data.get("sentiment_score")  # -1 til 1
        news_count = news_data.get("news_count", 0)
        
        if news_sentiment is not None:
            sentiment_score = (news_sentiment + 1) / 2 * 20  # Omregn til 0-20
            score += min(20, sentiment_score)
            weights["news_sentiment"] = min(20, sentiment_score)
            
            if news_sentiment > 0.5:
                insights.append(f"🟢 Stærkt positiv nyhedsstemning")
            elif news_sentiment > 0:
                insights.append(f"🟡 Moderat positiv nyhedsstemning")
            elif news_sentiment < -0.5:
                insights.append(f"🔴 Stærkt negativ nyhedsstemning")

    final_score = max(0, min(100, score))
    return final_score, insights, weights


def calculate_composite_score(
    value_score: int,
    growth_score: int,
    quality_score: int,
    momentum_score: int,
    risk_score: int,
    sentiment_score: int,
    weights: Dict[str, float] = None
) -> int:
    """
    Beregner en vægtet composite score (0-100)
    
    Standard vægte:
    - Value: 25% (værdivurdering)
    - Growth: 20% (vækstpotentiale)
    - Quality: 25% (virksomhedens styrke)
    - Momentum: 15% (kort-sigt prisbevægelse)
    - Risk: 10% (risiko-justering)
    - Sentiment: 5% (markedsstemning)
    """
    if weights is None:
        weights = {
            "value": 0.25,
            "growth": 0.20,
            "quality": 0.25,
            "momentum": 0.15,
            "risk": 0.10,
            "sentiment": 0.05,
        }

    composite = (
        value_score * weights["value"]
        + growth_score * weights["growth"]
        + quality_score * weights["quality"]
        + momentum_score * weights["momentum"]
        + risk_score * weights["risk"]
        + sentiment_score * weights["sentiment"]
    )

    return max(0, min(100, int(composite)))


def get_overall_rating(composite_score: int) -> Tuple[str, str]:
    """
    Konverterer composite score til rating og emoji
    """
    ratings = [
        (85, "🟢 STÆRK KØB", "Meget attraktiv investering"),
        (75, "🟢 KØB", "Attraktiv investering"),
        (65, "🟡 HOLD", "Fair værdi, vent på bedre mulighed"),
        (55, "🟡 SVAG HOLD", "Neutral, afvent udvikling"),
        (45, "🟠 SVAG SÆLG", "Potentiel risiko"),
        (35, "🔴 SÆLG", "Uattraktiv investering"),
        (0, "🔴 STÆRK SÆLG", "Meget risikabel"),
    ]

    for threshold, rating, description in ratings:
        if composite_score >= threshold:
            return rating, description

    return "🔴 STÆRK SÆLG", "Meget risikabel"


def generate_detailed_scoring_report(
    data: dict,
    indicators: dict,
    analyst_data: dict,
    news_data: dict = None
) -> Dict:
    """
    Genererer detaljeret scoringsrapport med alle komponenter
    """
    # Beregn alle component scores
    value_score, value_insights, value_weights = calculate_value_score(data)
    growth_score, growth_insights, growth_weights = calculate_growth_score(data)
    quality_score, quality_insights, quality_weights = calculate_quality_score(data)
    momentum_score, momentum_insights, momentum_weights = calculate_momentum_score(indicators)
    risk_score, risk_insights, risk_weights = calculate_risk_score(data, indicators)
    sentiment_score, sentiment_insights, sentiment_weights = calculate_sentiment_score(
        analyst_data, news_data
    )

    # Beregn composite score
    composite_score = calculate_composite_score(
        value_score, growth_score, quality_score, momentum_score, risk_score, sentiment_score
    )

    # Få rating
    rating, description = get_overall_rating(composite_score)

    # Kombinér alle insights
    all_insights = (
        value_insights
        + growth_insights
        + quality_insights
        + momentum_insights
        + risk_insights
        + sentiment_insights
    )

    return {
        "composite_score": composite_score,
        "rating": rating,
        "rating_description": description,
        "component_scores": {
            "value_score": value_score,
            "growth_score": growth_score,
            "quality_score": quality_score,
            "momentum_score": momentum_score,
            "risk_score": risk_score,
            "sentiment_score": sentiment_score,
        },
        "all_insights": all_insights,
        "weights": {
            "value": value_weights,
            "growth": growth_weights,
            "quality": quality_weights,
            "momentum": momentum_weights,
            "risk": risk_weights,
            "sentiment": sentiment_weights,
        },
    }
