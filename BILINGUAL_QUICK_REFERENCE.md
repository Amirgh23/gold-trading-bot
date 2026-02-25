# Bilingual System - Quick Reference

## Quick Start

### Run Bilingual GUI
```bash
python run_gui_bilingual.py
```
Select language from dropdown at top-left.

### Run Examples
```bash
python example_bilingual_usage.py
```

## Common Tasks

### Translate a String

```python
from trading_bot.i18n.translations import t, Language, set_language

# Set language
set_language(Language.PERSIAN)

# Translate
text = t("start_bot")  # "شروع ربات"
```

### Change Language Globally

```python
from trading_bot.gui.language_switcher import set_app_language
from trading_bot.i18n.translations import Language

set_app_language(Language.PERSIAN)
```

### In GUI Components

```python
from trading_bot.gui.dashboard import TradingDashboard
from trading_bot.i18n.translations import Language

# Create in Persian
dashboard = TradingDashboard(language=Language.PERSIAN)

# Change language
dashboard.set_language(Language.ENGLISH)
```

### Save Language Preference

```python
from trading_bot.config.language_config import LanguageConfig
from trading_bot.i18n.translations import Language

LanguageConfig.set_language(Language.PERSIAN)
```

### Load Saved Language

```python
from trading_bot.config.language_config import LanguageConfig

language = LanguageConfig.get_language()
```

### Add New Translation

```python
from trading_bot.i18n.translations import get_translator

translator = get_translator()
translator.add_translation(
    key="my_key",
    en_text="English",
    fa_text="فارسی"
)
```

### Format Message with Variables

```python
from trading_bot.i18n.translations import get_translator

translator = get_translator()
message = translator.format_message(
    "trade_result",
    pnl=100.50,
    pnl_percent=2.5
)
```

## Translation Keys (Sample)

### GUI
- `dashboard` - داشبورد
- `positions` - موضع‌ها
- `trades` - معاملات
- `settings` - تنظیمات
- `logs` - گزارش‌ها

### Buttons
- `start_bot` - شروع ربات
- `stop_bot` - توقف ربات
- `save_settings` - ذخیره تنظیمات
- `clear_logs` - پاک کردن گزارش‌ها

### Status
- `running` - در حال اجرا
- `stopped` - متوقف
- `account_equity` - سرمایه حساب
- `total_pnl` - سود/زیان کل

### Trading
- `buy_signal` - سیگنال خرید
- `sell_signal` - سیگنال فروش
- `position_opened` - موضع باز شد
- `position_closed` - موضع بسته شد

### Alerts
- `success` - موفق
- `error` - خطا
- `warning` - اخطار
- `critical` - بحرانی

## API Reference

### Translator

```python
from trading_bot.i18n.translations import Translator, Language

translator = Translator(Language.ENGLISH)
translator.set_language(Language.PERSIAN)
translator.t("key")  # Translate
translator.format_message("key", var=value)  # Format
translator.add_translation("key", "en", "fa")  # Add
```

### Language Switcher

```python
from trading_bot.gui.language_switcher import get_language_switcher

switcher = get_language_switcher()
switcher.set_language(Language.PERSIAN)
switcher.register_listener(callback)
switcher.t("key")
```

### Language Config

```python
from trading_bot.config.language_config import LanguageConfig

LanguageConfig.get_language()
LanguageConfig.set_language(Language.PERSIAN)
LanguageConfig.get_supported_languages()
```

## File Locations

- **Translations**: `trading_bot/i18n/translations.py`
- **Switcher**: `trading_bot/gui/language_switcher.py`
- **Config**: `trading_bot/config/language_config.py`
- **Dashboard**: `trading_bot/gui/dashboard.py`
- **Alerts**: `trading_bot/gui/alerts.py`
- **GUI Launcher**: `run_gui_bilingual.py`
- **Examples**: `example_bilingual_usage.py`
- **Saved Prefs**: `config/language.json`

## Supported Languages

| Language | Code | Display |
|----------|------|---------|
| English | `en` | English |
| Persian | `fa` | فارسی |

## Common Patterns

### Pattern 1: Simple Translation
```python
text = t("start_bot")
```

### Pattern 2: With Fallback
```python
text = t("key", default="Default Text")
```

### Pattern 3: Format Message
```python
msg = translator.format_message("trade_result", pnl=100)
```

### Pattern 4: Language Change Listener
```python
def on_lang_change(lang):
    print(f"Language changed to {lang.value}")

switcher.register_listener(on_lang_change)
set_app_language(Language.PERSIAN)
```

### Pattern 5: GUI Component
```python
class MyComponent:
    def __init__(self, language=Language.ENGLISH):
        self.translator = get_translator()
        self.translator.set_language(language)
    
    def set_language(self, language):
        self.translator.set_language(language)
        self.update_ui()
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Persian text not showing | Install Persian fonts, check PyQt5 version |
| Language not persisting | Check `config/language.json` exists |
| Translation missing | Use `t(key, default="fallback")` |
| GUI not updating | Ensure component has `set_language()` method |
| Import error | Check `trading_bot/i18n/` exists |

## Performance Tips

- Use `t()` shorthand for quick translations
- Cache translator instance if translating many strings
- Language switching is O(n) where n = listeners
- Translation lookup is O(1) - very fast

## Best Practices

1. **Always provide defaults**: `t("key", default="English")`
2. **Use consistent keys**: Follow naming convention
3. **Group related translations**: Organize by category
4. **Test both languages**: Verify all strings translate
5. **Handle missing translations**: Graceful fallback
6. **Document new keys**: Add comments for clarity

## Examples

### Example 1: Simple App
```python
from trading_bot.i18n.translations import t, set_language, Language

set_language(Language.PERSIAN)
print(t("start_bot"))  # شروع ربات
```

### Example 2: GUI with Switcher
```python
from trading_bot.gui.language_switcher import set_app_language
from trading_bot.i18n.translations import Language

# User selects Persian
set_app_language(Language.PERSIAN)
# All UI updates automatically
```

### Example 3: Bot Component
```python
from trading_bot.i18n.translations import get_translator

class TradingBot:
    def __init__(self):
        self.translator = get_translator()
    
    def log_trade(self, pnl):
        msg = self.translator.format_message(
            "trade_result",
            pnl=pnl
        )
        logger.info(msg)
```

## Resources

- **Full Guide**: `BILINGUAL_GUIDE.md`
- **Implementation**: `BILINGUAL_IMPLEMENTATION_SUMMARY.md`
- **Examples**: `example_bilingual_usage.py`
- **GUI**: `run_gui_bilingual.py`

## Support

For issues or questions:
1. Check `BILINGUAL_GUIDE.md` troubleshooting section
2. Review examples in `example_bilingual_usage.py`
3. Check code comments in `trading_bot/i18n/translations.py`
4. Verify file structure and imports

---

**Last Updated**: February 2026
**Version**: 1.0
**Status**: Production Ready
