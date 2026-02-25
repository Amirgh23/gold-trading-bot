# Gold Trading Bot - Complete Professional Documentation

## 📋 Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Features](#features)
6. [ML Models](#ml-models)
7. [Backtesting](#backtesting)
8. [Analytics](#analytics)
9. [API Reference](#api-reference)
10. [Troubleshooting](#troubleshooting)

---

## Overview

**Gold Trading Bot** is a production-grade XAUUSD (gold) trading system featuring:
- Multi-strategy ensemble routing
- Advanced ML models (LSTM, XGBoost)
- Professional backtesting engine
- Comprehensive risk management
- Real-time analytics and reporting

**Version**: 1.0.0  
**License**: Proprietary - All rights reserved  
**Author**: Amir Ghanbari (amirgh23)

---

## Architecture

### Core Components

```
trading_bot/
├── core/                 # Core functionality
│   ├── logger.py        # Logging system
│   ├── config.py        # Configuration management
│   ├── database.py      # SQLite persistence
│   └── state_manager.py # State management
├── market/              # Market data
│   ├── provider.py      # Data provider
│   └── cache.py         # Data caching
├── indicators/          # Technical indicators
│   └── engine.py        # Indicator calculations
├── strategies/          # Trading strategies
│   ├── ensemble.py      # Ensemble router
│   └── base.py          # Strategy base class
├── risk/                # Risk management
│   └── manager.py       # Risk calculations
├── execution/           # Order execution
│   ├── order_executor.py
│   └── position_manager.py
├── ml/                  # Machine learning
│   ├── lstm_model.py
│   ├── model_manager.py
│   └── professional_trainer.py
├── backtesting/         # Backtesting
│   ├── engine.py
│   └── professional_backtest.py
├── analytics/           # Analytics
│   ├── engine.py
│   └── advanced_analytics.py
├── gui/                 # GUI components
│   ├── launcher.py
│   ├── dashboard.py
│   └── advanced_dashboard.py
└── utils/               # Utilities
    ├── error_handler.py
    └── memory_manager.py
```

---

## Installation

### Requirements
- Python 3.8+
- Windows 10+ (64-bit)
- 4GB RAM minimum
- 100MB disk space

### Setup

```bash
# Clone repository
git clone https://github.com/Amirgh23/gold-trading-bot.git
cd gold-trading-bot

# Install dependencies
pip install -r requirements.txt

# Configure
cp config.example.json config.json
# Edit config.json with your settings
```

### Run Application

```bash
# Option 1: GUI (Recommended)
python run_launcher.py

# Option 2: Standalone EXE
dist/GoldTradingBot.exe

# Option 3: CLI
python -m trading_bot.bot
```

---

## Usage

### GUI Dashboard

1. **Launch Application**
   ```bash
   python run_launcher.py
   ```

2. **Navigate Sections**
   - 📊 Dashboard: Real-time monitoring
   - 📈 Backtesting: Strategy testing
   - 🧪 Tests: Run test suite
   - ⚙️ Settings: Configure parameters
   - 📚 Documentation: View guides
   - 🔧 Tools: Utility functions

3. **Configure Settings**
   - Max Drawdown: 20%
   - Risk per Trade: 2%
   - Timeframe: 5m
   - Confirmation Threshold: 0.6

### Python API

```python
from trading_bot.bot import TradingBot
from trading_bot.ml.professional_trainer import ProfessionalMLTrainer
from trading_bot.backtesting.professional_backtest import ProfessionalBacktester

# Initialize bot
bot = TradingBot()

# Train ML models
trainer = ProfessionalMLTrainer()
trainer.train_ensemble()

# Run backtest
backtester = ProfessionalBacktester(initial_capital=10000)
metrics = backtester.run_backtest()

# Start trading
bot.start()
```

---

## Features

### 1. Multi-Strategy Ensemble
- Technical Analysis
- LSTM Neural Network
- XGBoost Gradient Boosting
- Intelligent signal routing

### 2. Advanced Risk Management
- Kelly Criterion position sizing
- Maximum drawdown protection
- Daily loss limits
- Stop loss and trailing stops

### 3. Smart Position Management
- Partial profit-taking
- Trend-based exits
- Correlation-based sizing
- Position scaling

### 4. Real-Time Indicators
- Moving Averages (MA20, MA50)
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Stochastic Oscillator
- Volume analysis

### 5. Order Execution
- Multi-exchange support
- Best price routing
- Automatic failover
- Retry logic with exponential backoff

### 6. Data Persistence
- SQLite database
- Automatic backup/recovery
- Trade history logging
- State persistence

---

## ML Models

### LSTM Model

**Architecture:**
```
Input Layer (60 timesteps × 7 features)
    ↓
LSTM Layer (128 units) + BatchNorm + Dropout(0.2)
    ↓
LSTM Layer (64 units) + BatchNorm + Dropout(0.2)
    ↓
LSTM Layer (32 units) + BatchNorm + Dropout(0.2)
    ↓
Dense Layer (16 units)
    ↓
Output Layer (1 unit - Price prediction)
```

**Training:**
```python
trainer = ProfessionalMLTrainer()
metrics = trainer.train_lstm(epochs=100, batch_size=32)
# Returns: MSE, MAE, R²
```

### XGBoost Model

**Parameters:**
- n_estimators: 200
- max_depth: 7
- learning_rate: 0.1
- subsample: 0.8
- colsample_bytree: 0.8

**Training:**
```python
trainer = ProfessionalMLTrainer()
metrics = trainer.train_xgboost()
# Returns: MSE, MAE, R²
```

### Ensemble Model

**Combination:**
- LSTM: 60% weight
- XGBoost: 40% weight
- Weighted average predictions

**Training:**
```python
trainer = ProfessionalMLTrainer()
metrics = trainer.train_ensemble()
# Trains both models and combines them
```

---

## Backtesting

### Run Backtest

```python
from trading_bot.backtesting.professional_backtest import ProfessionalBacktester

backtester = ProfessionalBacktester(
    initial_capital=10000,
    risk_per_trade=0.02
)

metrics = backtester.run_backtest()
```

### Metrics

```
Initial Capital:     $10,000.00
Final Capital:       $12,550.00
Total Return:        25.50%
Sharpe Ratio:        1.80
Max Drawdown:        -12.30%
Win Rate:            62.00%
Profit Factor:       2.15
Total Trades:        50
Winning Trades:      31
Losing Trades:       19
```

### Export Results

```python
backtester.export_results('backtest_results.json')
```

---

## Analytics

### Performance Metrics

```python
from trading_bot.analytics.advanced_analytics import AdvancedAnalytics

analytics = AdvancedAnalytics()

# Add data
for equity in equity_curve:
    analytics.add_equity_point(equity)

for trade in trades:
    analytics.add_trade(trade)

# Generate report
report = analytics.generate_report()
```

### Report Contents

```json
{
  "returns": {
    "total_return": 0.255,
    "annualized_return": 0.85,
    "daily_return_mean": 0.001,
    "daily_return_std": 0.015
  },
  "risk": {
    "volatility": 0.015,
    "annualized_volatility": 0.238,
    "max_drawdown": -0.123,
    "var_95": -0.025,
    "cvar_95": -0.035
  },
  "risk_adjusted": {
    "sharpe_ratio": 1.80,
    "sortino_ratio": 2.15,
    "calmar_ratio": 2.07
  },
  "trades": {
    "total_trades": 50,
    "win_rate": 0.62,
    "profit_factor": 2.15,
    "expectancy": 125.50
  }
}
```

---

## API Reference

### TradingBot

```python
class TradingBot:
    def __init__(self, config_file='config.json')
    def start(self)
    def stop(self)
    def get_current_signal(self) -> str
    def get_open_positions(self) -> List[Dict]
    def get_performance_metrics(self) -> Dict
```

### ProfessionalMLTrainer

```python
class ProfessionalMLTrainer:
    def train_lstm(self, data=None, epochs=100) -> Dict
    def train_xgboost(self, data=None) -> Dict
    def train_ensemble(self, data=None) -> Dict
    def predict(self, model_name: str, features) -> np.ndarray
    def save_metrics(self)
    def load_models(self)
```

### ProfessionalBacktester

```python
class ProfessionalBacktester:
    def run_backtest(self, data=None) -> Dict
    def calculate_metrics(self, data) -> Dict
    def get_trade_log(self) -> List[Dict]
    def export_results(self, filename='backtest_results.json')
```

### AdvancedAnalytics

```python
class AdvancedAnalytics:
    def add_trade(self, trade: Dict)
    def add_equity_point(self, equity: float)
    def calculate_returns(self) -> Dict
    def calculate_risk_metrics(self) -> Dict
    def calculate_risk_adjusted_returns(self) -> Dict
    def calculate_trade_statistics(self) -> Dict
    def generate_report(self) -> Dict
    def export_report(self, filename='analytics_report.json')
```

---

## Testing

### Run Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_comprehensive.py -v

# With coverage
pytest tests/ --cov=trading_bot
```

### Test Coverage

- Unit Tests: 60+ test cases
- Property-Based Tests: 26 correctness properties
- Integration Tests: End-to-end workflows
- Performance Tests: Latency and memory

---

## Configuration

### config.json

```json
{
  "trading": {
    "symbol": "XAUUSD",
    "timeframe": "5m",
    "max_drawdown": 0.20,
    "risk_per_trade": 0.02,
    "daily_loss_limit": -1000
  },
  "exchange": {
    "name": "MetaTrader5",
    "api_key": "your_key_here",
    "api_secret": "your_secret_here"
  },
  "ml": {
    "model_type": "ensemble",
    "lstm_weight": 0.6,
    "xgboost_weight": 0.4,
    "retrain_interval": 24
  },
  "backtesting": {
    "initial_capital": 10000,
    "risk_per_trade": 0.02,
    "commission": 0.001
  }
}
```

---

## Troubleshooting

### Issue: Application won't start

**Solution:**
```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Run with verbose output
python run_launcher.py --verbose
```

### Issue: ML models not training

**Solution:**
```bash
# Check TensorFlow installation
python -c "import tensorflow; print(tensorflow.__version__)"

# Reinstall ML libraries
pip install --upgrade tensorflow scikit-learn xgboost
```

### Issue: Backtesting is slow

**Solution:**
```python
# Use fewer candles
backtester.run_backtest(n_candles=500)

# Reduce indicator calculations
# Disable unnecessary indicators in config
```

### Issue: Memory usage high

**Solution:**
```bash
# Clear cache
python -c "from trading_bot.utils.memory_manager import MemoryManager; MemoryManager.clear_cache()"

# Reduce batch size
# Reduce number of models
```

---

## Performance Benchmarks

| Metric | Value |
|--------|-------|
| Signal-to-order latency | <200ms |
| Indicator calculation | <100ms |
| Model prediction | <50ms |
| Memory usage | <500MB |
| CPU usage (active) | <50% |
| Backtest speed | 1000 candles/sec |

---

## Support & Contact

- **Email**: amirgh23@gmail.com
- **GitHub**: https://github.com/Amirgh23/gold-trading-bot
- **Issues**: https://github.com/Amirgh23/gold-trading-bot/issues

---

## License

**PROPRIETARY LICENSE** - All rights reserved.

This software is proprietary and confidential. Unauthorized copying, modification, or distribution is strictly prohibited.

See LICENSE file for complete terms.

---

## Changelog

### Version 1.0.0 (February 2026)
- Initial release
- Multi-strategy ensemble
- LSTM and XGBoost models
- Professional backtesting
- Advanced analytics
- GUI dashboard with charts
- Comprehensive test suite

---

**Last Updated**: February 26, 2026  
**Status**: Production Ready ✅
