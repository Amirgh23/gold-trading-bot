"""Unit tests for market data layer."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from datetime import datetime
from trading_bot.market.provider import MarketDataProvider
from trading_bot.market.cache import DataCache


class TestMarketDataProvider(unittest.TestCase):
    """Test MarketDataProvider."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_exchange = Mock()
        self.provider = MarketDataProvider(exchange=self.mock_exchange)
    
    def test_get_ohlcv_success(self):
        """Test successful OHLCV data fetching."""
        mock_data = [
            [1000, 100, 99, 100.5, 50],
            [2000, 100.5, 99.5, 101, 60],
        ]
        self.mock_exchange.fetch_ohlcv.return_value = mock_data
        
        result = self.provider.get_ohlcv('XAUUSD', '2m', 2)
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.mock_exchange.fetch_ohlcv.assert_called_once()
    
    def test_get_ohlcv_with_retry(self):
        """Test OHLCV fetching with retry on failure."""
        self.mock_exchange.fetch_ohlcv.side_effect = [
            Exception("Connection error"),
            [[1000, 100, 99, 100.5, 50]],
        ]
        
        result = self.provider.get_ohlcv('XAUUSD', '2m', 1)
        
        self.assertIsNotNone(result)
        self.assertEqual(self.mock_exchange.fetch_ohlcv.call_count, 2)
    
    def test_get_current_price(self):
        """Test getting current price."""
        self.mock_exchange.fetch_ticker.return_value = {
            'bid': 100.0,
            'ask': 100.1,
            'last': 100.05,
        }
        
        price = self.provider.get_current_price('XAUUSD')
        
        self.assertEqual(price, 100.05)
    
    def test_get_bid_ask(self):
        """Test getting bid/ask prices."""
        self.mock_exchange.fetch_ticker.return_value = {
            'bid': 100.0,
            'ask': 100.1,
        }
        
        bid, ask = self.provider.get_bid_ask('XAUUSD')
        
        self.assertEqual(bid, 100.0)
        self.assertEqual(ask, 100.1)
    
    def test_get_bid_ask_with_fallback(self):
        """Test bid/ask with fallback on error."""
        self.mock_exchange.fetch_ticker.side_effect = Exception("API error")
        
        bid, ask = self.provider.get_bid_ask('XAUUSD')
        
        self.assertIsNone(bid)
        self.assertIsNone(ask)


class TestDataCache(unittest.TestCase):
    """Test DataCache."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.cache = DataCache(ttl_seconds=60)
    
    def test_cache_set_and_get(self):
        """Test caching data."""
        data = pd.DataFrame({'close': [100, 101, 102]})
        
        self.cache.set('XAUUSD_2m', data)
        cached = self.cache.get('XAUUSD_2m')
        
        self.assertIsNotNone(cached)
        pd.testing.assert_frame_equal(cached, data)
    
    def test_cache_miss(self):
        """Test cache miss."""
        result = self.cache.get('nonexistent')
        
        self.assertIsNone(result)
    
    def test_cache_expiration(self):
        """Test cache expiration."""
        data = pd.DataFrame({'close': [100, 101, 102]})
        
        self.cache.set('XAUUSD_2m', data)
        
        # Manually expire the cache
        self.cache.cache['XAUUSD_2m']['timestamp'] = datetime.now().timestamp() - 120
        
        result = self.cache.get('XAUUSD_2m')
        
        self.assertIsNone(result)
    
    def test_cache_clear(self):
        """Test clearing cache."""
        data = pd.DataFrame({'close': [100, 101, 102]})
        
        self.cache.set('XAUUSD_2m', data)
        self.cache.clear()
        
        result = self.cache.get('XAUUSD_2m')
        
        self.assertIsNone(result)
    
    def test_cache_size_limit(self):
        """Test cache size limit."""
        cache = DataCache(max_size=2)
        
        cache.set('key1', pd.DataFrame({'a': [1]}))
        cache.set('key2', pd.DataFrame({'b': [2]}))
        cache.set('key3', pd.DataFrame({'c': [3]}))
        
        # First key should be evicted
        self.assertIsNone(cache.get('key1'))
        self.assertIsNotNone(cache.get('key2'))
        self.assertIsNotNone(cache.get('key3'))


class TestDataFallback(unittest.TestCase):
    """Test fallback mechanisms."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_exchange = Mock()
        self.provider = MarketDataProvider(exchange=self.mock_exchange)
    
    def test_fallback_to_cache(self):
        """Test fallback to cache when API fails."""
        # First call succeeds
        mock_data = [[1000, 100, 99, 100.5, 50]]
        self.mock_exchange.fetch_ohlcv.return_value = mock_data
        
        result1 = self.provider.get_ohlcv('XAUUSD', '2m', 1)
        self.assertIsNotNone(result1)
        
        # Second call fails but should return cached data
        self.mock_exchange.fetch_ohlcv.side_effect = Exception("API error")
        
        result2 = self.provider.get_ohlcv('XAUUSD', '2m', 1)
        
        # Should return cached data
        self.assertIsNotNone(result2)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in market data layer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_exchange = Mock()
        self.provider = MarketDataProvider(exchange=self.mock_exchange)
    
    def test_handle_connection_error(self):
        """Test handling connection errors."""
        self.mock_exchange.fetch_ohlcv.side_effect = ConnectionError("Network error")
        
        result = self.provider.get_ohlcv('XAUUSD', '2m', 1)
        
        # Should return None or cached data
        self.assertTrue(result is None or isinstance(result, (list, pd.DataFrame)))
    
    def test_handle_invalid_symbol(self):
        """Test handling invalid symbols."""
        self.mock_exchange.fetch_ohlcv.side_effect = Exception("Invalid symbol")
        
        result = self.provider.get_ohlcv('INVALID', '2m', 1)
        
        self.assertIsNone(result)
    
    def test_handle_rate_limit(self):
        """Test handling rate limiting."""
        self.mock_exchange.fetch_ohlcv.side_effect = Exception("Rate limit exceeded")
        
        result = self.provider.get_ohlcv('XAUUSD', '2m', 1)
        
        # Should handle gracefully
        self.assertTrue(result is None or isinstance(result, (list, pd.DataFrame)))


if __name__ == '__main__':
    unittest.main()
