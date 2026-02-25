# ربات تریدر اصلی
import time
import pandas as pd
from datetime import datetime
from strategy import FastScalpStrategy
from config import *

class GoldScalpBot:
    """ربات اسکلپ انس طلا"""
    
    def __init__(self):
        self.strategy = FastScalpStrategy()
        self.open_trades = []
        self.daily_pnl = 0
        self.is_running = False
        
    def get_market_data(self):
        """دریافت داده‌های بازار (باید با API صرافی متصل شود)"""
        # این تابع باید با API صرافی شما متصل شود
        # مثال: MetaTrader 5, Binance, etc.
        print(f"[{datetime.now()}] دریافت داده‌های {SYMBOL}...")
        
        # نمونه داده (در پروژه واقعی از API استفاده کنید)
        # return exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=50)
        pass
    
    def place_order(self, signal):
        """ثبت سفارش"""
        if len(self.open_trades) >= MAX_OPEN_TRADES:
            print("⚠️ حداکثر تعداد معاملات همزمان")
            return False
        
        if abs(self.daily_pnl) >= MAX_DAILY_LOSS:
            print("⚠️ حد ضرر روزانه")
            return False
        
        order_type = signal['signal']
        price = signal['price']
        sl = signal['stop_loss']
        tp = signal['take_profit']
        
        print(f"\n{'='*50}")
        print(f"🎯 سیگنال {order_type}")
        print(f"💰 قیمت: {price}")
        print(f"🛑 استاپ لاس: {sl}")
        print(f"✅ تیک پرافیت: {tp}")
        print(f"{'='*50}\n")
        
        # ثبت سفارش در صرافی (باید پیاده‌سازی شود)
        # order = exchange.create_order(SYMBOL, 'market', order_type.lower(), POSITION_SIZE)
        
        trade = {
            'type': order_type,
            'entry_price': price,
            'stop_loss': sl,
            'take_profit': tp,
            'size': POSITION_SIZE,
            'timestamp': datetime.now()
        }
        self.open_trades.append(trade)
        return True

    def check_positions(self):
        """بررسی و مدیریت پوزیشن‌های باز"""
        for trade in self.open_trades[:]:
            # بررسی استاپ لاس و تیک پرافیت
            # current_price = self.get_current_price()
            # if trade['type'] == 'BUY':
            #     if current_price <= trade['stop_loss']:
            #         self.close_trade(trade, 'STOP_LOSS')
            #     elif current_price >= trade['take_profit']:
            #         self.close_trade(trade, 'TAKE_PROFIT')
            pass
    
    def close_trade(self, trade, reason):
        """بستن معامله"""
        print(f"🔴 بستن معامله - دلیل: {reason}")
        self.open_trades.remove(trade)
    
    def run(self):
        """اجرای ربات"""
        self.is_running = True
        print("🚀 ربات اسکلپ طلا شروع به کار کرد")
        print(f"📊 نماد: {SYMBOL}")
        print(f"⏱️ تایم فریم: {TIMEFRAME}")
        print(f"💎 استراتژی: فست اسکلپ (EMA {FAST_EMA}/{SLOW_EMA} + RSI {RSI_PERIOD})")
        
        while self.is_running:
            try:
                # دریافت داده‌های بازار
                data = self.get_market_data()
                
                if data is not None:
                    # تبدیل به DataFrame
                    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    
                    # تحلیل و دریافت سیگنال
                    signal = self.strategy.analyze(df)
                    
                    if signal:
                        self.place_order(signal)
                    
                    # بررسی پوزیشن‌های باز
                    self.check_positions()
                
                # استراحت تا کندل بعدی
                time.sleep(120)  # 2 دقیقه
                
            except KeyboardInterrupt:
                print("\n⏹️ توقف ربات توسط کاربر")
                self.is_running = False
            except Exception as e:
                print(f"❌ خطا: {e}")
                time.sleep(10)
    
    def stop(self):
        """توقف ربات"""
        self.is_running = False
        print("ربات متوقف شد")

if __name__ == "__main__":
    bot = GoldScalpBot()
    bot.run()
