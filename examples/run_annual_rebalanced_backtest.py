from portfolio_opt.main import run_annual_rebalanced_backtest

run_annual_rebalanced_backtest(
    tickers=["AAPL", "MSFT", "NVDA"],
    start_date="2020-01-01",
    end_date="2024-12-31",
)