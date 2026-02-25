"""Order execution engine with multi-exchange support."""

from typing import Optional, Tuple, Dict
from datetime import datetime
import logging
import time
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class Order:
    """Represents a trading order."""
    
    def __init__(
        self,
        symbol: str,
        side: str,
        size: float,
        order_type: str = "MARKET",
        price: Optional[float] = None,
    ):
        self.id = str(uuid.uuid4())
        self.symbol = symbol
        self.side = side  # BUY or SELL
        self.size = size
        self.order_type = order_type
        self.price = price
        self.filled_size = 0.0
        self.average_price = 0.0
        self.status = "PENDING"
        self.timestamp = datetime.now()
        self.exchange_order_id = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'side': self.side,
            'size': self.size,
            'filled_size': self.filled_size,
            'average_price': self.average_price,
            'status': self.status,
            'order_type': self.order_type,
            'price': self.price,
            'timestamp': self.timestamp.isoformat(),
        }


class OrderExecutor:
    """Executes orders on exchanges with optimal routing and failover."""
    
    def __init__(self, exchange=None, backup_exchange=None):
        self.exchange = exchange
        self.backup_exchange = backup_exchange
        self.orders: Dict[str, Order] = {}
        self.order_history = []
        self.exchange_status = {
            'primary': 'ACTIVE',
            'backup': 'ACTIVE' if backup_exchange else 'INACTIVE',
        }
        self.failover_count = 0
        self.order_exchange_map = {}  # Track which exchange each order was placed on
        self.executor = ThreadPoolExecutor(max_workers=4)  # For async operations
    
    def place_order(
        self,
        symbol: str,
        side: str,
        size: float,
        order_type: str = "MARKET",
        price: Optional[float] = None,
    ) -> Optional[Order]:
        """
        Place order on exchange with automatic failover.
        
        Args:
            symbol: Trading pair
            side: BUY or SELL
            size: Order size
            order_type: MARKET or LIMIT
            price: Price for limit orders
        
        Returns:
            Order object or None on failure
        """
        if size <= 0:
            logger.error("Invalid order size")
            return None
        
        order = Order(symbol, side, size, order_type, price)
        
        try:
            # Try primary exchange
            if self.exchange and self.exchange_status['primary'] == 'ACTIVE':
                exchange_order = self._execute_on_exchange(
                    self.exchange, order
                )
                if exchange_order:
                    order.exchange_order_id = exchange_order.get('id')
                    order.status = "FILLED" if exchange_order.get('status') == 'closed' else "PARTIAL"
                    order.filled_size = exchange_order.get('filled', 0)
                    order.average_price = exchange_order.get('average', 0)
                    
                    self.orders[order.id] = order
                    self.order_history.append(order)
                    self.order_exchange_map[order.id] = 'primary'
                    
                    logger.info(
                        f"Order placed on primary exchange: {side} {size} {symbol} "
                        f"@ {order.average_price} (Status: {order.status})"
                    )
                    return order
                else:
                    # Primary exchange failed
                    self.exchange_status['primary'] = 'FAILED'
                    logger.warning("Primary exchange failed, attempting failover")
            
            # Failover to backup exchange
            if self.backup_exchange and self.exchange_status['backup'] == 'ACTIVE':
                logger.warning("Switching to backup exchange")
                exchange_order = self._execute_on_exchange(
                    self.backup_exchange, order
                )
                if exchange_order:
                    order.exchange_order_id = exchange_order.get('id')
                    order.status = "FILLED" if exchange_order.get('status') == 'closed' else "PARTIAL"
                    order.filled_size = exchange_order.get('filled', 0)
                    order.average_price = exchange_order.get('average', 0)
                    
                    self.orders[order.id] = order
                    self.order_history.append(order)
                    self.order_exchange_map[order.id] = 'backup'
                    self.failover_count += 1
                    
                    logger.info(
                        f"Order placed on backup exchange: {order.id} "
                        f"(Failover #{self.failover_count})"
                    )
                    return order
            
            logger.error("Failed to place order on any exchange")
            return None
        
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None
    
    def _execute_on_exchange(self, exchange, order: Order) -> Optional[dict]:
        """Execute order on specific exchange."""
        try:
            if order.order_type == "MARKET":
                result = exchange.create_market_order(
                    order.symbol,
                    order.side.lower(),
                    order.size
                )
            else:  # LIMIT
                result = exchange.create_limit_order(
                    order.symbol,
                    order.side.lower(),
                    order.size,
                    order.price
                )
            
            return result
        except Exception as e:
            logger.error(f"Exchange execution error: {e}")
            return None
    
    def get_order_status(self, order_id: str) -> Optional[str]:
        """Get order status."""
        if order_id not in self.orders:
            return None
        
        return self.orders[order_id].status
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""
        if order_id not in self.orders:
            logger.warning(f"Order {order_id} not found")
            return False
        
        order = self.orders[order_id]
        
        try:
            if self.exchange and order.exchange_order_id:
                self.exchange.cancel_order(order.exchange_order_id, order.symbol)
                order.status = "CANCELLED"
                logger.info(f"Order cancelled: {order_id}")
                return True
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return False
    
    def get_best_price(self, symbol: str, side: str) -> Optional[float]:
        """Get best available price across exchanges."""
        prices = []
        
        if self.exchange:
            try:
                ticker = self.exchange.fetch_ticker(symbol)
                if side == "BUY":
                    prices.append(ticker.get('ask', 0))
                else:
                    prices.append(ticker.get('bid', 0))
            except Exception as e:
                logger.error(f"Error fetching price from primary exchange: {e}")
        
        if self.backup_exchange:
            try:
                ticker = self.backup_exchange.fetch_ticker(symbol)
                if side == "BUY":
                    prices.append(ticker.get('ask', 0))
                else:
                    prices.append(ticker.get('bid', 0))
            except Exception as e:
                logger.error(f"Error fetching price from backup exchange: {e}")
        
        if not prices:
            return None
        
        # Return best price (lowest for BUY, highest for SELL)
        if side == "BUY":
            return min(prices)
        else:
            return max(prices)
    
    def estimate_slippage(self, symbol: str, size: float) -> float:
        """Estimate slippage for order size."""
        # Simple slippage estimation: 0.5-1 pip based on size
        base_slippage = 0.5
        size_factor = min(size / 100, 0.5)  # Max 0.5 pip additional
        
        return base_slippage + size_factor
    
    def retry_order(
        self,
        order_id: str,
        max_retries: int = 3,
    ) -> bool:
        """Retry failed order with exponential backoff."""
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        
        for attempt in range(max_retries):
            try:
                wait_time = 2 ** attempt
                logger.info(f"Retrying order {order_id}, attempt {attempt + 1}")
                time.sleep(wait_time)
                
                # Try to place order again
                new_order = self.place_order(
                    order.symbol,
                    order.side,
                    order.size - order.filled_size,
                    order.order_type,
                    order.price,
                )
                
                if new_order and new_order.status in ["FILLED", "PARTIAL"]:
                    logger.info(f"Order retry successful: {new_order.id}")
                    return True
            
            except Exception as e:
                logger.error(f"Retry attempt {attempt + 1} failed: {e}")
        
        logger.error(f"Order retry failed after {max_retries} attempts")
        return False
    
    def get_order_history(self, limit: int = 100) -> list:
        """Get recent order history."""
        return self.order_history[-limit:]
    
    def get_open_orders(self) -> list:
        """Get all open orders."""
        return [
            order for order in self.orders.values()
            if order.status in ["PENDING", "PARTIAL"]
        ]
    
    def check_exchange_health(self) -> Dict[str, str]:
        """Check health of both exchanges."""
        health = {
            'primary': 'UNKNOWN',
            'backup': 'UNKNOWN',
        }
        
        try:
            if self.exchange:
                ticker = self.exchange.fetch_ticker('XAUUSD')
                health['primary'] = 'HEALTHY' if ticker else 'UNHEALTHY'
        except Exception as e:
            logger.warning(f"Primary exchange health check failed: {e}")
            health['primary'] = 'UNHEALTHY'
        
        try:
            if self.backup_exchange:
                ticker = self.backup_exchange.fetch_ticker('XAUUSD')
                health['backup'] = 'HEALTHY' if ticker else 'UNHEALTHY'
        except Exception as e:
            logger.warning(f"Backup exchange health check failed: {e}")
            health['backup'] = 'UNHEALTHY'
        
        # Update status based on health
        self.exchange_status['primary'] = 'ACTIVE' if health['primary'] == 'HEALTHY' else 'FAILED'
        self.exchange_status['backup'] = 'ACTIVE' if health['backup'] == 'HEALTHY' else 'FAILED'
        
        return health
    
    def verify_order_consistency(self, order_id: str) -> bool:
        """Verify order exists on the exchange it was placed on."""
        if order_id not in self.orders:
            logger.warning(f"Order {order_id} not found locally")
            return False
        
        order = self.orders[order_id]
        exchange_name = self.order_exchange_map.get(order_id, 'unknown')
        
        try:
            exchange = self.exchange if exchange_name == 'primary' else self.backup_exchange
            if not exchange or not order.exchange_order_id:
                return False
            
            remote_order = exchange.fetch_order(order.exchange_order_id, order.symbol)
            
            # Verify consistency
            if remote_order:
                if remote_order.get('filled', 0) != order.filled_size:
                    logger.warning(
                        f"Order {order_id} fill mismatch: "
                        f"local={order.filled_size}, remote={remote_order.get('filled', 0)}"
                    )
                    order.filled_size = remote_order.get('filled', 0)
                
                if remote_order.get('status') != order.status.lower():
                    logger.info(
                        f"Order {order_id} status update: "
                        f"{order.status} -> {remote_order.get('status')}"
                    )
                    order.status = remote_order.get('status').upper()
                
                return True
        except Exception as e:
            logger.error(f"Error verifying order consistency: {e}")
            return False
        
        return False
    
    def recover_from_failover(self) -> bool:
        """Attempt to recover primary exchange and sync orders."""
        logger.info("Attempting to recover from failover...")
        
        health = self.check_exchange_health()
        
        if health['primary'] == 'HEALTHY':
            logger.info("Primary exchange recovered")
            self.exchange_status['primary'] = 'ACTIVE'
            
            # Verify all orders are consistent
            for order_id in list(self.orders.keys()):
                self.verify_order_consistency(order_id)
            
            return True
        
        return False
    
    def place_order_async(
        self,
        symbol: str,
        side: str,
        size: float,
        order_type: str = "MARKET",
        price: Optional[float] = None,
    ) -> Optional[Order]:
        """
        Place order asynchronously for lower latency.
        
        Args:
            symbol: Trading pair
            side: BUY or SELL
            size: Order size
            order_type: MARKET or LIMIT
            price: Price for limit orders
        
        Returns:
            Order object or None on failure
        """
        # Use thread pool for async execution
        future = self.executor.submit(
            self.place_order,
            symbol,
            side,
            size,
            order_type,
            price,
        )
        
        try:
            # Wait with timeout for fast execution
            order = future.result(timeout=0.2)
            return order
        except Exception as e:
            logger.error(f"Async order placement failed: {e}")
            return None
    
    def shutdown(self) -> None:
        """Shutdown executor."""
        self.executor.shutdown(wait=False)
