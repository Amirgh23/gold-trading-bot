# استراتژی بهینه برای سرمایه پایین
import pandas as pd
import numpy as np

class LowCapitalStrategy:
    """
    استراتژی بهینه برای سرمایه پایین
    
    ویژگی‌ها:
    - ریسک بسیار پایین (0.5% در هر معامله)
    - نسبت ریسک به ریوارد 1:3
    - فقط معاملات با احتمال بالا
    - مدیریت سرمایه دقیق
    """
    
    def __init__(self, capital=100, risk_per_trade=0.005):
        self.capital = capital
        self.risk_per_trade = risk_per_trade  # 0.5% ریسک
        self.min_win_rate = 0.6  # حداقل 60% احتمال برد
        
    def calculate_position_size(self, entry_price, stop_loss):
        """محاسبه حجم معامله بر اساس ریسک"""
        risk_amount = self.capital * self.risk_per_trade
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk == 0:
            return 0
        
        position_size = risk_amount / price_risk
        return position_size
    
    def analyze(self, df):
        """تحلیل و تولید سیگنال"""
        if len(df) < 50:
            return None
        
        # محاسبه اندیکاتورها
        df['ema_5'] = df['close'].ewm(span=5, adjust=False).mean()
        df['ema_13'] = df['close'].ewm(span=13, adjust=False).mean()
        df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = df['ema_12'] - df['ema_26']
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        df['bb_std'] = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * 2)
        df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * 2)
        
        # آخرین مقادیر
        current = df.iloc[-1]
        previous = df.iloc[-2]
        
        # شرایط خرید (باید همه شرایط برقرار باشند)
        buy_conditions = [
            current['ema_5'] > current['ema_13'],  # روند صعودی کوتاه‌مدت
            current['ema_13'] > current['ema_50'],  # روند صعودی میان‌مدت
            current['rsi'] > 40 and current['rsi'] < 70,  # RSI در محدوده مناسب
            current['macd'] > current['signal'],  # MACD مثبت
            current['close'] > current['bb_lower'],  # بالای باند پایین
            current['close'] < current['bb_upper'],  # زیر باند بالا
            previous['ema_5'] <= previous['ema_13'],  # کراس اوور تازه
        ]
        
        # شرایط فروش
        sell_conditions = [
            current['ema_5'] < current['ema_13'],
            current['ema_13'] < current['ema_50'],
            current['rsi'] > 30 and current['rsi'] < 60,
            current['macd'] < current['signal'],
            current['close'] < current['bb_upper'],
            current['close'] > current['bb_lower'],
            previous['ema_5'] >= previous['ema_13'],
        ]
        
        # سیگنال خرید
        if sum(buy_conditions) >= 5:  # حداقل 5 شرط برقرار باشد
            atr = df['close'].rolling(window=14).std().iloc[-1]
            stop_loss = current['close'] - (atr * 1.5)
            take_profit = current['close'] + (atr * 4.5)  # نسبت 1:3
            
            position_size = self.calculate_position_size(current['close'], stop_loss)
            
            return {
                'signal': 'BUY',
                'price': current['close'],
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'position_size': position_size,
                'confidence': sum(buy_conditions) / len(buy_conditions),
                'risk_reward': 3.0,
                'indicators': {
                    'rsi': current['rsi'],
                    'macd': current['macd'],
                    'ema_5': current['ema_5'],
                    'ema_13': current['ema_13']
                }
            }
        
        # سیگنال فروش
        if sum(sell_conditions) >= 5:
            atr = df['close'].rolling(window=14).std().iloc[-1]
            stop_loss = current['close'] + (atr * 1.5)
            take_profit = current['close'] - (atr * 4.5)
            
            position_size = self.calculate_position_size(current['close'], stop_loss)
            
            return {
                'signal': 'SELL',
                'price': current['close'],
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'position_size': position_size,
                'confidence': sum(sell_conditions) / len(sell_conditions),
                'risk_reward': 3.0,
                'indicators': {
                    'rsi': current['rsi'],
                    'macd': current['macd'],
                    'ema_5': current['ema_5'],
                    'ema_13': current['ema_13']
                }
            }
        
        return None
    
    def update_capital(self, new_capital):
        """به‌روزرسانی سرمایه"""
        self.capital = new_capital
