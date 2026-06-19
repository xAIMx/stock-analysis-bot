from datetime import datetime


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
- Seneste pris: {data.get("latest_price")}

## Nøgletal

- Market Cap: {data.get("market_cap")}
- P/E: {data.get("pe_ratio")}
- Forward P/E: {data.get("forward_pe")}
- EPS: {data.get("eps")}
- Dividend Yield: {data.get("dividend_yield")}

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