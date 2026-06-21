"""
HOVEDANALYZER MODULE
====================
Kombinerer alle scoring-komponenter til en samlet vurdering
"""

from src.advanced_scorer import (
    calculate_value_score,
    calculate_growth_score,
    calculate_quality_score,
    calculate_momentum_score,
    calculate_risk_score,
    calculate_sentiment_score,
    calculate_composite_score,
    get_overall_rating,
    generate_detailed_scoring_report,
)
from src.analyst_ratings import get_analyst_ratings, get_analyst_sentiment_score


def analyze_stock(data: dict, indicators: dict, analyst_data: dict = None, news_data: dict = None) -> dict:
    """
    Komplet aktieanalyse med alle scorer
    Returnerer samlet vurdering med alle komponenter
    """
    
    # Sikr at vi har analytikerdata
    if analyst_data is None:
        analyst_data = {}
    
    # Generér detaljeret scoringsrapport
    report = generate_detailed_scoring_report(data, indicators, analyst_data, news_data)
    
    return {
        "ticker": data.get("ticker"),
        "name": data.get("name"),
        "latest_price": data.get("latest_price"),
        "currency": data.get("currency"),
        "composite_score": report["composite_score"],
        "rating": report["rating"],
        "rating_description": report["rating_description"],
        "component_scores": report["component_scores"],
        "insights": report["all_insights"],
        "weights": report["weights"],
        "timestamp": data.get("timestamp"),
    }


def get_analysis_summary(analysis_result: dict) -> str:
    """
    Genererer tekstsammenfattelse af analysen
    """
    lines = []
    lines.append(f"\n{'='*60}")
    lines.append(f"AKTIEANALYSE: {analysis_result.get('name')} ({analysis_result.get('ticker')})")
    lines.append(f"{'='*60}\n")
    
    lines.append(f"Pris: {analysis_result.get('latest_price')} {analysis_result.get('currency')}")
    lines.append(f"Samlet Score: {analysis_result.get('composite_score')}/100")
    lines.append(f"Rating: {analysis_result.get('rating')}")
    lines.append(f"Beskrivelse: {analysis_result.get('rating_description')}\n")
    
    # Component scores
    scores = analysis_result.get("component_scores", {})
    lines.append("KOMPONENTER:")
    lines.append(f"  Værdi Score:     {scores.get('value_score', 'N/A')}/100")
    lines.append(f"  Vækst Score:     {scores.get('growth_score', 'N/A')}/100")
    lines.append(f"  Kvalitet Score:  {scores.get('quality_score', 'N/A')}/100")
    lines.append(f"  Momentum Score:  {scores.get('momentum_score', 'N/A')}/100")
    lines.append(f"  Risiko Score:    {scores.get('risk_score', 'N/A')}/100")
    lines.append(f"  Sentiment Score: {scores.get('sentiment_score', 'N/A')}/100\n")
    
    # Key insights
    insights = analysis_result.get("insights", [])
    if insights:
        lines.append("VIGTIGSTE PUNKTER:")
        for i, insight in enumerate(insights[:15], 1):  # Top 15 insights
            lines.append(f"  {i}. {insight}")
    
    lines.append(f"\n{'='*60}\n")
    
    return "\n".join(lines)


# Behold gamle funktioner for kompatibilitet
def calculate_fundamental_score(data: dict) -> int:
    """
    Beregner værdi-baseret score (gamle version for kompatibilitet)
    """
    value_score, _, _ = calculate_value_score(data)
    return value_score