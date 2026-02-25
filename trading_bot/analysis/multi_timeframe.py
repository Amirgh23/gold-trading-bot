"""Multi-timeframe analysis with signal confirmation."""

from typing import Dict, Optional, List
import pandas as pd
import logging
from trading_bot.indicators.engine import IndicatorEngine

logger = logging.getLogger(__name__)


class MultiTimeframeAnalyzer:
    """Analyzes signals across multiple timeframes."""
    
    def __init__(self):
        self.timeframes = ['2m', '5m', '15m']
        self.data_cache = {}
    
    def analyze(
        self,
        data_2m: pd.DataFrame,
        data_5m: pd.DataFrame,
        data_15m: pd.DataFrame,
    ) -> Dict:
        """
        Analyze signals across timeframes.
        
        Args:
            data_2m: 2-minute OHLCV data
            data_5m: 5-minute OHLCV data
            data_15m: 15-minute OHLCV data
        
        Returns:
            Multi-timeframe analysis results
        """
        # Calculate indicators for each timeframe
        data_2m = IndicatorEngine.calculate_all(data_2m)
        data_5m = IndicatorEngine.calculate_all(data_5m)
        data_15m = IndicatorEngine.calculate_all(data_15m)
        
        # Get trends
        trend_2m = IndicatorEngine.detect_trend(data_2m)
        trend_5m = IndicatorEngine.detect_trend(data_5m)
        trend_15m = IndicatorEngine.detect_trend(data_15m)
        
        # Check alignment
        alignment = self._check_alignment(trend_2m, trend_5m, trend_15m)
        
        # Get signals
        signal_2m = self._get_signal(data_2m, trend_2m)
        signal_5m = self._get_signal(data_5m, trend_5m)
        signal_15m = self._get_signal(data_15m, trend_15m)
        
        return {
            'trend_2m': trend_2m,
            'trend_5m': trend_5m,
            'trend_15m': trend_15m,
            'alignment': alignment,
            'signal_2m': signal_2m,
            'signal_5m': signal_5m,
            'signal_15m': signal_15m,
            'confirmation_strength': self._calculate_confirmation_strength(
                signal_2m, signal_5m, signal_15m
            ),
            'position_size_adjustment': self._calculate_position_adjustment(alignment),
        }
    
    def _check_alignment(self, trend_2m: str, trend_5m: str, trend_15m: str) -> str:
        """Check if timeframes are aligned."""
        # All uptrend
        if trend_2m == "UPTREND" and trend_5m == "UPTREND" and trend_15m == "UPTREND":
            return "STRONG_UPTREND"
        
        # All downtrend
        if trend_2m == "DOWNTREND" and trend_5m == "DOWNTREND" and trend_15m == "DOWNTREND":
            return "STRONG_DOWNTREND"
        
        # 2 out of 3 uptrend
        uptrend_count = sum(1 for t in [trend_2m, trend_5m, trend_15m] if t == "UPTREND")
        if uptrend_count == 2:
            return "WEAK_UPTREND"
        
        # 2 out of 3 downtrend
        downtrend_count = sum(1 for t in [trend_2m, trend_5m, trend_15m] if t == "DOWNTREND")
        if downtrend_count == 2:
            return "WEAK_DOWNTREND"
        
        return "CONFLICTED"
    
    def _get_signal(self, df: pd.DataFrame, trend: str) -> Optional[str]:
        """Get signal from timeframe."""
        if len(df) < 2:
            return None
        
        rsi = df['rsi'].iloc[-1]
        macd_hist = df['macd_hist'].iloc[-1]
        
        # Uptrend signal
        if trend == "UPTREND":
            if rsi < 70 and macd_hist > 0:
                return "BUY"
        
        # Downtrend signal
        elif trend == "DOWNTREND":
            if rsi > 30 and macd_hist < 0:
                return "SELL"
        
        return None
    
    def _calculate_confirmation_strength(
        self,
        signal_2m: Optional[str],
        signal_5m: Optional[str],
        signal_15m: Optional[str],
    ) -> float:
        """Calculate confirmation strength (0-100%)."""
        signals = [signal_2m, signal_5m, signal_15m]
        
        # Count matching signals
        buy_count = sum(1 for s in signals if s == "BUY")
        sell_count = sum(1 for s in signals if s == "SELL")
        
        # All agree
        if buy_count == 3 or sell_count == 3:
            return 100.0
        
        # 2 out of 3 agree
        if buy_count == 2 or sell_count == 2:
            return 75.0
        
        # Only 1 signal
        if buy_count == 1 or sell_count == 1:
            return 50.0
        
        # No signals
        return 0.0
    
    def _calculate_position_adjustment(self, alignment: str) -> float:
        """Calculate position size adjustment based on alignment."""
        adjustments = {
            'STRONG_UPTREND': 1.25,      # +25%
            'STRONG_DOWNTREND': 1.25,    # +25%
            'WEAK_UPTREND': 1.0,         # No change
            'WEAK_DOWNTREND': 1.0,       # No change
            'CONFLICTED': 0.5,           # -50%
        }
        
        return adjustments.get(alignment, 1.0)
    
    def get_confirmation_status(
        self,
        analysis: Dict,
    ) -> Dict:
        """Get detailed confirmation status."""
        return {
            'alignment': analysis['alignment'],
            'confirmation_strength': analysis['confirmation_strength'],
            'position_adjustment': analysis['position_size_adjustment'],
            'signals': {
                '2m': analysis['signal_2m'],
                '5m': analysis['signal_5m'],
                '15m': analysis['signal_15m'],
            },
            'trends': {
                '2m': analysis['trend_2m'],
                '5m': analysis['trend_5m'],
                '15m': analysis['trend_15m'],
            },
        }
