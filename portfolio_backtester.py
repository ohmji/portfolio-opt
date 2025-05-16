import numpy as np

# PortfolioBacktester class for backtesting portfolio strategies
class PortfolioBacktester:
    def __init__(self, returns, weights, initial_value=1_000_000):
        self.weights = weights
        self.returns = returns
        self.initial_value = initial_value
        self.daily_returns = None
        self.equity_curve = None

    def run(self):
        assert np.isclose(self.weights.sum(), 1), "Weights must sum to 1"
        assert (self.weights >= 0).all(), "Weights must be non-negative"
        self.daily_returns = self.returns @ self.weights
        self.equity_curve = (1 + self.daily_returns).cumprod() * self.initial_value
        return self

    def summary(self, risk_free_rate=0.03):
        assert self.equity_curve is not None, "Must run backtest before calling summary"
        total_return = self.equity_curve.iloc[-1] / self.equity_curve.iloc[0] - 1
        cagr = (self.equity_curve.iloc[-1] / self.equity_curve.iloc[0]) ** (1 / (len(self.equity_curve) / 252)) - 1
        volatility = self.daily_returns.std() * np.sqrt(252)
        sharpe = (self.daily_returns.mean() * 252 - risk_free_rate) / volatility
        max_dd = (self.equity_curve / self.equity_curve.cummax() - 1).min()

        # Assuming CVaR (95%) is computed elsewhere and attached as attribute cvar_95
        cvar_95 = getattr(self, 'cvar_95', None)

        summary_dict = {
            'Total Return': total_return,
            'CAGR': cagr,
            'Volatility': volatility,
            'Sharpe Ratio': sharpe,
            'Max Drawdown': max_dd
        }
        if cvar_95 is not None:
            summary_dict['CVaR (95%)'] = cvar_95


        return summary_dict