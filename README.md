# 📈 Portfolio Optimization & Backtesting

A lightweight and modular framework for backtesting quantitative portfolio strategies using **annual rebalancing**, **efficient frontier analysis**, and **Sharpe ratio optimization**.

---

## 📖 Documentation

Explore the full documentation here: [https://ohmji.github.io/portfolio-opt/](https://ohmji.github.io/portfolio-opt/)

---

## 🚀 Features

- ✅ Downloads historical stock data from Yahoo Finance via `vectorbt`
- ✅ Samples 10,000 random portfolios per calendar year
- ✅ Selects the **maximum Sharpe ratio portfolio** annually
- ✅ Computes and plots the **Efficient Frontier** using `cvxpy`
- ✅ Tracks performance vs. benchmark (`SPY`)
- ✅ Exports detailed reports: PNG plots and CSV summaries

---

## 🗂️ Project Structure

```
portfolio-opt/
├── main.py                    # Main orchestration script
├── portfolio_backtester.py    # Custom backtester with performance metrics
├── portfolio_plotter.py       # Visualization tools using matplotlib
├── reports/                   # Auto-generated plots (.png)
└── exports/                   # Auto-generated summaries (.csv)
```

| Module                     | Description                                         |
|---------------------------|-----------------------------------------------------|
| `main.py`                 | Coordinates data loading, optimization, backtest    |
| `portfolio_backtester.py` | Runs backtests and computes risk/return metrics     |
| `portfolio_plotter.py`    | All portfolio and asset visualizations              |

---

## 🛠️ Tools & Libraries

| Tool            | Role                                  |
|-----------------|----------------------------------------|
| Python 3.13     | Core language                         |
| Poetry          | Dependency & environment management   |
| vectorbt        | Market data ingestion & helpers       |
| cvxpy           | Portfolio optimization engine         |
| pandas / numpy  | Data analysis                         |
| matplotlib      | Chart rendering                       |

---

## ⚡ Quick Start

```bash
# Install dependencies
poetry install

# Run the full analysis
poetry run python main.py
```

### Output Files:
| Folder | Output |
|--------|--------|
| `reports/` | Efficient frontier charts, equity curves, drawdown |
| `exports/` | CSV files for annual summaries, weights, benchmark |

---

## ⚙️ Configuration Tips

| Feature | How to change |
|--------|----------------|
| Tickers | Modify `tickers` list in `main.py` |
| Risk-Free Rate | Change `rf = 0.03` in `main.py` |
| Portfolio Samples | Adjust `n_ports = 10_000` |
| Date Range | Update `start=` and `end=` in data loader |

---

## 🔧 Possible Extensions

1. **Live Trading** – Integrate with live modules from `vectorbt` or `QuantConnect`
2. **Factor Models** – Score stocks on valuation, momentum, etc., instead of random
3. **Risk Constraints** – Add CVaR, max drawdown, or concentration limits
4. **Visualization Dashboard** – Use Streamlit, Dash, or Jupyter for dynamic charts

---

## 📜 License

**MIT License** – Free to use and modify. Attribution appreciated.

---

> _"In investing, what is comfortable is rarely profitable." – Robert Arnott_

Enjoy building your own quantitative strategies! 🎯