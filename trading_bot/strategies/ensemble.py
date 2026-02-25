"""Ensemble signal router with weighted voting."""

from typing import List, Optional, Dict
from datetime import datetime
import logging
from trading_bot.models.signal import Signal

logger = logging.getLogger(__name__)


class EnsembleSignal:
    """Ensemble signal combining multiple strategies."""
    
    def __init__(
        self,
        direction: str,
        confidence: float,
        confirming_strategies: List[str],
        conflicting_strategies: List[str],
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        reason: str,
    ):
        self.direction = direction
        self.confidence = confidence
        self.confirming_strategies = confirming_strategies
        self.conflicting_strategies = conflicting_strategies
        self.entry_price = entry_price
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.reason = reason
        self.timestamp = datetime.now()
    
    @property
    def recommendation(self) -> str:
        """Get trading recommendation."""
        if self.confidence > 80:
            return f"STRONG_{self.direction}"
        elif self.confidence > 60:
            return self.direction
        elif self.confidence > 40:
            return "WEAK_" + self.direction
        else:
            return "HOLD"
    
    def to_signal(self, symbol: str = "XAUUSD") -> Signal:
        """Convert to Signal object."""
        return Signal(
            timestamp=self.timestamp,
            symbol=symbol,
            direction=self.direction,
            strategy="ENSEMBLE",
            confidence=self.confidence,
            entry_price=self.entry_price,
            stop_loss=self.stop_loss,
            take_profit=self.take_profit,
            reason=self.reason,
            indicators={
                'confirming_strategies': len(self.confirming_strategies),
                'conflicting_strategies': len(self.conflicting_strategies),
            }
        )


class EnsembleRouter:
    """Routes and combines signals from multiple strategies."""
    
    def __init__(self):
        self.strategy_weights = {}
        self.signal_history = []
    
    def route_signal(
        self,
        signals: List[Signal],
        volatility: float = 1.0,
        confirmation_threshold: int = 2,
        high_volatility_threshold: float = 2.0,
        ml_confidence_threshold: float = 40.0,
    ) -> Optional[EnsembleSignal]:
        """
        Route signals through ensemble logic with ML confidence filtering.
        
        Args:
            signals: List of signals from different strategies
            volatility: Current market volatility
            confirmation_threshold: Minimum strategies to confirm
            high_volatility_threshold: Volatility threshold for increased confirmation
            ml_confidence_threshold: Minimum confidence for ML signals (0-100%)
        
        Returns:
            EnsembleSignal or None if no consensus
        """
        if not signals:
            return None
        
        # Filter signals based on confidence and strategy type
        filtered_signals = self._filter_signals_by_confidence(
            signals, ml_confidence_threshold
        )
        
        if not filtered_signals:
            logger.debug("All signals filtered out due to low confidence")
            return None
        
        # Adjust confirmation threshold based on volatility
        if volatility > high_volatility_threshold:
            required_confirmations = confirmation_threshold + 1
        else:
            required_confirmations = confirmation_threshold
        
        # Separate BUY and SELL signals
        buy_signals = [s for s in filtered_signals if s.direction == "BUY"]
        sell_signals = [s for s in filtered_signals if s.direction == "SELL"]
        
        # Check for conflicts
        if buy_signals and sell_signals:
            logger.warning("Conflicting signals detected (BUY and SELL)")
            return None
        
        # Determine direction and get confirming signals
        if buy_signals:
            direction = "BUY"
            confirming = buy_signals
            conflicting = sell_signals
        elif sell_signals:
            direction = "SELL"
            confirming = sell_signals
            conflicting = buy_signals
        else:
            return None
        
        # Check confirmation threshold
        if len(confirming) < required_confirmations:
            logger.debug(
                f"Insufficient confirmations: {len(confirming)}/{required_confirmations}"
            )
            return None
        
        # Calculate ensemble confidence
        confidence = self._calculate_confidence(confirming)
        
        # Use first signal's entry/exit levels
        primary_signal = confirming[0]
        
        # Create ensemble signal
        ensemble_signal = EnsembleSignal(
            direction=direction,
            confidence=confidence,
            confirming_strategies=[s.strategy for s in confirming],
            conflicting_strategies=[s.strategy for s in conflicting],
            entry_price=primary_signal.entry_price,
            stop_loss=primary_signal.stop_loss,
            take_profit=primary_signal.take_profit,
            reason=f"Confirmed by {len(confirming)} strategies: {', '.join([s.strategy for s in confirming])}",
        )
        
        self.signal_history.append(ensemble_signal)
        logger.info(f"Ensemble signal generated: {ensemble_signal.recommendation}")
        
        return ensemble_signal
    
    def _calculate_confidence(self, signals: List[Signal]) -> float:
        """Calculate ensemble confidence from individual signals."""
        if not signals:
            return 0.0
        
        # Average confidence with weights
        total_confidence = sum(s.confidence for s in signals)
        avg_confidence = total_confidence / len(signals)
        
        # Boost confidence if all strategies agree
        if len(signals) >= 3:
            avg_confidence = min(100, avg_confidence * 1.1)
        
        return avg_confidence
    
    def _filter_signals_by_confidence(
        self,
        signals: List[Signal],
        ml_confidence_threshold: float = 40.0,
    ) -> List[Signal]:
        """
        Filter signals based on confidence levels and strategy type.
        
        ML signals filtering rules:
        - Confidence < 40%: Filter out (too low confidence)
        - Confidence 40-70%: Keep only if technical confirmation exists
        - Confidence > 70%: Keep (high confidence)
        
        Technical signals: Always keep
        
        Args:
            signals: List of signals to filter
            ml_confidence_threshold: Minimum confidence for ML signals
        
        Returns:
            Filtered list of signals
        """
        filtered = []
        ml_signals = []
        technical_signals = []
        
        # Separate ML and technical signals
        for signal in signals:
            if signal.strategy in ["LSTM", "DQN", "ML"]:
                ml_signals.append(signal)
            else:
                technical_signals.append(signal)
        
        # Always keep technical signals
        filtered.extend(technical_signals)
        
        # Filter ML signals by confidence
        for signal in ml_signals:
            if signal.confidence < ml_confidence_threshold:
                logger.debug(
                    f"Filtering out {signal.strategy} signal: "
                    f"confidence {signal.confidence:.1f}% < {ml_confidence_threshold}%"
                )
                continue
            
            # For 40-70% confidence, require technical confirmation
            if ml_confidence_threshold <= signal.confidence <= 70:
                if not technical_signals:
                    logger.debug(
                        f"Filtering out {signal.strategy} signal: "
                        f"confidence {signal.confidence:.1f}% requires technical confirmation"
                    )
                    continue
                
                # Check if technical signals agree on direction
                tech_directions = [s.direction for s in technical_signals]
                if signal.direction not in tech_directions:
                    logger.debug(
                        f"Filtering out {signal.strategy} signal: "
                        f"no technical confirmation for {signal.direction}"
                    )
                    continue
            
            # Keep signal if it passes all filters
            filtered.append(signal)
        
        return filtered
    
    def update_strategy_weights(self, performance: Dict[str, float]):
        """Update strategy weights based on performance."""
        for strategy_name, accuracy in performance.items():
            self.strategy_weights[strategy_name] = accuracy
        
        logger.info(f"Updated strategy weights: {self.strategy_weights}")
    
    def get_confirmation_status(self, signals: List[Signal]) -> Dict[str, any]:
        """Get detailed confirmation status."""
        buy_count = len([s for s in signals if s.direction == "BUY"])
        sell_count = len([s for s in signals if s.direction == "SELL"])
        
        return {
            'total_signals': len(signals),
            'buy_signals': buy_count,
            'sell_signals': sell_count,
            'has_conflict': buy_count > 0 and sell_count > 0,
            'avg_confidence': sum(s.confidence for s in signals) / len(signals) if signals else 0,
        }
