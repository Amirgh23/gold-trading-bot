#!/usr/bin/env python3
"""
Test script for bilingual system.
Verifies all components work correctly.
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


class TestResults:
    """Track test results."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def add_pass(self, test_name):
        self.passed += 1
        self.tests.append((test_name, "PASS", None))
        print(f"✓ {test_name}")
    
    def add_fail(self, test_name, error):
        self.failed += 1
        self.tests.append((test_name, "FAIL", str(error)))
        print(f"✗ {test_name}: {error}")
    
    def print_summary(self):
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Total: {self.passed + self.failed}")
        
        if self.failed == 0:
            print("\n✓ All tests passed!")
        else:
            print(f"\n✗ {self.failed} test(s) failed")
        print("="*60)


def test_translator_creation():
    """Test 1: Create translator instance."""
    results = TestResults()
    
    try:
        translator = Translator()
        assert translator is not None
        results.add_pass("Create Translator instance")
    except Exception as e:
        results.add_fail("Create Translator instance", e)
    
    return results


def test_language_enum():
    """Test 2: Language enum."""
    results = TestResults()
    
    try:
        assert Language.ENGLISH.value == "en"
        results.add_pass("Language.ENGLISH value")
        
        assert Language.PERSIAN.value == "fa"
        results.add_pass("Language.PERSIAN value")
    except Exception as e:
        results.add_fail("Language enum", e)
    
    return results


def test_translation_lookup():
    """Test 3: Translation lookup."""
    results = TestResults()
    
    try:
        translator = get_translator()
        
        # Test English
        translator.set_language(Language.ENGLISH)
        text = translator.t("start_bot")
        assert text == "Start Bot", f"Expected 'Start Bot', got '{text}'"
        results.add_pass("English translation lookup")
        
        # Test Persian
        translator.set_language(Language.PERSIAN)
        text = translator.t("start_bot")
        assert text == "شروع ربات", f"Expected 'شروع ربات', got '{text}'"
        results.add_pass("Persian translation lookup")
    except Exception as e:
        results.add_fail("Translation lookup", e)
    
    return results


def test_shorthand_function():
    """Test 4: Shorthand translation function."""
    results = TestResults()
    
    try:
        set_language(Language.ENGLISH)
        text = t("dashboard")
        assert text == "Dashboard", f"Expected 'Dashboard', got '{text}'"
        results.add_pass("Shorthand translation function")
    except Exception as e:
        results.add_fail("Shorthand translation function", e)
    
    return results


def test_language_switcher():
    """Test 5: Language switcher."""
    results = TestResults()
    
    try:
        switcher = get_language_switcher()
        
        # Set to English
        switcher.set_language(Language.ENGLISH)
        assert switcher.get_language() == Language.ENGLISH
        results.add_pass("Language switcher - set English")
        
        # Set to Persian
        switcher.set_language(Language.PERSIAN)
        assert switcher.get_language() == Language.PERSIAN
        results.add_pass("Language switcher - set Persian")
    except Exception as e:
        results.add_fail("Language switcher", e)
    
    return results


def test_listener_pattern():
    """Test 6: Listener pattern."""
    results = TestResults()
    
    try:
        switcher = get_language_switcher()
        
        # Track language changes
        changes = []
        
        def listener(lang):
            changes.append(lang)
        
        switcher.register_listener(listener)
        
        # Change language
        switcher.set_language(Language.ENGLISH)
        switcher.set_language(Language.PERSIAN)
        
        assert len(changes) == 2, f"Expected 2 changes, got {len(changes)}"
        assert changes[0] == Language.ENGLISH
        assert changes[1] == Language.PERSIAN
        
        results.add_pass("Listener pattern")
        
        # Cleanup
        switcher.unregister_listener(listener)
    except Exception as e:
        results.add_fail("Listener pattern", e)
    
    return results


def test_add_translation():
    """Test 7: Add new translation."""
    results = TestResults()
    
    try:
        translator = get_translator()
        
        # Add translation
        translator.add_translation(
            key="test_key",
            en_text="Test English",
            fa_text="تست فارسی"
        )
        
        # Test English
        translator.set_language(Language.ENGLISH)
        text = translator.t("test_key")
        assert text == "Test English", f"Expected 'Test English', got '{text}'"
        results.add_pass("Add translation - English")
        
        # Test Persian
        translator.set_language(Language.PERSIAN)
        text = translator.t("test_key")
        assert text == "تست فارسی", f"Expected 'تست فارسی', got '{text}'"
        results.add_pass("Add translation - Persian")
    except Exception as e:
        results.add_fail("Add translation", e)
    
    return results


def test_format_message():
    """Test 8: Format message with variables."""
    results = TestResults()
    
    try:
        translator = get_translator()
        
        # Add format message
        translator.add_translation(
            key="test_format",
            en_text="Value: {value}",
            fa_text="مقدار: {value}"
        )
        
        # Test English
        translator.set_language(Language.ENGLISH)
        text = translator.format_message("test_format", value=42)
        assert text == "Value: 42", f"Expected 'Value: 42', got '{text}'"
        results.add_pass("Format message - English")
        
        # Test Persian
        translator.set_language(Language.PERSIAN)
        text = translator.format_message("test_format", value=42)
        assert text == "مقدار: 42", f"Expected 'مقدار: 42', got '{text}'"
        results.add_pass("Format message - Persian")
    except Exception as e:
        results.add_fail("Format message", e)
    
    return results


def test_language_config():
    """Test 9: Language configuration."""
    results = TestResults()
    
    try:
        # Get supported languages
        supported = LanguageConfig.get_supported_languages()
        assert "en" in supported, "English not in supported languages"
        assert "fa" in supported, "Persian not in supported languages"
        results.add_pass("Get supported languages")
        
        # Load default language
        lang = LanguageConfig.get_language()
        assert lang in [Language.ENGLISH, Language.PERSIAN]
        results.add_pass("Load language configuration")
    except Exception as e:
        results.add_fail("Language configuration", e)
    
    return results


def test_translation_coverage():
    """Test 10: Translation coverage."""
    results = TestResults()
    
    try:
        translator = get_translator()
        
        # Sample keys to check
        sample_keys = [
            "dashboard", "positions", "trades", "settings", "logs",
            "start_bot", "stop_bot", "save_settings",
            "account_equity", "total_pnl", "drawdown",
            "buy_signal", "sell_signal", "position_opened",
            "error", "success", "warning"
        ]
        
        missing = []
        for key in sample_keys:
            translator.set_language(Language.ENGLISH)
            en_text = translator.t(key)
            if en_text == key:  # Not found
                missing.append(key)
            
            translator.set_language(Language.PERSIAN)
            fa_text = translator.t(key)
            if fa_text == key:  # Not found
                missing.append(key)
        
        if missing:
            results.add_fail("Translation coverage", f"Missing: {missing}")
        else:
            results.add_pass("Translation coverage")
    except Exception as e:
        results.add_fail("Translation coverage", e)
    
    return results


def test_global_functions():
    """Test 11: Global functions."""
    results = TestResults()
    
    try:
        # Test set_language
        set_language(Language.ENGLISH)
        assert get_translator().get_language() == Language.ENGLISH
        results.add_pass("Global set_language function")
        
        # Test t function
        text = t("dashboard")
        assert text == "Dashboard"
        results.add_pass("Global t function")
        
        # Test set_app_language
        set_app_language(Language.PERSIAN)
        assert get_app_language() == Language.PERSIAN
        results.add_pass("Global set_app_language function")
    except Exception as e:
        results.add_fail("Global functions", e)
    
    return results


def test_fallback_translation():
    """Test 12: Fallback translation."""
    results = TestResults()
    
    try:
        translator = get_translator()
        
        # Test with default
        text = translator.t("nonexistent_key", default="Default Text")
        assert text == "Default Text", f"Expected 'Default Text', got '{text}'"
        results.add_pass("Fallback translation with default")
        
        # Test without default (should return key)
        text = translator.t("nonexistent_key")
        assert text == "nonexistent_key", f"Expected 'nonexistent_key', got '{text}'"
        results.add_pass("Fallback translation without default")
    except Exception as e:
        results.add_fail("Fallback translation", e)
    
    return results


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("BILINGUAL SYSTEM - TEST SUITE")
    print("="*60 + "\n")
    
    all_results = TestResults()
    
    # Run tests
    tests = [
        ("Translator Creation", test_translator_creation),
        ("Language Enum", test_language_enum),
        ("Translation Lookup", test_translation_lookup),
        ("Shorthand Function", test_shorthand_function),
        ("Language Switcher", test_language_switcher),
        ("Listener Pattern", test_listener_pattern),
        ("Add Translation", test_add_translation),
        ("Format Message", test_format_message),
        ("Language Config", test_language_config),
        ("Translation Coverage", test_translation_coverage),
        ("Global Functions", test_global_functions),
        ("Fallback Translation", test_fallback_translation),
    ]
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        results = test_func()
        all_results.passed += results.passed
        all_results.failed += results.failed
        all_results.tests.extend(results.tests)
    
    # Print summary
    all_results.print_summary()
    
    return all_results.failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
