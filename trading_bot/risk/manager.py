"""Advanced risk management with Kelly Criterion and dynamic position sizing."""

from typing import List, Optional, Dict
import logging
from trading_bot.models.position import Position

logger = logging.getLogger(__name__)


class RiskManager:
    """Manages position sizing and risk controls."""
    
    def __init__(
        self,
        account_equity: float,
        max_position_size_percent: float = 2.0,
        max_concurrent_positions: int = 5,
        max_drawdown_percent: float = 20.0,
        daily_loss_limit_percent: float = 5.0,
        kelly_fraction: float = 0.25,
    ):
        self.account_equity = account_equity
        self.initial_equity = account_equity
        self.max_position_size_percent = max_position_size_percent
        self.max_concurrent_positions = max_concurrent_positions
        self.max_drawdown_percent = max_drawdown_percent
        self.daily_loss_limit_percent = daily_loss_limit_percent
        self.kelly_fraction = kelly_fraction
        
        self.daily_pnl = 0.0
        self.peak_equity = account_equity
        self.consecutive_losses = 0
        self.consecutive_wins = 0
    
    def calculate_position_size(
        self,
        entry_price: float,
        stop_loss: float,
        win_rate: float = 0.55,
        risk_reward_ratio: float = 2.0,
    ) -> float:
        """
        Calculate optimal position size using Kelly Criterion.
        
        Kelly Criterion: f* = (bp - q) / b
        where:
        - f* = fraction of capital to risk
        - b = risk/reward ratio
        - p = win probability
        - q = loss probability (1 - p)
        """
        if entry_price <= 0 or stop_loss <= 0:
            return 0.0
        
        # Calculate risk per trade
        risk_per_trade = abs(entry_price - stop_loss)
        if risk_per_trade == 0:
            return 0.0
        
        # Kelly Criterion calculation
        q = 1 - win_rate
        kelly_fraction = (risk_reward_ratio * win_rate - q) / risk_reward_ratio
        
        # Apply conservative multiplier
        kelly_fraction = kelly_fraction * self.kelly_fraction
        
        # Ensure positive
        kelly_fraction = max(0, kelly_fraction)
        
        # Calculate position size
        risk_amount = self.account_equity * kelly_fraction
        position_size = risk_amount / risk_per_trade
        
        # Apply maximum position size limit
        max_size = (self.account_equity * self.max_position_size_percent) / 100
        position_size = min(position_size, max_size)
        
        logger.debug(
            f"Position size: {position_size:.4f} "
            f"(Kelly: {kelly_fraction:.4f}, Risk: {risk_amount:.2f})"
        )
        
        return position_size
    
    def check_risk_limits(
        self,
        position_size: float,
        current_drawdown: float,
        open_positions_count: int,
    ) -> bool:
        """Check if position respects all risk limits."""
        # Check maximum position size
        max_size = (self.account_equity * self.max_position_size_percent) / 100
        if position_size > max_size:
            logger.warning(f"Position size {position_size} exceeds maximum {max_size}")
            return False
        
        # Check maximum concurrent positions
        if open_positions_count >= self.max_concurrent_positions:
            logger.warning(
                f"Maximum concurrent positions ({self.max_concurrent_positions}) reached"
            )
            return False
        
        # Check drawdown limit
        if current_drawdown > self.max_drawdown_percent:
            logger.warning(
                f"Drawdown {current_drawdown:.2f}% exceeds limit {self.max_drawdown_percent}%"
            )
            return False
        
        # Check daily loss limit
        if self.daily_pnl < -(self.account_equity * self.daily_loss_limit_percent / 100):
            logger.warning(
                f"Daily loss limit reached: {self.daily_pnl:.2f}"
            )
            return False
        
        return True
    
    def adjust_for_volatility(
        self,
        position_size: float,
        volatility: float,
        normal_volatility: float = 1.0,
    ) -> float:
        """Adjust position size based on volatility."""
        if volatility > normal_volatility * 2:
            # High volatility: reduce by 30%
            adjusted_size = position_size * 0.7
            logger.debug(f"Reduced position size for high volatility: {adjusted_size:.4f}")
            return adjusted_size
        elif volatility < normal_volatility * 0.5:
            # Low volatility: increase by 10%
            adjusted_size = position_size * 1.1
            logger.debug(f"Increased position size for low volatility: {adjusted_size:.4f}")
            return adjusted_size
        
        return position_size
    
    def adjust_for_spread(
        self,
        position_size: float,
        spread: float,
        normal_spread: float = 0.1,
    ) -> float:
        """Adjust position size based on bid-ask spread."""
        if spread > normal_spread * 5:
            # Very wide spread: reduce by 20%
            adjusted_size = position_size * 0.8
            logger.debug(f"Reduced position size for wide spread: {adjusted_size:.4f}")
            return adjusted_size
        
        return position_size
    
    def calculate_correlation_adjustment(
        self,
        open_positions: List[Position],
        new_position: Position,
    ) -> float:
        """Calculate position size adjustment based on correlation."""
        if not open_positions:
            return 1.0
        
        # Simple correlation check: if all positions are same direction, reduce
        same_direction_count = sum(
            1 for p in open_positions if p.side == new_position.side
        )
        
        if same_direction_count >= len(open_positions):
            # All positions in same direction: reduce by 20%
            adjustment = 0.8
            logger.debug(f"Reduced position size for high correlation: {adjustment}")
            return adjustment
        
        return 1.0
    
    def update_equity(self, new_equity: float):
        """Update account equity."""
        previous_equity = self.account_equity
        self.account_equity = new_equity
        
        # Update peak equity
        if new_equity > self.peak_equity:
            self.peak_equity = new_equity
        
        # Update daily P&L
        self.daily_pnl += (new_equity - previous_equity)
        
        # Track consecutive wins/losses
        if new_equity > previous_equity:
            self.consecutive_wins += 1
            self.consecutive_losses = 0
        else:
            self.consecutive_losses += 1
            self.consecutive_wins = 0
    
    def get_current_drawdown(self) -> float:
        """Calculate current drawdown percentage."""
        if self.peak_equity == 0:
            return 0.0
        
        drawdown = ((self.peak_equity - self.account_equity) / self.peak_equity) * 100
        return max(0, drawdown)
    
    def get_position_size_adjustment(self) -> float:
        """Get position size adjustment based on consecutive trades."""
        # Reduce after consecutive losses
        if self.consecutive_losses > 0:
            reduction = 0.9 ** self.consecutive_losses
            return max(0.1, reduction)
        
        # Increase after consecutive wins
        if self.consecutive_wins > 0:
            increase = 1.05 ** self.consecutive_wins
            return min(1.5, increase)
        
        return 1.0
    
    def should_stop_trading(self) -> bool:
        """Check if trading should be stopped."""
        # Stop if daily loss limit reached
        daily_loss_limit = self.account_equity * self.daily_loss_limit_percent / 100
        if self.daily_pnl < -daily_loss_limit:
            logger.warning("Daily loss limit reached, stopping trading")
            return True
        
        # Stop if drawdown exceeds limit
        if self.get_current_drawdown() > self.max_drawdown_percent:
            logger.warning("Maximum drawdown exceeded, stopping trading")
            return True
        
        return False
    
    def reset_daily_metrics(self):
        """Reset daily metrics."""
        self.daily_pnl = 0.0
        logger.info("Daily metrics reset")
