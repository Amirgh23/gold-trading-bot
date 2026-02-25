"""Indicator calculation engine with 15+ technical indicators."""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
import logging
import time
from functools import lru_cache

logger = logging.getLogger(__name__)


class IndicatorCache:
    """Cache for indicator calculations."""
    
    def __init__(self, max_size: int = 100):
        self.cache = {}
        self.max_size = max_size
    
    def get(self, key: str) -> Optional[pd.Series]:
        """Get cached indicator."""
        return self.cache.get(key)
    
    def set(self, key: str, value: pd.Series) -> None:
        """Cache indicator."""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            self.cache.pop(next(iter(self.cache)))
        self.cache[key] = value
    
    def clear(self) -> None:
        """Clear cache."""
        self.cache.clear()


class IndicatorEngine:
    """Calculates 15+ technical indicators in real-time."""
    
    _cache = IndicatorCache()
    
    @staticmethod
    def calculate_all(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all indicators efficiently."""
        start_time = time.time()
        
        # Trend indicators
        df['ema_5'] = IndicatorEngine.ema(df['close'], 5)
        df['ema_13'] = IndicatorEngine.ema(df['close'], 13)
        df['ema_50'] = IndicatorEngine.ema(df['close'], 50)
        df['ema_200'] = IndicatorEngine.ema(df['close'], 200)
        df['adx'] = IndicatorEngine.adx(df)
        
        # Momentum indicators
        df['rsi'] = IndicatorEngine.rsi(df['close'], 14)
        df['macd'], df['macd_signal'], df['macd_hist'] = IndicatorEngine.macd(df['close'])
        df['stochastic'] = IndicatorEngine.stochastic(df, 14)
        df['cci'] = IndicatorEngine.cci(df, 20)
        
        # Volatility indicators
        df['bb_upper'], df['bb_middle'], df['bb_lower'] = IndicatorEngine.bollinger_bands(df['close'], 20)
        df['atr'] = IndicatorEngine.atr(df, 14)
        df['std_dev'] = IndicatorEngine.std_dev(df['close'], 20)
        
        # Volume indicators
        df['obv'] = IndicatorEngine.obv(df)
        df['vpt'] = IndicatorEngine.vpt(df)
        
        elapsed = time.time() - start_time
        if elapsed > 0.1:
            logger.warning(f"Indicator calculation took {elapsed:.3f}s (target: <0.1s)")
        else:
            logger.debug(f"Calculated all indicators in {elapsed:.3f}s")
        
        return df
    
    @staticmethod
    def ema(series: pd.Series, period: int) -> pd.Series:
        """Exponential Moving Average."""
        return series.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def sma(series: pd.Series, period: int) -> pd.Series:
        """Simple Moving Average."""
        return series.rolling(window=period).mean()
    
    @staticmethod
    def rsi(series: pd.Series, period: int = 14) -> pd.Series:
        """Relative Strength Index."""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """MACD indicator."""
        ema_fast = series.ewm(span=fast, adjust=False).mean()
        ema_slow = series.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
    @staticmethod
    def bollinger_bands(series: pd.Series, period: int = 20, std_dev: int = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Bollinger Bands."""
        sma = series.rolling(window=period).mean()
        std = series.rolling(window=period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return upper, sma, lower
    
    @staticmethod
    def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Average True Range."""
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr
    
    @staticmethod
    def stochastic(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Stochastic Oscillator."""
        low_min = df['low'].rolling(window=period).min()
        high_max = df['high'].rolling(window=period).max()
        stoch = 100 * (df['close'] - low_min) / (high_max - low_min)
        return stoch
    
    @staticmethod
    def cci(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """Commodity Channel Index."""
        tp = (df['high'] + df['low'] + df['close']) / 3
        sma = tp.rolling(window=period).mean()
        mad = tp.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
        cci = (tp - sma) / (0.015 * mad)
        return cci
    
    @staticmethod
    def adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Average Directional Index."""
        plus_dm = df['high'].diff()
        minus_dm = -df['low'].diff()
        
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        tr = IndicatorEngine.atr(df, 1)
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / tr.rolling(window=period).mean())
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / tr.rolling(window=period).mean())
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        return adx
    
    @staticmethod
    def obv(df: pd.DataFrame) -> pd.Series:
        """On-Balance Volume."""
        obv = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
        return obv
    
    @staticmethod
    def vpt(df: pd.DataFrame) -> pd.Series:
        """Volume Price Trend."""
        vpt = (df['volume'] * df['close'].pct_change()).fillna(0).cumsum()
        return vpt
    
    @staticmethod
    def std_dev(series: pd.Series, period: int = 20) -> pd.Series:
        """Standard Deviation."""
        return series.rolling(window=period).std()
    
    @staticmethod
    def detect_trend(df: pd.DataFrame) -> str:
        """Detect market trend direction."""
        if len(df) < 50:
            return "UNKNOWN"
        
        ema_5 = df['ema_5'].iloc[-1]
        ema_13 = df['ema_13'].iloc[-1]
        ema_50 = df['ema_50'].iloc[-1]
        adx = df['adx'].iloc[-1]
        
        # Strong uptrend
        if ema_5 > ema_13 > ema_50 and adx > 25:
            return "UPTREND"
        
        # Strong downtrend
        if ema_5 < ema_13 < ema_50 and adx > 25:
            return "DOWNTREND"
        
        # Weak trend or consolidation
        if adx < 20:
            return "SIDEWAYS"
        
        # Weak uptrend
        if ema_5 > ema_13 > ema_50:
            return "UPTREND"
        
        # Weak downtrend
        if ema_5 < ema_13 < ema_50:
            return "DOWNTREND"
        
        return "SIDEWAYS"
    
    @staticmethod
    def find_support_resistance(df: pd.DataFrame, lookback: int = 20) -> Dict[str, list]:
        """Find support and resistance levels."""
        highs = df['high'].tail(lookback)
        lows = df['low'].tail(lookback)
        
        # Find swing highs and lows
        resistance_levels = []
        support_levels = []
        
        for i in range(1, len(highs) - 1):
            if highs.iloc[i] > highs.iloc[i-1] and highs.iloc[i] > highs.iloc[i+1]:
                resistance_levels.append(highs.iloc[i])
            if lows.iloc[i] < lows.iloc[i-1] and lows.iloc[i] < lows.iloc[i+1]:
                support_levels.append(lows.iloc[i])
        
        return {
            'resistance': sorted(set(resistance_levels), reverse=True)[:3],
            'support': sorted(set(support_levels))[:3],
        }
    
    @staticmethod
    def calculate_volatility(df: pd.DataFrame) -> float:
        """Calculate current volatility."""
        if len(df) < 20:
            return 0.0
        
        returns = df['close'].pct_change().tail(20)
        volatility = returns.std() * 100
        return volatility
    
    @staticmethod
    def detect_divergence(df: pd.DataFrame) -> Dict[str, bool]:
        """Detect bullish/bearish divergences."""
        if len(df) < 20:
            return {'bullish': False, 'bearish': False}
        
        # Simple divergence detection
        recent_rsi = df['rsi'].tail(5)
        recent_price = df['close'].tail(5)
        
        bullish = (recent_rsi.iloc[-1] > recent_rsi.iloc[-3] and 
                  recent_price.iloc[-1] < recent_price.iloc[-3])
        bearish = (recent_rsi.iloc[-1] < recent_rsi.iloc[-3] and 
                  recent_price.iloc[-1] > recent_price.iloc[-3])
        
        return {'bullish': bullish, 'bearish': bearish}
