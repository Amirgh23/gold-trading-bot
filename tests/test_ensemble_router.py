"""Tests for ensemble signal routing."""

import pytest
from datetime import datetime
from hypothesis import given, strategies as st
from trading_bot.strategies.ensemble import EnsembleRouter
from trading_bot.models.signal import Signal


class TestEnsembleRouter:
    """Test EnsembleRouter component."""
    
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
    
    def test_confirmation_threshold_enforcement(self):
        """Property 2: Confirmation threshold should be enforced."""
        # Single signal - should not route
        signals = [self._create_signal("BUY", "TECHNICAL", 70)]
        result = self.router.route_signal(signals, confirmation_threshold=2)
        assert result is None
        
        # Two signals - should route
        signals = [
            self._create_signal("BUY", "TECHNICAL", 70),
            self._create_signal("BUY", "LSTM", 65),
        ]
        result = self.router.route_signal(signals, confirmation_threshold=2)
        assert result is not None
        assert result.direction == "BUY"
    
    def test_high_volatility_confirmation(self):
        """Property 2: High volatility should increase confirmation threshold."""
        # Two signals with high volatility
        signals = [
            self._create_signal("BUY", "TECHNICAL", 70),
            self._create_signal("BUY", "LSTM", 65),
        ]
        
        # Should fail with high volatility (needs 3)
        result = self.router.route_signal(
            signals,
            volatility=2.5,
            confirmation_threshold=2,
            high_volatility_threshold=2.0,
        )
        assert result is None
        
        # Should pass with 3 signals
        signals.append(self._create_signal("BUY", "DQN", 60))
        result = self.router.route_signal(
            signals,
            volatility=2.5,
            confirmation_threshold=2,
            high_volatility_threshold=2.0,
        )
        assert result is not None
    
    def test_conflict_detection(self):
        """Conflicting signals should not route."""
        signals = [
            self._create_signal("BUY", "TECHNICAL", 70),
            self._create_signal("SELL", "LSTM", 65),
        ]
        
        result = self.router.route_signal(signals)
        assert result is None
    
    def test_ensemble_confidence_calculation(self):
        """Ensemble confidence should be calculated correctly."""
        signals = [
            self._create_signal("BUY", "TECHNICAL", 80),
            self._create_signal("BUY", "LSTM", 60),
            self._create_signal("BUY", "DQN", 70),
        ]
        
        result = self.router.route_signal(signals)
        assert result is not None
        
        # Average confidence should be around 70
        expected_confidence = (80 + 60 + 70) / 3
        assert abs(result.confidence - expected_confidence) < 5
    
    def test_recommendation_levels(self):
        """Recommendation should reflect confidence levels."""
        # High confidence
        signals = [
            self._create_signal("BUY", "TECHNICAL", 90),
            self._create_signal("BUY", "LSTM", 85),
            self._create_signal("BUY", "DQN", 88),
        ]
        result = self.router.route_signal(signals)
        assert "STRONG" in result.recommendation
        
        # Medium confidence
        signals = [
            self._create_signal("BUY", "TECHNICAL", 65),
            self._create_signal("BUY", "LSTM", 60),
        ]
        result = self.router.route_signal(signals)
        assert result.recommendation == "BUY"
        
        # Low confidence
        signals = [
            self._create_signal("BUY", "TECHNICAL", 45),
            self._create_signal("BUY", "LSTM", 42),
        ]
        result = self.router.route_signal(signals)
        assert "WEAK" in result.recommendation
