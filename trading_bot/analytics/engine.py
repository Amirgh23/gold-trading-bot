"""Analytics engine for performance metrics calculation."""

from typing import List, Dict, Optional
from datetime import datetime
import numpy as np
import logging
from trading_bot.models.trade import Trade
from trading_bot.models.metrics import PerformanceMetrics

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """Calculates trading performance metrics."""
    
    @staticmethod
    def calculate_metrics(trades: List[Trade]) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics."""
        if not trades:
            return PerformanceMetrics(date=datetime.now())
        
        # Basic metrics
        total_trades = len(trades)
        winning_trades = sum(1 for t in trades if t.is_profitable)
        losing_trades = total_trades - winning_trades
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # P&L metrics
        total_pnl = sum(t.pnl for t in trades)
        gross_profit = sum(t.pnl for t in trades if t.is_profitable)
        gross_loss = abs(sum(t.pnl for t in trades if not t.is_profitable))
        
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 0
        
        # Sharpe ratio
        pnl_list = [t.pnl for t in trades]
        sharpe_ratio = AnalyticsEngine._calculate_sharpe_ratio(pnl_list)
        
        # Drawdown
        max_drawdown = AnalyticsEngine._calculate_max_drawdown(trades)
        
        # Recovery factor
        recovery_factor = (total_pnl / max_drawdown) if max_drawdown > 0 else 0
        
        metrics = PerformanceMetrics(
            date=datetime.now(),
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            profit_factor=profit_factor,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            recovery_factor=recovery_factor,
            daily_pnl=total_pnl,
            cumulative_pnl=total_pnl,
        )
        
        logger.info(
            f"Metrics: {total_trades} trades, "
            f"Win Rate: {win_rate:.2f}%, "
            f"Profit Factor: {profit_factor:.2f}, "
            f"Sharpe: {sharpe_ratio:.2f}"
        )
        
        return metrics
    
    @staticmethod
    def _calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio."""
        if len(returns) < 2:
            return 0.0
        
        returns_array = np.array(returns)
        excess_returns = returns_array - (risk_free_rate / 252)
        
        if excess_returns.std() == 0:
            return 0.0
        
        sharpe = (excess_returns.mean() / excess_returns.std()) * np.sqrt(252)
        return sharpe
    
    @staticmethod
    def _calculate_max_drawdown(trades: List[Trade]) -> float:
        """Calculate maximum drawdown."""
        if not trades:
            return 0.0
        
        cumulative_pnl = 0
        peak = 0
        max_dd = 0
        
        for trade in trades:
            cumulative_pnl += trade.pnl
            
            if cumulative_pnl > peak:
                peak = cumulative_pnl
            
            drawdown = peak - cumulative_pnl
            if drawdown > max_dd:
                max_dd = drawdown
        
        return max_dd
    
    @staticmethod
    def generate_daily_report(trades: List[Trade], date: datetime) -> Dict:
        """Generate daily trading report."""
        daily_trades = [
            t for t in trades
            if t.entry_time.date() == date.date()
        ]
        
        metrics = AnalyticsEngine.calculate_metrics(daily_trades)
        
        return {
            'date': date.isoformat(),
            'total_trades': metrics.total_trades,
            'winning_trades': metrics.winning_trades,
            'losing_trades': metrics.losing_trades,
            'win_rate': metrics.win_rate,
            'profit_factor': metrics.profit_factor,
            'daily_pnl': metrics.daily_pnl,
            'sharpe_ratio': metrics.sharpe_ratio,
            'max_drawdown': metrics.max_drawdown,
        }
    
    @staticmethod
    def generate_monthly_report(trades: List[Trade], year: int, month: int) -> Dict:
        """Generate monthly trading report."""
        monthly_trades = [
            t for t in trades
            if t.entry_time.year == year and t.entry_time.month == month
        ]
        
        metrics = AnalyticsEngine.calculate_metrics(monthly_trades)
        
        return {
            'year': year,
            'month': month,
            'total_trades': metrics.total_trades,
            'winning_trades': metrics.winning_trades,
            'losing_trades': metrics.losing_trades,
            'win_rate': metrics.win_rate,
            'profit_factor': metrics.profit_factor,
            'monthly_pnl': metrics.daily_pnl,
            'sharpe_ratio': metrics.sharpe_ratio,
            'max_drawdown': metrics.max_drawdown,
        }
    
    @staticmethod
    def compare_strategies(trades: List[Trade]) -> Dict[str, Dict]:
        """Compare performance across strategies."""
        strategies = {}
        
        for trade in trades:
            if trade.strategy not in strategies:
                strategies[trade.strategy] = []
            strategies[trade.strategy].append(trade)
        
        comparison = {}
        for strategy_name, strategy_trades in strategies.items():
            metrics = AnalyticsEngine.calculate_metrics(strategy_trades)
            comparison[strategy_name] = {
                'total_trades': metrics.total_trades,
                'win_rate': metrics.win_rate,
                'profit_factor': metrics.profit_factor,
                'sharpe_ratio': metrics.sharpe_ratio,
                'total_pnl': metrics.daily_pnl,
            }
        
        return comparison
    
    @staticmethod
    def generate_equity_curve(trades: List[Trade]) -> List[float]:
        """Generate equity curve from trades."""
        equity_curve = [0]
        cumulative_pnl = 0
        
        for trade in sorted(trades, key=lambda t: t.exit_time):
            cumulative_pnl += trade.pnl
            equity_curve.append(cumulative_pnl)
        
        return equity_curve
    
    @staticmethod
    def generate_drawdown_curve(trades: List[Trade]) -> List[float]:
        """Generate drawdown curve from trades."""
        equity_curve = AnalyticsEngine.generate_equity_curve(trades)
        drawdown_curve = []
        peak = 0
        
        for equity in equity_curve:
            if equity > peak:
                peak = equity
            
            drawdown = ((peak - equity) / peak * 100) if peak > 0 else 0
            drawdown_curve.append(drawdown)
        
        return drawdown_curve
    
    @staticmethod
    def generate_monthly_returns(trades: List[Trade]) -> Dict[str, float]:
        """Generate monthly returns breakdown."""
        monthly_returns = {}
        
        for trade in trades:
            month_key = trade.exit_time.strftime('%Y-%m')
            if month_key not in monthly_returns:
                monthly_returns[month_key] = 0
            monthly_returns[month_key] += trade.pnl
        
        return monthly_returns
    
    @staticmethod
    def generate_performance_report(trades: List[Trade]) -> Dict:
        """Generate comprehensive performance report."""
        if not trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'recovery_factor': 0,
                'equity_curve': [],
                'drawdown_curve': [],
                'monthly_returns': {},
            }
        
        metrics = AnalyticsEngine.calculate_metrics(trades)
        equity_curve = AnalyticsEngine.generate_equity_curve(trades)
        drawdown_curve = AnalyticsEngine.generate_drawdown_curve(trades)
        monthly_returns = AnalyticsEngine.generate_monthly_returns(trades)
        
        return {
            'total_trades': metrics.total_trades,
            'winning_trades': metrics.winning_trades,
            'losing_trades': metrics.losing_trades,
            'win_rate': metrics.win_rate,
            'profit_factor': metrics.profit_factor,
            'sharpe_ratio': metrics.sharpe_ratio,
            'max_drawdown': metrics.max_drawdown,
            'recovery_factor': metrics.recovery_factor,
            'equity_curve': equity_curve,
            'drawdown_curve': drawdown_curve,
            'monthly_returns': monthly_returns,
        }
