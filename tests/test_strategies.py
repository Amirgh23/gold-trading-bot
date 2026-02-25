"""Unit tests for trading strategies."""

import unittest
from unittest.mock import Mock, patch
import pandas as pd
import numpy as np
from datetime import datetime
from trading_bot.strategies.ensemble import EnsembleRouter, EnsembleSignal
from trading_bot.models.signal import Signal


class TestEnsembleRouter(unittest.TestCase):
    """Test EnsembleRouter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.router = EnsembleRouter()
    
    def create_signal(self, direction: str, strategy: str, confidence: float = 80.0) -> Signal:
        """Helper to create test signals."""
        return Signal(
            timestamp=datetime.now(),
            symbol='XAUUSD',
            direction=direction,
            strategy=strategy,
            confidence=confidence,
            entry_price=100.0,
            stop_loss=99.0,
            take_profit=101.0,
            reason='Test signal',
        )
    
    def test_ensemble_signal_with_confirmation(self):
        """Test ensemble signal with confirmation."""
        signals = [
            self.create_signal('BUY', 'TECHNICAL', 85.0),
            self.create_signal('BUY', 'LSTM', 75.0),
        ]
        
        ensemble = self.router.route_signal(signals, confirmation_threshold=2)
        
        self.assertIsNotNone(ensemble)
        self.assertEqual(ensemble.direction, 'BUY')
        self.assertGreater(ensemble.confidence, 0)
    
    def test_ensemble_signal_insufficient_confirmation(self):
        """Test ensemble signal with insufficient confirmation."""
        signals = [
            self.create_signal('BUY', 'TECHNICAL', 85.0),
        ]
        
        ensemble = self.router.route_signal(signals, confirmation_threshold=2)
        
        self.assertIsNone(ensemble)
    
    def test_ensemble_signal_conflict_detection(self):
        """Test conflict detection."""
        signals = [
            self.create_signal('BUY', 'TECHNICAL', 85.0),
            self.create_signal('SELL', 'LSTM', 75.0),
        ]
        
        ensemble = self.router.route_signal(signals)
        
        self.assertIsNone(ensemble)
    
    def test_ml_signal_filtering_low_confidence(self):
        """Test ML signal filtering for low confidence."""
        signals = [
            self.create_signal('BUY', 'TECHNICAL', 85.0),
            self.create_signal('BUY', 'LSTM', 30.0),  # Below 40% threshold
        ]
        
        ensemble = self.router.route_signal(signals, ml_confidence_threshold=40.0)
        
        # Should still have ensemble signal from technical
        self.assertIsNotNone(ensemble)
    
    def test_ml_signal_filtering_medium_confidence_with_confirmation(self):
        """Test ML signal filtering for medium confidence with technical confirmation."""
        signals = [
            self.create_signal('BUY', 'TECHNICAL', 85.0),
            self.create_signal('BUY', 'LSTM', 55.0),  # 40-70% range
        ]
        
        ensemble = self.router.route_signal(signals, ml_confidence_threshold=40.0)
        
        # Should have ensemble signal with both confirmations
        self.assertIsNotNone(ensemble)
        self.assertEqual(len(ensemble.confirming_strategies), 2)
    
    def test_ml_signal_filtering_medium_confidence_no_confirmation(self):
        """Test ML signal filtering for medium confidence without technical confirmation."""
        signals = [
            self.create_signal('BUY', 'LSTM', 55.0),  # 40-70% range, no technical
        ]
        
        ensemble = self.router.route_signal(signals, ml_confidence_threshold=40.0)
        
        # Should be filtered out due to lack of technical confirmation
        self.assertIsNone(ensemble)
    
    def test_ml_signal_filtering_high_confidence(self):
        """Test ML signal filtering for high confidence."""
        signals = [
            self.create_signal('BUY', 'LSTM', 85.0),  # Above 70%
        ]
        
        ensemble = self.router.route_signal(signals, ml_confidence_threshold=40.0)
        
        # Should have ensemble signal
        self.assertIsNotNone(ensemble)
    
    def test_volatility_adjustment(self):
        """Test confirmation threshold adjustment for high volatility."""
        signals = [
            self.create_signal('BUY', 'TECHNICAL', 85.0),
            self.create_signal('BUY', 'LSTM', 75.0),
            self.create_signal('BUY', 'DQN', 70.0),
        ]
        
        # Low volatility - 2 confirmations needed
        ensemble_low = self.router.route_signal(
            signals[:2],
            volatility=1.0,
            confirmation_threshold=2,
            high_volatility_threshold=2.0,
        )
        self.assertIsNotNone(ensemble_low)
        
        # High volatility - 3 confirmations needed
        ensemble_high = self.router.route_signal(
            signals[:2],
            volatility=3.0,
            confirmation_threshold=2,
            high_volatility_threshold=2.0,
        )
        self.assertIsNone(ensemble_high)
    
    def test_confidence_calculation(self):
        """Test confidence calculation."""
        signals = [
            self.create_signal('BUY', 'TECHNICAL', 100.0),
            self.create_signal('BUY', 'LSTM', 80.0),
            self.create_signal('BUY', 'DQN', 60.0),
        ]
        
        ensemble = self.router.route_signal(signals, confirmation_threshold=2)
        
        # Confidence should be average of signals
        expected_confidence = (100.0 + 80.0 + 60.0) / 3
        self.assertAlmostEqual(ensemble.confidence, expected_confidence * 1.1, delta=1)
    
    def test_ensemble_signal_recommendation(self):
        """Test ensemble signal recommendation levels."""
        # Strong buy
        ensemble = EnsembleSignal(
            direction='BUY',
            confidence=85.0,
            confirming_strategies=['TECHNICAL', 'LSTM'],
            conflicting_strategies=[],
            entry_price=100.0,
            stop_loss=99.0,
            take_profit=101.0,
            reason='Test',
        )
        self.assertEqual(ensemble.recommendation, 'STRONG_BUY')
        
        # Buy
        ensemble.confidence = 65.0
        self.assertEqual(ensemble.recommendation, 'BUY')
        
        # Weak buy
        ensemble.confidence = 45.0
        self.assertEqual(ensemble.recommendation, 'WEAK_BUY')
        
        # Hold
        ensemble.confidence = 35.0
        self.assertEqual(ensemble.recommendation, 'HOLD')


class TestSignalFiltering(unittest.TestCase):
    """Test signal filtering logic."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.router = EnsembleRouter()
    
    def create_signal(self, direction: str, strategy: str, confidence: float = 80.0) -> Signal:
        """Helper to create test signals."""
        return Signal(
            timestamp=datetime.now(),
            symbol='XAUUSD',
            direction=direction,
            strategy=strategy,
            confidence=confidence,
            entry_price=100.0,
            stop_loss=99.0,
            take_profit=101.0,
            reason='Test signal',
        )
    
    def test_filter_signals_by_confidence(self):
        """Test signal filtering by confidence."""
        signals = [
            self.create_signal('BUY', 'TECHNICAL', 85.0),
            self.create_signal('BUY', 'LSTM', 30.0),
            self.create_signal('BUY', 'DQN', 55.0),
        ]
        
        filtered = self.router._filter_signals_by_confidence(signals, ml_confidence_threshold=40.0)
        
        # Should have technical (always kept) and DQN (55% > 40%)
        # LSTM should be filtered out (30% < 40%)
        self.assertEqual(len(filtered), 2)
        strategies = [s.strategy for s in filtered]
        self.assertIn('TECHNICAL', strategies)
        self.assertIn('DQN', strategies)
        self.assertNotIn('LSTM', strategies)
    
    def test_filter_ml_signals_require_technical_confirmation(self):
        """Test ML signals require technical confirmation in 40-70% range."""
        signals = [
            self.create_signal('BUY', 'LSTM', 55.0),  # No technical confirmation
        ]
        
        filtered = self.router._filter_signals_by_confidence(signals, ml_confidence_threshold=40.0)
        
        # Should be filtered out
        self.assertEqual(len(filtered), 0)
    
    def test_filter_ml_signals_with_conflicting_technical(self):
        """Test ML signals filtered when technical disagrees."""
        signals = [
            self.create_signal('BUY', 'TECHNICAL', 85.0),
            self.create_signal('SELL', 'LSTM', 55.0),  # Conflicts with technical
        ]
        
        filtered = self.router._filter_signals_by_confidence(signals, ml_confidence_threshold=40.0)
        
        # Should only have technical
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].strategy, 'TECHNICAL')


if __name__ == '__main__':
    unittest.main()
