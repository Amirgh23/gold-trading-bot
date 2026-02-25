"""Position data model."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class Position:
    """Represents an open trading position."""
    
    symbol: str
    side: str  # 'LONG' or 'SHORT'
    entry_price: float
    entry_time: datetime
    entry_size: float
    stop_loss: float
    take_profit: float
    entry_reason: str
    strategy: str
    current_price: float = 0.0
    current_size: float = 0.0
    trailing_stop: Optional[float] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "OPEN"
    
    @property
    def unrealized_pnl(self) -> float:
        """Calculate unrealized profit/loss."""
        if self.side == "LONG":
            return (self.current_price - self.entry_price) * self.current_size
        else:  # SHORT
            return (self.entry_price - self.current_price) * self.current_size
    
    @property
    def unrealized_pnl_percent(self) -> float:
        """Calculate unrealized profit/loss percentage."""
        if self.entry_price == 0:
            return 0.0
        if self.side == "LONG":
            return ((self.current_price - self.entry_price) / self.entry_price) * 100
        else:  # SHORT
            return ((self.entry_price - self.current_price) / self.entry_price) * 100
    
    @property
    def profit_distance(self) -> float:
        """Distance to take profit."""
        if self.side == "LONG":
            return self.take_profit - self.current_price
        else:
            return self.current_price - self.take_profit
    
    @property
    def loss_distance(self) -> float:
        """Distance to stop loss."""
        if self.side == "LONG":
            return self.current_price - self.stop_loss
        else:
            return self.stop_loss - self.current_price
    
    @property
    def risk_reward_ratio(self) -> float:
        """Calculate risk/reward ratio."""
        risk = abs(self.entry_price - self.stop_loss)
        reward = abs(self.take_profit - self.entry_price)
        if risk == 0:
            return 0.0
        return reward / risk
    
    def update_price(self, current_price: float):
        """Update current price."""
        self.current_price = current_price
    
    def update_size(self, new_size: float):
        """Update position size."""
        self.current_size = new_size
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'side': self.side,
            'entry_price': self.entry_price,
            'entry_time': self.entry_time.isoformat(),
            'entry_size': self.entry_size,
            'current_price': self.current_price,
            'current_size': self.current_size,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'trailing_stop': self.trailing_stop,
            'unrealized_pnl': self.unrealized_pnl,
            'unrealized_pnl_percent': self.unrealized_pnl_percent,
            'entry_reason': self.entry_reason,
            'strategy': self.strategy,
            'status': self.status,
        }
