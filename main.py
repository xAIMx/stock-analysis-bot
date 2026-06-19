import sys
from src.data_fetcher import get_stock_data
from src.analyzer import calculate_fundamental_score
from src.report_generator import generate_markdown_report, save_report


def main():
    if len(sys.argv) < 2:
        print("Brug: python main.py TICKER")
        print("Eksempel: python main.py NOVO-B.CO")
        return

    ticker = sys.argv[1]
    data = get_stock_data(ticker)
    score = calculate_fundamental_score(data)
    report = generate_markdown_report(data, score)
    filename = save_report(ticker, report)

    print("\n=== Aktieanalyse Data ===")
    for key, value in data.items():
        print(f"{key}: {value}")

    print("\n=== Analyse ===")
    print(f"Fundamental Score: {score}/100")
    print(f"\nRapport gemt som: {filename}")


if __name__ == "__main__":
    main()