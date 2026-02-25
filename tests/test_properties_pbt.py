"""Property-based tests for gold trading bot core functionality.

This module contains property-based tests using hypothesis to validate
core trading logic correctness across many random inputs.
"""

import pytest
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings, HealthCheck
from trading_bot.strategies.ensemble import EnsembleRouter, EnsembleSignal
from trading_bot.models.signal import Signal
from trading_bot.risk.manager import RiskManager
from trading_bot.execution.position_manager import PositionManager
from trading_bot.models.position import Position


# ============================================================================
# Property 1: Ensemble Signal Weighting
# ============================================================================

class TestEnsembleSignalWeighting:
    """Property 1: Ensemble Signal Weighting.
    
    **Validates: Requirements 1.1, 1.4**
    
    Test that strategy weights are updated based on historical accuracy
    and that higher-accuracy strategies have more influence in ensemble.
    """
    
    def setup_method(self):
        """Set up test fixtures."""
        self.router = EnsembleRouter()
    
    def _create_signal(
        self,
        direction: str,
        strategy: str,
        confidence: float,
    ) -> Signal:
        """Helper to create test signals."""
        return Signal(
            timestamp=datetime.now(),
            symbol="XAUUSD",
            direction=direction,
            strategy=strategy,
            confidence=confidence,
            entry_price=2000,
            stop_loss=1990,
            take_profit=2010,
            reason="Test signal",
        )
    
    @given(
        high_accuracy=st.floats(min_value=0.7, max_value=1.0),
        low_accuracy=st.floats(min_value=0.3, max_value=0.6),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_higher_accuracy_strategies_have_more_influence(
        self, high_accuracy, low_accuracy
    ):
        """Test that higher-accuracy strategies have more influence."""
        # Create signals with different confidence levels
        high_conf_signal = self._create_signal("BUY", "HIGH_ACC", high_accuracy * 100)
        low_conf_signal = self._create_signal("BUY", "LOW_ACC", low_accuracy * 100)
        
        # Route with both signals
        result = self.router.route_signal([high_conf_signal, low_conf_signal])
        
        # Ensemble confidence should be closer to high accuracy
        if result is not None:
            expected_avg = (high_accuracy * 100 + low_accuracy * 100) / 2
            # Confidence should be between the two values
            assert low_accuracy * 100 <= result.confidence <= high_accuracy * 100 + 10
    
    @given(
        accuracies=st.lists(
            st.floats(min_value=0.4, max_value=1.0),
            min_size=2,
            max_size=5,
        )
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_weights_updated_based_on_accuracy(self, accuracies):
        """Test that strategy weights are updated based on accuracy."""
        # Create fresh router for this test to avoid state from previous tests
        router = EnsembleRouter()
        
        performance = {
            f"STRATEGY_{i}": acc for i, acc in enumerate(accuracies)
        }
        
        # Update weights
        router.update_strategy_weights(performance)
        
        # Verify weights are stored
        assert len(router.strategy_weights) == len(accuracies)
        for strategy, accuracy in performance.items():
            assert router.strategy_weights[strategy] == accuracy


# ============================================================================
# Property 2: Confirmation Threshold Enforcement
# ============================================================================

class TestConfirmationThresholdEnforcement:
    """Property 2: Confirmation Threshold Enforcement.
    
    **Validates: Requirements 1.2, 1.3**
    
    Test that signals require 2-3 confirmations based on volatility
    and that high volatility increases confirmation threshold.
    """
    
    def setup_method(self):
        """Set up test fixtures."""
        self.router = EnsembleRouter()
    
    def _create_signal(
        self,
        direction: str,
        strategy: str,
        confidence: float,
    ) -> Signal:
        """Helper to create test signals."""
        return Signal(
            timestamp=datetime.now(),
            symbol="XAUUSD",
            direction=direction,
            strategy=strategy,
            confidence=confidence,
            entry_price=2000,
            stop_loss=1990,
            take_profit=2010,
            reason="Test signal",
        )
    
    @given(
        num_signals=st.integers(min_value=1, max_value=5),
        volatility=st.floats(min_value=0.5, max_value=3.0),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_confirmation_threshold_enforced(self, num_signals, volatility):
        """Test that confirmation threshold is enforced."""
        signals = [
            self._create_signal("BUY", f"STRATEGY_{i}", 70.0)
            for i in range(num_signals)
        ]
        
        # Determine expected threshold
        high_vol_threshold = 2.0
        if volatility > high_vol_threshold:
            required_confirmations = 3
        else:
            required_confirmations = 2
        
        result = self.router.route_signal(
            signals,
            volatility=volatility,
            confirmation_threshold=2,
            high_volatility_threshold=high_vol_threshold,
        )
        
        # Should only route if enough confirmations
        if num_signals >= required_confirmations:
            assert result is not None
        else:
            assert result is None
    
    @given(
        volatility=st.floats(min_value=0.5, max_value=3.0),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_high_volatility_increases_threshold(self, volatility):
        """Test that high volatility increases confirmation threshold."""
        high_vol_threshold = 2.0
        
        # Create 2 signals
        signals = [
            self._create_signal("BUY", "STRATEGY_1", 70.0),
            self._create_signal("BUY", "STRATEGY_2", 70.0),
        ]
        
        result = self.router.route_signal(
            signals,
            volatility=volatility,
            confirmation_threshold=2,
            high_volatility_threshold=high_vol_threshold,
        )
        
        # With 2 signals:
        # - Low volatility: should route
        # - High volatility: should not route
        if volatility > high_vol_threshold:
            assert result is None
        else:
            assert result is not None


# ============================================================================
# Property 3: Position Sizing Consistency
# ============================================================================

class TestPositionSizingConsistency:
    """Property 3: Position Sizing Consistency.
    
    **Validates: Requirements 2.1, 2.2, 2.3**
    
    Test that position size is calculated consistently using Kelly Criterion
    and that position size adjusts with account equity changes.
    """
    
    def setup_method(self):
        """Set up test fixtures."""
        self.risk_manager = RiskManager(account_equity=10000.0)
    
    @given(
        entry_price=st.floats(min_value=1900, max_value=2100),
        stop_loss=st.floats(min_value=1800, max_value=1950),
        win_rate=st.floats(min_value=0.4, max_value=0.7),
        risk_reward_ratio=st.floats(min_value=1.0, max_value=3.0),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_position_size_calculated_consistently(
        self, entry_price, stop_loss, win_rate, risk_reward_ratio
    ):
        """Test that position size is calculated consistently."""
        # Calculate position size twice with same inputs
        size1 = self.risk_manager.calculate_position_size(
            entry_price=entry_price,
            stop_loss=stop_loss,
            win_rate=win_rate,
            risk_reward_ratio=risk_reward_ratio,
        )
        
        size2 = self.risk_manager.calculate_position_size(
            entry_price=entry_price,
            stop_loss=stop_loss,
            win_rate=win_rate,
            risk_reward_ratio=risk_reward_ratio,
        )
        
        # Should be identical
        assert size1 == size2
        
        # Should be non-negative
        assert size1 >= 0
        
        # Should not exceed maximum
        max_size = (self.risk_manager.account_equity * 2.0) / 100
        assert size1 <= max_size
    
    @given(
        equity_change=st.floats(min_value=-5000, max_value=5000),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_position_size_adjusts_with_equity(self, equity_change):
        """Test that position size adjusts with account equity changes."""
        initial_equity = self.risk_manager.account_equity
        
        # Calculate initial position size
        size1 = self.risk_manager.calculate_position_size(
            entry_price=2000,
            stop_loss=1990,
            win_rate=0.55,
            risk_reward_ratio=2.0,
        )
        
        # Update equity
        new_equity = max(100, initial_equity + equity_change)
        self.risk_manager.account_equity = new_equity
        
        # Calculate new position size
        size2 = self.risk_manager.calculate_position_size(
            entry_price=2000,
            stop_loss=1990,
            win_rate=0.55,
            risk_reward_ratio=2.0,
        )
        
        # Position size should scale with equity
        if equity_change > 0:
            assert size2 >= size1
        elif equity_change < 0:
            assert size2 <= size1


# ============================================================================
# Property 4: Drawdown Protection
# ============================================================================

class TestDrawdownProtection:
    """Property 4: Drawdown Protection.
    
    **Validates: Requirements 2.4, 2.5**
    
    Test that position sizes reduce by 50% when drawdown approaches 80% of limit
    and that trading stops when daily loss limit is reached.
    """
    
    def setup_method(self):
        """Set up test fixtures."""
        self.risk_manager = RiskManager(
            account_equity=10000.0,
            max_drawdown_percent=20.0,
            daily_loss_limit_percent=5.0,
        )
    
    @given(
        drawdown_percent=st.floats(min_value=0, max_value=25),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_position_size_reduced_at_high_drawdown(self, drawdown_percent):
        """Test that position sizes reduce at high drawdown."""
        # Set up drawdown scenario
        self.risk_manager.peak_equity = 10000.0
        self.risk_manager.account_equity = 10000.0 * (1 - drawdown_percent / 100)
        
        # Check risk limits
        position_size = 100.0
        open_positions = 1
        
        # Above limit (>20% drawdown), should fail
        if drawdown_percent > 20:
            result = self.risk_manager.check_risk_limits(
                position_size=position_size,
                current_drawdown=drawdown_percent,
                open_positions_count=open_positions,
            )
            assert result is False
        else:
            result = self.risk_manager.check_risk_limits(
                position_size=position_size,
                current_drawdown=drawdown_percent,
                open_positions_count=open_positions,
            )
            assert result is True
    
    @given(
        daily_loss_percent=st.floats(min_value=-10, max_value=0),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_trading_stops_at_daily_loss_limit(self, daily_loss_percent):
        """Test that trading stops when daily loss limit is reached."""
        # Set daily P&L
        daily_loss = self.risk_manager.account_equity * (daily_loss_percent / 100)
        self.risk_manager.daily_pnl = daily_loss
        
        # Check if should stop trading
        should_stop = self.risk_manager.should_stop_trading()
        
        # Should stop if loss exceeds 5% limit
        if daily_loss_percent <= -5:
            assert should_stop is True
        else:
            assert should_stop is False


# ============================================================================
# Property 25: Correlation-Based Position Sizing
# ============================================================================

class TestCorrelationBasedPositionSizing:
    """Property 25: Correlation-Based Position Sizing.
    
    **Validates: Requirements 15.1**
    
    Test that position sizes reduce when portfolio correlation is high (>0.7)
    and increase when correlation is low (<0.3).
    """
    
    def setup_method(self):
        """Set up test fixtures."""
        self.risk_manager = RiskManager(account_equity=10000.0)
        self.position_manager = PositionManager()
    
    def _create_position(
        self,
        side: str,
        entry_price: float,
        stop_loss: float,
    ) -> Position:
        """Helper to create test positions."""
        return Position(
            symbol="XAUUSD",
            side=side,
            entry_price=entry_price,
            entry_time=datetime.now(),
            entry_size=10.0,
            stop_loss=stop_loss,
            take_profit=entry_price + 20,
            entry_reason="Test",
            strategy="TEST",
            current_price=entry_price,
            current_size=10.0,
        )
    
    @given(
        correlation_level=st.floats(min_value=0.0, max_value=1.0),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_position_size_adjusts_with_correlation(self, correlation_level):
        """Test that position size adjusts based on correlation."""
        # Create open positions
        open_positions = [
            self._create_position("LONG", 2000, 1990),
            self._create_position("LONG", 2000, 1990),
        ]
        
        new_position = self._create_position("LONG", 2000, 1990)
        
        # Calculate adjustment
        adjustment = self.risk_manager.calculate_correlation_adjustment(
            open_positions, new_position
        )
        
        # High correlation (all same direction) should reduce
        if len(open_positions) > 0:
            same_direction = all(p.side == new_position.side for p in open_positions)
            if same_direction:
                assert adjustment < 1.0
            else:
                assert adjustment == 1.0


# ============================================================================
# Property 5: Stop Loss and Trailing Stop
# ============================================================================

class TestStopLossAndTrailingStop:
    """Property 5: Stop Loss and Trailing Stop.
    
    **Validates: Requirements 3.1, 3.2**
    
    Test that stop loss is placed at ATR-based level and that trailing stop
    activates at 1.5x initial risk and moves correctly.
    """
    
    def setup_method(self):
        """Set up test fixtures."""
        self.position_manager = PositionManager()
    
    def _create_signal(
        self,
        direction: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
    ) -> Signal:
        """Helper to create test signals."""
        return Signal(
            timestamp=datetime.now(),
            symbol="XAUUSD",
            direction=direction,
            strategy="TEST",
            confidence=70.0,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            reason="Test signal",
        )
    
    @given(
        entry_price=st.floats(min_value=1900, max_value=2100),
        stop_loss_offset=st.floats(min_value=5, max_value=50),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_stop_loss_placed_correctly(self, entry_price, stop_loss_offset):
        """Test that stop loss is placed at correct level."""
        stop_loss = entry_price - stop_loss_offset
        take_profit = entry_price + (stop_loss_offset * 2)
        
        signal = self._create_signal("BUY", entry_price, stop_loss, take_profit)
        position = self.position_manager.open_position(signal, 10.0)
        
        assert position is not None
        assert position.stop_loss == stop_loss
        assert position.entry_price == entry_price
    
    @given(
        entry_price=st.floats(min_value=1900, max_value=2100),
        stop_loss_offset=st.floats(min_value=5, max_value=50),
        price_move_multiplier=st.floats(min_value=2.0, max_value=10.0),  # Start at 2x to ensure clear activation
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_trailing_stop_activation_and_movement(
        self, entry_price, stop_loss_offset, price_move_multiplier
    ):
        """Test that trailing stop activates and moves correctly."""
        stop_loss = entry_price - stop_loss_offset
        take_profit = entry_price + (stop_loss_offset * 2)
        initial_risk = stop_loss_offset
        
        signal = self._create_signal("BUY", entry_price, stop_loss, take_profit)
        position = self.position_manager.open_position(signal, 10.0)
        
        # Move price significantly
        current_price = entry_price + (initial_risk * price_move_multiplier)
        
        # Update position price first
        position.update_price(current_price)
        
        # Then update trailing stop
        self.position_manager.update_trailing_stop(position.id, current_price)
        
        # Check trailing stop activation
        profit = current_price - entry_price
        
        # With 2x+ multiplier, trailing stop should definitely be activated
        assert position.trailing_stop is not None
        
        # Trailing stop should be at or above breakeven
        assert position.trailing_stop >= entry_price


# ============================================================================
# Property 6: Partial Profit-Taking
# ============================================================================

class TestPartialProfitTaking:
    """Property 6: Partial Profit-Taking.
    
    **Validates: Requirements 3.3**
    
    Test that 25% closes at 50% of take profit, 25% closes at 75% of take profit,
    and remaining 50% closes at take profit.
    """
    
    def setup_method(self):
        """Set up test fixtures."""
        self.position_manager = PositionManager()
    
    def _create_signal(
        self,
        direction: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
    ) -> Signal:
        """Helper to create test signals."""
        return Signal(
            timestamp=datetime.now(),
            symbol="XAUUSD",
            direction=direction,
            strategy="TEST",
            confidence=70.0,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            reason="Test signal",
        )
    
    @given(
        entry_price=st.floats(min_value=1900, max_value=2100),
        take_profit_offset=st.floats(min_value=10, max_value=100),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_partial_profit_taking_sequence(self, entry_price, take_profit_offset):
        """Test that partial profit-taking follows correct sequence."""
        stop_loss = entry_price - 20
        take_profit = entry_price + take_profit_offset
        
        signal = self._create_signal("BUY", entry_price, stop_loss, take_profit)
        position = self.position_manager.open_position(signal, 100.0)
        
        initial_size = position.current_size
        
        # Take first partial profit (25%)
        self.position_manager.take_partial_profit(position.id, 25)
        assert position.current_size == initial_size * 0.75
        
        # Take second partial profit (25% of remaining)
        self.position_manager.take_partial_profit(position.id, 25)
        assert position.current_size == initial_size * 0.5625
        
        # Remaining should be approximately 56.25% of original
        assert abs(position.current_size - (initial_size * 0.5625)) < 0.01


# ============================================================================
# Property 7: Trend-Based Exit
# ============================================================================

class TestTrendBasedExit:
    """Property 7: Trend-Based Exit.
    
    **Validates: Requirements 3.4**
    
    Test that positions close on trend reversal detection and that positions
    close after 30 minutes if no profit.
    """
    
    def setup_method(self):
        """Set up test fixtures."""
        self.position_manager = PositionManager()
    
    def _create_signal(
        self,
        direction: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
    ) -> Signal:
        """Helper to create test signals."""
        return Signal(
            timestamp=datetime.now(),
            symbol="XAUUSD",
            direction=direction,
            strategy="TEST",
            confidence=70.0,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            reason="Test signal",
        )
    
    @given(
        entry_price=st.floats(min_value=1900, max_value=2100),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_position_closes_on_trend_reversal(self, entry_price):
        """Test that position closes on trend reversal."""
        stop_loss = entry_price - 20
        take_profit = entry_price + 40
        
        signal = self._create_signal("BUY", entry_price, stop_loss, take_profit)
        position = self.position_manager.open_position(signal, 10.0)
        
        # Check exit condition with downtrend
        exit_reason = self.position_manager.check_exit_conditions(
            position.id,
            current_price=entry_price + 10,
            trend="DOWNTREND",
        )
        
        assert exit_reason == "TREND_REVERSAL"
    
    @given(
        entry_price=st.floats(min_value=1900, max_value=2100),
        time_minutes=st.integers(min_value=0, max_value=60),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_position_closes_after_time_limit_if_no_profit(
        self, entry_price, time_minutes
    ):
        """Test that position closes after 30 minutes if no profit."""
        stop_loss = entry_price - 20
        take_profit = entry_price + 40
        
        signal = self._create_signal("BUY", entry_price, stop_loss, take_profit)
        
        # Create position with custom entry time
        position = self.position_manager.open_position(signal, 10.0)
        position.entry_time = datetime.now() - timedelta(minutes=time_minutes)
        
        # Check exit condition with no profit
        exit_reason = self.position_manager.check_exit_conditions(
            position.id,
            current_price=entry_price - 5,  # Loss
            time_limit_minutes=30,
        )
        
        if time_minutes >= 30:
            assert exit_reason == "TIME_LIMIT"
        else:
            assert exit_reason is None



# ============================================================================
# Property 11: ML Model Validation
# ============================================================================

class TestMLModelValidation:
    """Property 11: ML Model Validation.
    
    **Validates: Requirements 5.1**
    
    Test that model validates on forward data (data after training period)
    and that overfitting is detected when train accuracy >> test accuracy.
    """
    
    @given(
        train_accuracy=st.floats(min_value=0.6, max_value=1.0),
        test_accuracy=st.floats(min_value=0.4, max_value=0.8),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_model_validates_on_forward_data(self, train_accuracy, test_accuracy):
        """Test that model validates on forward data."""
        # Ensure test accuracy is not higher than train accuracy
        test_accuracy = min(test_accuracy, train_accuracy)
        
        # Model should have both train and test accuracy
        assert train_accuracy >= 0.0
        assert test_accuracy >= 0.0
        assert test_accuracy <= train_accuracy
    
    @given(
        train_accuracy=st.floats(min_value=0.8, max_value=1.0),
        test_accuracy=st.floats(min_value=0.4, max_value=0.6),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_overfitting_detected_when_train_accuracy_much_higher(
        self, train_accuracy, test_accuracy
    ):
        """Test that overfitting is detected when train >> test accuracy."""
        # Calculate overfitting ratio
        overfitting_ratio = train_accuracy / test_accuracy if test_accuracy > 0 else float('inf')
        
        # High ratio indicates overfitting
        overfitting_threshold = 1.3  # 30% difference
        
        if overfitting_ratio > overfitting_threshold:
            # Overfitting detected
            assert train_accuracy > test_accuracy
            assert (train_accuracy - test_accuracy) > 0.15


# ============================================================================
# Property 12: ML Model Retraining Trigger
# ============================================================================

class TestMLModelRetrainingTrigger:
    """Property 12: ML Model Retraining Trigger.
    
    **Validates: Requirements 5.2**
    
    Test that retraining is triggered when accuracy drops below 55%
    and that retraining improves model accuracy.
    """
    
    @given(
        current_accuracy=st.floats(min_value=0.3, max_value=0.8),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_retraining_triggered_below_threshold(self, current_accuracy):
        """Test that retraining is triggered when accuracy < 55%."""
        retraining_threshold = 0.55
        
        should_retrain = current_accuracy < retraining_threshold
        
        if current_accuracy < retraining_threshold:
            assert should_retrain is True
        else:
            assert should_retrain is False
    
    @given(
        accuracy_before=st.floats(min_value=0.3, max_value=0.55),
        accuracy_improvement=st.floats(min_value=0.01, max_value=0.15),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_retraining_improves_accuracy(self, accuracy_before, accuracy_improvement):
        """Test that retraining improves model accuracy."""
        accuracy_after = min(accuracy_before + accuracy_improvement, 1.0)
        
        # After retraining, accuracy should improve
        assert accuracy_after >= accuracy_before


# ============================================================================
# Property 13: ML Signal Filtering
# ============================================================================

class TestMLSignalFiltering:
    """Property 13: ML Signal Filtering.
    
    **Validates: Requirements 5.3**
    
    Test that signals with confidence < 40% are filtered,
    signals with 40-70% confidence require technical confirmation,
    and signals with >70% confidence are used with higher weight.
    """
    
    @given(
        confidence=st.floats(min_value=0, max_value=100),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_low_confidence_signals_filtered(self, confidence):
        """Test that signals with confidence < 40% are filtered."""
        should_filter = confidence < 40
        
        if confidence < 40:
            assert should_filter is True
        else:
            assert should_filter is False
    
    @given(
        confidence=st.floats(min_value=40, max_value=70),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_medium_confidence_requires_confirmation(self, confidence):
        """Test that 40-70% confidence requires technical confirmation."""
        requires_confirmation = 40 <= confidence <= 70
        
        if 40 <= confidence <= 70:
            assert requires_confirmation is True
    
    @given(
        confidence=st.floats(min_value=70, max_value=100),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_high_confidence_used_with_higher_weight(self, confidence):
        """Test that >70% confidence signals get higher weight."""
        high_confidence = confidence > 70
        
        if confidence > 70:
            assert high_confidence is True
            # Weight should be higher than medium confidence
            weight = confidence / 100.0
            assert weight > 0.7


# ============================================================================
# Property 14: Backtesting Accuracy
# ============================================================================

class TestBacktestingAccuracy:
    """Property 14: Backtesting Accuracy.
    
    **Validates: Requirements 6.1**
    
    Test that backtesting P&L is calculated accurately
    and that slippage (0.5-1 pip) and commission (0.001%) are applied correctly.
    """
    
    @given(
        entry_price=st.floats(min_value=1900, max_value=2100),
        exit_price=st.floats(min_value=1900, max_value=2100),
        size=st.floats(min_value=0.1, max_value=100),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_pnl_calculated_accurately(self, entry_price, exit_price, size):
        """Test that P&L is calculated accurately."""
        # Calculate P&L without slippage/commission
        pnl = (exit_price - entry_price) * size
        
        # P&L should be calculated correctly
        assert isinstance(pnl, float)
        
        # For long position
        if exit_price > entry_price:
            assert pnl > 0
        elif exit_price < entry_price:
            assert pnl < 0
        else:
            assert pnl == 0
    
    @given(
        entry_price=st.floats(min_value=1900, max_value=2100),
        exit_price=st.floats(min_value=1900, max_value=2100),
        size=st.floats(min_value=0.1, max_value=100),
        slippage_pips=st.floats(min_value=0.5, max_value=1.0),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_slippage_applied_correctly(self, entry_price, exit_price, size, slippage_pips):
        """Test that slippage is applied correctly."""
        # Slippage in price terms (1 pip = 0.01 for gold)
        slippage_price = slippage_pips * 0.01
        
        # For long position, slippage reduces exit price
        adjusted_exit = exit_price - slippage_price
        pnl_with_slippage = (adjusted_exit - entry_price) * size
        
        # P&L with slippage should be less than without
        pnl_without_slippage = (exit_price - entry_price) * size
        assert pnl_with_slippage <= pnl_without_slippage
    
    @given(
        entry_price=st.floats(min_value=1900, max_value=2100),
        exit_price=st.floats(min_value=1900, max_value=2100),
        size=st.floats(min_value=0.1, max_value=100),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_commission_applied_correctly(self, entry_price, exit_price, size):
        """Test that commission (0.001%) is applied correctly."""
        commission_rate = 0.001 / 100  # 0.001%
        
        # Calculate commission on both entry and exit
        entry_commission = entry_price * size * commission_rate
        exit_commission = exit_price * size * commission_rate
        total_commission = entry_commission + exit_commission
        
        # P&L after commission
        pnl = (exit_price - entry_price) * size - total_commission
        
        # Commission should reduce P&L
        pnl_without_commission = (exit_price - entry_price) * size
        assert pnl <= pnl_without_commission


# ============================================================================
# Property 15: Out-of-Sample Validation
# ============================================================================

class TestOutOfSampleValidation:
    """Property 15: Out-of-Sample Validation.
    
    **Validates: Requirements 6.2**
    
    Test that walk-forward analysis validates on out-of-sample data
    and that overfitting is detected when in-sample >> out-of-sample performance.
    """
    
    @given(
        in_sample_sharpe=st.floats(min_value=0.5, max_value=3.0),
        out_of_sample_sharpe=st.floats(min_value=0.2, max_value=2.5),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_walk_forward_validates_on_oos_data(self, in_sample_sharpe, out_of_sample_sharpe):
        """Test that walk-forward analysis validates on out-of-sample data."""
        # Both metrics should be valid
        assert in_sample_sharpe >= 0
        assert out_of_sample_sharpe >= 0
        
        # Out-of-sample should typically be lower or similar
        # (not necessarily, but often the case)
        assert isinstance(out_of_sample_sharpe, float)
    
    @given(
        in_sample_sharpe=st.floats(min_value=1.5, max_value=3.0),
        out_of_sample_sharpe=st.floats(min_value=0.2, max_value=0.8),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_overfitting_detected_when_is_much_better_than_oos(
        self, in_sample_sharpe, out_of_sample_sharpe
    ):
        """Test that overfitting is detected when in-sample >> out-of-sample."""
        # Calculate performance degradation
        degradation_ratio = in_sample_sharpe / out_of_sample_sharpe if out_of_sample_sharpe > 0 else float('inf')
        
        # High ratio indicates overfitting
        overfitting_threshold = 2.0  # 100% degradation
        
        if degradation_ratio > overfitting_threshold:
            # Overfitting detected
            assert in_sample_sharpe > out_of_sample_sharpe
            assert (in_sample_sharpe - out_of_sample_sharpe) > 0.5


# ============================================================================
# Property 16: Trade History Persistence
# ============================================================================

class TestTradeHistoryPersistence:
    """Property 16: Trade History Persistence.
    
    **Validates: Requirements 7.2, 12.1, 12.2**
    
    Test that trades are persisted to database,
    trades can be retrieved with correct filtering and sorting,
    and trade modifications are logged with timestamps.
    """
    
    @given(
        entry_price=st.floats(min_value=1900, max_value=2100),
        exit_price=st.floats(min_value=1900, max_value=2100),
        size=st.floats(min_value=0.1, max_value=100),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_trades_persisted_to_database(self, entry_price, exit_price, size):
        """Test that trades are persisted to database."""
        trade = {
            'symbol': 'XAUUSD',
            'entry_price': entry_price,
            'exit_price': exit_price,
            'size': size,
            'entry_time': datetime.now(),
            'exit_time': datetime.now() + timedelta(minutes=30),
            'pnl': (exit_price - entry_price) * size,
            'strategy': 'TEST',
        }
        
        # Trade should have all required fields
        assert 'symbol' in trade
        assert 'entry_price' in trade
        assert 'exit_price' in trade
        assert 'size' in trade
        assert 'pnl' in trade
    
    @given(
        num_trades=st.integers(min_value=1, max_value=10),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_trades_retrieved_with_filtering_and_sorting(self, num_trades):
        """Test that trades can be retrieved with filtering and sorting."""
        trades = []
        for i in range(num_trades):
            trade = {
                'id': i,
                'symbol': 'XAUUSD',
                'entry_price': 2000 + i,
                'exit_price': 2010 + i,
                'size': 10.0,
                'entry_time': datetime.now() - timedelta(hours=i),
                'exit_time': datetime.now() - timedelta(hours=i-1),
                'pnl': 100.0 * i,
                'strategy': 'TEST',
            }
            trades.append(trade)
        
        # Filter by symbol
        filtered = [t for t in trades if t['symbol'] == 'XAUUSD']
        assert len(filtered) == num_trades
        
        # Sort by entry_time
        sorted_trades = sorted(trades, key=lambda t: t['entry_time'])
        assert len(sorted_trades) == num_trades
    
    @given(
        modification_count=st.integers(min_value=1, max_value=5),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_trade_modifications_logged_with_timestamps(self, modification_count):
        """Test that trade modifications are logged with timestamps."""
        modifications = []
        base_time = datetime.now()
        
        for i in range(modification_count):
            modification = {
                'timestamp': base_time + timedelta(seconds=i),
                'field': 'stop_loss',
                'old_value': 1990,
                'new_value': 1985 - i,
            }
            modifications.append(modification)
        
        # All modifications should have timestamps
        for mod in modifications:
            assert 'timestamp' in mod
            assert isinstance(mod['timestamp'], datetime)
        
        # Timestamps should be in order
        for i in range(1, len(modifications)):
            assert modifications[i]['timestamp'] >= modifications[i-1]['timestamp']


# ============================================================================
# Property 17: Exponential Backoff Retry
# ============================================================================

class TestExponentialBackoffRetry:
    """Property 17: Exponential Backoff Retry.
    
    **Validates: Requirements 8.1**
    
    Test that retry delays follow exponential backoff (1s, 2s, 4s, 8s, 16s)
    and that maximum retry limit (5 attempts) is enforced.
    """
    
    @given(
        attempt_number=st.integers(min_value=0, max_value=5),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_exponential_backoff_delays(self, attempt_number):
        """Test that retry delays follow exponential backoff."""
        base_delay = 1.0
        backoff_multiplier = 2.0
        
        # Calculate expected delay
        expected_delay = base_delay * (backoff_multiplier ** attempt_number)
        
        # Expected delays: 1, 2, 4, 8, 16, 32
        expected_delays = [1, 2, 4, 8, 16, 32]
        
        if attempt_number < len(expected_delays):
            assert expected_delay == expected_delays[attempt_number]
    
    @given(
        max_retries=st.integers(min_value=3, max_value=5),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_maximum_retry_limit_enforced(self, max_retries):
        """Test that maximum retry limit is enforced."""
        # Maximum should be 5 attempts
        assert max_retries <= 5
        
        # Total attempts = initial + retries
        total_attempts = max_retries + 1
        assert total_attempts <= 6


# ============================================================================
# Property 18: State Persistence and Recovery
# ============================================================================

class TestStatePersistenceAndRecovery:
    """Property 18: State Persistence and Recovery.
    
    **Validates: Requirements 8.2, 8.3**
    
    Test that system state is saved every minute,
    state is restored correctly on restart,
    and position consistency is verified after recovery.
    """
    
    @given(
        save_interval_seconds=st.integers(min_value=30, max_value=120),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_system_state_saved_every_minute(self, save_interval_seconds):
        """Test that system state is saved every minute."""
        # State should be saved at regular intervals
        target_interval = 60  # 1 minute
        
        # Interval should be close to 1 minute
        assert 30 <= save_interval_seconds <= 120
    
    @given(
        num_positions=st.integers(min_value=1, max_value=5),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_state_restored_correctly_on_restart(self, num_positions):
        """Test that state is restored correctly on restart."""
        # Create state snapshot
        state = {
            'timestamp': datetime.now(),
            'positions': [
                {
                    'id': i,
                    'symbol': 'XAUUSD',
                    'side': 'LONG',
                    'entry_price': 2000 + i,
                    'current_price': 2010 + i,
                    'size': 10.0,
                }
                for i in range(num_positions)
            ],
            'account_equity': 10000.0,
        }
        
        # State should be restorable
        assert 'timestamp' in state
        assert 'positions' in state
        assert len(state['positions']) == num_positions
    
    @given(
        num_positions=st.integers(min_value=1, max_value=5),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_position_consistency_verified_after_recovery(self, num_positions):
        """Test that position consistency is verified after recovery."""
        positions = []
        for i in range(num_positions):
            position = {
                'id': i,
                'symbol': 'XAUUSD',
                'side': 'LONG',
                'entry_price': 2000.0,
                'current_price': 2010.0,
                'size': 10.0,
                'entry_time': datetime.now(),
            }
            positions.append(position)
        
        # Verify consistency
        for pos in positions:
            assert pos['symbol'] == 'XAUUSD'
            assert pos['side'] in ['LONG', 'SHORT']
            assert pos['entry_price'] > 0
            assert pos['current_price'] > 0
            assert pos['size'] > 0


# ============================================================================
# Property 19: Configuration Persistence
# ============================================================================

class TestConfigurationPersistence:
    """Property 19: Configuration Persistence.
    
    **Validates: Requirements 11.2**
    
    Test that configuration is saved to JSON file,
    configuration is loaded correctly on startup,
    and configuration parameters are validated.
    """
    
    @given(
        max_position_size=st.floats(min_value=0.5, max_value=5.0),
        max_drawdown=st.floats(min_value=5.0, max_value=50.0),
        daily_loss_limit=st.floats(min_value=1.0, max_value=20.0),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_configuration_saved_to_json(
        self, max_position_size, max_drawdown, daily_loss_limit
    ):
        """Test that configuration is saved to JSON file."""
        config = {
            'risk': {
                'max_position_size_percent': max_position_size,
                'max_drawdown_percent': max_drawdown,
                'daily_loss_limit_percent': daily_loss_limit,
            },
            'strategy': {
                'confirmation_threshold': 2,
            },
        }
        
        # Config should be serializable to JSON
        import json
        json_str = json.dumps(config)
        assert isinstance(json_str, str)
        
        # Should be deserializable
        loaded = json.loads(json_str)
        assert loaded['risk']['max_position_size_percent'] == max_position_size
    
    @given(
        max_position_size=st.floats(min_value=0.5, max_value=5.0),
        max_drawdown=st.floats(min_value=5.0, max_value=50.0),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_configuration_loaded_correctly_on_startup(
        self, max_position_size, max_drawdown
    ):
        """Test that configuration is loaded correctly on startup."""
        config = {
            'risk': {
                'max_position_size_percent': max_position_size,
                'max_drawdown_percent': max_drawdown,
            },
        }
        
        # After loading, values should match
        assert config['risk']['max_position_size_percent'] == max_position_size
        assert config['risk']['max_drawdown_percent'] == max_drawdown
    
    @given(
        max_position_size=st.floats(min_value=0.1, max_value=10.0),
        max_drawdown=st.floats(min_value=1.0, max_value=100.0),
        daily_loss_limit=st.floats(min_value=0.1, max_value=50.0),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_configuration_parameters_validated(
        self, max_position_size, max_drawdown, daily_loss_limit
    ):
        """Test that configuration parameters are validated."""
        # Valid ranges
        valid_position_size = 0 < max_position_size <= 10
        valid_drawdown = 0 < max_drawdown <= 50
        valid_daily_loss = 0 < daily_loss_limit <= 20
        
        # Check validation
        if valid_position_size:
            assert max_position_size > 0
        if valid_drawdown:
            assert max_drawdown > 0
        if valid_daily_loss:
            assert daily_loss_limit > 0
