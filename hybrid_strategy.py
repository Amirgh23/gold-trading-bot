# استراتژی ترکیبی: تحلیل تکنیکال + LSTM
from strategy import FastScalpStrategy
from ml_model import GoldPriceLSTM
import pandas as pd

class HybridStrategy:
    """استراتژی ترکیبی با تحلیل تکنیکال و یادگیری ماشین"""
    
    def __init__(self, use_ml=True):
        self.technical_strategy = FastScalpStrategy()
        self.ml_model = GoldPriceLSTM(lookback=60, features=5)
        self.use_ml = use_ml
        
        # بارگذاری مدل آموزش دیده
        if use_ml:
            self.ml_model.load_model()
    
    def analyze(self, df):
        """تحلیل ترکیبی"""
        # سیگنال تحلیل تکنیکال
        technical_signal = self.technical_strategy.analyze(df)
        
        if not self.use_ml or not self.ml_model.is_trained:
            return technical_signal
        
        # پیش‌بینی LSTM
        ml_prediction = self.ml_model.predict_trend(df)
        
        if ml_prediction is None:
            return technical_signal
        
        # ترکیب سیگنال‌ها
        return self._combine_signals(technical_signal, ml_prediction, df)
    
    def _combine_signals(self, technical_signal, ml_prediction, df):
        """ترکیب سیگنال تکنیکال و ML"""
        current_price = df['close'].iloc[-1]
        
        # اگر هیچ سیگنال تکنیکالی نیست
        if technical_signal is None:
            # فقط از ML استفاده کن اگر اطمینان بالا باشد
            if ml_prediction['confidence'] > 0.3:
                signal_type = 'BUY' if ml_prediction['trend'] == 'BULLISH' else 'SELL'
                
                if signal_type == 'BUY':
                    return {
                        'signal': 'BUY',
                        'price': current_price,
                        'stop_loss': current_price - (current_price * 0.002),
                        'take_profit': ml_prediction['predicted_price'],
                        'source': 'ML_ONLY',
                        'confidence': ml_prediction['confidence']
                    }
                else:
                    return {
                        'signal': 'SELL',
                        'price': current_price,
                        'stop_loss': current_price + (current_price * 0.002),
                        'take_profit': ml_prediction['predicted_price'],
                        'source': 'ML_ONLY',
                        'confidence': ml_prediction['confidence']
                    }
            return None
        
        # اگر هر دو سیگنال موافق هستند
        technical_type = technical_signal['signal']
        ml_type = 'BUY' if ml_prediction['trend'] == 'BULLISH' else 'SELL'
        
        if technical_type == ml_type:
            # تقویت سیگنال
            technical_signal['source'] = 'HYBRID_CONFIRMED'
            technical_signal['ml_confidence'] = ml_prediction['confidence']
            technical_signal['ml_target'] = ml_prediction['predicted_price']
            return technical_signal
        
        # اگر سیگنال‌ها مخالف هستند
        if ml_prediction['confidence'] > 0.5:
            # اعتماد به ML بیشتر است
            return None  # عدم ورود به معامله
        
        # اعتماد به تحلیل تکنیکال
        technical_signal['source'] = 'TECHNICAL_ONLY'
        technical_signal['ml_warning'] = True
        return technical_signal
