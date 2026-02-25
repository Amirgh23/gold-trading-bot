# تنظیمات ربات تریدر طلا
import os

# تنظیمات صرافی
API_KEY = os.getenv('API_KEY', 'your_api_key_here')
API_SECRET = os.getenv('API_SECRET', 'your_api_secret_here')

# تنظیمات معاملاتی
SYMBOL = 'XAUUSD'  # انس طلا
TIMEFRAME = '1m'   # تایم فریم 1 دقیقه (Binance از 2m پشتیبانی نمی‌کنه)
POSITION_SIZE = 0.01  # حجم معامله
LEVERAGE = 10

# پارامترهای استراتژی فست اسکلپ
FAST_EMA = 5
SLOW_EMA = 13
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TAKE_PROFIT_PIPS = 5  # تیک پرافیت 5 پیپ
STOP_LOSS_PIPS = 3    # استاپ لاس 3 پیپ

# تنظیمات ریسک
MAX_DAILY_LOSS = 100  # حداکثر ضرر روزانه (دلار)
MAX_OPEN_TRADES = 3   # حداکثر معاملات همزمان
