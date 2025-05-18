# Portfolio‑Opt — Optimise, Backtest, Repeat 🚀

> “In the short run the market is a voting machine, but in the long run it is a weighing machine.”  
> — **Benjamin Graham**

Remember those 1 a.m. Excel sessions, pasting tickers and promising yourself *this time* you’d keep it neat? **Portfolio‑Opt** turns that spreadsheet pain into a few lines of Python. No gigantic notebooks, no 300‑line boilerplate—just a focused toolkit for running honest‑to‑goodness portfolio experiments.

---

## What Makes It Useful?

* **Sharpe‑hunting** – samples thousands of random portfolios each rebalance period and keeps the one with the best risk‑adjusted return.  
* **Visual sanity checks** – Efficient Frontier, equity curve, drawdown, benchmark overlay… all rendered in PNGs ready for your slide deck.  
* **Zero‑friction workflow** – install, run, read the CSVs, repeat. Works with any liquid tickers you throw at it.

If you want the *full* feature list, flag explanations, or project layout, jump to the main <kbd>README</kbd>. This page keeps things high‑level and narrative so the docs don’t feel like déjà vu.

---

## Installation

```bash
pip install portfolio-opt          # or 'poetry add portfolio-opt'
```

Python ≥ 3.9 and an internet connection for price data—that’s the entire setup.

---

## Five‑Minute Tour

```bash
# 1) Choose a basket of stocks
portfolio-opt --tickers AAPL MSFT NVDA META AMZN

# 2) Pick a rhythm (default is yearly “YE”)
portfolio-opt --rebalance 6M     # Semi‑annual
portfolio-opt --rebalance Q      # Quarterly

# 3) Open the PNGs & CSVs
open reports/equity_and_drawdown_plot.png
```

You’ll see:

| Folder | What’s inside |
|--------|---------------|
| `reports/` | Efficient frontier, equity vs. SPY, drawdown, allocation plots |
| `exports/` | CSVs for backtest summary, annual stats, yearly weights |

Need more knobs (risk‑free rate, benchmark, random seed, etc.)? Check the CLI table in the README.

---

## Use It Like a Library

```python
from portfolio_opt.main import run_annual_rebalanced_backtest

run_annual_rebalanced_backtest(
    tickers=["AAPL", "MSFT", "NVDA"],
    start_date="2020-01-01",
    end_date="2024-12-31",
    rebalance_freq="6M",          # A / 6M / Q / 3M
)
```

Same outputs, no shell required.

---

## Reading the Numbers

* **Backtest Summary** – total return, CAGR, volatility, Sharpe, max drawdown, CVaR (stdout).  
* **Annual Summary** – one row per period (`exports/annual_summary.csv`).  
* **Annual Weights** – how allocation shifts over time (`exports/annual_weights.csv`).  
* **Margin Plot** – Herfindahl concentration score per year.

---

## Tips, Tricks & Caveats

* Swap the random Dirichlet draw for your own factor ranking to turn it into a factor model.  
* Hook the weight CSV into a broker API for live trading—the backtester is state‑agnostic.  
* Long‑only, daily bars for now. Intraday and shorting are future projects.  
* Sampling 100 k portfolios on a 15‑year window is CPU‑bound—brew coffee first.

---

## License & Credits

MIT license. Fork it, break it, improve it—just drop a ⭐ if it saves you time.

Made with midnight coffee in Bangkok. Happy compounding! ☕