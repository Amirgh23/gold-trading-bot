"""Performance metrics data model."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional


@dataclass
class PerformanceMetrics:
    """Represents trading performance metrics."""
    
    date: datetime
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    recovery_factor: float = 0.0
    daily_pnl: float = 0.0
    cumulative_pnl: float = 0.0
    strategy_performance: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    @property
    def is_profitable(self) -> bool:
        """Check if day was profitable."""
        return self.daily_pnl > 0
    
    @property
    def average_win(self) -> float:
        """Calculate average winning trade."""
        if self.winning_trades == 0:
            return 0.0
        return self.daily_pnl / self.winning_trades if self.daily_pnl > 0 else 0.0
    
    @property
    def average_loss(self) -> float:
        """Calculate average losing trade."""
        if self.losing_trades == 0:
            return 0.0
        return abs(self.daily_pnl) / self.losing_trades if self.daily_pnl < 0 else 0.0
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'date': self.date.isoformat(),
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': self.win_rate,
            'profit_factor': self.profit_factor,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'recovery_factor': self.recovery_factor,
            'daily_pnl': self.daily_pnl,
            'cumulative_pnl': self.cumulative_pnl,
            'strategy_performance': self.strategy_performance,
        }
