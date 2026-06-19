from datetime import datetime
from src.technical_analyzer import get_technical_insights
from src.analyst_ratings import get_analyst_insights

def format_large_number(value):
    if value is None:
        return "N/A"

    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f} mia."

    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f} mio."

    return str(value)


def format_number(value):
    if value is None:
        return "N/A"

    return f"{value:.2f}"


def generate_markdown_report(data: dict, fundamental_score: int, technical_indicators: dict = None, technical_score: int = 0, analyst_ratings: dict = None, analyst_score: int = 50) -> str:
    today = datetime.now().strftime("%Y-%m-%d")

    # Basis rapport
    report = f"""# Aktieanalyse: {data.get("name")} ({data.get("ticker")})

Dato: {today}

## Overblik

- Navn: {data.get("name")}
- Ticker: {data.get("ticker")}
- Sektor: {data.get("sector")}
- Industri: {data.get("industry")}
- Valuta: {data.get("currency")}
- Seneste pris: {format_number(data.get("latest_price"))} {data.get("currency")}

## Nøgletal

- Market Cap: {format_large_number(data.get("market_cap"))} {data.get("currency")}
- P/E: {format_number(data.get("pe_ratio"))}
- Forward P/E: {format_number(data.get("forward_pe"))}
- EPS: {format_number(data.get("eps"))}
- Dividend Yield: {format_number(data.get("dividend_yield"))}%
- 52 Week High: {format_number(data.get("fifty_two_week_high"))} {data.get("currency")}
- 52 Week Low: {format_number(data.get("fifty_two_week_low"))} {data.get("currency")}
- Average Volume: {format_large_number(data.get("average_volume"))}

## Scores

- Fundamental Score: {fundamental_score}/100
"""

    # Tilføj teknisk analyse hvis tilgængelig
    if technical_indicators:
        report += f"- Technical Score: {technical_score}/100\n"
    
    # Tilføj analyst score
    if analyst_ratings:
        report += f"- Analyst Score: {analyst_score}/100\n"

    report += "\n"

    if technical_indicators:
        report += f"""
### Tekniske Indikatorer

- **50-dages gennemsnit (SMA50):** {format_number(technical_indicators.get("sma50"))} {data.get("currency")}
- **200-dages gennemsnit (SMA200):** {format_number(technical_indicators.get("sma200"))} {data.get("currency")}
- **RSI (14):** {format_number(technical_indicators.get("rsi"))}
- **Momentum (10-dag):** {format_number(technical_indicators.get("momentum"))}%

"""
        
        # Tilføj insights
        insights = get_technical_insights(technical_indicators, technical_score)
        if insights:
            report += "### Teknisk Analyse - Insights\n\n"
            for insight in insights:
                report += f"{insight}\n"
            report += "\n"

    # Tilføj analyst ratings hvis tilgængelig
    if analyst_ratings:
        report += f"""
### Analyst Vurderinger

- **Anbefaling:** {analyst_ratings.get("recommendation", "N/A")}
- **Antal analytikere:** {analyst_ratings.get("num_analysts", 0)}
- **Target pris (gennemsnit):** {format_number(analyst_ratings.get("target_mean"))} {data.get("currency")}
- **Target pris (median):** {format_number(analyst_ratings.get("target_median"))} {data.get("currency")}
- **Target range:** {format_number(analyst_ratings.get("target_low"))} - {format_number(analyst_ratings.get("target_high"))} {data.get("currency")}

"""
        
        # Tilføj analyst insights
        analyst_insights = get_analyst_insights(analyst_ratings, data.get("latest_price"))
        if analyst_insights:
            report += "### Analyst Analyse - Insights\n\n"
            for insight in analyst_insights:
                report += f"{insight}\n"
            report += "\n"

    report += """
## Foreløbig vurdering

Denne rapport er automatisk genereret baseret på data fra Yahoo Finance.

Bemærk: Dette er ikke finansiel rådgivning.
"""

    return report


def save_report(ticker: str, report: str) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"reports/{ticker}_{today}.md"

    with open(filename, "w", encoding="utf-8") as file:
        file.write(report)

    return filename