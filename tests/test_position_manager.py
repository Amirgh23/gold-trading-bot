"""Tests for position management."""

import pytest
from datetime import datetime
from trading_bot.execution.position_manager import PositionManager
from trading_bot.models.signal import Signal


class TestPositionManager:
    """Test PositionManager component."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = PositionManager()
    
    def _create_signal(self, direction: str) -> Signal:
        """Helper to create test signals."""
        return Signal(
            timestamp=datetime.now(),
            symbol="XAUUSD",
            direction=direction,
            strategy="TEST",
            confidence=70,
            entry_price=2000,
            stop_loss=1990 if direction == "BUY" else 2010,
            take_profit=2010 if direction == "BUY" else 1990,
            reason="Test signal",
        )
    
    def test_open_position(self):
        """Test opening a position."""
        signal = self._create_signal("BUY")
        position = self.manager.open_position(signal, 1.0)
        
        assert position is not None
        assert position.side == "LONG"
        assert position.entry_price == 2000
        assert position.current_size == 1.0
    
    def test_close_position(self):
        """Test closing a position."""
        signal = self._create_signal("BUY")
        position = self.manager.open_position(signal, 1.0)
        
        trade = self.manager.close_position(position.id, 2010, "TEST_EXIT")
        
        assert trade is not None
        assert trade.exit_price == 2010
        assert trade.pnl > 0
    
    def test_stop_loss_exit(self):
        """Property 5: Stop loss should trigger exit."""
        signal = self._create_signal("BUY")
        position = self.manager.open_position(signal, 1.0)
        
        # Update price to stop loss
        self.manager.update_position_price(position.id, 1990)
        
        exit_reason = self.manager.check_exit_conditions(
            position.id,
            1990,
        )
        
        assert exit_reason == "STOP_LOSS"
    
    def test_take_profit_exit(self):
        """Test take profit exit."""
        signal = self._create_signal("BUY")
        position = self.manager.open_position(signal, 1.0)
        
        # Update price to take profit
        self.manager.update_position_price(position.id, 2010)
        
        exit_reason = self.manager.check_exit_conditions(
            position.id,
            2010,
        )
        
        assert exit_reason == "TAKE_PROFIT"
    
    def test_trailing_stop_activation(self):
        """Property 5: Trailing stop should activate at 1.5x risk."""
        signal = self._create_signal("BUY")
        position = self.manager.open_position(signal, 1.0)
        
        # Initial risk is 10 (2000 - 1990)
        # Trailing stop should activate at 1.5x risk = 15 profit
        # So price should be 2015
        
        self.manager.update_trailing_stop(position.id, 2015)
        
        assert position.trailing_stop is not None
        assert position.trailing_stop == 2000  # Breakeven
    
    def test_partial_profit_taking(self):
        """Property 6: Partial profit-taking should close percentages."""
        signal = self._create_signal("BUY")
        position = self.manager.open_position(signal, 100.0)
        
        # Take 25% profit
        self.manager.take_partial_profit(position.id, 25)
        
        assert position.current_size == 75.0
    
    def test_trend_reversal_exit(self):
        """Property 7: Trend reversal should trigger exit."""
        signal = self._create_signal("BUY")
        position = self.manager.open_position(signal, 1.0)
        
        exit_reason = self.manager.check_exit_conditions(
            position.id,
            2005,
            trend="DOWNTREND",
        )
        
        assert exit_reason == "TREND_REVERSAL"
    
    def test_unrealized_pnl_calculation(self):
        """Test unrealized P&L calculation."""
        signal = self._create_signal("BUY")
        position = self.manager.open_position(signal, 1.0)
        
        # Update price
        self.manager.update_position_price(position.id, 2010)
        
        # Unrealized P&L should be positive
        assert position.unrealized_pnl > 0
        assert position.unrealized_pnl_percent > 0
    
    def test_multiple_positions(self):
        """Test managing multiple positions."""
        signal1 = self._create_signal("BUY")
        signal2 = self._create_signal("SELL")
        
        pos1 = self.manager.open_position(signal1, 1.0)
        pos2 = self.manager.open_position(signal2, 1.0)
        
        assert len(self.manager.get_open_positions()) == 2
        
        # Close one position
        self.manager.close_position(pos1.id, 2010, "TEST")
        
        assert len(self.manager.get_open_positions()) == 1
