# Examples of using the market_scraper library
from financial_scraper import StatusInvestProvider, FundamentusProvider, InvestorTenProvider, TradingViewProvider, MarketDataService
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def status_invest_example():
    # Initialize the service with Status Invest provider
    service = StatusInvestProvider(
        download_path=BASE_DIR,
        filename="status_invest_stocks.csv",
        show_browser=True
    )

    # Fetch and save data
    service.run(sector=StatusInvestProvider.Sector.FINANCIAL_AND_OTHERS)


def fundamentus_example():
    # Initialize the service with Fundamentus provider
    service = FundamentusProvider(
        download_path=BASE_DIR,
        filename="fundamentus_stocks.csv"
    )

    # Fetch and save data
    service.run()


def investor_ten_example():
    """
    Example showing how to use the InvestorTenProvider to scrape REIT (FII) dividend data
    from Investidor10 website for a specific year.
    """
    # Initialize the provider with default filename (funds-{year}.csv)
    service = InvestorTenProvider(
        download_path=BASE_DIR
    )

    # Fetch and save data for 2023
    # This will create a file named 'funds-2023.csv'
    service.run("2023")

    # Example with custom filename
    service_custom = InvestorTenProvider(
        download_path=BASE_DIR,
        filename="fiis-dividends-2024.csv"
    )

    # Fetch and save data for 2024 with custom filename
    service_custom.run("2024")


def trading_view_example():
    # Get stocks list (in this example we use the csv get by status_invest_example)
    stocks_file = os.path.join(BASE_DIR, "stocks_for_trading_view_example.csv")
    with open(stocks_file, "r") as f:
        stocks = [line.split(";")[0] for line in f.readlines()[1:]]  # Skip header
    stocks = stocks[:10]

    # Initialize the service with Trading View provider
    service = TradingViewProvider(
        download_path=BASE_DIR,
        filename="trading_view_stocks.csv"
    )
    service.run(stocks=stocks)


def market_data_example():
    # Initialize the service with Market Data provider
    service = MarketDataService(
        download_path=BASE_DIR,
        filename="market_data_stocks.csv",
        show_browser=True
    )

    # Fetch and save data
    service.run()


if __name__ == "__main__":
    status_invest_example()
    fundamentus_example()
    investor_ten_example()
