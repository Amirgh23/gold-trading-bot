"""Base strategy interface."""

from abc import ABC, abstractmethod
from typing import Optional, Dict
import pandas as pd
from trading_bot.models.signal import Signal


class BaseStrategy(ABC):
    """Abstract base class for all trading strategies."""
    
    def __init__(self, name: str):
        self.name = name
        self.performance_metrics = {
            'total_signals': 0,
            'winning_signals': 0,
            'losing_signals': 0,
            'accuracy': 0.0,
            'win_rate': 0.0,
        }
    
    @abstractmethod
    def generate_signal(self, df: pd.DataFrame) -> Optional[Signal]:
        """
        Generate trading signal based on strategy logic.
        
        Args:
            df: DataFrame with OHLCV data and indicators
        
        Returns:
            Signal object or None if no signal
        """
        pass
    
    def get_confidence(self) -> float:
        """Get strategy confidence (0-100%)."""
        return self.performance_metrics.get('accuracy', 0.0)
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get strategy performance metrics."""
        return self.performance_metrics.copy()
    
    def update_performance(self, is_winning: bool):
        """Update performance metrics after trade."""
        self.performance_metrics['total_signals'] += 1
        
        if is_winning:
            self.performance_metrics['winning_signals'] += 1
        else:
            self.performance_metrics['losing_signals'] += 1
        
        total = self.performance_metrics['total_signals']
        if total > 0:
            self.performance_metrics['win_rate'] = (
                self.performance_metrics['winning_signals'] / total * 100
            )
            self.performance_metrics['accuracy'] = self.performance_metrics['win_rate']
