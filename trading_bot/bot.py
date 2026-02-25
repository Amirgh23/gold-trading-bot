"""Main trading bot orchestrator."""

import logging
from datetime import datetime
from typing import Optional, List
import pandas as pd

from trading_bot.core.config import ConfigManager
from trading_bot.core.database import DatabaseManager
from trading_bot.core.logger import setup_logger
from trading_bot.market.provider import MarketDataProvider
from trading_bot.market.cache import DataCache
from trading_bot.indicators.engine import IndicatorEngine
from trading_bot.strategies.ensemble import EnsembleRouter
from trading_bot.risk.manager import RiskManager
from trading_bot.execution.position_manager import PositionManager
from trading_bot.execution.order_executor import OrderExecutor
from trading_bot.analysis.multi_timeframe import MultiTimeframeAnalyzer
from trading_bot.analytics.engine import AnalyticsEngine

logger = setup_logger(__name__)


class TradingBot:
    """Main trading bot orchestrator."""
    
    def __init__(self, config_file: str = "config.json"):
        """Initialize trading bot."""
        logger.info("Initializing Trading Bot...")
        
        # Load configuration
        self.config = ConfigManager(config_file)
        self.config.validate()
        
        # Initialize components
        self.db = DatabaseManager()
        self.market_data = MarketDataProvider(
            self.config.exchange.exchange,
            self.config.exchange.symbol,
        )
        self.cache = DataCache(ttl_minutes=60)
        
        self.risk_manager = RiskManager(
            account_equity=10000,  # Default, will be updated
            max_position_size_percent=self.config.risk.max_position_size_percent,
            max_concurrent_positions=self.config.risk.max_concurrent_positions,
            max_drawdown_percent=self.config.risk.max_drawdown_percent,
            daily_loss_limit_percent=self.config.risk.daily_loss_limit_percent,
            kelly_fraction=self.config.risk.kelly_fraction,
        )
        
        self.position_manager = PositionManager()
        self.order_executor = OrderExecutor()
        self.ensemble_router = EnsembleRouter()
        self.multi_timeframe = MultiTimeframeAnalyzer()
        
        self.is_running = False
        logger.info("Trading Bot initialized successfully")
    
    def start(self):
        """Start trading bot."""
        logger.info("Starting Trading Bot...")
        self.is_running = True
        
        try:
            self._trading_loop()
        except KeyboardInterrupt:
            logger.info("Trading bot stopped by user")
        except Exception as e:
            logger.error(f"Trading bot error: {e}", exc_info=True)
        finally:
            self.stop()
    
    def stop(self):
        """Stop trading bot."""
        logger.info("Stopping Trading Bot...")
        self.is_running = False
        
        # Close all positions
        for position in self.position_manager.get_open_positions():
            current_price = self.market_data.get_current_price()
            if current_price:
                self.position_manager.close_position(
                    position.id,
                    current_price,
                    "BOT_SHUTDOWN",
                )
        
        # Close database
        self.db.close()
        logger.info("Trading Bot stopped")
    
    def _trading_loop(self):
        """Main trading loop."""
        while self.is_running:
            try:
                # Fetch market data
                df = self.market_data.get_ohlcv(
                    self.config.exchange.symbol,
                    self.config.exchange.timeframe,
                    limit=200,
                )
                
                if df is None or len(df) < 50:
                    logger.warning("Insufficient market data")
                    continue
                
                # Calculate indicators
                df = IndicatorEngine.calculate_all(df)
                
                # Get current price
                current_price = df['close'].iloc[-1]
                
                # Update position prices
                for position in self.position_manager.get_open_positions():
                    self.position_manager.update_position_price(position.id, current_price)
                    self.position_manager.update_trailing_stop(position.id, current_price)
                
                # Check exit conditions
                self._check_exits(current_price)
                
                # Generate signals
                signals = self._generate_signals(df)
                
                # Route through ensemble
                if signals:
                    ensemble_signal = self.ensemble_router.route_signal(
                        signals,
                        volatility=IndicatorEngine.calculate_volatility(df),
                        confirmation_threshold=self.config.strategy.confirmation_threshold,
                        high_volatility_threshold=self.config.strategy.high_volatility_threshold,
                    )
                    
                    if ensemble_signal:
                        self._execute_signal(ensemble_signal, current_price)
                
                # Log metrics
                self._log_metrics()
            
            except Exception as e:
                logger.error(f"Error in trading loop: {e}", exc_info=True)
    
    def _generate_signals(self, df: pd.DataFrame) -> List:
        """Generate signals from strategies."""
        signals = []
        
        # Technical analysis signal
        if self.config.strategy.technical_enabled:
            signal = self._technical_signal(df)
            if signal:
                signals.append(signal)
        
        # LSTM signal
        if self.config.strategy.lstm_enabled:
            signal = self._lstm_signal(df)
            if signal:
                signals.append(signal)
        
        # DQN signal
        if self.config.strategy.dqn_enabled:
            signal = self._dqn_signal(df)
            if signal:
                signals.append(signal)
        
        return signals
    
    def _technical_signal(self, df: pd.DataFrame):
        """Generate technical analysis signal."""
        if len(df) < 20:
            return None
        
        ema_5 = df['ema_5'].iloc[-1]
        ema_13 = df['ema_13'].iloc[-1]
        rsi = df['rsi'].iloc[-1]
        atr = df['atr'].iloc[-1]
        close = df['close'].iloc[-1]
        
        # BUY signal
        if ema_5 > ema_13 and rsi < 70 and rsi > 40:
            from trading_bot.models.signal import Signal
            return Signal(
                timestamp=datetime.now(),
                symbol=self.config.exchange.symbol,
                direction="BUY",
                strategy="TECHNICAL",
                confidence=60.0,
                entry_price=close,
                stop_loss=close - (atr * 2),
                take_profit=close + (atr * 3),
                reason="EMA crossover + RSI confirmation",
            )
        
        # SELL signal
        if ema_5 < ema_13 and rsi > 30 and rsi < 60:
            from trading_bot.models.signal import Signal
            return Signal(
                timestamp=datetime.now(),
                symbol=self.config.exchange.symbol,
                direction="SELL",
                strategy="TECHNICAL",
                confidence=60.0,
                entry_price=close,
                stop_loss=close + (atr * 2),
                take_profit=close - (atr * 3),
                reason="EMA crossover + RSI confirmation",
            )
        
        return None
    
    def _lstm_signal(self, df: pd.DataFrame):
        """Generate LSTM signal (placeholder)."""
        # TODO: Implement LSTM signal generation
        return None
    
    def _dqn_signal(self, df: pd.DataFrame):
        """Generate DQN signal (placeholder)."""
        # TODO: Implement DQN signal generation
        return None
    
    def _execute_signal(self, ensemble_signal, current_price: float):
        """Execute ensemble signal."""
        # Calculate position size
        position_size = self.risk_manager.calculate_position_size(
            ensemble_signal.entry_price,
            ensemble_signal.stop_loss,
        )
        
        # Check risk limits
        if not self.risk_manager.check_risk_limits(
            position_size,
            self.risk_manager.get_current_drawdown(),
            len(self.position_manager.get_open_positions()),
        ):
            logger.warning("Position rejected due to risk limits")
            return
        
        # Open position
        position = self.position_manager.open_position(
            ensemble_signal.to_signal(),
            position_size,
        )
        
        if position:
            # Save signal to database
            self.db.save_signal(ensemble_signal.to_signal().to_dict())
            logger.info(f"Signal executed: {ensemble_signal.recommendation}")
    
    def _check_exits(self, current_price: float):
        """Check exit conditions for all positions."""
        for position in self.position_manager.get_open_positions():
            exit_reason = self.position_manager.check_exit_conditions(
                position.id,
                current_price,
            )
            
            if exit_reason:
                trade = self.position_manager.close_position(
                    position.id,
                    current_price,
                    exit_reason,
                )
                
                if trade:
                    self.db.save_trade(trade.to_dict())
                    logger.info(f"Position closed: {exit_reason} (P&L: {trade.pnl:.2f})")
    
    def _log_metrics(self):
        """Log current metrics."""
        open_positions = self.position_manager.get_open_positions()
        total_unrealized = self.position_manager.get_total_unrealized_pnl()
        
        logger.debug(
            f"Open positions: {len(open_positions)}, "
            f"Unrealized P&L: {total_unrealized:.2f}, "
            f"Drawdown: {self.risk_manager.get_current_drawdown():.2f}%"
        )
    
    def get_status(self) -> dict:
        """Get bot status."""
        return {
            'is_running': self.is_running,
            'open_positions': len(self.position_manager.get_open_positions()),
            'total_trades': len(self.position_manager.closed_trades),
            'account_equity': self.risk_manager.account_equity,
            'unrealized_pnl': self.position_manager.get_total_unrealized_pnl(),
            'drawdown': self.risk_manager.get_current_drawdown(),
        }
