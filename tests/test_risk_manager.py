"""Tests for risk management system."""

import pytest
from hypothesis import given, strategies as st
from trading_bot.risk.manager import RiskManager


class TestRiskManager:
    """Test RiskManager component."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.risk_manager = RiskManager(
            account_equity=10000,
            max_position_size_percent=2.0,
            max_concurrent_positions=5,
            max_drawdown_percent=20.0,
            daily_loss_limit_percent=5.0,
            kelly_fraction=0.25,
        )
    
    @given(
        entry_price=st.floats(min_value=100, max_value=2000),
        stop_loss=st.floats(min_value=50, max_value=1900),
        win_rate=st.floats(min_value=0.3, max_value=0.7),
        risk_reward_ratio=st.floats(min_value=1.0, max_value=5.0),
    )
    def test_position_sizing_consistency(
        self,
        entry_price,
        stop_loss,
        win_rate,
        risk_reward_ratio,
    ):
        """Property 3: Position sizing should follow Kelly Criterion."""
        # Ensure stop loss is different from entry price
        if abs(entry_price - stop_loss) < 1:
            stop_loss = entry_price - 10
        
        position_size = self.risk_manager.calculate_position_size(
            entry_price,
            stop_loss,
            win_rate,
            risk_reward_ratio,
        )
        
        # Position size should be positive
        assert position_size >= 0
        
        # Position size should not exceed maximum
        max_size = (self.risk_manager.account_equity * 2.0) / 100
        assert position_size <= max_size
    
    def test_drawdown_protection(self):
        """Property 4: Drawdown protection should reduce position sizes."""
        # Simulate drawdown
        self.risk_manager.peak_equity = 10000
        self.risk_manager.account_equity = 8000  # 20% drawdown
        
        drawdown = self.risk_manager.get_current_drawdown()
        assert drawdown == 20.0
        
        # Should stop trading at max drawdown
        assert self.risk_manager.should_stop_trading() is False
        
        # Simulate exceeding max drawdown
        self.risk_manager.account_equity = 7900  # 21% drawdown
        assert self.risk_manager.should_stop_trading() is True
    
    def test_daily_loss_limit(self):
        """Property 4: Daily loss limit should stop trading."""
        # Simulate daily loss
        daily_loss_limit = self.risk_manager.account_equity * 5.0 / 100
        self.risk_manager.daily_pnl = -daily_loss_limit - 1
        
        assert self.risk_manager.should_stop_trading() is True
    
    def test_consecutive_loss_adjustment(self):
        """Position size should decrease after consecutive losses."""
        self.risk_manager.consecutive_losses = 3
        adjustment = self.risk_manager.get_position_size_adjustment()
        
        # Should be less than 1.0
        assert adjustment < 1.0
        assert adjustment > 0
    
    def test_consecutive_win_adjustment(self):
        """Position size should increase after consecutive wins."""
        self.risk_manager.consecutive_wins = 3
        adjustment = self.risk_manager.get_position_size_adjustment()
        
        # Should be greater than 1.0
        assert adjustment > 1.0
    
    def test_volatility_adjustment(self):
        """Position size should adjust for volatility."""
        base_size = 100
        
        # High volatility
        adjusted_high = self.risk_manager.adjust_for_volatility(
            base_size,
            volatility=2.5,
            normal_volatility=1.0,
        )
        assert adjusted_high < base_size
        
        # Low volatility
        adjusted_low = self.risk_manager.adjust_for_volatility(
            base_size,
            volatility=0.3,
            normal_volatility=1.0,
        )
        assert adjusted_low > base_size
    
    def test_spread_adjustment(self):
        """Position size should adjust for spread."""
        base_size = 100
        
        # Wide spread
        adjusted = self.risk_manager.adjust_for_spread(
            base_size,
            spread=0.6,
            normal_spread=0.1,
        )
        assert adjusted < base_size
