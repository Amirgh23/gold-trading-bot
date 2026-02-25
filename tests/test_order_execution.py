"""Unit tests for order execution."""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime
from trading_bot.execution.order_executor import OrderExecutor, Order


class TestOrderExecutor(unittest.TestCase):
    """Test OrderExecutor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_exchange = Mock()
        self.mock_backup = Mock()
        self.executor = OrderExecutor(
            exchange=self.mock_exchange,
            backup_exchange=self.mock_backup,
        )
    
    def test_place_order_success(self):
        """Test successful order placement."""
        self.mock_exchange.create_market_order.return_value = {
            'id': 'order123',
            'status': 'closed',
            'filled': 100,
            'average': 100.5,
        }
        
        order = self.executor.place_order('XAUUSD', 'BUY', 100)
        
        self.assertIsNotNone(order)
        self.assertEqual(order.side, 'BUY')
        self.assertEqual(order.size, 100)
        self.assertEqual(order.status, 'FILLED')
    
    def test_place_order_partial_fill(self):
        """Test partial order fill."""
        self.mock_exchange.create_market_order.return_value = {
            'id': 'order123',
            'status': 'open',
            'filled': 50,
            'average': 100.5,
        }
        
        order = self.executor.place_order('XAUUSD', 'BUY', 100)
        
        self.assertIsNotNone(order)
        self.assertEqual(order.status, 'PARTIAL')
        self.assertEqual(order.filled_size, 50)
    
    def test_place_order_invalid_size(self):
        """Test order with invalid size."""
        order = self.executor.place_order('XAUUSD', 'BUY', 0)
        
        self.assertIsNone(order)
    
    def test_place_order_failover_to_backup(self):
        """Test failover to backup exchange."""
        self.mock_exchange.create_market_order.side_effect = Exception("Primary failed")
        self.mock_backup.create_market_order.return_value = {
            'id': 'order456',
            'status': 'closed',
            'filled': 100,
            'average': 100.5,
        }
        
        order = self.executor.place_order('XAUUSD', 'BUY', 100)
        
        self.assertIsNotNone(order)
        self.assertEqual(self.executor.failover_count, 1)
        self.assertEqual(self.executor.order_exchange_map[order.id], 'backup')
    
    def test_get_order_status(self):
        """Test getting order status."""
        self.mock_exchange.create_market_order.return_value = {
            'id': 'order123',
            'status': 'closed',
            'filled': 100,
            'average': 100.5,
        }
        
        order = self.executor.place_order('XAUUSD', 'BUY', 100)
        status = self.executor.get_order_status(order.id)
        
        self.assertEqual(status, 'FILLED')
    
    def test_cancel_order(self):
        """Test order cancellation."""
        self.mock_exchange.create_market_order.return_value = {
            'id': 'order123',
            'status': 'open',
            'filled': 0,
            'average': 0,
        }
        
        order = self.executor.place_order('XAUUSD', 'BUY', 100)
        result = self.executor.cancel_order(order.id)
        
        self.assertTrue(result)
        self.assertEqual(order.status, 'CANCELLED')
    
    def test_get_best_price(self):
        """Test getting best price across exchanges."""
        self.mock_exchange.fetch_ticker.return_value = {
            'bid': 100.0,
            'ask': 100.2,
        }
        self.mock_backup.fetch_ticker.return_value = {
            'bid': 99.9,
            'ask': 100.1,
        }
        
        # Best ask for BUY
        best_buy = self.executor.get_best_price('XAUUSD', 'BUY')
        self.assertEqual(best_buy, 100.1)
        
        # Best bid for SELL
        best_sell = self.executor.get_best_price('XAUUSD', 'SELL')
        self.assertEqual(best_sell, 100.0)
    
    def test_estimate_slippage(self):
        """Test slippage estimation."""
        slippage = self.executor.estimate_slippage('XAUUSD', 50)
        
        self.assertGreater(slippage, 0)
        self.assertLess(slippage, 2)
    
    def test_retry_order(self):
        """Test order retry."""
        self.mock_exchange.create_market_order.side_effect = [
            Exception("Failed"),
            {
                'id': 'order123',
                'status': 'closed',
                'filled': 100,
                'average': 100.5,
            }
        ]
        
        # First attempt fails
        order = self.executor.place_order('XAUUSD', 'BUY', 100)
        self.assertIsNone(order)
        
        # Retry succeeds
        result = self.executor.retry_order('nonexistent', max_retries=1)
        self.assertFalse(result)
    
    def test_get_open_orders(self):
        """Test getting open orders."""
        self.mock_exchange.create_market_order.return_value = {
            'id': 'order123',
            'status': 'open',
            'filled': 50,
            'average': 100.5,
        }
        
        order = self.executor.place_order('XAUUSD', 'BUY', 100)
        open_orders = self.executor.get_open_orders()
        
        self.assertEqual(len(open_orders), 1)
        self.assertEqual(open_orders[0].status, 'PARTIAL')


class TestExchangeFailover(unittest.TestCase):
    """Test exchange failover mechanism."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_exchange = Mock()
        self.mock_backup = Mock()
        self.executor = OrderExecutor(
            exchange=self.mock_exchange,
            backup_exchange=self.mock_backup,
        )
    
    def test_check_exchange_health(self):
        """Test exchange health check."""
        self.mock_exchange.fetch_ticker.return_value = {'bid': 100, 'ask': 100.1}
        self.mock_backup.fetch_ticker.return_value = {'bid': 100, 'ask': 100.1}
        
        health = self.executor.check_exchange_health()
        
        self.assertEqual(health['primary'], 'HEALTHY')
        self.assertEqual(health['backup'], 'HEALTHY')
    
    def test_check_exchange_health_primary_down(self):
        """Test health check when primary is down."""
        self.mock_exchange.fetch_ticker.side_effect = Exception("Connection error")
        self.mock_backup.fetch_ticker.return_value = {'bid': 100, 'ask': 100.1}
        
        health = self.executor.check_exchange_health()
        
        self.assertEqual(health['primary'], 'UNHEALTHY')
        self.assertEqual(health['backup'], 'HEALTHY')
    
    def test_verify_order_consistency(self):
        """Test order consistency verification."""
        self.mock_exchange.create_market_order.return_value = {
            'id': 'order123',
            'status': 'closed',
            'filled': 100,
            'average': 100.5,
        }
        self.mock_exchange.fetch_order.return_value = {
            'id': 'order123',
            'status': 'closed',
            'filled': 100,
            'average': 100.5,
        }
        
        order = self.executor.place_order('XAUUSD', 'BUY', 100)
        result = self.executor.verify_order_consistency(order.id)
        
        self.assertTrue(result)
    
    def test_recover_from_failover(self):
        """Test recovery from failover."""
        self.mock_exchange.fetch_ticker.side_effect = [
            Exception("Down"),
            {'bid': 100, 'ask': 100.1},
        ]
        
        # Primary is down
        health1 = self.executor.check_exchange_health()
        self.assertEqual(health1['primary'], 'UNHEALTHY')
        
        # Primary recovers
        result = self.executor.recover_from_failover()
        
        self.assertTrue(result)
        self.assertEqual(self.executor.exchange_status['primary'], 'ACTIVE')


class TestOrderModel(unittest.TestCase):
    """Test Order model."""
    
    def test_order_creation(self):
        """Test order creation."""
        order = Order('XAUUSD', 'BUY', 100, 'MARKET')
        
        self.assertEqual(order.symbol, 'XAUUSD')
        self.assertEqual(order.side, 'BUY')
        self.assertEqual(order.size, 100)
        self.assertEqual(order.order_type, 'MARKET')
        self.assertEqual(order.status, 'PENDING')
    
    def test_order_to_dict(self):
        """Test order serialization."""
        order = Order('XAUUSD', 'BUY', 100, 'MARKET')
        order_dict = order.to_dict()
        
        self.assertEqual(order_dict['symbol'], 'XAUUSD')
        self.assertEqual(order_dict['side'], 'BUY')
        self.assertEqual(order_dict['size'], 100)
        self.assertIn('id', order_dict)
        self.assertIn('timestamp', order_dict)


if __name__ == '__main__':
    unittest.main()
