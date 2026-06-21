import sys
import os
from dotenv import load_dotenv
from datetime import datetime
from src.data_fetcher import get_stock_data
from src.technical_analyzer import calculate_technical_indicators
from src.analyst_ratings import get_analyst_ratings
from src.analyzer import analyze_stock, get_analysis_summary
from src.report_generator import generate_markdown_report, save_report
from src.discord_client import send_report_async

# Load environment variables from .env
load_dotenv()


def main():
    if len(sys.argv) < 2:
        print("Brug: python main.py TICKER")
        print("Eksempel: python main.py NOVO-B.CO")
        return

    ticker = sys.argv[1].upper()
    
    print(f"🔄 Henter data for {ticker}...")
    
    # Hent aktiedata med alle metriker
    data = get_stock_data(ticker, period="2y")
    
    if not data.get("latest_price"):
        print(f"❌ Kunne ikke hente data for {ticker}")
        return
    
    print(f"✅ Hentede data for {data.get('name')}")
    
    # Beregn tekniske indikatorer
    print("📊 Beregner tekniske indikatorer...")
    
    # Vi skal hente historien igen for technical_analyzer
    import yfinance as yf
    stock = yf.Ticker(ticker)
    history_2y = stock.history(period="2y")
    
    technical_indicators = calculate_technical_indicators(history_2y)
    
    if technical_indicators is None:
        print("⚠️ Kunne ikke beregne tekniske indikatorer")
        technical_indicators = {}
    
    # Hent analyst ratings
    print("📈 Henter analytiker-vurderinger...")
    analyst_data = get_analyst_ratings(data)
    
    if analyst_data is None:
        analyst_data = {}
    
    # Tilføj nuværende pris til analyst_data
    analyst_data["current_price"] = data.get("latest_price")
    
    # Udfør omfattende analyse
    print("🤖 Udfører avanceret analyse...")
    analysis = analyze_stock(data, technical_indicators, analyst_data)
    
    # Tilføj timestamp
    analysis["timestamp"] = datetime.now().isoformat()
    
    # Print sammenfattelse
    summary = get_analysis_summary(analysis)
    print(summary)
    
    # Generer markdown rapport
    print("📝 Genererer rapport...")
    report_data = {
        **data,
        **technical_indicators,
        "analysis": analysis,
    }
    
    # Generér markdown report med alle komponenter
    report = generate_markdown_report_v2(report_data)
    filename = save_report(ticker, report)
    
    print(f"✅ Rapport gemt som: {filename}")
    
    # Send til Discord
    print("\n=== Discord Upload ===")
    if send_report_async(ticker, filename):
        print("✅ Rapport sendt til Discord")
    else:
        print("⚠️ Rapport kunne ikke sendes til Discord (tjek DISCORD_BOT_TOKEN)")


def generate_markdown_report_v2(data: dict) -> str:
    """
    Genererer omfattende markdown rapport med alle analyskomponenter
    """
    from datetime import datetime
    
    today = datetime.now().strftime("%Y-%m-%d")
    analysis = data.get("analysis", {})
    scores = analysis.get("component_scores", {})
    insights = analysis.get("insights", [])
    
    report = f"""# Aktieanalyse: {data.get("name")} ({data.get("ticker")})

**Analysedato:** {today}  
**Seneste pris:** {data.get("latest_price")} {data.get("currency")}

---

## 📊 COMPOSITE SCORE: {analysis.get("composite_score")}/100

### Rating: {analysis.get("rating")}
{analysis.get("rating_description")}

---

## 📈 KOMPONENT SCORES

| Komponent | Score | Status |
|-----------|-------|--------|
| **Værdi** | {scores.get("value_score", "N/A")}/100 | {"🟢" if scores.get("value_score", 0) > 65 else "🟡" if scores.get("value_score", 0) > 45 else "🔴"} |
| **Vækst** | {scores.get("growth_score", "N/A")}/100 | {"🟢" if scores.get("growth_score", 0) > 65 else "🟡" if scores.get("growth_score", 0) > 45 else "🔴"} |
| **Kvalitet** | {scores.get("quality_score", "N/A")}/100 | {"🟢" if scores.get("quality_score", 0) > 65 else "🟡" if scores.get("quality_score", 0) > 45 else "🔴"} |
| **Momentum** | {scores.get("momentum_score", "N/A")}/100 | {"🟢" if scores.get("momentum_score", 0) > 65 else "🟡" if scores.get("momentum_score", 0) > 45 else "🔴"} |
| **Risiko** | {scores.get("risk_score", "N/A")}/100 | {"🟢" if scores.get("risk_score", 0) > 65 else "🟡" if scores.get("risk_score", 0) > 45 else "🔴"} |
| **Sentiment** | {scores.get("sentiment_score", "N/A")}/100 | {"🟢" if scores.get("sentiment_score", 0) > 65 else "🟡" if scores.get("sentiment_score", 0) > 45 else "🔴"} |

---

## 📋 VIRKSOMHEDSINFO

| Felt | Værdi |
|------|-------|
| **Navn** | {data.get("name")} |
| **Ticker** | {data.get("ticker")} |
| **Sektor** | {data.get("sector", "N/A")} |
| **Industri** | {data.get("industry", "N/A")} |
| **Market Cap** | {format_large_number(data.get("market_cap"))} |

---

## 💰 VÆRDI METRIKER

| Metrik | Værdi |
|--------|-------|
| **P/E Ratio** | {format_number(data.get("pe_ratio"))} |
| **Forward P/E** | {format_number(data.get("forward_pe"))} |
| **P/B Ratio** | {format_number(data.get("pb_ratio"))} |
| **P/S Ratio** | {format_number(data.get("ps_ratio"))} |
| **PEG Ratio** | {format_number(data.get("peg_ratio"))} |
| **EV/EBITDA** | {format_number(data.get("ev_ebitda"))} |
| **Dividend Yield** | {format_percent(data.get("dividend_yield"))} |

---

## 📊 KVALITETS METRIKER

| Metrik | Værdi |
|--------|-------|
| **ROE** | {format_percent(data.get("return_on_equity"))} |
| **ROA** | {format_percent(data.get("return_on_assets"))} |
| **ROIC** | {format_percent(data.get("return_on_invested_capital"))} |
| **Debt/Equity** | {format_number(data.get("debt_to_equity"))} |
| **Current Ratio** | {format_number(data.get("current_ratio"))} |
| **Debt/EBITDA** | {format_number(data.get("debt_to_ebitda"))} |
| **Interest Coverage** | {format_number(data.get("interest_coverage_ratio"))} |

---

## 📈 VÆKST METRIKER

| Metrik | Værdi |
|--------|-------|
| **Revenue Growth** | {format_percent(data.get("revenue_growth"))} |
| **EPS Growth** | {format_percent(data.get("eps_growth"))} |
| **Operating Margin** | {format_percent(data.get("operating_margin"))} |
| **Net Margin** | {format_percent(data.get("net_margin"))} |
| **FCF Yield** | {format_percent(data.get("fcf_yield"))} |

---

## 📉 TEKNISK ANALYSE

| Metrik | Værdi |
|--------|-------|
| **Aktuel Pris** | {format_number(data.get("current_price"))} |
| **SMA 50** | {format_number(data.get("sma50"))} |
| **SMA 200** | {format_number(data.get("sma200"))} |
| **RSI** | {format_number(data.get("rsi"))} |
| **Momentum** | {format_percent(data.get("momentum"))} |
| **1-Måned Change** | {format_percent(data.get("price_change_1m"))} |
| **3-Måned Change** | {format_percent(data.get("price_change_3m"))} |

---

## ⚠️ RISIKO METRIKER

| Metrik | Værdi |
|--------|-------|
| **Beta** | {format_number(data.get("beta"))} |
| **Volatilitet** | {format_percent(data.get("volatility"))} |
| **Sharpe Ratio** | {format_number(data.get("sharpe_ratio"))} |
| **Max Drawdown** | {format_percent(data.get("max_drawdown"))} |
| **52-Week High** | {format_number(data.get("fifty_two_week_high"))} |
| **52-Week Low** | {format_number(data.get("fifty_two_week_low"))} |

---

## 💡 NØGLEINDSIGTER

"""
    
    # Tilføj insights
    if insights:
        for i, insight in enumerate(insights[:20], 1):
            report += f"{i}. {insight}\n"
    
    report += f"""

---

## 📌 KONKLUSION

**Samlet Vurdering:** {analysis.get("rating")}  
**Composite Score:** {analysis.get("composite_score")}/100

Denne rapport er baseret på:
- Værdi-analyse (værdiering, nøgletal)
- Vækst-analyse (omsætning, earnings, vækstpotentiale)
- Kvalitets-analyse (rentabilitet, gæld, likviditet)
- Teknisk analyse (prismønstre, momentum, indikatorer)
- Risiko-analyse (volatilitet, nedgang, finansiel styrke)
- Sentiment-analyse (analytiker vurderinger)

**Bemærk:** Dette er ikke finansiel rådgivning. Investér kun efter grundig research og konsulter en finansiel advisor.

---
*Rapport genereret af Stock Analysis Bot*  
*Data fra Yahoo Finance og teknisk analyse*
"""
    
    return report


def format_number(value):
    if value is None:
        return "N/A"
    try:
        return f"{float(value):.2f}"
    except:
        return "N/A"


def format_large_number(value):
    if value is None:
        return "N/A"
    try:
        value = float(value)
        if value >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f}B"
        if value >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"
        return f"{value:,.0f}"
    except:
        return "N/A"


def format_percent(value):
    if value is None:
        return "N/A"
    try:
        return f"{float(value) * 100:.2f}%"
    except:
        return "N/A"


if __name__ == "__main__":
    main()