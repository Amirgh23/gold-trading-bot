# Bilingual Support Guide (English & Persian)

This trading bot now has complete bilingual support for English and Persian (Farsi). All user-facing text, labels, messages, and notifications can be displayed in either language.

## Features

- **Complete Bilingual Support**: All UI elements, messages, and notifications in English and Persian
- **Runtime Language Switching**: Change language without restarting the application
- **Persistent Language Settings**: Language preference is saved and restored
- **Comprehensive Translation Dictionary**: 300+ translated strings covering all aspects of the bot
- **Easy Extension**: Simple API to add new translations

## Quick Start

### Running the Bilingual GUI

```bash
python run_gui_bilingual.py
```

This launches the main GUI with a language selector dropdown at the top.

### Switching Languages

1. Open the bilingual GUI
2. Use the language dropdown at the top-left
3. Select "English" or "فارسی (Persian)"
4. All UI elements update instantly

## Translation System Architecture

### Core Components

#### 1. Translation Module (`trading_bot/i18n/translations.py`)

The main translation system with:
- `Translator` class: Handles translation logic
- `Language` enum: Supported languages (ENGLISH, PERSIAN)
- Global translator instance for easy access

**Usage:**
```python
from trading_bot.i18n.translations import get_translator, Language

# Get translator
translator = get_translator()

# Set language
translator.set_language(Language.PERSIAN)

# Translate a key
text = translator.t("start_bot")  # Returns "شروع ربات" in Persian

# Format messages with variables
message = translator.format_message("trade_profit", amount=100.50)
```

#### 2. Language Switcher (`trading_bot/gui/language_switcher.py`)

Manages application-wide language switching with:
- Global language state
- Listener pattern for UI updates
- Automatic notification of all components

**Usage:**
```python
from trading_bot.gui.language_switcher import set_app_language, get_app_language
from trading_bot.i18n.translations import Language

# Change language globally
set_app_language(Language.PERSIAN)

# Get current language
current = get_app_language()
```

#### 3. Language Configuration (`trading_bot/config/language_config.py`)

Persists language preferences to disk:
- Saves user's language choice
- Loads on startup
- Supports auto-detection

**Usage:**
```python
from trading_bot.config.language_config import LanguageConfig
from trading_bot.i18n.translations import Language

# Get saved language
lang = LanguageConfig.get_language()

# Save language preference
LanguageConfig.set_language(Language.PERSIAN)
```

## Updated Components

### GUI Dashboard (`trading_bot/gui/dashboard.py`)

Now supports bilingual display:
- All tab names translated
- All labels and headers translated
- Status messages in selected language
- Table headers in selected language

**Example:**
```python
from trading_bot.gui.dashboard import TradingDashboard
from trading_bot.i18n.translations import Language

# Create dashboard in Persian
dashboard = TradingDashboard(language=Language.PERSIAN)

# Change language later
dashboard.set_language(Language.ENGLISH)
```

### Alert Manager (`trading_bot/gui/alerts.py`)

Bilingual alert notifications:
- Alert titles and messages can be translated
- Supports both English and Persian

**Example:**
```python
from trading_bot.gui.alerts import AlertManager
from trading_bot.i18n.translations import Language

alert_manager = AlertManager(language=Language.PERSIAN)
alert_manager.trigger_alert(
    title="سیگنال خرید",  # Buy Signal in Persian
    message="قیمت طلا به $2050 رسید"  # Gold price reached $2050
)
```

## Translation Dictionary

The system includes 300+ translated strings organized by category:

### GUI Elements
- Dashboard, Positions, Trades, Settings, Logs
- Start Bot, Stop Bot, Pause Bot, Resume Bot
- Save Settings, Load Settings, Clear Logs, Export Data

### Status Messages
- Running, Stopped, Paused
- Account Equity, Total P&L, Drawdown
- Open Positions, Win Rate, Profit Factor

### Trading Terms
- Buy Signal, Sell Signal, Position Opened, Position Closed
- Entry Price, Exit Price, Stop Loss, Take Profit
- P&L, Duration, Strategy

### Error Messages
- Connection Error, Timeout Error, Order Failed
- Insufficient Data, Position Rejected
- Configuration Error, Validation Error

### Alerts
- Alert, Warning, Critical, Info
- Success, Failed
- Settings Saved, Data Exported, Logs Cleared

## Adding New Translations

### Method 1: Direct Addition

```python
from trading_bot.i18n.translations import get_translator

translator = get_translator()
translator.add_translation(
    key="my_new_key",
    en_text="English text",
    fa_text="متن فارسی"
)
```

### Method 2: Update Translation Dictionary

Edit `trading_bot/i18n/translations.py` and add to the `TRANSLATIONS` dictionary:

```python
"my_new_key": {
    "en": "English text",
    "fa": "متن فارسی"
}
```

## Using Translations in Your Code

### In GUI Components

```python
from trading_bot.i18n.translations import get_translator

translator = get_translator()

# Create a button with translated text
button = QPushButton(translator.t("start_bot"))

# Create a label with translated text
label = QLabel(translator.t("account_equity"))
```

### In Bot Logic

```python
from trading_bot.i18n.translations import get_translator
import logging

logger = logging.getLogger(__name__)
translator = get_translator()

# Log messages in current language
logger.info(translator.t("bot_started"))

# Format messages with variables
message = translator.format_message("trade_profit", amount=100.50)
logger.info(message)
```

### In Configuration

```python
from trading_bot.config.language_config import LanguageConfig
from trading_bot.i18n.translations import Language

# Load user's preferred language
language = LanguageConfig.get_language()

# Use it in your application
translator.set_language(language)
```

## Language-Specific Considerations

### Persian (Farsi) Support

- **Right-to-Left (RTL) Text**: PyQt5 automatically handles RTL rendering
- **Unicode Support**: Full UTF-8 support for Persian characters
- **Font Rendering**: Ensure system has Persian fonts installed
- **Number Formatting**: Numbers display in English numerals (standard for trading)

### English Support

- **Standard LTR**: Left-to-right text rendering
- **ASCII Compatible**: All English text is ASCII-compatible

## Configuration File

Language preferences are saved in `config/language.json`:

```json
{
  "language": "en",
  "auto_detect": false,
  "supported_languages": ["en", "fa"]
}
```

## Bilingual GUI Features

The `run_gui_bilingual.py` launcher provides:

1. **Language Selector Dropdown**
   - Located at top-left of window
   - Shows "English" and "فارسی (Persian)"
   - Changes language instantly

2. **Persistent Language**
   - Saves language preference
   - Restores on next launch

3. **Real-Time Updates**
   - All UI elements update when language changes
   - No need to restart application

4. **Complete Translation**
   - All tabs, buttons, labels translated
   - All status messages translated
   - All table headers translated

## Testing Translations

### Test English
```bash
python run_gui_bilingual.py
# Select "English" from dropdown
```

### Test Persian
```bash
python run_gui_bilingual.py
# Select "فارسی (Persian)" from dropdown
```

### Verify All Strings
```python
from trading_bot.i18n.translations import Translator, Language

translator = Translator()

# Check English
translator.set_language(Language.ENGLISH)
print(translator.t("start_bot"))  # Should print "Start Bot"

# Check Persian
translator.set_language(Language.PERSIAN)
print(translator.t("start_bot"))  # Should print "شروع ربات"
```

## Extending to More Languages

To add a new language (e.g., Spanish):

1. Add to `Language` enum:
```python
class Language(Enum):
    ENGLISH = "en"
    PERSIAN = "fa"
    SPANISH = "es"  # New language
```

2. Add translations to dictionary:
```python
"start_bot": {
    "en": "Start Bot",
    "fa": "شروع ربات",
    "es": "Iniciar Bot"  # Spanish translation
}
```

3. Update GUI dropdown:
```python
self.language_combo.addItem("Español", Language.SPANISH)
```

## Performance Considerations

- **Translation Lookup**: O(1) dictionary lookup - very fast
- **Memory**: ~50KB for all translations
- **Language Switching**: Instant, no reload needed
- **No External Dependencies**: Uses only Python standard library for translations

## Troubleshooting

### Persian Text Not Displaying Correctly

1. Ensure system has Persian fonts installed
2. Check PyQt5 version (5.12+)
3. Verify UTF-8 encoding in files

### Language Not Persisting

1. Check `config/language.json` exists
2. Verify write permissions to config directory
3. Check for errors in language_config.py

### Translations Missing

1. Check key exists in TRANSLATIONS dictionary
2. Verify spelling of translation key
3. Use `translator.t(key, default="fallback")` for safety

## API Reference

### Translator Class

```python
class Translator:
    def set_language(language: Language) -> None
    def get_language() -> Language
    def translate(key: str, default: str = "") -> str
    def t(key: str, default: str = "") -> str  # Shorthand
    def format_message(key: str, **kwargs) -> str
    def add_translation(key: str, en_text: str, fa_text: str) -> None
```

### LanguageSwitcher Class

```python
class LanguageSwitcher:
    def set_language(language: Language) -> None
    def get_language() -> Language
    def register_listener(callback: Callable) -> None
    def unregister_listener(callback: Callable) -> None
    def translate(key: str, default: str = "") -> str
    def t(key: str, default: str = "") -> str
```

### LanguageConfig Class

```python
class LanguageConfig:
    @classmethod
    def load() -> dict
    @classmethod
    def save(config: dict) -> bool
    @classmethod
    def get_language() -> Language
    @classmethod
    def set_language(language: Language) -> bool
    @classmethod
    def get_supported_languages() -> list
```

## Summary

The trading bot now has complete bilingual support with:
- ✅ 300+ translated strings
- ✅ Runtime language switching
- ✅ Persistent language preferences
- ✅ Easy-to-use translation API
- ✅ Extensible architecture for more languages
- ✅ No external translation dependencies
- ✅ Full Persian (RTL) support
- ✅ Complete English support

All components are ready for production use with both English and Persian interfaces.
