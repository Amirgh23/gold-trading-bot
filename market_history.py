# ذخیره و بارگذاری تاریخچه بازار
import pandas as pd
import os
from datetime import datetime
from market_data import MarketDataProvider

class MarketHistory:
    """مدیریت تاریخچه بازار"""
    
    def __init__(self, filename='market_history.csv'):
        self.filename = filename
        self.data = None
        self.load_history()
    
    def load_history(self):
        """بارگذاری تاریخچه"""
        if os.path.exists(self.filename):
            self.data = pd.read_csv(self.filename, parse_dates=['timestamp'])
            print(f"✅ Loaded {len(self.data)} candles from history")
        else:
            self.data = pd.DataFrame()
            print("📝 No history found, starting fresh")
    
    def fetch_and_save(self, limit=500):
        """دریافت داده‌های تاریخی و ذخیره"""
        print(f"📊 Fetching {limit} candles from Binance...")
        
        provider = MarketDataProvider('binance')
        df = provider.get_ohlcv(limit=limit)
        
        if df is not None and len(df) > 0:
            # اضافه کردن timestamp
            df['timestamp'] = pd.to_datetime(df.index)
            df = df.reset_index(drop=True)
            
            # ذخیره
            self.data = df
            self.save_history()
            print(f"✅ Saved {len(df)} candles to {self.filename}")
            
            return df
        
        return None
    
    def save_history(self):
        """ذخیره تاریخچه"""
        if self.data is not None and len(self.data) > 0:
            self.data.to_csv(self.filename, index=False)
    
    def add_new_candle(self, candle_data):
        """اضافه کردن کندل جدید"""
        if self.data is None:
            self.data = pd.DataFrame([candle_data])
        else:
            self.data = pd.concat([self.data, pd.DataFrame([candle_data])], ignore_index=True)
        
        self.save_history()
    
    def get_data(self, limit=None):
        """دریافت داده‌ها"""
        if self.data is None or len(self.data) == 0:
            return None
        
        if limit:
            return self.data.tail(limit)
        return self.data
    
    def get_stats(self):
        """دریافت آمار"""
        if self.data is None or len(self.data) == 0:
            return None
        
        return {
            'total_candles': len(self.data),
            'start_time': self.data['timestamp'].min(),
            'end_time': self.data['timestamp'].max(),
            'min_price': self.data['low'].min(),
            'max_price': self.data['high'].max(),
            'avg_price': self.data['close'].mean(),
            'total_volume': self.data['volume'].sum()
        }

# تست
if __name__ == "__main__":
    print("="*60)
    print("Market History Manager")
    print("="*60)
    
    history = MarketHistory()
    
    # دریافت داده‌های تاریخی
    df = history.fetch_and_save(limit=500)
    
    if df is not None:
        # نمایش آمار
        stats = history.get_stats()
        print("\nMarket Statistics:")
        print(f"Total Candles: {stats['total_candles']}")
        print(f"Period: {stats['start_time']} to {stats['end_time']}")
        print(f"Price Range: ${stats['min_price']:.2f} - ${stats['max_price']:.2f}")
        print(f"Average Price: ${stats['avg_price']:.2f}")
        print(f"Total Volume: {stats['total_volume']:.2f}")
        
        # نمایش داده‌های اخیر
        print("\nRecent Candles:")
        print(df.tail(10))
