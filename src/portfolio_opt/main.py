import vectorbt as vbt
import numpy as np
import matplotlib.pyplot as plt
import cvxpy as cp
import pandas as pd
from pathlib import Path
from portfolio_opt.portfolio_backtester import PortfolioBacktester
from portfolio_opt.portfolio_plotter import PortfolioPlotter


def construct_efficient_frontier(returns, tickers, num_points=100):
    mus = (returns.mean() * 252).values
    cov = returns.cov().values * 252
    target_returns = np.linspace(mus.min(), mus.max(), num_points)

    ef_returns, ef_vols = [], []
    for target in target_returns:
        w = cp.Variable(len(tickers))
        risk = cp.quad_form(w, cov)
        constraints = [
            cp.sum(w) == 1,
            w >= 0,
            mus @ w >= target
        ]
        try:
            prob = cp.Problem(cp.Minimize(risk), constraints)
            prob.solve()
            if w.value is None:
                raise ValueError("Infeasible solution")
            ef_returns.append(target)
            ef_vols.append(np.sqrt(risk.value))
        except Exception as e:
            print(f"⚠️ Optimization failed at target return {target:.4f}: {e}")
            continue
    return ef_returns, ef_vols



def summarize_equity_curve(equity_curve, returns, risk_free_rate):
    weights = np.ones(len(returns.columns)) / len(returns.columns)
    bt = PortfolioBacktester(returns, weights, initial_value=equity_curve.iloc[0])
    bt.run()  # use run to compute all metrics
    bt.equity_curve = equity_curve  # override only equity_curve if needed for external curve
    summary = bt.summary(risk_free_rate=risk_free_rate)
    return summary, bt

def format_summary_df(df, percent_cols):
    formatted_df = df.copy()
    for col in formatted_df.columns:
        if col in percent_cols:
            formatted_df[col] = formatted_df[col].apply(lambda x: f"{x:.2%}")
        else:
            formatted_df[col] = formatted_df[col].apply(lambda x: f"{x:.4f}")
    return formatted_df

def main():
    # Load historical price data for selected tickers
    
    # Ensure output directories exist
    Path("reports").mkdir(exist_ok=True)
    Path("reports/efficient_frontier").mkdir(parents=True, exist_ok=True)
    Path("exports").mkdir(exist_ok=True)

    tickers = ['AAPL', 'MSFT', 'AMZN', 'META', 'GOOGL', 'NVDA','BRK-B','V','JNJ','HCA']

    # Load historical price data for selected tickers
    price = vbt.YFData.download(tickers, start='2019-01-01',end ='2024-12-31').get('Close')
    price = price.dropna(how='any')  # Drop all rows with any NaN values to align symbols properly

    # Download benchmark SPY
    spy = vbt.YFData.download('SPY', start='2019-01-01', end='2024-12-31').get('Close')
    spy = spy.dropna()
    spy_returns = spy.pct_change(fill_method=None).dropna().to_frame(name='SPY')

    # Calculate daily log returns
    returns = price.pct_change(fill_method=None).dropna(how='any')

    rf = 0.03  # Risk-free rate

    print("\n📅 Running annual rebalancing backtest...")
    all_equity = pd.Series(dtype=float)

    n_ports = 10_000
    np.random.seed(42)

    yearly_summaries = {}
    annual_weights = {}

    for year in sorted(returns.index.to_series().dropna().dt.year.unique()):
        start = f"{year}-01-01"
        end = f"{year}-12-31"
        yearly_returns = returns.loc[start:end]

        if len(yearly_returns) < 50:
            continue

        weights = np.random.dirichlet(np.ones(len(tickers)), size=n_ports)
        port_returns = np.dot(weights, yearly_returns.mean()) * 252
        port_vols = np.sqrt(np.diag(weights @ yearly_returns.cov().values @ weights.T)) * np.sqrt(252)
        sharpe_ratios = (port_returns - rf) / port_vols

        max_sharpe_idx = np.argmax(sharpe_ratios)
        opt_weights = weights[max_sharpe_idx]

        annual_weights[year] = dict(zip(tickers, opt_weights))

        ef_returns, ef_vols = construct_efficient_frontier(yearly_returns, tickers)
        PortfolioPlotter.plot_efficient_frontier(
            port_vols,
            port_returns,
            sharpe_ratios,
            ef_vols,
            ef_returns,
            max_sharpe_idx,
            filename=f"reports/efficient_frontier/efficient_frontier_{year}.png"
        )

        initial_value = all_equity.iloc[-1] if not all_equity.empty else 1_000_000
        bt = PortfolioBacktester(yearly_returns, opt_weights, initial_value=initial_value).run()
        year_equity = bt.equity_curve
        if all_equity.empty:
            all_equity = year_equity
        else:
            all_equity = pd.concat([all_equity, year_equity])
        
        year_summary = bt.summary(risk_free_rate=rf)
        yearly_summaries[year] = year_summary

    # Plot portfolio margin per year
    margin_per_year = {}

    for year, weights in annual_weights.items():
        w = np.array(list(weights.values()))
        margin = np.sum(w ** 2)  # Herfindahl index style margin (proxy for concentration)
        margin_per_year[year] = margin

    PortfolioPlotter.plot_portfolio_margin(margin_per_year)
    PortfolioPlotter.plot_portfolio_allocation(annual_weights)

    all_equity.to_csv("exports/annual_rebalanced_equity.csv")
    PortfolioPlotter.plot_equity_curve(all_equity)
    PortfolioPlotter.plot_equity_vs_benchmark(all_equity, spy)

    percent_cols = {'Total Return', 'CAGR', 'Volatility', 'Max Drawdown', 'CVaR (95%)'}

    # Full backtest summary export
    full_returns = pd.DataFrame(all_equity.pct_change().dropna(), columns=['Portfolio'])
    summary_dict, full_bt = summarize_equity_curve(all_equity, full_returns, rf)

    print("\n📊 Backtest Summary (Annual Rebalanced Portfolio):")
    for k, v in summary_dict.items():
        if isinstance(v, float):
            if k in percent_cols:
                print(f"{k}: {v:.2%}")
            else:
                print(f"{k}: {v:.4f}")
        else:
            print(f"{k}: {v}")

    full_df = pd.DataFrame([summary_dict])
    formatted_full_df = format_summary_df(full_df, percent_cols)
    formatted_full_df.to_csv("exports/full_backtest_summary.csv", index=False)

    # Benchmark Summary
    benchmark_bt = PortfolioBacktester(spy_returns, np.array([1.0]), initial_value=1_000_000).run()
    benchmark_summary = benchmark_bt.summary(risk_free_rate=rf)
    benchmark_df = pd.DataFrame([benchmark_summary])
    formatted_benchmark_df = format_summary_df(benchmark_df, percent_cols)
    formatted_benchmark_df.to_csv("exports/benchmark_summary.csv", index=False)

    print("\n📊 Benchmark (SPY) Summary:")
    print(benchmark_df.to_string(float_format=lambda x: f"{x:.2%}" if isinstance(x, float) else str(x)))

    # Annual summary export
    summary_df = pd.DataFrame(yearly_summaries).T
    formatted_annual_df = format_summary_df(summary_df, percent_cols)
    formatted_annual_df.to_csv("exports/annual_summary.csv")
    print("\n📊 Annual Summary:")
    print(summary_df.to_string(float_format=lambda x: f"{x:.2%}" if isinstance(x, float) else str(x)))

    if 'annual_weights' in locals():
        weights_df = pd.DataFrame(annual_weights).T
        weights_df.to_csv("exports/annual_weights.csv")
        print("\n📊 Annual Portfolio Weights:")
        print(weights_df)

if __name__ == "__main__":
    main()
