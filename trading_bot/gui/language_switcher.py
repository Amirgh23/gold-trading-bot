"""Language switcher for GUI applications."""

from typing import Callable, List
from trading_bot.i18n.translations import Language, get_translator


class LanguageSwitcher:
    """Manages language switching for the application."""
    
    def __init__(self):
        self.current_language = Language.ENGLISH
        self.listeners: List[Callable[[Language], None]] = []
        self.translator = get_translator()
    
    def set_language(self, language: Language) -> None:
        """
        Set application language and notify all listeners.
        
        Args:
            language: Language to switch to
        """
        self.current_language = language
        self.translator.set_language(language)
        
        # Notify all listeners
        for listener in self.listeners:
            try:
                listener(language)
            except Exception as e:
                print(f"Error notifying language change listener: {e}")
    
    def get_language(self) -> Language:
        """Get current language."""
        return self.current_language
    
    def register_listener(self, callback: Callable[[Language], None]) -> None:
        """
        Register a callback to be notified when language changes.
        
        Args:
            callback: Function to call with new language
        """
        self.listeners.append(callback)
    
    def unregister_listener(self, callback: Callable[[Language], None]) -> None:
        """Unregister a language change listener."""
        if callback in self.listeners:
            self.listeners.remove(callback)
    
    def translate(self, key: str, default: str = "") -> str:
        """Translate a key using current language."""
        return self.translator.translate(key, default)
    
    def t(self, key: str, default: str = "") -> str:
        """Shorthand for translate()."""
        return self.translate(key, default)


# Global language switcher instance
_language_switcher = LanguageSwitcher()


def get_language_switcher() -> LanguageSwitcher:
    """Get global language switcher instance."""
    return _language_switcher


def set_app_language(language: Language) -> None:
    """Set application language globally."""
    _language_switcher.set_language(language)


def get_app_language() -> Language:
    """Get current application language."""
    return _language_switcher.get_language()
