"""Translation module for English and Persian support."""

from enum import Enum
from typing import Dict, Any


class Language(Enum):
    """Supported languages."""
    ENGLISH = "en"
    PERSIAN = "fa"


class Translator:
    """Handles translations between English and Persian."""
    
    # Translation dictionary
    TRANSLATIONS: Dict[str, Dict[str, str]] = {
        # GUI - Dashboard
        "dashboard": {
            "en": "Dashboard",
            "fa": "داشبورد"
        },
        "positions": {
            "en": "Positions",
            "fa": "موضع‌ها"
        },
        "trades": {
            "en": "Trades",
            "fa": "معاملات"
        },
        "settings": {
            "en": "Settings",
            "fa": "تنظیمات"
        },
        "logs": {
            "en": "Logs",
            "fa": "گزارش‌ها"
        },
        
        # Status
        "status": {
            "en": "Status",
            "fa": "وضعیت"
        },
        "running": {
            "en": "Running",
            "fa": "در حال اجرا"
        },
        "stopped": {
            "en": "Stopped",
            "fa": "متوقف"
        },
        "paused": {
            "en": "Paused",
            "fa": "مکث شده"
        },
        
        # Account Info
        "account_equity": {
            "en": "Account Equity",
            "fa": "سرمایه حساب"
        },
        "total_pnl": {
            "en": "Total P&L",
            "fa": "سود/زیان کل"
        },
        "drawdown": {
            "en": "Drawdown",
            "fa": "کاهش سرمایه"
        },
        "open_positions": {
            "en": "Open Positions",
            "fa": "موضع‌های باز"
        },
        
        # Performance Metrics
        "performance_metrics": {
            "en": "Performance Metrics",
            "fa": "معیارهای عملکرد"
        },
        "win_rate": {
            "en": "Win Rate",
            "fa": "نسبت برد"
        },
        "profit_factor": {
            "en": "Profit Factor",
            "fa": "ضریب سود"
        },
        "sharpe_ratio": {
            "en": "Sharpe Ratio",
            "fa": "نسبت شارپ"
        },
        "total_trades": {
            "en": "Total Trades",
            "fa": "کل معاملات"
        },
        
        # Table Headers - Positions
        "id": {
            "en": "ID",
            "fa": "شناسه"
        },
        "side": {
            "en": "Side",
            "fa": "جهت"
        },
        "entry_price": {
            "en": "Entry Price",
            "fa": "قیمت ورود"
        },
        "current_price": {
            "en": "Current Price",
            "fa": "قیمت فعلی"
        },
        "size": {
            "en": "Size",
            "fa": "حجم"
        },
        "pnl": {
            "en": "P&L",
            "fa": "سود/زیان"
        },
        "pnl_percent": {
            "en": "P&L %",
            "fa": "سود/زیان %"
        },
        "stop_loss": {
            "en": "Stop Loss",
            "fa": "حد ضرر"
        },
        
        # Table Headers - Trades
        "entry_time": {
            "en": "Entry Time",
            "fa": "زمان ورود"
        },
        "exit_time": {
            "en": "Exit Time",
            "fa": "زمان خروج"
        },
        "exit_price": {
            "en": "Exit Price",
            "fa": "قیمت خروج"
        },
        "duration": {
            "en": "Duration",
            "fa": "مدت زمان"
        },
        "strategy": {
            "en": "Strategy",
            "fa": "استراتژی"
        },
        
        # Buttons
        "start_bot": {
            "en": "Start Bot",
            "fa": "شروع ربات"
        },
        "stop_bot": {
            "en": "Stop Bot",
            "fa": "توقف ربات"
        },
        "pause_bot": {
            "en": "Pause Bot",
            "fa": "مکث ربات"
        },
        "resume_bot": {
            "en": "Resume Bot",
            "fa": "ادامه ربات"
        },
        "save_settings": {
            "en": "Save Settings",
            "fa": "ذخیره تنظیمات"
        },
        "load_settings": {
            "en": "Load Settings",
            "fa": "بارگذاری تنظیمات"
        },
        "clear_logs": {
            "en": "Clear Logs",
            "fa": "پاک کردن گزارش‌ها"
        },
        "export_data": {
            "en": "Export Data",
            "fa": "صادر کردن داده‌ها"
        },
        
        # Bot Messages
        "bot_initializing": {
            "en": "Initializing Trading Bot...",
            "fa": "در حال راه‌اندازی ربات تریدر..."
        },
        "bot_initialized": {
            "en": "Trading Bot initialized successfully",
            "fa": "ربات تریدر با موفقیت راه‌اندازی شد"
        },
        "bot_starting": {
            "en": "Starting Trading Bot...",
            "fa": "در حال شروع ربات تریدر..."
        },
        "bot_started": {
            "en": "Trading Bot started successfully",
            "fa": "ربات تریدر با موفقیت شروع شد"
        },
        "bot_stopping": {
            "en": "Stopping Trading Bot...",
            "fa": "در حال توقف ربات تریدر..."
        },
        "bot_stopped": {
            "en": "Trading Bot stopped",
            "fa": "ربات تریدر متوقف شد"
        },
        "bot_paused": {
            "en": "Trading Bot paused",
            "fa": "ربات تریدر مکث شد"
        },
        "bot_resumed": {
            "en": "Trading Bot resumed",
            "fa": "ربات تریدر ادامه یافت"
        },
        
        # Signals
        "signal_generated": {
            "en": "Signal Generated",
            "fa": "سیگنال تولید شد"
        },
        "buy_signal": {
            "en": "BUY Signal",
            "fa": "سیگنال خرید"
        },
        "sell_signal": {
            "en": "SELL Signal",
            "fa": "سیگنال فروش"
        },
        "signal_executed": {
            "en": "Signal Executed",
            "fa": "سیگنال اجرا شد"
        },
        "signal_rejected": {
            "en": "Signal Rejected",
            "fa": "سیگنال رد شد"
        },
        
        # Trades
        "position_opened": {
            "en": "Position Opened",
            "fa": "موضع باز شد"
        },
        "position_closed": {
            "en": "Position Closed",
            "fa": "موضع بسته شد"
        },
        "trade_logged": {
            "en": "Trade Logged",
            "fa": "معامله ثبت شد"
        },
        "trade_profit": {
            "en": "Trade Profit",
            "fa": "سود معامله"
        },
        "trade_loss": {
            "en": "Trade Loss",
            "fa": "زیان معامله"
        },
        
        # Alerts
        "alert": {
            "en": "Alert",
            "fa": "هشدار"
        },
        "warning": {
            "en": "Warning",
            "fa": "اخطار"
        },
        "critical": {
            "en": "Critical",
            "fa": "بحرانی"
        },
        "info": {
            "en": "Info",
            "fa": "اطلاعات"
        },
        
        # Errors
        "error": {
            "en": "Error",
            "fa": "خطا"
        },
        "insufficient_data": {
            "en": "Insufficient market data",
            "fa": "داده‌های بازار ناکافی"
        },
        "position_rejected": {
            "en": "Position rejected due to risk limits",
            "fa": "موضع به دلیل محدودیت‌های ریسک رد شد"
        },
        "order_failed": {
            "en": "Order execution failed",
            "fa": "اجرای سفارش ناموفق بود"
        },
        "connection_error": {
            "en": "Connection error",
            "fa": "خطای اتصال"
        },
        "timeout_error": {
            "en": "Request timeout",
            "fa": "زمان درخواست تمام شد"
        },
        
        # Risk Management
        "risk_management": {
            "en": "Risk Management",
            "fa": "مدیریت ریسک"
        },
        "max_daily_loss": {
            "en": "Max Daily Loss",
            "fa": "حداکثر زیان روزانه"
        },
        "max_open_trades": {
            "en": "Max Open Trades",
            "fa": "حداکثر معاملات باز"
        },
        "position_size": {
            "en": "Position Size",
            "fa": "حجم موضع"
        },
        "leverage": {
            "en": "Leverage",
            "fa": "اهرم"
        },
        "max_drawdown": {
            "en": "Max Drawdown",
            "fa": "حداکثر کاهش سرمایه"
        },
        
        # Strategy Settings
        "strategy_settings": {
            "en": "Strategy Settings",
            "fa": "تنظیمات استراتژی"
        },
        "ema_fast": {
            "en": "EMA Fast",
            "fa": "EMA سریع"
        },
        "ema_slow": {
            "en": "EMA Slow",
            "fa": "EMA آهسته"
        },
        "rsi_period": {
            "en": "RSI Period",
            "fa": "دوره RSI"
        },
        "take_profit": {
            "en": "Take Profit",
            "fa": "جایزه سود"
        },
        "confidence_threshold": {
            "en": "Confidence Threshold",
            "fa": "آستانه اطمینان"
        },
        
        # ML Settings
        "ml_settings": {
            "en": "ML Settings",
            "fa": "تنظیمات یادگیری ماشین"
        },
        "model_status": {
            "en": "Model Status",
            "fa": "وضعیت مدل"
        },
        "accuracy": {
            "en": "Accuracy",
            "fa": "دقت"
        },
        "lookback": {
            "en": "Lookback",
            "fa": "نگاه به عقب"
        },
        "model_loaded": {
            "en": "Model Loaded",
            "fa": "مدل بارگذاری شد"
        },
        "model_training": {
            "en": "Model Training",
            "fa": "آموزش مدل"
        },
        
        # Market Data
        "market_data": {
            "en": "Market Data",
            "fa": "داده‌های بازار"
        },
        "current_price": {
            "en": "Current Price",
            "fa": "قیمت فعلی"
        },
        "price_change": {
            "en": "Price Change",
            "fa": "تغییر قیمت"
        },
        "volume": {
            "en": "Volume",
            "fa": "حجم معاملات"
        },
        "high": {
            "en": "High",
            "fa": "بالاترین"
        },
        "low": {
            "en": "Low",
            "fa": "پایین‌ترین"
        },
        "open": {
            "en": "Open",
            "fa": "باز"
        },
        "close": {
            "en": "Close",
            "fa": "بسته"
        },
        
        # Time
        "today": {
            "en": "Today",
            "fa": "امروز"
        },
        "this_week": {
            "en": "This Week",
            "fa": "این هفته"
        },
        "this_month": {
            "en": "This Month",
            "fa": "این ماه"
        },
        "all_time": {
            "en": "All Time",
            "fa": "تمام دوره"
        },
        
        # Confirmation
        "confirm": {
            "en": "Confirm",
            "fa": "تایید"
        },
        "cancel": {
            "en": "Cancel",
            "fa": "لغو"
        },
        "yes": {
            "en": "Yes",
            "fa": "بله"
        },
        "no": {
            "en": "No",
            "fa": "خیر"
        },
        "ok": {
            "en": "OK",
            "fa": "تایید"
        },
        
        # Notifications
        "success": {
            "en": "Success",
            "fa": "موفق"
        },
        "failed": {
            "en": "Failed",
            "fa": "ناموفق"
        },
        "settings_saved": {
            "en": "Settings saved successfully",
            "fa": "تنظیمات با موفقیت ذخیره شد"
        },
        "settings_loaded": {
            "en": "Settings loaded successfully",
            "fa": "تنظیمات با موفقیت بارگذاری شد"
        },
        "data_exported": {
            "en": "Data exported successfully",
            "fa": "داده‌ها با موفقیت صادر شدند"
        },
        "logs_cleared": {
            "en": "Logs cleared successfully",
            "fa": "گزارش‌ها با موفقیت پاک شدند"
        },
    }
    
    def __init__(self, language: Language = Language.ENGLISH):
        """Initialize translator with default language."""
        self.current_language = language
    
    def set_language(self, language: Language) -> None:
        """Set current language."""
        self.current_language = language
    
    def get_language(self) -> Language:
        """Get current language."""
        return self.current_language
    
    def translate(self, key: str, default: str = "") -> str:
        """
        Translate a key to current language.
        
        Args:
            key: Translation key
            default: Default value if key not found
            
        Returns:
            Translated string or default
        """
        if key not in self.TRANSLATIONS:
            return default or key
        
        lang_code = self.current_language.value
        translation_dict = self.TRANSLATIONS[key]
        
        return translation_dict.get(lang_code, translation_dict.get("en", default or key))
    
    def t(self, key: str, default: str = "") -> str:
        """Shorthand for translate()."""
        return self.translate(key, default)
    
    def format_message(self, key: str, **kwargs) -> str:
        """
        Translate and format a message with variables.
        
        Args:
            key: Translation key
            **kwargs: Format variables
            
        Returns:
            Formatted translated string
        """
        message = self.translate(key)
        try:
            return message.format(**kwargs)
        except KeyError:
            return message
    
    def add_translation(self, key: str, en_text: str, fa_text: str) -> None:
        """Add a new translation."""
        if key not in self.TRANSLATIONS:
            self.TRANSLATIONS[key] = {}
        
        self.TRANSLATIONS[key]["en"] = en_text
        self.TRANSLATIONS[key]["fa"] = fa_text


# Global translator instance
_translator = Translator(Language.ENGLISH)


def get_translator() -> Translator:
    """Get global translator instance."""
    return _translator


def set_language(language: Language) -> None:
    """Set global language."""
    _translator.set_language(language)


def t(key: str, default: str = "") -> str:
    """Global translate function."""
    return _translator.translate(key, default)
