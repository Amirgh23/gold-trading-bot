"""
Advanced Analytics and Reporting Engine
"""

import numpy as np
import pandas as pd
from datetime import datetime
import json
from typing import Dict, List


class AdvancedAnalytics:
    """Advanced analytics for trading performance"""
    
    def __init__(self):
        self.trades = []
        self.equity_curve = []
        
    def add_trade(self, trade: Dict):
        """Add trade to analytics"""
        self.trades.append(trade)
    
    def add_equity_point(self, equity: float):
        """Add equity point"""
        self.equity_curve.append(equity)
    
    def calculate_returns(self) -> Dict:
        """Calculate return metrics"""
        if len(self.equity_curve) < 2:
            return {}
        
        equity_array = np.array(self.equity_curve)
        initial = equity_array[0]
        final = equity_array[-1]
        
        total_return = (final - initial) / initial
        
        # Daily returns
        daily_returns = np.diff(equity_array) / equity_array[:-1]
        
        # Annualized return
        n_days = len(equity_array)
        annualized_return = (final / initial) ** (252 / n_days) - 1
        
        return {
            'total_return': float(total_return),
            'total_return_pct': float(total_return * 100),
            'annualized_return': float(annualized_return),
            'annualized_return_pct': float(annualized_return * 100),
            'daily_return_mean': float(np.mean(daily_returns)),
            'daily_return_std': float(np.std(daily_returns))
        }
    
    def calculate_risk_metrics(self) -> Dict:
        """Calculate risk metrics"""
        if len(self.equity_curve) < 2:
            return {}
        
        equity_array = np.array(self.equity_curve)
        daily_returns = np.diff(equity_array) / equity_array[:-1]
        
        # Volatility
        volatility = np.std(daily_returns)
        annualized_volatility = volatility * np.sqrt(252)
        
        # Value at Risk (95%)
        var_95 = np.percentile(daily_returns, 5)
        
        # Conditional Value at Risk
        cvar_95 = np.mean(daily_returns[daily_returns <= var_95])
        
        # Maximum Drawdown
        cummax = np.maximum.accumulate(equity_array)
        drawdown = (equity_array - cummax) / cummax
        max_drawdown = np.min(drawdown)
        
        # Drawdown Duration
        drawdown_duration = self.calculate_drawdown_duration(equity_array)
        
        return {
            'volatility': float(volatility),
            'annualized_volatility': float(annualized_volatility),
            'var_95': float(var_95),
            'cvar_95': float(cvar_95),
            'max_drawdown': float(max_drawdown),
            'max_drawdown_pct': float(max_drawdown * 100),
            'max_drawdown_duration': drawdown_duration
        }
    
    def calculate_risk_adjusted_returns(self) -> Dict:
        """Calculate risk-adjusted return metrics"""
        if len(self.equity_curve) < 2:
            return {}
        
        equity_array = np.array(self.equity_curve)
        daily_returns = np.diff(equity_array) / equity_array[:-1]
        
        mean_return = np.mean(daily_returns)
        std_return = np.std(daily_returns)
        
        # Sharpe Ratio (assuming 0% risk-free rate)
        sharpe_ratio = (mean_return / std_return) * np.sqrt(252) if std_return > 0 else 0
        
        # Sortino Ratio (only downside volatility)
        downside_returns = daily_returns[daily_returns < 0]
        downside_std = np.std(downside_returns) if len(downside_returns) > 0 else 0
        sortino_ratio = (mean_return / downside_std) * np.sqrt(252) if downside_std > 0 else 0
        
        # Calmar Ratio
        cummax = np.maximum.accumulate(equity_array)
        max_drawdown = np.min((equity_array - cummax) / cummax)
        annual_return = (equity_array[-1] / equity_array[0]) ** (252 / len(equity_array)) - 1
        calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        return {
            'sharpe_ratio': float(sharpe_ratio),
            'sortino_ratio': float(sortino_ratio),
            'calmar_ratio': float(calmar_ratio)
        }
    
    def calculate_trade_statistics(self) -> Dict:
        """Calculate trade statistics"""
        if not self.trades:
            return {}
        
        profits = [t.get('profit', 0) for t in self.trades if 'profit' in t]
        
        if not profits:
            return {}
        
        profits_array = np.array(profits)
        
        # Win/Loss statistics
        winning_trades = profits_array[profits_array > 0]
        losing_trades = profits_array[profits_array < 0]
        
        win_rate = len(winning_trades) / len(profits) if len(profits) > 0 else 0
        
        # Profit statistics
        avg_win = np.mean(winning_trades) if len(winning_trades) > 0 else 0
        avg_loss = np.mean(losing_trades) if len(losing_trades) > 0 else 0
        
        # Profit factor
        gross_profit = np.sum(winning_trades)
        gross_loss = abs(np.sum(losing_trades))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Expectancy
        expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)
        
        return {
            'total_trades': len(profits),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': float(win_rate),
            'win_rate_pct': float(win_rate * 100),
            'avg_win': float(avg_win),
            'avg_loss': float(avg_loss),
            'profit_factor': float(profit_factor),
            'expectancy': float(expectancy),
            'total_profit': float(np.sum(profits_array))
        }
    
    def calculate_monthly_returns(self) -> Dict:
        """Calculate monthly returns"""
        if len(self.equity_curve) < 2:
            return {}
        
        # Simulate monthly data
        equity_array = np.array(self.equity_curve)
        n_months = max(1, len(equity_array) // 21)  # Assuming 21 trading days per month
        
        monthly_returns = {}
        for i in range(n_months):
            start_idx = i * 21
            end_idx = min((i + 1) * 21, len(equity_array))
            
            if start_idx < len(equity_array):
                start_equity = equity_array[start_idx]
                end_equity = equity_array[end_idx - 1]
                monthly_return = (end_equity - start_equity) / start_equity
                monthly_returns[f'Month_{i+1}'] = float(monthly_return)
        
        return monthly_returns
    
    @staticmethod
    def calculate_drawdown_duration(equity_curve: np.ndarray) -> int:
        """Calculate maximum drawdown duration"""
        cummax = np.maximum.accumulate(equity_curve)
        drawdown = (equity_curve - cummax) / cummax
        
        in_drawdown = drawdown < 0
        drawdown_periods = []
        current_period = 0
        
        for in_dd in in_drawdown:
            if in_dd:
                current_period += 1
            else:
                if current_period > 0:
                    drawdown_periods.append(current_period)
                current_period = 0
        
        return max(drawdown_periods) if drawdown_periods else 0
    
    def generate_report(self) -> Dict:
        """Generate comprehensive analytics report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'returns': self.calculate_returns(),
            'risk': self.calculate_risk_metrics(),
            'risk_adjusted': self.calculate_risk_adjusted_returns(),
            'trades': self.calculate_trade_statistics(),
            'monthly_returns': self.calculate_monthly_returns()
        }
        
        return report
    
    def export_report(self, filename: str = 'analytics_report.json'):
        """Export analytics report"""
        report = self.generate_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✓ Report exported to {filename}")
        
        return report


def generate_sample_report():
    """Generate sample analytics report"""
    analytics = AdvancedAnalytics()
    
    # Simulate equity curve
    np.random.seed(42)
    equity = 10000
    for _ in range(252):  # 1 year of trading
        daily_return = np.random.randn() * 0.01
        equity *= (1 + daily_return)
        analytics.add_equity_point(equity)
    
    # Simulate trades
    for i in range(50):
        profit = np.random.randn() * 100
        analytics.add_trade({'profit': profit})
    
    # Generate report
    report = analytics.generate_report()
    
    print("=" * 60)
    print("📊 Advanced Analytics Report")
    print("=" * 60)
    print(json.dumps(report, indent=2))
    
    # Export
    analytics.export_report()
    
    return analytics, report


if __name__ == "__main__":
    analytics, report = generate_sample_report()
