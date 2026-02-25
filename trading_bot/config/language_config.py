"""Language configuration for the trading bot."""

from trading_bot.i18n.translations import Language
import json
from pathlib import Path


class LanguageConfig:
    """Manages language configuration."""
    
    CONFIG_FILE = Path("config/language.json")
    
    DEFAULT_CONFIG = {
        "language": "en",
        "auto_detect": False,
        "supported_languages": ["en", "fa"]
    }
    
    @classmethod
    def load(cls) -> dict:
        """Load language configuration from file."""
        try:
            if cls.CONFIG_FILE.exists():
                with open(cls.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading language config: {e}")
        
        return cls.DEFAULT_CONFIG.copy()
    
    @classmethod
    def save(cls, config: dict) -> bool:
        """Save language configuration to file."""
        try:
            cls.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(cls.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving language config: {e}")
            return False
    
    @classmethod
    def get_language(cls) -> Language:
        """Get configured language."""
        config = cls.load()
        lang_code = config.get("language", "en")
        
        if lang_code == "fa":
            return Language.PERSIAN
        return Language.ENGLISH
    
    @classmethod
    def set_language(cls, language: Language) -> bool:
        """Set and save language."""
        config = cls.load()
        config["language"] = language.value
        return cls.save(config)
    
    @classmethod
    def get_supported_languages(cls) -> list:
        """Get list of supported languages."""
        config = cls.load()
        return config.get("supported_languages", ["en", "fa"])
