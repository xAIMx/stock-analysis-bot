import requests
from bs4 import BeautifulSoup
import re


def get_analyst_ratings(analyst_data: dict) -> dict:
    """
    Henter expert/analyst vurderinger fra data.
    Returnerer dict med vurderinger og target priser.
    """
    if not analyst_data:
        return None

    rating_map = {
        1.0: "Stærk køb",
        1.5: "Stærk køb",
        2.0: "Køb",
        2.5: "Hold",
        3.0: "Hold",
        3.5: "Sælg",
        4.0: "Sælg",
        4.5: "Stærk sælg",
        5.0: "Stærk sælg",
    }

    recommendation_mean = analyst_data.get("recommendation_mean")
    recommendation_key = analyst_data.get("recommendation_key", "").lower()
    num_analysts = analyst_data.get("numberOfAnalystOpinions", 0)

    # Oversæt recommendation key
    recommendation_translate = {
        "strong buy": "Stærk køb",
        "buy": "Køb",
        "hold": "Hold",
        "sell": "Sælg",
        "strong sell": "Stærk sælg",
    }

    current_recommendation = recommendation_translate.get(
        recommendation_key, recommendation_key if recommendation_key else "Ukendt"
    )

    # Hvis vi har recommendation_mean, brug det til at bestemme rating
    if recommendation_mean:
        nearest_rating = min(
            rating_map.keys(), key=lambda x: abs(x - recommendation_mean)
        )
        current_recommendation = rating_map[nearest_rating]

    return {
        "recommendation": current_recommendation,
        "recommendation_mean": recommendation_mean,
        "num_analysts": num_analysts,
        "target_mean": analyst_data.get("targetMeanPrice"),
        "target_median": analyst_data.get("targetMedianPrice"),
        "target_high": analyst_data.get("targetHighPrice"),
        "target_low": analyst_data.get("targetLowPrice"),
    }


def get_analyst_sentiment_score(analyst_ratings: dict) -> int:
    """
    Konverterer analyst ratings til score (0-100).
    Baseret på recommendation mean værdi.
    
    1.0 = 100 (Stærk køb)
    2.0 = 75 (Køb)
    3.0 = 50 (Hold)
    4.0 = 25 (Sælg)
    5.0 = 0 (Stærk sælg)
    """
    if not analyst_ratings:
        return 50

    rec_mean = analyst_ratings.get("recommendation_mean")
    if rec_mean is None:
        return 50

    # Omregn fra 1-5 skala til 0-100
    score = 100 - (rec_mean - 1) * 25
    return max(0, min(100, int(score)))


def get_analyst_insights(analyst_ratings: dict, current_price: float) -> list:
    """
    Genererer tekstuelle insights baseret på expert ratings.
    """
    insights = []

    if not analyst_ratings:
        return insights

    recommendation = analyst_ratings.get("recommendation", "")
    num_analysts = analyst_ratings.get("num_analysts", 0)
    target_mean = analyst_ratings.get("target_mean")
    target_median = analyst_ratings.get("target_median")
    target_high = analyst_ratings.get("target_high")
    target_low = analyst_ratings.get("target_low")

    # Hoved anbefaling
    if recommendation:
        if "køb" in recommendation.lower():
            emoji = "✓"
        elif "sælg" in recommendation.lower():
            emoji = "✗"
        else:
            emoji = "•"

        insights.append(
            f"{emoji} Analytiker consensus: {recommendation} ({num_analysts} analytikere)"
        )

    # Target pris analyse
    if target_mean and current_price:
        upside = ((target_mean - current_price) / current_price) * 100
        if upside > 0:
            insights.append(
                f"✓ Target pris (gennemsnit): {target_mean:.2f} ({upside:+.1f}% potentiale)"
            )
        else:
            insights.append(
                f"✗ Target pris (gennemsnit): {target_mean:.2f} ({upside:+.1f}% risiko)"
            )

    # Target range
    if target_high and target_low:
        insights.append(
            f"• Target range: {target_low:.2f} - {target_high:.2f}"
        )

    return insights


def scrape_nordnet_rating(ticker: str) -> dict:
    """
    Forsøger at scrape NordNet ekspertvurdering hvis muligt.
    Note: Dette kan kræve JavaScript rendering eller direkte API adgang.
    """
    # Placeholder for evt. fremtidig NordNet integration
    # NordNet har desværre CORS protection, så standard scraping virker ikke
    return None


def scrape_seeking_alpha_ratings(ticker: str) -> dict:
    """
    Forsøger at hente ratings fra Seeking Alpha.
    Note: Seeking Alpha har også API protection.
    """
    # Placeholder for evt. fremtidig Seeking Alpha integration
    return None
