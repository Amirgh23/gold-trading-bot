# مدل LSTM برای پیش‌بینی قیمت طلا
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
import joblib
import os

class GoldPriceLSTM:
    """مدل LSTM برای پیش‌بینی قیمت انس طلا"""
    
    def __init__(self, lookback=60, features=5):
        self.lookback = lookback  # تعداد کندل‌های گذشته
        self.features = features  # تعداد ویژگی‌ها
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.is_trained = False
        
    def create_model(self):
        """ساخت معماری LSTM"""
        model = Sequential([
            LSTM(units=50, return_sequences=True, input_shape=(self.lookback, self.features)),
            Dropout(0.2),
            
            LSTM(units=50, return_sequences=True),
            Dropout(0.2),
            
            LSTM(units=50, return_sequences=False),
            Dropout(0.2),
            
            Dense(units=25),
            Dense(units=1)  # پیش‌بینی قیمت بعدی
        ])
        
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')
        self.model = model
        return model
    
    def prepare_data(self, df):
        """آماده‌سازی داده‌ها برای LSTM"""
        # ویژگی‌های مورد استفاده
        features = ['open', 'high', 'low', 'close', 'volume']
        data = df[features].values
        
        # نرمال‌سازی داده‌ها
        scaled_data = self.scaler.fit_transform(data)
        
        X, y = [], []
        for i in range(self.lookback, len(scaled_data)):
            X.append(scaled_data[i-self.lookback:i])
            y.append(scaled_data[i, 3])  # قیمت close
        
        return np.array(X), np.array(y)

    def train(self, df, epochs=50, batch_size=32, validation_split=0.2):
        """آموزش مدل"""
        print("🎓 شروع آموزش مدل LSTM...")
        
        # آماده‌سازی داده‌ها
        X, y = self.prepare_data(df)
        
        if len(X) == 0:
            print("❌ داده کافی برای آموزش وجود ندارد")
            return False
        
        # ساخت مدل
        if self.model is None:
            self.create_model()
        
        # آموزش
        history = self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            verbose=1
        )
        
        self.is_trained = True
        print("✅ آموزش مدل با موفقیت انجام شد")
        return history
    
    def predict_next_price(self, df):
        """پیش‌بینی قیمت بعدی"""
        if not self.is_trained or self.model is None:
            print("⚠️ مدل هنوز آموزش داده نشده")
            return None
        
        # آماده‌سازی داده‌های ورودی
        features = ['open', 'high', 'low', 'close', 'volume']
        recent_data = df[features].tail(self.lookback).values
        
        if len(recent_data) < self.lookback:
            return None
        
        # نرمال‌سازی
        scaled_data = self.scaler.transform(recent_data)
        X = np.array([scaled_data])
        
        # پیش‌بینی
        prediction = self.model.predict(X, verbose=0)
        
        # برگرداندن به مقیاس اصلی
        dummy = np.zeros((1, self.features))
        dummy[0, 3] = prediction[0, 0]
        predicted_price = self.scaler.inverse_transform(dummy)[0, 3]
        
        return predicted_price
    
    def predict_trend(self, df):
        """پیش‌بینی روند (صعودی/نزولی)"""
        predicted_price = self.predict_next_price(df)
        
        if predicted_price is None:
            return None
        
        current_price = df['close'].iloc[-1]
        price_change = ((predicted_price - current_price) / current_price) * 100
        
        return {
            'predicted_price': predicted_price,
            'current_price': current_price,
            'change_percent': price_change,
            'trend': 'BULLISH' if price_change > 0 else 'BEARISH',
            'confidence': abs(price_change)
        }
    
    def save_model(self, model_path='models/lstm_model.h5', scaler_path='models/scaler.pkl'):
        """ذخیره مدل"""
        os.makedirs('models', exist_ok=True)
        self.model.save(model_path)
        joblib.dump(self.scaler, scaler_path)
        print(f"💾 مدل ذخیره شد: {model_path}")
    
    def load_model(self, model_path='models/lstm_model.h5', scaler_path='models/scaler.pkl'):
        """بارگذاری مدل"""
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            self.model = load_model(model_path)
            self.scaler = joblib.load(scaler_path)
            self.is_trained = True
            print(f"✅ مدل بارگذاری شد: {model_path}")
            return True
        return False
