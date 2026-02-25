# دریافت داده‌های واقعی بازار
import ccxt
import pandas as pd
from datetime import datetime
from config import SYMBOL, TIMEFRAME

class MarketDataProvider:
    """دریافت داده‌های واقعی از صرافی"""
    
    def __init__(self, exchange_name='binance'):
        """
        راه‌اندازی اتصال به صرافی
        exchange_name: نام صرافی (binance, bybit, okx, etc.)
        """
        try:
            exchange_class = getattr(ccxt, exchange_name)
            self.exchange = exchange_class({
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'future',  # برای معاملات فیوچرز
                }
            })
            self.connected = True
            print(f"✅ اتصال به {exchange_name} برقرار شد")
        except Exception as e:
            print(f"❌ خطا در اتصال به صرافی: {e}")
            self.connected = False
    
    def get_symbol_for_exchange(self):
        """تبدیل نماد به فرمت صرافی"""
        # XAUUSD -> XAU/USDT برای Binance
        if SYMBOL == 'XAUUSD':
            return 'XAU/USDT'
        return SYMBOL
    
    def get_current_price(self):
        """دریافت قیمت فعلی"""
        if not self.connected:
            return None
        
        try:
            symbol = self.get_symbol_for_exchange()
            ticker = self.exchange.fetch_ticker(symbol)
            
            return {
                'symbol': symbol,
                'price': ticker.get('last', ticker.get('close', 0)),
                'bid': ticker.get('bid', 0),
                'ask': ticker.get('ask', 0),
                'high': ticker.get('high', 0),
                'low': ticker.get('low', 0),
                'volume': ticker.get('baseVolume', ticker.get('volume', 0)),
                'change': ticker.get('percentage', 0),
                'timestamp': datetime.now()
            }
        except Exception as e:
            print(f"❌ خطا در دریافت قیمت: {e}")
            return None
    
    def get_ohlcv(self, limit=100):
        """دریافت داده‌های OHLCV"""
        if not self.connected:
            return None
        
        try:
            symbol = self.get_symbol_for_exchange()
            ohlcv = self.exchange.fetch_ohlcv(symbol, TIMEFRAME, limit=limit)
            
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            return df
        except Exception as e:
            print(f"❌ خطا در دریافت OHLCV: {e}")
            return None
    
    def get_orderbook(self, limit=10):
        """دریافت دفترچه سفارشات"""
        if not self.connected:
            return None
        
        try:
            symbol = self.get_symbol_for_exchange()
            orderbook = self.exchange.fetch_order_book(symbol, limit)
            
            return {
                'bids': orderbook['bids'][:limit],
                'asks': orderbook['asks'][:limit],
                'timestamp': datetime.now()
            }
        except Exception as e:
            print(f"❌ خطا در دریافت orderbook: {e}")
            return None
    
    def test_connection(self):
        """تست اتصال"""
        print("🔍 تست اتصال به صرافی...")
        
        if not self.connected:
            print("❌ اتصال برقرار نیست")
            return False
        
        # دریافت قیمت
        price_data = self.get_current_price()
        if price_data:
            print(f"✅ قیمت فعلی {price_data['symbol']}: ${price_data['price']:.2f}")
            print(f"   تغییر 24 ساعته: {price_data['change']:.2f}%")
            return True
        
        return False

# تست اتصال
if __name__ == "__main__":
    print("="*60)
    print("🚀 تست اتصال به داده‌های واقعی بازار")
    print("="*60)
    
    provider = MarketDataProvider('binance')
    
    if provider.test_connection():
        print("\n📊 دریافت داده‌های OHLCV...")
        df = provider.get_ohlcv(limit=10)
        if df is not None:
            print(df.tail())
        
        print("\n📖 دریافت orderbook...")
        orderbook = provider.get_orderbook(limit=5)
        if orderbook:
            print(f"بهترین قیمت خرید: ${orderbook['bids'][0][0]:.2f}")
            print(f"بهترین قیمت فروش: ${orderbook['asks'][0][0]:.2f}")
