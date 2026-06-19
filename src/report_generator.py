from datetime import datetime

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


def generate_markdown_report(data: dict, fundamental_score: int) -> str:
    today = datetime.now().strftime("%Y-%m-%d")

    return f"""# Aktieanalyse: {data.get("name")} ({data.get("ticker")})

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

## Scores

- Fundamental Score: {fundamental_score}/100

## Foreløbig vurdering

Denne rapport er automatisk genereret baseret på data fra Yahoo Finance.

Bemærk: Dette er ikke finansiel rådgivning.
"""


def save_report(ticker: str, report: str) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"reports/{ticker}_{today}.md"

    with open(filename, "w", encoding="utf-8") as file:
        file.write(report)

    return filename