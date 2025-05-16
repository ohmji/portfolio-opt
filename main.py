import vectorbt as vbt
import numpy as np
import matplotlib.pyplot as plt
import cvxpy as cp
import pandas as pd
from portfolio_backtester import PortfolioBacktester
from portfolio_plotter import PortfolioPlotter


# Load historical price data for selected tickers
tickers = ['BRK-B', 'META','UNH','JD','GOOGL','HCA','BABA']

# Load historical price data for selected tickers
price = vbt.YFData.download(tickers, start='2015-01-01').get('Close')
price = price.dropna()  # remove rows with any missing data across assets

# Calculate daily log returns
returns = price.pct_change(fill_method=None).dropna()

# Number of simulated portfolios
n_ports = 10_000
np.random.seed(42)
weights = np.random.dirichlet(np.ones(len(tickers)), size=n_ports)

# Calculate expected return & volatility
port_returns = np.dot(weights, returns.mean()) * 252
port_vols = np.sqrt(np.diag(weights @ returns.cov().values @ weights.T)) * np.sqrt(252)
rf = 0.03  # Risk-free rate

sharpe_ratios = (port_returns - rf) / port_vols

# Export Monte Carlo portfolio metrics
port_df = pd.DataFrame({
    'Return': port_returns,
    'Volatility': port_vols,
    'Sharpe Ratio': sharpe_ratios
})
port_df.to_csv("monte_carlo_portfolios.csv", index=False)

# Construct Efficient Frontier using cvxpy
mus = (returns.mean() * 252).values  # convert to numpy array for cvxpy compatibility
cov = returns.cov().values * 252
target_returns = np.linspace(mus.min(), mus.max(), 100)

ef_returns, ef_vols = [], []

for target in target_returns:
    w = cp.Variable(len(tickers))
    risk = cp.quad_form(w, cov)
    constraints = [
        cp.sum(w) == 1,
        w >= 0,
        mus @ w >= target
    ]
    prob = cp.Problem(cp.Minimize(risk), constraints)
    prob.solve()

    if w.value is None:
        print(f"⚠️ Optimization failed at target return {target:.4f}")
        continue
    ef_returns.append(target)
    ef_vols.append(np.sqrt(risk.value))
    
# Find max Sharpe portfolio
max_sharpe_idx = np.argmax(sharpe_ratios)
opt_weights = weights[max_sharpe_idx]

# Calculate metrics of max Sharpe portfolio
opt_return = port_returns[max_sharpe_idx]
opt_vol = port_vols[max_sharpe_idx]
opt_sharpe = sharpe_ratios[max_sharpe_idx]

# Display financial metrics of max Sharpe portfolio
print(f"\n🔍 Portfolio with Maximum Sharpe Ratio:")
print(f"Expected Annual Return: {opt_return:.2%}")
print(f"Annual Volatility: {opt_vol:.2%}")
print(f"Sharpe Ratio: {opt_sharpe:.2f}")

# Calculate daily returns of the optimal portfolio
port_daily_returns = returns @ opt_weights

# Calculate max drawdown of the optimal portfolio
portfolio = (returns @ opt_weights).add(1).cumprod()
drawdown = (portfolio / portfolio.cummax()) - 1
max_drawdown = drawdown.min()

print(f"Max Drawdown: {max_drawdown:.2%}")

# Calculate Calmar Ratio
calmar_ratio = opt_return / abs(max_drawdown)
print(f"Calmar Ratio: {calmar_ratio:.2f}")

downside_returns = port_daily_returns[port_daily_returns < 0]
sortino_ratio = (opt_return - rf) / np.std(downside_returns)
print(f"Sortino Ratio: {sortino_ratio:.2f}")

PortfolioPlotter.plot_drawdown(drawdown)

# Calculate 95% Value at Risk (VaR)
confidence_level = 0.95
var_95 = -np.percentile(port_daily_returns, (1 - confidence_level) * 100)
print(f"Value at Risk (95%): {var_95:.2%}")

cvar_95 = -port_daily_returns[port_daily_returns <= -var_95].mean()
print(f"Conditional Value at Risk (95%): {cvar_95:.2%}")

PortfolioPlotter.plot_efficient_frontier(port_vols, port_returns, sharpe_ratios, ef_vols, ef_returns, max_sharpe_idx)

# Export Efficient Frontier data
ef_df = pd.DataFrame({
    'Target Return': ef_returns,
    'Volatility': ef_vols
})
ef_df.to_csv("efficient_frontier.csv", index=False)

# Print weights of the optimal portfolio
for t, w in zip(tickers, opt_weights):
    print(f"{t}: {w:.2%}")

def run_backtest(returns, weights):
    bt = PortfolioBacktester(returns, weights).run()
    print("\n📊 Backtest Summary:")
    summary = bt.summary()
    print(f"Total Return: {summary['Total Return']:.2%}")
    print(f"CAGR: {summary['CAGR']:.2%}")
    print(f"Volatility: {summary['Volatility']:.2f}")
    print(f"Sharpe Ratio: {summary['Sharpe Ratio']:.2f}")
    print(f"Max Drawdown: {summary['Max Drawdown']:.2f}")

    equity_curve = bt.equity_curve
    PortfolioPlotter.plot_equity_curve(equity_curve)


run_backtest(returns, opt_weights)

summary = PortfolioBacktester(returns, opt_weights).run().summary(risk_free_rate=rf)
start_date = price.index.min().strftime("%Y-%m-%d")
end_date = price.index.max().strftime("%Y-%m-%d")
top_weights = sorted(zip(tickers, opt_weights), key=lambda x: x[1], reverse=True)[:5]
top_weight_dict = {f"Top Weight {i+1} ({t})": w for i, (t, w) in enumerate(top_weights)}

# Export full result summary to CSV for feedback loop
result_dict = {
    'Start Date': start_date,
    'End Date': end_date,
    'Num Assets': len(tickers),
    'Expected Annual Return': opt_return,
    'Annual Volatility': opt_vol,
    'Sharpe Ratio': opt_sharpe,
    'Max Drawdown': max_drawdown,
    'Calmar Ratio': calmar_ratio,
    'Sortino Ratio': sortino_ratio,
    'Value at Risk (95%)': var_95,
    'Conditional Value at Risk (95%)': cvar_95,
    'Backtest Total Return': summary['Total Return'],
    'Backtest CAGR': summary['CAGR'],
    'Backtest Volatility': summary['Volatility'],
    'Backtest Sharpe Ratio': summary['Sharpe Ratio'],
    'Backtest Max Drawdown': summary['Max Drawdown'],
    **top_weight_dict
}

pd.DataFrame([result_dict]).to_csv("portfolio_metrics_summary.csv", index=False)

PortfolioPlotter.plot_asset_prices(price)

pd.Series(opt_weights, index=tickers).to_csv("best_weights.csv")

if opt_sharpe > 0.7 and max_drawdown > -0.3:
    print("✅ Portfolio meets real-world criteria (Sharpe > 0.7 and Max DD > -30%)")
else:
    print("⚠️ Portfolio does NOT meet real-world criteria.")
