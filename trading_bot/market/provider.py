"""Market data provider with multi-exchange support."""

import pandas as pd
from typing import Optional, Tuple
import logging
import time

logger = logging.getLogger(__name__)


class MarketDataProvider:
    """Fetches and manages real-time market data from exchanges."""
    
    def __init__(self, exchange_name: str = "binance", symbol: str = "XAUUSD"):
        self.exchange_name = exchange_name
        self.symbol = symbol
        self.exchange = None
        self._initialize_exchange()
    
    def _initialize_exchange(self):
        """Initialize exchange connection."""
        try:
            import ccxt
            exchange_class = getattr(ccxt, self.exchange_name)
            self.exchange = exchange_class({
                'enableRateLimit': True,
                'timeout': 30000,
            })
            logger.info(f"Initialized {self.exchange_name} exchange")
        except Exception as e:
            logger.error(f"Error initializing exchange: {e}")
            raise
    
    def get_ohlcv(
        self,
        symbol: str = None,
        timeframe: str = "2m",
        limit: int = 100
    ) -> Optional[pd.DataFrame]:
        """
        Fetch OHLCV data from exchange.
        
        Args:
            symbol: Trading pair (default: self.symbol)
            timeframe: Candlestick period
            limit: Number of candles to fetch
        
        Returns:
            DataFrame with OHLCV data or None on error
        """
        symbol = symbol or self.symbol
        
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            logger.debug(f"Fetched {len(df)} candles for {symbol}")
            return df
        except Exception as e:
            logger.error(f"Error fetching OHLCV data: {e}")
            return None
    
    def get_current_price(self, symbol: str = None) -> Optional[float]:
        """Get current price for symbol."""
        symbol = symbol or self.symbol
        
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            price = ticker['last']
            logger.debug(f"Current price for {symbol}: {price}")
            return price
        except Exception as e:
            logger.error(f"Error fetching current price: {e}")
            return None
    
    def get_bid_ask(self, symbol: str = None) -> Optional[Tuple[float, float]]:
        """Get bid and ask prices."""
        symbol = symbol or self.symbol
        
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            bid = ticker['bid']
            ask = ticker['ask']
            logger.debug(f"Bid/Ask for {symbol}: {bid}/{ask}")
            return (bid, ask)
        except Exception as e:
            logger.error(f"Error fetching bid/ask: {e}")
            return None
    
    def get_spread(self, symbol: str = None) -> Optional[float]:
        """Get bid-ask spread in pips."""
        bid_ask = self.get_bid_ask(symbol)
        if not bid_ask:
            return None
        
        bid, ask = bid_ask
        spread = ask - bid
        logger.debug(f"Spread for {symbol}: {spread}")
        return spread
    
    def reconnect_with_backoff(self, max_retries: int = 5):
        """Reconnect with exponential backoff."""
        for attempt in range(max_retries):
            try:
                self._initialize_exchange()
                logger.info("Reconnection successful")
                return True
            except Exception as e:
                wait_time = 2 ** attempt
                logger.warning(f"Reconnection attempt {attempt + 1} failed, retrying in {wait_time}s")
                time.sleep(wait_time)
        
        logger.error("Failed to reconnect after max retries")
        return False
