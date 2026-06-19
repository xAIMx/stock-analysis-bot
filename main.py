import sys
import os
from dotenv import load_dotenv
from src.data_fetcher import get_stock_data
from src.analyzer import calculate_fundamental_score
from src.technical_analyzer import calculate_technical_indicators, calculate_technical_score
from src.analyst_ratings import get_analyst_ratings, get_analyst_sentiment_score
from src.report_generator import generate_markdown_report, save_report
from src.discord_client import send_report_async

# Load environment variables from .env
load_dotenv()


def main():
    if len(sys.argv) < 2:
        print("Brug: python main.py TICKER")
        print("Eksempel: python main.py NOVO-B.CO")
        return

    ticker = sys.argv[1]
    data = get_stock_data(ticker)
    
    fundamental_score = calculate_fundamental_score(data)
    
    # Beregn tekniske indikatorer
    technical_indicators = calculate_technical_indicators(data.get("history"))
    technical_score = calculate_technical_score(technical_indicators)

    # Hent analyst ratings
    analyst_data = {
        "recommendation_mean": data.get("recommendation_mean"),
        "recommendation_key": data.get("recommendation_key"),
        "numberOfAnalystOpinions": data.get("number_of_analysts"),
        "targetMeanPrice": data.get("target_mean_price"),
        "targetMedianPrice": data.get("target_median_price"),
        "targetHighPrice": data.get("target_high_price"),
        "targetLowPrice": data.get("target_low_price"),
    }
    analyst_ratings = get_analyst_ratings(analyst_data)
    analyst_score = get_analyst_sentiment_score(analyst_ratings)

    report = generate_markdown_report(data, fundamental_score, technical_indicators, technical_score, analyst_ratings, analyst_score)
    filename = save_report(ticker, report)

    print("\n=== Aktieanalyse Data ===")
    for key, value in data.items():
        if key != "history":  # Gem historien fra print output
            print(f"{key}: {value}")

    print("\n=== Analyse ===")
    print(f"Fundamental Score: {fundamental_score}/100")
    print(f"Technical Score: {technical_score}/100")
    print(f"Analyst Score: {analyst_score}/100")
    print(f"\nRapport gemt som: {filename}")

    # Send til Discord
    print("\n=== Discord Upload ===")
    if send_report_async(ticker, filename):
        print("Rapport sendt til Discord ✅")
    else:
        print("Rapport kunne ikke sendes til Discord (tjek DISCORD_BOT_TOKEN)")



if __name__ == "__main__":
    main()