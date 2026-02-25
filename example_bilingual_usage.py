#!/usr/bin/env python3
"""
Example usage of the bilingual translation system.
Demonstrates how to use translations in your code.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from trading_bot.i18n.translations import (
    Translator, Language, get_translator, set_language, t
)
from trading_bot.gui.language_switcher import (
    get_language_switcher, set_app_language, get_app_language
)
from trading_bot.config.language_config import LanguageConfig


def example_1_basic_translation():
    """Example 1: Basic translation usage."""
    print("\n" + "="*60)
    print("Example 1: Basic Translation")
    print("="*60)
    
    translator = get_translator()
    
    # English
    translator.set_language(Language.ENGLISH)
    print(f"English: {translator.t('start_bot')}")
    print(f"English: {translator.t('account_equity')}")
    print(f"English: {translator.t('total_pnl')}")
    
    # Persian
    translator.set_language(Language.PERSIAN)
    print(f"Persian: {translator.t('start_bot')}")
    print(f"Persian: {translator.t('account_equity')}")
    print(f"Persian: {translator.t('total_pnl')}")


def example_2_shorthand_translation():
    """Example 2: Using shorthand translation function."""
    print("\n" + "="*60)
    print("Example 2: Shorthand Translation")
    print("="*60)
    
    set_language(Language.ENGLISH)
    print(f"English: {t('dashboard')}")
    print(f"English: {t('positions')}")
    print(f"English: {t('trades')}")
    
    set_language(Language.PERSIAN)
    print(f"Persian: {t('dashboard')}")
    print(f"Persian: {t('positions')}")
    print(f"Persian: {t('trades')}")


def example_3_language_switcher():
    """Example 3: Using language switcher."""
    print("\n" + "="*60)
    print("Example 3: Language Switcher")
    print("="*60)
    
    switcher = get_language_switcher()
    
    # Set to English
    set_app_language(Language.ENGLISH)
    print(f"Current language: {get_app_language().value}")
    print(f"Translation: {switcher.t('start_bot')}")
    
    # Set to Persian
    set_app_language(Language.PERSIAN)
    print(f"Current language: {get_app_language().value}")
    print(f"Translation: {switcher.t('start_bot')}")


def example_4_language_config():
    """Example 4: Saving and loading language preferences."""
    print("\n" + "="*60)
    print("Example 4: Language Configuration")
    print("="*60)
    
    # Save Persian preference
    LanguageConfig.set_language(Language.PERSIAN)
    print("Saved language preference: Persian")
    
    # Load saved preference
    saved_language = LanguageConfig.get_language()
    print(f"Loaded language preference: {saved_language.value}")
    
    # Get supported languages
    supported = LanguageConfig.get_supported_languages()
    print(f"Supported languages: {supported}")


def example_5_adding_translations():
    """Example 5: Adding new translations."""
    print("\n" + "="*60)
    print("Example 5: Adding New Translations")
    print("="*60)
    
    translator = get_translator()
    
    # Add a new translation
    translator.add_translation(
        key="custom_message",
        en_text="This is a custom message",
        fa_text="این یک پیام سفارشی است"
    )
    
    # Use the new translation
    translator.set_language(Language.ENGLISH)
    print(f"English: {translator.t('custom_message')}")
    
    translator.set_language(Language.PERSIAN)
    print(f"Persian: {translator.t('custom_message')}")


def example_6_format_messages():
    """Example 6: Formatting messages with variables."""
    print("\n" + "="*60)
    print("Example 6: Format Messages with Variables")
    print("="*60)
    
    translator = get_translator()
    
    # Add a format message
    translator.add_translation(
        key="trade_result",
        en_text="Trade closed with P&L: ${pnl:.2f} ({pnl_percent:.2f}%)",
        fa_text="معامله بسته شد با سود/زیان: ${pnl:.2f} ({pnl_percent:.2f}%)"
    )
    
    # Format in English
    translator.set_language(Language.ENGLISH)
    message = translator.format_message("trade_result", pnl=150.50, pnl_percent=2.5)
    print(f"English: {message}")
    
    # Format in Persian
    translator.set_language(Language.PERSIAN)
    message = translator.format_message("trade_result", pnl=150.50, pnl_percent=2.5)
    print(f"Persian: {message}")


def example_7_all_translations():
    """Example 7: Display all available translations."""
    print("\n" + "="*60)
    print("Example 7: All Available Translations (Sample)")
    print("="*60)
    
    translator = get_translator()
    
    # Sample keys to display
    sample_keys = [
        "dashboard", "positions", "trades", "settings", "logs",
        "start_bot", "stop_bot", "save_settings",
        "account_equity", "total_pnl", "drawdown",
        "buy_signal", "sell_signal", "position_opened",
        "error", "success", "warning"
    ]
    
    print("\nEnglish Translations:")
    translator.set_language(Language.ENGLISH)
    for key in sample_keys[:5]:
        print(f"  {key}: {translator.t(key)}")
    
    print("\nPersian Translations:")
    translator.set_language(Language.PERSIAN)
    for key in sample_keys[:5]:
        print(f"  {key}: {translator.t(key)}")


def example_8_listener_pattern():
    """Example 8: Using listener pattern for language changes."""
    print("\n" + "="*60)
    print("Example 8: Listener Pattern for Language Changes")
    print("="*60)
    
    switcher = get_language_switcher()
    
    # Define a callback
    def on_language_changed(language: Language):
        print(f"Language changed to: {language.value}")
        print(f"Dashboard text: {switcher.t('dashboard')}")
    
    # Register listener
    switcher.register_listener(on_language_changed)
    
    # Change language (will trigger callback)
    print("Setting language to English:")
    set_app_language(Language.ENGLISH)
    
    print("\nSetting language to Persian:")
    set_app_language(Language.PERSIAN)


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("BILINGUAL TRANSLATION SYSTEM - EXAMPLES")
    print("="*60)
    
    try:
        example_1_basic_translation()
        example_2_shorthand_translation()
        example_3_language_switcher()
        example_4_language_config()
        example_5_adding_translations()
        example_6_format_messages()
        example_7_all_translations()
        example_8_listener_pattern()
        
        print("\n" + "="*60)
        print("All examples completed successfully!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
