import matplotlib.pyplot as plt

class PortfolioPlotter:
    @staticmethod
    def plot_drawdown(drawdown):
        plt.figure(figsize=(10, 4))
        drawdown.plot(title='Drawdown of Max Sharpe Portfolio', color='blue')
        plt.ylabel('Drawdown')
        plt.xlabel('Date')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("reports/drawdown_plot.png")
        plt.close()

    @staticmethod
    def plot_equity_curve(equity_curve):
        plt.figure(figsize=(10, 4))
        equity_curve.plot(title='Equity Curve of Max Sharpe Portfolio', color='green')
        plt.ylabel('Portfolio Value')
        plt.xlabel('Date')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("reports/equity_curve_plot.png")
        plt.close()

    @staticmethod
    def plot_efficient_frontier(port_vols, port_returns, sharpe_ratios, ef_vols, ef_returns, max_sharpe_idx):
        plt.figure(figsize=(10, 6))
        plt.scatter(port_vols, port_returns, c=sharpe_ratios, cmap='viridis', alpha=0.6)
        plt.colorbar(label='Sharpe Ratio')
        plt.scatter(port_vols[max_sharpe_idx], port_returns[max_sharpe_idx], c='red', label='Max Sharpe', s=100)
        plt.plot(ef_vols, ef_returns, color='black', label='Efficient Frontier', linewidth=2)
        plt.xlabel('Volatility')
        plt.ylabel('Expected Return')
        plt.legend()
        plt.title('Efficient Frontier with Random Portfolios')
        plt.grid(True)
        plt.savefig("reports/efficient_frontier_plot.png")
        plt.close()

    @staticmethod
    def plot_asset_prices(price):
        plt.figure(figsize=(12, 6))
        price.plot(title="Asset Prices Over Time")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("reports/asset_prices_plot.png")
        plt.close()