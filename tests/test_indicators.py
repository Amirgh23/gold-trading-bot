"""Tests for indicator calculations."""

import pytest
import pandas as pd
import numpy as np
from hypothesis import given, strategies as st
from trading_bot.indicators.engine import IndicatorEngine


class TestIndicatorEngine:
    """Test IndicatorEngine component."""
    
    @staticmethod
    def create_sample_data(length: int = 100) -> pd.DataFrame:
        """Create sample OHLCV data."""
        np.random.seed(42)
        close = 2000 + np.cumsum(np.random.randn(length) * 5)
        
        return pd.DataFrame({
            'open': close + np.random.randn(length) * 2,
            'high': close + abs(np.random.randn(length) * 3),
            'low': close - abs(np.random.randn(length) * 3),
            'close': close,
            'volume': np.random.randint(1000, 10000, length),
        })
    
    def test_ema_calculation(self):
        """Test EMA calculation."""
        df = self.create_sample_data()
        ema = IndicatorEngine.ema(df['close'], 5)
        
        assert len(ema) == len(df)
        assert not ema.isna().all()
    
    def test_rsi_calculation(self):
        """Test RSI calculation."""
        df = self.create_sample_data()
        rsi = IndicatorEngine.rsi(df['close'], 14)
        
        assert len(rsi) == len(df)
        # RSI should be between 0 and 100
        assert (rsi[~rsi.isna()] >= 0).all()
        assert (rsi[~rsi.isna()] <= 100).all()
    
    def test_macd_calculation(self):
        """Test MACD calculation."""
        df = self.create_sample_data()
        macd, signal, hist = IndicatorEngine.macd(df['close'])
        
        assert len(macd) == len(df)
        assert len(signal) == len(df)
        assert len(hist) == len(df)
    
    def test_bollinger_bands(self):
        """Test Bollinger Bands calculation."""
        df = self.create_sample_data()
        upper, middle, lower = IndicatorEngine.bollinger_bands(df['close'], 20)
        
        assert len(upper) == len(df)
        # Upper should be above middle, middle above lower
        valid_idx = ~(upper.isna() | middle.isna() | lower.isna())
        assert (upper[valid_idx] > middle[valid_idx]).all()
        assert (middle[valid_idx] > lower[valid_idx]).all()
    
    def test_atr_calculation(self):
        """Test ATR calculation."""
        df = self.create_sample_data()
        atr = IndicatorEngine.atr(df, 14)
        
        assert len(atr) == len(df)
        assert (atr[~atr.isna()] > 0).all()
    
    def test_trend_detection(self):
        """Property 9: Trend detection should work correctly."""
        df = self.create_sample_data(100)
        df = IndicatorEngine.calculate_all(df)
        
        trend = IndicatorEngine.detect_trend(df)
        
        assert trend in ["UPTREND", "DOWNTREND", "SIDEWAYS", "UNKNOWN"]
    
    def test_support_resistance(self):
        """Test support/resistance detection."""
        df = self.create_sample_data(100)
        levels = IndicatorEngine.find_support_resistance(df, 20)
        
        assert 'support' in levels
        assert 'resistance' in levels
        assert isinstance(levels['support'], list)
        assert isinstance(levels['resistance'], list)
    
    def test_volatility_calculation(self):
        """Test volatility calculation."""
        df = self.create_sample_data(100)
        volatility = IndicatorEngine.calculate_volatility(df)
        
        assert volatility >= 0
    
    def test_divergence_detection(self):
        """Test divergence detection."""
        df = self.create_sample_data(100)
        df = IndicatorEngine.calculate_all(df)
        
        divergence = IndicatorEngine.detect_divergence(df)
        
        assert 'bullish' in divergence
        assert 'bearish' in divergence
        assert isinstance(divergence['bullish'], (bool, np.bool_))
        assert isinstance(divergence['bearish'], (bool, np.bool_))
    
    @given(st.integers(min_value=50, max_value=200))
    def test_calculate_all_performance(self, length: int):
        """Property 8: All indicators should calculate in <100ms."""
        import time
        
        df = self.create_sample_data(length)
        
        start = time.time()
        df = IndicatorEngine.calculate_all(df)
        elapsed = time.time() - start
        
        # Should complete in less than 100ms
        assert elapsed < 0.1
        
        # All indicators should be present
        expected_indicators = [
            'ema_5', 'ema_13', 'ema_50', 'ema_200', 'adx',
            'rsi', 'macd', 'macd_signal', 'macd_hist',
            'stochastic', 'cci',
            'bb_upper', 'bb_middle', 'bb_lower', 'atr', 'std_dev',
            'obv', 'vpt',
        ]
        
        for indicator in expected_indicators:
            assert indicator in df.columns
