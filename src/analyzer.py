def calculate_fundamental_score(data: dict) -> int:
    score = 50

    pe = data.get("pe_ratio")
    market_cap = data.get("market_cap")
    dividend = data.get("dividend_yield")

    if pe:
        if pe < 15:
            score += 20
        elif pe < 25:
            score += 10

    if market_cap:
        if market_cap > 100_000_000_000:
            score += 15

    if dividend:
        if dividend > 0.01:
            score += 5

    return min(score, 100)