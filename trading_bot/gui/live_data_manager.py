"""
Live Data Manager - Real-time market data updates
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
import threading
import time


class LiveDataUpdater(QThread):
    """Background thread for live data updates"""
    data_updated = pyqtSignal(pd.DataFrame)
    analysis_updated = pyqtSignal(dict)
    
    def __init__(self, initial_data):
        super().__init__()
        self.data = initial_data.copy()
        self.running = True
        self.update_interval = 1  # Update every 1 second
        
    def run(self):
        """Run live data updates"""
        while self.running:
            try:
                # Update data with new candle
                self.update_live_data()
                self.data_updated.emit(self.data)
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"Error updating live data: {e}")
                time.sleep(1)
    
    def update_live_data(self):
        """Update data with new candle"""
        # Get last price
        last_price = self.data['close'].iloc[-1]
        
        # Generate new price (random walk)
        price_change = np.random.randn() * 2  # Random change
        new_price = last_price + price_change
        
        # Create new candle
        now = datetime.now()
        new_candle = {
            'date': now,
            'open': new_price - np.random.rand() * 1,
            'high': new_price + np.abs(np.random.randn() * 1.5),
            'low': new_price - np.abs(np.random.randn() * 1.5),
            'close': new_price,
            'volume': np.random.randint(1000, 10000)
        }
        
        # Add new candle to data
        new_row = pd.DataFrame([new_candle])
        self.data = pd.concat([self.data, new_row], ignore_index=True)
        
        # Keep only last 300 candles
        if len(self.data) > 300:
            self.data = self.data.tail(300).reset_index(drop=True)
        
        # Recalculate MAs
        self.data['MA20'] = self.data['close'].rolling(20).mean()
        self.data['MA50'] = self.data['close'].rolling(50).mean()
        self.data['MA200'] = self.data['close'].rolling(200).mean()
    
    def stop(self):
        """Stop the updater"""
        self.running = False


class LiveAnalysisUpdater(QThread):
    """Background thread for live analysis updates"""
    analysis_updated = pyqtSignal(dict)
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.running = True
        self.update_interval = 2  # Update every 2 seconds
        
    def run(self):
        """Run live analysis updates"""
        while self.running:
            try:
                analysis = self.perform_analysis()
                self.analysis_updated.emit(analysis)
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"Error updating analysis: {e}")
                time.sleep(1)
    
    def perform_analysis(self):
        """Perform live analysis"""
        data = self.data_manager.data
        prices = data['close'].values
        
        # Trend analysis
        ma20 = np.mean(prices[-20:]) if len(prices) >= 20 else np.mean(prices)
        ma50 = np.mean(prices[-50:]) if len(prices) >= 50 else np.mean(prices)
        ma200 = np.mean(prices[-200:]) if len(prices) >= 200 else np.mean(prices)
        current_price = prices[-1]
        
        trend = "UPTREND" if ma20 > ma50 > ma200 else "DOWNTREND" if ma20 < ma50 < ma200 else "SIDEWAYS"
        trend_strength = abs(ma20 - ma50) / ma50 * 100
        
        # RSI Analysis
        rsi = self.calculate_rsi(prices)
        rsi_signal = "OVERBOUGHT" if rsi > 70 else "OVERSOLD" if rsi < 30 else "NEUTRAL"
        
        # MACD Analysis
        ema12 = self.calculate_ema(prices, 12)
        ema26 = self.calculate_ema(prices, 26)
        macd = ema12 - ema26
        macd_signal = "BULLISH" if macd > 0 else "BEARISH"
        
        # Stochastic Analysis
        stoch = self.calculate_stochastic(prices)
        stoch_signal = "OVERBOUGHT" if stoch > 80 else "OVERSOLD" if stoch < 20 else "NEUTRAL"
        
        # Bollinger Bands
        bb_middle = np.mean(prices[-20:])
        bb_std = np.std(prices[-20:])
        bb_upper = bb_middle + (bb_std * 2)
        bb_lower = bb_middle - (bb_std * 2)
        
        if current_price > bb_upper:
            bb_signal = "OVERBOUGHT"
        elif current_price < bb_lower:
            bb_signal = "OVERSOLD"
        else:
            bb_signal = "NEUTRAL"
        
        # ATR (Average True Range)
        atr = self.calculate_atr(data)
        volatility = "HIGH" if atr > np.mean(prices) * 0.02 else "LOW"
        
        # AI Recommendation
        signals = [
            ("BULL" if "UP" in trend else "BEAR"),
            ("BULL" if "OVERBOUGHT" not in rsi_signal else "BEAR"),
            ("BULL" if "BULLISH" in macd_signal else "BEAR"),
            ("BULL" if "OVERBOUGHT" not in stoch_signal else "BEAR"),
            ("BULL" if "OVERBOUGHT" not in bb_signal else "BEAR"),
        ]
        
        bullish_count = sum(1 for s in signals if "BULL" in s)
        bearish_count = len(signals) - bullish_count
        
        if bullish_count > bearish_count:
            recommendation = "BUY"
            confidence = (bullish_count / len(signals)) * 100
        elif bearish_count > bullish_count:
            recommendation = "SELL"
            confidence = (bearish_count / len(signals)) * 100
        else:
            recommendation = "HOLD"
            confidence = 50
        
        return {
            'timestamp': datetime.now().strftime("%H:%M:%S"),
            'trend': trend,
            'trend_strength': trend_strength,
            'rsi': rsi,
            'rsi_signal': rsi_signal,
            'macd': macd,
            'macd_signal': macd_signal,
            'stoch': stoch,
            'stoch_signal': stoch_signal,
            'bb_signal': bb_signal,
            'volatility': volatility,
            'atr': atr,
            'recommendation': recommendation,
            'confidence': confidence,
            'current_price': current_price,
            'ma20': ma20,
            'ma50': ma50,
            'ma200': ma200,
            'bb_upper': bb_upper,
            'bb_lower': bb_lower,
            'bb_middle': bb_middle
        }
    
    @staticmethod
    def calculate_rsi(prices, period=14):
        """Calculate RSI"""
        if len(prices) < period:
            return 50
        
        delta = np.diff(prices[-period-1:])
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        
        avg_gain = np.mean(gain)
        avg_loss = np.mean(loss)
        
        if avg_loss == 0:
            return 100 if avg_gain > 0 else 50
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_ema(prices, period):
        """Calculate EMA"""
        multiplier = 2 / (period + 1)
        ema = np.mean(prices[:period])
        
        for price in prices[period:]:
            ema = price * multiplier + ema * (1 - multiplier)
        
        return ema
    
    @staticmethod
    def calculate_stochastic(prices, period=14):
        """Calculate Stochastic"""
        if len(prices) < period:
            return 50
        
        low = np.min(prices[-period:])
        high = np.max(prices[-period:])
        close = prices[-1]
        
        if high == low:
            return 50
        
        stoch = ((close - low) / (high - low)) * 100
        return stoch
    
    @staticmethod
    def calculate_atr(data, period=14):
        """Calculate ATR"""
        if len(data) < period:
            return 0
        
        high = data['high'].values[-period:]
        low = data['low'].values[-period:]
        close = data['close'].values[-period:]
        
        tr = np.maximum(
            high - low,
            np.maximum(
                np.abs(high - np.roll(close, 1)),
                np.abs(low - np.roll(close, 1))
            )
        )
        
        atr = np.mean(tr)
        return atr
    
    def stop(self):
        """Stop the updater"""
        self.running = False

