"""Trade data model."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
import uuid


@dataclass
class Trade:
    """Represents a completed trade."""
    
    symbol: str
    entry_time: datetime
    entry_price: float
    entry_size: float
    entry_reason: str
    exit_time: datetime
    exit_price: float
    exit_size: float
    exit_reason: str
    strategy: str
    timeframe: str = "2m"
    stop_loss: float = 0.0
    take_profit: float = 0.0
    max_profit: float = 0.0
    max_loss: float = 0.0
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    @property
    def pnl(self) -> float:
        """Calculate profit/loss in currency."""
        return (self.exit_price - self.entry_price) * self.exit_size
    
    @property
    def pnl_percent(self) -> float:
        """Calculate profit/loss percentage."""
        if self.entry_price == 0:
            return 0.0
        return ((self.exit_price - self.entry_price) / self.entry_price) * 100
    
    @property
    def duration(self) -> timedelta:
        """Calculate trade duration."""
        return self.exit_time - self.entry_time
    
    @property
    def duration_seconds(self) -> int:
        """Get duration in seconds."""
        return int(self.duration.total_seconds())
    
    @property
    def is_profitable(self) -> bool:
        """Check if trade is profitable."""
        return self.pnl > 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'entry_time': self.entry_time.isoformat(),
            'entry_price': self.entry_price,
            'entry_size': self.entry_size,
            'entry_reason': self.entry_reason,
            'exit_time': self.exit_time.isoformat(),
            'exit_price': self.exit_price,
            'exit_size': self.exit_size,
            'exit_reason': self.exit_reason,
            'pnl': self.pnl,
            'pnl_percent': self.pnl_percent,
            'strategy': self.strategy,
            'timeframe': self.timeframe,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'max_profit': self.max_profit,
            'max_loss': self.max_loss,
            'duration_seconds': self.duration_seconds,
        }
