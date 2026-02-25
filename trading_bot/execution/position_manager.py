"""Position management with smart exits."""

from typing import List, Optional, Dict
from datetime import datetime, timedelta
import logging
import uuid
from trading_bot.models.position import Position
from trading_bot.models.trade import Trade
from trading_bot.models.signal import Signal

logger = logging.getLogger(__name__)


class PositionManager:
    """Manages open positions with smart exits."""
    
    def __init__(self):
        self.open_positions: Dict[str, Position] = {}
        self.closed_trades: List[Trade] = []
    
    def open_position(
        self,
        signal: Signal,
        size: float,
        symbol: str = "XAUUSD",
    ) -> Optional[Position]:
        """Open a new position based on signal."""
        if size <= 0:
            logger.warning("Invalid position size")
            return None
        
        # Determine side
        side = "LONG" if signal.direction == "BUY" else "SHORT"
        
        position = Position(
            symbol=symbol,
            side=side,
            entry_price=signal.entry_price,
            entry_time=signal.timestamp,
            entry_size=size,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            entry_reason=signal.reason,
            strategy=signal.strategy,
            current_price=signal.entry_price,
            current_size=size,
        )
        
        self.open_positions[position.id] = position
        logger.info(
            f"Opened {side} position: {position.id} "
            f"@ {signal.entry_price} (size: {size})"
        )
        
        return position
    
    def close_position(
        self,
        position_id: str,
        exit_price: float,
        exit_reason: str,
    ) -> Optional[Trade]:
        """Close an open position."""
        if position_id not in self.open_positions:
            logger.warning(f"Position {position_id} not found")
            return None
        
        position = self.open_positions[position_id]
        
        # Create trade record
        trade = Trade(
            symbol=position.symbol,
            entry_time=position.entry_time,
            entry_price=position.entry_price,
            entry_size=position.entry_size,
            entry_reason=position.entry_reason,
            exit_time=datetime.now(),
            exit_price=exit_price,
            exit_size=position.current_size,
            exit_reason=exit_reason,
            strategy=position.strategy,
            stop_loss=position.stop_loss,
            take_profit=position.take_profit,
        )
        
        self.closed_trades.append(trade)
        del self.open_positions[position_id]
        
        logger.info(
            f"Closed {position.side} position: {position_id} "
            f"@ {exit_price} (P&L: {trade.pnl:.2f}, {trade.pnl_percent:.2f}%)"
        )
        
        return trade
    
    def update_position_price(self, position_id: str, current_price: float):
        """Update position current price."""
        if position_id in self.open_positions:
            self.open_positions[position_id].update_price(current_price)
    
    def update_trailing_stop(self, position_id: str, current_price: float):
        """Update trailing stop for position."""
        if position_id not in self.open_positions:
            return
        
        position = self.open_positions[position_id]
        initial_risk = abs(position.entry_price - position.stop_loss)
        
        if position.side == "LONG":
            # For long positions
            profit = current_price - position.entry_price
            
            # Activate trailing stop at 1.5x risk
            if profit >= initial_risk * 1.5 and position.trailing_stop is None:
                position.trailing_stop = position.entry_price
                logger.debug(f"Activated trailing stop at breakeven for {position_id}")
            
            # Move trailing stop to 50% profit at 3x risk
            if profit >= initial_risk * 3:
                new_stop = position.entry_price + (initial_risk * 1.5)
                if position.trailing_stop is None or new_stop > position.trailing_stop:
                    position.trailing_stop = new_stop
                    logger.debug(f"Moved trailing stop to 50% profit for {position_id}")
            
            # Move trailing stop to 75% profit at 5x risk
            if profit >= initial_risk * 5:
                new_stop = position.entry_price + (initial_risk * 3.75)
                if position.trailing_stop is None or new_stop > position.trailing_stop:
                    position.trailing_stop = new_stop
                    logger.debug(f"Moved trailing stop to 75% profit for {position_id}")
        
        else:  # SHORT
            # For short positions
            profit = position.entry_price - current_price
            
            # Activate trailing stop at 1.5x risk
            if profit >= initial_risk * 1.5 and position.trailing_stop is None:
                position.trailing_stop = position.entry_price
                logger.debug(f"Activated trailing stop at breakeven for {position_id}")
            
            # Move trailing stop to 50% profit at 3x risk
            if profit >= initial_risk * 3:
                new_stop = position.entry_price - (initial_risk * 1.5)
                if position.trailing_stop is None or new_stop < position.trailing_stop:
                    position.trailing_stop = new_stop
                    logger.debug(f"Moved trailing stop to 50% profit for {position_id}")
            
            # Move trailing stop to 75% profit at 5x risk
            if profit >= initial_risk * 5:
                new_stop = position.entry_price - (initial_risk * 3.75)
                if position.trailing_stop is None or new_stop < position.trailing_stop:
                    position.trailing_stop = new_stop
                    logger.debug(f"Moved trailing stop to 75% profit for {position_id}")
    
    def take_partial_profit(self, position_id: str, percentage: float) -> bool:
        """Close percentage of position to lock in profits."""
        if position_id not in self.open_positions:
            return False
        
        position = self.open_positions[position_id]
        close_size = position.current_size * (percentage / 100)
        
        if close_size <= 0:
            return False
        
        position.update_size(position.current_size - close_size)
        logger.info(f"Took partial profit: closed {close_size:.4f} from {position_id}")
        
        return True
    
    def check_exit_conditions(
        self,
        position_id: str,
        current_price: float,
        trend: str = "UNKNOWN",
        time_limit_minutes: int = 30,
    ) -> Optional[str]:
        """Check if position should be exited."""
        if position_id not in self.open_positions:
            return None
        
        position = self.open_positions[position_id]
        
        # Check stop loss
        if position.side == "LONG":
            if current_price <= position.stop_loss:
                return "STOP_LOSS"
        else:  # SHORT
            if current_price >= position.stop_loss:
                return "STOP_LOSS"
        
        # Check take profit
        if position.side == "LONG":
            if current_price >= position.take_profit:
                return "TAKE_PROFIT"
        else:  # SHORT
            if current_price <= position.take_profit:
                return "TAKE_PROFIT"
        
        # Check trailing stop
        if position.trailing_stop is not None:
            if position.side == "LONG":
                if current_price <= position.trailing_stop:
                    return "TRAILING_STOP"
            else:  # SHORT
                if current_price >= position.trailing_stop:
                    return "TRAILING_STOP"
        
        # Check trend reversal
        if trend == "DOWNTREND" and position.side == "LONG":
            return "TREND_REVERSAL"
        elif trend == "UPTREND" and position.side == "SHORT":
            return "TREND_REVERSAL"
        
        # Check time-based exit
        time_in_trade = datetime.now() - position.entry_time
        if time_in_trade > timedelta(minutes=time_limit_minutes):
            # Only exit if not profitable
            if position.unrealized_pnl <= 0:
                return "TIME_LIMIT"
        
        return None
    
    def get_open_positions(self) -> List[Position]:
        """Get all open positions."""
        return list(self.open_positions.values())
    
    def get_position_by_id(self, position_id: str) -> Optional[Position]:
        """Get position by ID."""
        return self.open_positions.get(position_id)
    
    def get_trade_history(self, limit: int = 100) -> List[Trade]:
        """Get recent closed trades."""
        return self.closed_trades[-limit:]
    
    def get_total_unrealized_pnl(self) -> float:
        """Get total unrealized P&L from all open positions."""
        return sum(p.unrealized_pnl for p in self.open_positions.values())
    
    def get_total_unrealized_pnl_percent(self) -> float:
        """Get total unrealized P&L percentage."""
        total_risk = sum(
            abs(p.entry_price - p.stop_loss) * p.current_size
            for p in self.open_positions.values()
        )
        
        if total_risk == 0:
            return 0.0
        
        return (self.get_total_unrealized_pnl() / total_risk) * 100
