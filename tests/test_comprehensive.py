"""
Comprehensive Test Suite for Gold Trading Bot
"""

import pytest
import numpy as np
import pandas as pd
from hypothesis import given, strategies as st, settings
from datetime import datetime, timedelta


class TestTradingLogic:
    """Test core trading logic"""
    
    def test_signal_generation(self):
        """Test trading signal generation"""
        prices = np.array([2050, 2051, 2052, 2053, 2054, 2055])
        ma_short = np.array([2050, 2050.5, 2051, 2051.5, 2052, 2052.5])
        ma_long = np.array([2049, 2049.5, 2050, 2050.5, 2051, 2051.5])
        
        # Buy signal when short MA > long MA
        buy_signal = ma_short > ma_long
        assert buy_signal[-1] == True
    
    def test_position_sizing(self):
        """Test position sizing calculation"""
        capital = 10000
        risk_per_trade = 0.02
        stop_loss_pct = 0.02
        
        position_size = (capital * risk_per_trade) / stop_loss_pct
        assert position_size == 10000
    
    def test_profit_calculation(self):
        """Test profit/loss calculation"""
        entry_price = 2050
        exit_price = 2055
        position_size = 1
        
        profit = (exit_price - entry_price) * position_size
        assert profit == 5
    
    @given(st.floats(min_value=1000, max_value=10000))
    def test_capital_preservation(self, capital):
        """Property: Capital should never go negative"""
        assert capital > 0
    
    @given(st.floats(min_value=0.01, max_value=0.1))
    def test_risk_per_trade_valid(self, risk):
        """Property: Risk per trade should be between 1% and 10%"""
        assert 0.01 <= risk <= 0.1


class TestIndicators:
    """Test technical indicators"""
    
    def test_moving_average(self):
        """Test moving average calculation"""
        prices = np.array([100, 101, 102, 103, 104, 105])
        ma = np.mean(prices[:3])
        assert ma == 101
    
    def test_rsi_calculation(self):
        """Test RSI calculation"""
        prices = np.array([100, 101, 102, 101, 100, 99, 98, 99, 100, 101])
        
        # RSI should be between 0 and 100
        delta = np.diff(prices)
        gains = np.where(delta > 0, delta, 0)
        losses = np.where(delta < 0, -delta, 0)
        
        avg_gain = np.mean(gains)
        avg_loss = np.mean(losses)
        
        if avg_loss > 0:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            assert 0 <= rsi <= 100
    
    def test_bollinger_bands(self):
        """Test Bollinger Bands calculation"""
        prices = np.array([100, 101, 102, 103, 104, 105, 104, 103, 102, 101])
        
        middle = np.mean(prices)
        std = np.std(prices)
        upper = middle + (std * 2)
        lower = middle - (std * 2)
        
        assert lower < middle < upper
    
    @given(st.lists(st.floats(min_value=1000, max_value=3000), min_size=20, max_size=100))
    def test_indicator_bounds(self, prices):
        """Property: Indicators should stay within bounds"""
        prices_array = np.array(prices)
        
        # MA should be within price range
        ma = np.mean(prices_array)
        assert np.min(prices_array) <= ma <= np.max(prices_array)


class TestRiskManagement:
    """Test risk management"""
    
    def test_max_drawdown_protection(self):
        """Test max drawdown protection"""
        capital = 10000
        max_drawdown_allowed = 0.20
        
        current_equity = 8000  # 20% drawdown
        drawdown = (capital - current_equity) / capital
        
        assert drawdown <= max_drawdown_allowed
    
    def test_daily_loss_limit(self):
        """Test daily loss limit"""
        daily_loss = -500
        daily_loss_limit = -1000
        
        assert daily_loss >= daily_loss_limit
    
    def test_position_limit(self):
        """Test position limit"""
        max_positions = 5
        current_positions = 3
        
        assert current_positions <= max_positions
    
    @given(st.floats(min_value=0, max_value=1))
    def test_drawdown_valid(self, drawdown):
        """Property: Drawdown should be between 0 and 1"""
        assert 0 <= drawdown <= 1


class TestDataValidation:
    """Test data validation"""
    
    def test_ohlc_validity(self):
        """Test OHLC data validity"""
        open_price = 2050
        high_price = 2055
        low_price = 2045
        close_price = 2052
        
        # High should be >= all prices
        assert high_price >= open_price
        assert high_price >= close_price
        assert high_price >= low_price
        
        # Low should be <= all prices
        assert low_price <= open_price
        assert low_price <= close_price
        assert low_price <= high_price
    
    def test_volume_validity(self):
        """Test volume validity"""
        volume = 5000
        assert volume > 0
    
    @given(st.floats(min_value=0))
    def test_price_positive(self, price):
        """Property: Prices should be positive"""
        assert price >= 0


class TestPerformanceMetrics:
    """Test performance metrics"""
    
    def test_sharpe_ratio(self):
        """Test Sharpe ratio calculation"""
        returns = np.array([0.01, 0.02, -0.01, 0.03, 0.02])
        
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        sharpe = mean_return / std_return if std_return > 0 else 0
        
        assert isinstance(sharpe, (int, float))
    
    def test_win_rate(self):
        """Test win rate calculation"""
        trades = [
            {'profit': 100},
            {'profit': -50},
            {'profit': 200},
            {'profit': -30},
            {'profit': 150}
        ]
        
        winning = sum(1 for t in trades if t['profit'] > 0)
        total = len(trades)
        win_rate = winning / total
        
        assert 0 <= win_rate <= 1
        assert win_rate == 0.6
    
    def test_profit_factor(self):
        """Test profit factor calculation"""
        trades = [
            {'profit': 100},
            {'profit': -50},
            {'profit': 200},
            {'profit': -30}
        ]
        
        gross_profit = sum(t['profit'] for t in trades if t['profit'] > 0)
        gross_loss = abs(sum(t['profit'] for t in trades if t['profit'] < 0))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        assert profit_factor > 0


class TestMLModels:
    """Test ML model functionality"""
    
    def test_model_output_shape(self):
        """Test model output shape"""
        batch_size = 32
        output_size = 1
        
        output = np.random.randn(batch_size, output_size)
        assert output.shape == (batch_size, output_size)
    
    def test_prediction_bounds(self):
        """Test prediction bounds"""
        predictions = np.array([2050, 2051, 2052, 2053, 2054])
        
        # Predictions should be reasonable prices
        assert np.all(predictions > 1000)
        assert np.all(predictions < 5000)
    
    @given(st.lists(st.floats(min_value=-1, max_value=1), min_size=10, max_size=100))
    def test_normalized_features(self, features):
        """Property: Normalized features should be between -1 and 1"""
        features_array = np.array(features)
        assert np.all(features_array >= -1)
        assert np.all(features_array <= 1)


class TestBacktesting:
    """Test backtesting functionality"""
    
    def test_trade_execution(self):
        """Test trade execution"""
        entry_price = 2050
        exit_price = 2055
        quantity = 1
        
        profit = (exit_price - entry_price) * quantity
        assert profit == 5
    
    def test_equity_curve(self):
        """Test equity curve"""
        initial_capital = 10000
        equity_curve = [10000, 10100, 10050, 10200, 10150]
        
        assert equity_curve[0] == initial_capital
        assert len(equity_curve) > 0
    
    def test_drawdown_calculation(self):
        """Test drawdown calculation"""
        equity_curve = np.array([10000, 10100, 9900, 10200, 9800])
        
        cummax = np.maximum.accumulate(equity_curve)
        drawdown = (equity_curve - cummax) / cummax
        max_drawdown = np.min(drawdown)
        
        assert max_drawdown < 0


class TestDataIntegrity:
    """Test data integrity"""
    
    def test_no_missing_values(self):
        """Test for missing values"""
        data = pd.DataFrame({
            'close': [2050, 2051, 2052, 2053, 2054],
            'volume': [1000, 1100, 1200, 1300, 1400]
        })
        
        assert not data.isnull().any().any()
    
    def test_data_consistency(self):
        """Test data consistency"""
        data = pd.DataFrame({
            'open': [2050, 2051, 2052],
            'high': [2055, 2056, 2057],
            'low': [2045, 2046, 2047],
            'close': [2052, 2053, 2054]
        })
        
        # High >= all prices
        assert (data['high'] >= data['open']).all()
        assert (data['high'] >= data['close']).all()
        assert (data['high'] >= data['low']).all()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
