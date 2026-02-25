# اسکریپت آموزش مدل LSTM
import pandas as pd
import numpy as np
from ml_model import GoldPriceLSTM
from datetime import datetime, timedelta

def generate_sample_data(days=180):
    """تولید داده نمونه برای تست (در پروژه واقعی از داده‌های واقعی استفاده کنید)"""
    print("📊 تولید داده نمونه...")
    
    dates = pd.date_range(end=datetime.now(), periods=days*720, freq='2min')
    
    # شبیه‌سازی قیمت طلا
    base_price = 2000
    trend = np.linspace(0, 100, len(dates))
    noise = np.random.normal(0, 5, len(dates))
    prices = base_price + trend + noise
    
    data = {
        'timestamp': dates,
        'open': prices + np.random.uniform(-2, 2, len(dates)),
        'high': prices + np.random.uniform(0, 5, len(dates)),
        'low': prices - np.random.uniform(0, 5, len(dates)),
        'close': prices,
        'volume': np.random.uniform(1000, 5000, len(dates))
    }
    
    return pd.DataFrame(data)

def train_lstm_model():
    """آموزش مدل LSTM"""
    print("="*60)
    print("🚀 شروع آموزش مدل LSTM برای پیش‌بینی قیمت طلا")
    print("="*60)
    
    # دریافت داده‌ها
    # در پروژه واقعی از API صرافی استفاده کنید
    df = generate_sample_data(days=180)
    print(f"✅ {len(df)} کندل دریافت شد")
    
    # ساخت و آموزش مدل
    lstm_model = GoldPriceLSTM(lookback=60, features=5)
    
    history = lstm_model.train(
        df,
        epochs=50,
        batch_size=32,
        validation_split=0.2
    )
    
    # ذخیره مدل
    lstm_model.save_model()
    
    # تست پیش‌بینی
    print("\n" + "="*60)
    print("🔮 تست پیش‌بینی")
    print("="*60)
    
    prediction = lstm_model.predict_trend(df)
    if prediction:
        print(f"💰 قیمت فعلی: ${prediction['current_price']:.2f}")
        print(f"🎯 قیمت پیش‌بینی شده: ${prediction['predicted_price']:.2f}")
        print(f"📈 تغییر: {prediction['change_percent']:.2f}%")
        print(f"🔥 روند: {prediction['trend']}")
    
    print("\n✅ آموزش مدل با موفقیت انجام شد!")

if __name__ == "__main__":
    train_lstm_model()
