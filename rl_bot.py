# ربات معاملاتی با یادگیری تقویتی
import time
import pandas as pd
from datetime import datetime
from rl_strategy import DQNAgent, TradingEnvironment
from market_data import MarketDataProvider
from config import *

class RLTradingBot:
    """ربات معاملاتی با DQN"""
    
    def __init__(self, initial_balance=100):
        self.agent = DQNAgent(state_size=8, action_size=3)
        self.agent.load()  # بارگذاری مدل آموزش دیده
        
        self.market_data = MarketDataProvider('binance')
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.position = 0
        self.entry_price = 0
        self.trades = []
        self.is_running = False
    
    def prepare_state(self, df):
        """آماده‌سازی state برای ایجنت"""
        if len(df) < 14:
            return None
        
        # محاسبه اندیکاتورها
        df['ema_fast'] = df['close'].ewm(span=5, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=13, adjust=False).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # آخرین ردیف
        row = df.iloc[-1]
        
        state = [
            row['close'] / 10000,
            row['volume'] / 1000,
            row['rsi'] / 100 if not pd.isna(row['rsi']) else 0.5,
            row['ema_fast'] / 10000,
            row['ema_slow'] / 10000,
            self.position,
            self.balance / self.initial_balance,
            (row['close'] - self.entry_price) / 100 if self.entry_price > 0 else 0
        ]
        
        return state
    
    def execute_action(self, action, current_price):
        """اجرای اکشن"""
        action_names = ['HOLD', 'BUY', 'SELL']
        
        if action == 1 and self.position == 0:  # خرید
            self.position = 1
            self.entry_price = current_price
            cost = current_price * 0.001  # کمیسیون
            self.balance -= cost
            
            print(f"\n{'='*50}")
            print(f"🟢 خرید در قیمت: ${current_price:.2f}")
            print(f"💰 موجودی: ${self.balance:.2f}")
            print(f"{'='*50}\n")
            
            return True
            
        elif action == 2 and self.position == 1:  # فروش
            profit = current_price - self.entry_price
            profit_pct = (profit / self.entry_price) * 100
            
            cost = current_price * 0.001
            self.balance += profit - cost
            
            self.trades.append({
                'entry': self.entry_price,
                'exit': current_price,
                'profit': profit,
                'profit_pct': profit_pct,
                'timestamp': datetime.now()
            })
            
            print(f"\n{'='*50}")
            print(f"🔴 فروش در قیمت: ${current_price:.2f}")
            print(f"💵 سود/زیان: ${profit:.2f} ({profit_pct:+.2f}%)")
            print(f"💰 موجودی: ${self.balance:.2f}")
            print(f"📊 کل معاملات: {len(self.trades)}")
            print(f"{'='*50}\n")
            
            self.position = 0
            self.entry_price = 0
            
            return True
        
        return False
    
    def run(self):
        """اجرای ربات"""
        self.is_running = True
        
        print("="*60)
        print("🤖 ربات معاملاتی با یادگیری تقویتی")
        print("="*60)
        print(f"💰 سرمایه اولیه: ${self.initial_balance}")
        print(f"📊 نماد: {SYMBOL}")
        print(f"⏱️ تایم فریم: {TIMEFRAME}")
        print("="*60)
        
        if not self.market_data.connected:
            print("❌ اتصال به صرافی برقرار نیست")
            return
        
        print("✅ ربات شروع به کار کرد\n")
        
        while self.is_running:
            try:
                # دریافت داده‌ها
                df = self.market_data.get_ohlcv(limit=100)
                
                if df is not None and len(df) > 14:
                    current_price = df['close'].iloc[-1]
                    
                    # آماده‌سازی state
                    state = self.prepare_state(df)
                    
                    if state is not None:
                        # دریافت اکشن از ایجنت
                        action = self.agent.act(state, training=False)
                        
                        # اجرای اکشن
                        self.execute_action(action, current_price)
                    
                    # نمایش وضعیت
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                          f"قیمت: ${current_price:.2f} | "
                          f"پوزیشن: {'خرید' if self.position == 1 else 'خنثی'} | "
                          f"موجودی: ${self.balance:.2f}")
                
                # استراحت
                time.sleep(60)  # هر 1 دقیقه
                
            except KeyboardInterrupt:
                print("\n⏹️ توقف ربات توسط کاربر")
                self.is_running = False
            except Exception as e:
                print(f"❌ خطا: {e}")
                time.sleep(10)
        
        # نمایش نتایج نهایی
        self.show_results()
    
    def show_results(self):
        """نمایش نتایج"""
        print("\n" + "="*60)
        print("📊 نتایج نهایی")
        print("="*60)
        print(f"💰 سرمایه اولیه: ${self.initial_balance:.2f}")
        print(f"💵 موجودی نهایی: ${self.balance:.2f}")
        print(f"📈 سود/زیان کل: ${self.balance - self.initial_balance:.2f}")
        print(f"📊 تعداد معاملات: {len(self.trades)}")
        
        if len(self.trades) > 0:
            winning_trades = sum(1 for t in self.trades if t['profit'] > 0)
            win_rate = (winning_trades / len(self.trades)) * 100
            avg_profit = sum(t['profit'] for t in self.trades) / len(self.trades)
            
            print(f"✅ نرخ برد: {win_rate:.1f}%")
            print(f"💵 میانگین سود: ${avg_profit:.2f}")
        
        print("="*60)
    
    def stop(self):
        """توقف ربات"""
        self.is_running = False

if __name__ == "__main__":
    bot = RLTradingBot(initial_balance=100)
    bot.run()
