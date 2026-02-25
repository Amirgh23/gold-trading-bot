# ربات تریدر با یادگیری ماشین
import time
import pandas as pd
from datetime import datetime
from hybrid_strategy import HybridStrategy
from config import *

class MLGoldScalpBot:
    """ربات اسکلپ طلا با LSTM"""
    
    def __init__(self, use_ml=True):
        self.strategy = HybridStrategy(use_ml=use_ml)
        self.open_trades = []
        self.daily_pnl = 0
        self.is_running = False
        self.trade_history = []
        
    def get_market_data(self):
        """دریافت داده‌های بازار"""
        print(f"[{datetime.now()}] دریافت داده‌های {SYMBOL}...")
        # باید با API صرافی متصل شود
        pass
    
    def place_order(self, signal):
        """ثبت سفارش با اطلاعات ML"""
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
        source = signal.get('source', 'UNKNOWN')
        
        print(f"\n{'='*60}")
        print(f"🎯 سیگنال {order_type} - منبع: {source}")
        print(f"💰 قیمت: ${price:.2f}")
        print(f"🛑 استاپ لاس: ${sl:.2f}")
        print(f"✅ تیک پرافیت: ${tp:.2f}")
        
        if 'ml_confidence' in signal:
            print(f"🤖 اطمینان ML: {signal['ml_confidence']:.2%}")
        if 'ml_target' in signal:
            print(f"🎯 هدف ML: ${signal['ml_target']:.2f}")
        if signal.get('ml_warning'):
            print("⚠️ هشدار: ML با این سیگنال موافق نیست")
        
        print(f"{'='*60}\n")
        
        trade = {
            'type': order_type,
            'entry_price': price,
            'stop_loss': sl,
            'take_profit': tp,
            'size': POSITION_SIZE,
            'timestamp': datetime.now(),
            'source': source
        }
        self.open_trades.append(trade)
        return True
    
    def check_positions(self):
        """بررسی پوزیشن‌های باز"""
        for trade in self.open_trades[:]:
            pass
    
    def close_trade(self, trade, reason):
        """بستن معامله"""
        print(f"🔴 بستن معامله - دلیل: {reason}")
        self.trade_history.append({**trade, 'close_reason': reason})
        self.open_trades.remove(trade)
    
    def run(self):
        """اجرای ربات"""
        self.is_running = True
        print("🚀 ربات اسکلپ طلا با LSTM شروع به کار کرد")
        print(f"📊 نماد: {SYMBOL}")
        print(f"⏱️ تایم فریم: {TIMEFRAME}")
        print(f"🤖 استراتژی: ترکیبی (تحلیل تکنیکال + LSTM)")
        print(f"🧠 مدل: LSTM با {self.strategy.ml_model.lookback} کندل lookback")
        
        while self.is_running:
            try:
                data = self.get_market_data()
                
                if data is not None:
                    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    
                    signal = self.strategy.analyze(df)
                    
                    if signal:
                        self.place_order(signal)
                    
                    self.check_positions()
                
                time.sleep(120)
                
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
    bot = MLGoldScalpBot(use_ml=True)
    bot.run()
