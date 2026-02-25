"""Specialized logging for trades and signals."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from trading_bot.models.trade import Trade
from trading_bot.models.signal import Signal

logger = logging.getLogger(__name__)


class TradeLogger:
    """Logs all trades with complete details in JSON format."""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.trade_log_file = self.log_dir / "trades.json"
        self.signal_log_file = self.log_dir / "signals.json"
        self.error_log_file = self.log_dir / "errors.json"
    
    def log_trade(self, trade: Trade) -> bool:
        """Log completed trade."""
        try:
            trade_data = {
                'timestamp': datetime.now().isoformat(),
                'trade_id': trade.id,
                'symbol': trade.symbol,
                'entry_time': trade.entry_time.isoformat(),
                'entry_price': trade.entry_price,
                'entry_size': trade.entry_size,
                'entry_reason': trade.entry_reason,
                'exit_time': trade.exit_time.isoformat() if trade.exit_time else None,
                'exit_price': trade.exit_price,
                'exit_size': trade.exit_size,
                'exit_reason': trade.exit_reason,
                'pnl': trade.pnl,
                'pnl_percent': trade.pnl_percent,
                'strategy': trade.strategy,
                'stop_loss': trade.stop_loss,
                'take_profit': trade.take_profit,
                'max_profit': trade.max_profit,
                'max_loss': trade.max_loss,
                'duration_seconds': trade.duration_seconds,
            }
            
            self._append_json_log(self.trade_log_file, trade_data)
            logger.info(f"Trade logged: {trade.id} - P&L: {trade.pnl:.2f}")
            return True
        except Exception as e:
            logger.error(f"Error logging trade: {e}")
            return False
    
    def log_signal(
        self,
        signal: Signal,
        indicators: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Log trading signal with confidence and indicators."""
        try:
            signal_data = {
                'timestamp': datetime.now().isoformat(),
                'signal_id': signal.id,
                'symbol': signal.symbol,
                'direction': signal.direction,
                'strategy': signal.strategy,
                'confidence': signal.confidence,
                'entry_price': signal.entry_price,
                'stop_loss': signal.stop_loss,
                'take_profit': signal.take_profit,
                'reason': signal.reason,
                'indicators': indicators or {},
            }
            
            self._append_json_log(self.signal_log_file, signal_data)
            logger.debug(f"Signal logged: {signal.strategy} {signal.direction} (confidence: {signal.confidence:.1f}%)")
            return True
        except Exception as e:
            logger.error(f"Error logging signal: {e}")
            return False
    
    def log_error(
        self,
        error_type: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        stack_trace: Optional[str] = None,
    ) -> bool:
        """Log error with context and stack trace."""
        try:
            error_data = {
                'timestamp': datetime.now().isoformat(),
                'error_type': error_type,
                'message': message,
                'context': context or {},
                'stack_trace': stack_trace,
            }
            
            self._append_json_log(self.error_log_file, error_data)
            logger.error(f"Error logged: {error_type} - {message}")
            return True
        except Exception as e:
            logger.error(f"Error logging error: {e}")
            return False
    
    def _append_json_log(self, log_file: Path, data: Dict[str, Any]) -> None:
        """Append JSON data to log file."""
        try:
            # Read existing logs
            logs = []
            if log_file.exists():
                with open(log_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            logs.append(json.loads(line))
            
            # Append new log
            logs.append(data)
            
            # Keep only last 10000 entries
            if len(logs) > 10000:
                logs = logs[-10000:]
            
            # Write back
            with open(log_file, 'w') as f:
                for log in logs:
                    f.write(json.dumps(log) + '\n')
        except Exception as e:
            logger.error(f"Error appending to log file: {e}")
    
    def get_recent_trades(self, limit: int = 100) -> list:
        """Get recent trades from log."""
        try:
            if not self.trade_log_file.exists():
                return []
            
            trades = []
            with open(self.trade_log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        trades.append(json.loads(line))
            
            return trades[-limit:]
        except Exception as e:
            logger.error(f"Error reading trades: {e}")
            return []
    
    def get_recent_signals(self, limit: int = 100) -> list:
        """Get recent signals from log."""
        try:
            if not self.signal_log_file.exists():
                return []
            
            signals = []
            with open(self.signal_log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        signals.append(json.loads(line))
            
            return signals[-limit:]
        except Exception as e:
            logger.error(f"Error reading signals: {e}")
            return []
    
    def get_recent_errors(self, limit: int = 100) -> list:
        """Get recent errors from log."""
        try:
            if not self.error_log_file.exists():
                return []
            
            errors = []
            with open(self.error_log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        errors.append(json.loads(line))
            
            return errors[-limit:]
        except Exception as e:
            logger.error(f"Error reading errors: {e}")
            return []
