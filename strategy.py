# استراتژی فست اسکلپ برای انس طلا
import pandas as pd
import numpy as np
from config import *

class FastScalpStrategy:
    """استراتژی فست اسکلپ با EMA و RSI"""
    
    def __init__(self):
        self.fast_ema = FAST_EMA
        self.slow_ema = SLOW_EMA
        self.rsi_period = RSI_PERIOD
        
    def calculate_ema(self, data, period):
        """محاسبه EMA"""
        return data['close'].ewm(span=period, adjust=False).mean()
    
    def calculate_rsi(self, data, period):
        """محاسبه RSI"""
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def analyze(self, df):
        """تحلیل داده‌ها و تولید سیگنال"""
        if len(df) < max(self.slow_ema, self.rsi_period):
            return None
        
        # محاسبه اندیکاتورها
        df['ema_fast'] = self.calculate_ema(df, self.fast_ema)
        df['ema_slow'] = self.calculate_ema(df, self.slow_ema)
        df['rsi'] = self.calculate_rsi(df, self.rsi_period)
        
        # آخرین مقادیر
        current = df.iloc[-1]
        previous = df.iloc[-2]
        
        # سیگنال خرید
        if (current['ema_fast'] > current['ema_slow'] and 
            previous['ema_fast'] <= previous['ema_slow'] and
            current['rsi'] < RSI_OVERBOUGHT):
            return {
                'signal': 'BUY',
                'price': current['close'],
                'stop_loss': current['close'] - (STOP_LOSS_PIPS * 0.1),
                'take_profit': current['close'] + (TAKE_PROFIT_PIPS * 0.1)
            }
        
        # سیگنال فروش
        if (current['ema_fast'] < current['ema_slow'] and 
            previous['ema_fast'] >= previous['ema_slow'] and
            current['rsi'] > RSI_OVERSOLD):
            return {
                'signal': 'SELL',
                'price': current['close'],
                'stop_loss': current['close'] + (STOP_LOSS_PIPS * 0.1),
                'take_profit': current['close'] - (TAKE_PROFIT_PIPS * 0.1)
            }
        
        return None
