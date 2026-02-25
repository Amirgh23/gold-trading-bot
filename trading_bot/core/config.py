"""Configuration management system with validation."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class RiskConfig:
    """Risk management configuration."""
    max_position_size_percent: float = 2.0  # Max 2% of account per trade
    max_concurrent_positions: int = 5
    max_drawdown_percent: float = 20.0
    daily_loss_limit_percent: float = 5.0
    risk_per_trade_percent: float = 1.0
    kelly_fraction: float = 0.25  # Conservative Kelly fraction
    
    def validate(self):
        """Validate configuration parameters."""
        if not 0 < self.max_position_size_percent <= 10:
            raise ValueError("max_position_size_percent must be between 0 and 10")
        if self.max_concurrent_positions < 1:
            raise ValueError("max_concurrent_positions must be at least 1")
        if not 0 < self.max_drawdown_percent <= 50:
            raise ValueError("max_drawdown_percent must be between 0 and 50")
        if not 0 < self.daily_loss_limit_percent <= 20:
            raise ValueError("daily_loss_limit_percent must be between 0 and 20")
        if not 0 < self.risk_per_trade_percent <= 5:
            raise ValueError("risk_per_trade_percent must be between 0 and 5")
        if not 0 < self.kelly_fraction <= 1:
            raise ValueError("kelly_fraction must be between 0 and 1")


@dataclass
class StrategyConfig:
    """Strategy configuration."""
    technical_enabled: bool = True
    lstm_enabled: bool = True
    dqn_enabled: bool = True
    confirmation_threshold: int = 2  # Require 2 strategies to confirm
    high_volatility_threshold: float = 2.0  # 2 std dev
    high_volatility_confirmation: int = 3  # Require 3 strategies when volatile
    
    def validate(self):
        """Validate strategy configuration."""
        if self.confirmation_threshold < 1:
            raise ValueError("confirmation_threshold must be at least 1")
        if self.high_volatility_confirmation < self.confirmation_threshold:
            raise ValueError("high_volatility_confirmation must be >= confirmation_threshold")


@dataclass
class ExchangeConfig:
    """Exchange configuration."""
    exchange: str = "binance"
    symbol: str = "XAUUSD"
    timeframe: str = "2m"
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    sandbox_mode: bool = True
    
    def validate(self):
        """Validate exchange configuration."""
        if not self.exchange:
            raise ValueError("exchange must be specified")
        if not self.symbol:
            raise ValueError("symbol must be specified")
        if self.sandbox_mode and (not self.api_key or not self.api_secret):
            logger.warning("API credentials not set, using sandbox mode")


class ConfigManager:
    """Manages application configuration with validation."""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.risk = RiskConfig()
        self.strategy = StrategyConfig()
        self.exchange = ExchangeConfig()
        self._load_from_env()
        self._load_from_file()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        # Exchange config from env
        if api_key := os.getenv('TRADING_BOT_API_KEY'):
            self.exchange.api_key = api_key
        if api_secret := os.getenv('TRADING_BOT_API_SECRET'):
            self.exchange.api_secret = api_secret
        if exchange := os.getenv('TRADING_BOT_EXCHANGE'):
            self.exchange.exchange = exchange
        if symbol := os.getenv('TRADING_BOT_SYMBOL'):
            self.exchange.symbol = symbol
    
    def _load_from_file(self):
        """Load configuration from JSON file."""
        if not Path(self.config_file).exists():
            logger.info(f"Config file {self.config_file} not found, using defaults")
            return
        
        try:
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
            
            # Load risk config
            if 'risk' in config_data:
                self.risk = RiskConfig(**config_data['risk'])
            
            # Load strategy config
            if 'strategy' in config_data:
                self.strategy = StrategyConfig(**config_data['strategy'])
            
            # Load exchange config
            if 'exchange' in config_data:
                self.exchange = ExchangeConfig(**config_data['exchange'])
            
            logger.info(f"Configuration loaded from {self.config_file}")
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
            raise
    
    def save(self, filepath: Optional[str] = None):
        """Save current configuration to file."""
        filepath = filepath or self.config_file
        
        config_data = {
            'risk': asdict(self.risk),
            'strategy': asdict(self.strategy),
            'exchange': asdict(self.exchange),
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(config_data, f, indent=2)
            logger.info(f"Configuration saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            raise
    
    def validate(self):
        """Validate all configuration sections."""
        try:
            self.risk.validate()
            self.strategy.validate()
            self.exchange.validate()
            logger.info("Configuration validation passed")
        except ValueError as e:
            logger.error(f"Configuration validation failed: {e}")
            raise
    
    def get_template(self, style: str = "balanced") -> Dict[str, Any]:
        """Get configuration template for different trading styles."""
        templates = {
            "aggressive": {
                "risk": {
                    "max_position_size_percent": 3.0,
                    "max_concurrent_positions": 5,
                    "max_drawdown_percent": 30.0,
                    "daily_loss_limit_percent": 10.0,
                    "risk_per_trade_percent": 2.0,
                    "kelly_fraction": 0.5,
                },
                "strategy": {
                    "confirmation_threshold": 1,
                    "high_volatility_confirmation": 2,
                }
            },
            "balanced": {
                "risk": {
                    "max_position_size_percent": 2.0,
                    "max_concurrent_positions": 5,
                    "max_drawdown_percent": 20.0,
                    "daily_loss_limit_percent": 5.0,
                    "risk_per_trade_percent": 1.0,
                    "kelly_fraction": 0.25,
                },
                "strategy": {
                    "confirmation_threshold": 2,
                    "high_volatility_confirmation": 3,
                }
            },
            "conservative": {
                "risk": {
                    "max_position_size_percent": 1.0,
                    "max_concurrent_positions": 3,
                    "max_drawdown_percent": 10.0,
                    "daily_loss_limit_percent": 2.0,
                    "risk_per_trade_percent": 0.5,
                    "kelly_fraction": 0.1,
                },
                "strategy": {
                    "confirmation_threshold": 3,
                    "high_volatility_confirmation": 3,
                }
            }
        }
        
        return templates.get(style, templates["balanced"])
