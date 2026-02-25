"""Signal data model."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional
import uuid


@dataclass
class Signal:
    """Represents a trading signal."""
    
    timestamp: datetime
    symbol: str
    direction: str  # 'BUY' or 'SELL'
    strategy: str
    confidence: float  # 0-100%
    entry_price: float
    stop_loss: float
    take_profit: float
    reason: str
    indicators: Dict[str, float] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    @property
    def is_strong_signal(self) -> bool:
        """Check if signal is strong (confidence > 70%)."""
        return self.confidence > 70
    
    @property
    def is_weak_signal(self) -> bool:
        """Check if signal is weak (confidence < 40%)."""
        return self.confidence < 40
    
    @property
    def risk_reward_ratio(self) -> float:
        """Calculate risk/reward ratio."""
        risk = abs(self.entry_price - self.stop_loss)
        reward = abs(self.take_profit - self.entry_price)
        if risk == 0:
            return 0.0
        return reward / risk
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'symbol': self.symbol,
            'direction': self.direction,
            'strategy': self.strategy,
            'confidence': self.confidence,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'reason': self.reason,
            'indicators': self.indicators,
        }
