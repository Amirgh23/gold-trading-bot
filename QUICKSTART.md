# Gold Trading Bot - Quick Start Guide

## Installation

```bash
# Clone or download the project
cd trading_bot

# Install dependencies
pip install -r requirements.txt

# Create configuration file
cp config.example.json config.json
```

## Configuration

Edit `config.json` to set your trading parameters:

```json
{
  "risk": {
    "max_position_size_percent": 2.0,
    "max_concurrent_positions": 5,
    "max_drawdown_percent": 20.0,
    "daily_loss_limit_percent": 5.0,
    "risk_per_trade_percent": 1.0,
    "kelly_fraction": 0.25
  },
  "strategy": {
    "technical_enabled": true,
    "lstm_enabled": true,
    "dqn_enabled": true,
    "confirmation_threshold": 2,
    "high_volatility_threshold": 2.0,
    "high_volatility_confirmation": 3
  },
  "exchange": {
    "exchange": "binance",
    "symbol": "XAUUSD",
    "timeframe": "2m",
    "sandbox_mode": true
  }
}
```

## Running the Bot

### Start Trading Bot

```python
from trading_bot.bot import TradingBot

# Initialize bot
bot = TradingBot("config.json")

# Start trading
bot.start()
```

### Run Backtesting

```python
from trading_bot.backtesting.engine import BacktestEngine
from trading_bot.market.provider import MarketDataProvider
import pandas as pd

# Load historical data
provider = MarketDataProvider()
df = provider.get_ohlcv("XAUUSD", "2m", limit=1000)

# Create backtest engine
backtest = BacktestEngine(initial_equity=10000)

# Run backtest
results = backtest.run_backtest(
    df,
    signal_generator=your_signal_function,
    position_manager=position_manager,
    risk_manager=risk_manager,
)

print(f"Total Trades: {results['total_trades']}")
print(f"Win Rate: {results['win_rate']:.2f}%")
print(f"Profit Factor: {results['profit_factor']:.2f}")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
```

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_risk_manager.py -v

# Run with coverage
pytest tests/ --cov=trading_bot
```

## Key Components

### 1. Market Data Provider
```python
from trading_bot.market.provider import MarketDataProvider

provider = MarketDataProvider("binance", "XAUUSD")
df = provider.get_ohlcv("XAUUSD", "2m", limit=100)
price = provider.get_current_price()
bid, ask = provider.get_bid_ask()
```

### 2. Indicator Engine
```python
from trading_bot.indicators.engine import IndicatorEngine

df = IndicatorEngine.calculate_all(df)
trend = IndicatorEngine.detect_trend(df)
levels = IndicatorEngine.find_support_resistance(df)
volatility = IndicatorEngine.calculate_volatility(df)
```

### 3. Risk Manager
```python
from trading_bot.risk.manager import RiskManager

risk_mgr = RiskManager(
    account_equity=10000,
    max_position_size_percent=2.0,
)

position_size = risk_mgr.calculate_position_size(
    entry_price=2000,
    stop_loss=1990,
    win_rate=0.55,
    risk_reward_ratio=2.0,
)
```

### 4. Position Manager
```python
from trading_bot.execution.position_manager import PositionManager

pos_mgr = PositionManager()

# Open position
position = pos_mgr.open_position(signal, size=1.0)

# Update price
pos_mgr.update_position_price(position.id, current_price)

# Check exit conditions
exit_reason = pos_mgr.check_exit_conditions(position.id, current_price)

# Close position
trade = pos_mgr.close_position(position.id, exit_price, "TAKE_PROFIT")
```

### 5. Ensemble Router
```python
from trading_bot.strategies.ensemble import EnsembleRouter

router = EnsembleRouter()

# Route signals through ensemble
ensemble_signal = router.route_signal(
    signals=[signal1, signal2, signal3],
    volatility=1.5,
    confirmation_threshold=2,
)

if ensemble_signal:
    print(f"Recommendation: {ensemble_signal.recommendation}")
    print(f"Confidence: {ensemble_signal.confidence}%")
```

### 6. Analytics Engine
```python
from trading_bot.analytics.engine import AnalyticsEngine

# Calculate metrics
metrics = AnalyticsEngine.calculate_metrics(trades)
print(f"Win Rate: {metrics.win_rate:.2f}%")
print(f"Sharpe Ratio: {metrics.sharpe_ratio:.2f}")

# Generate reports
daily_report = AnalyticsEngine.generate_daily_report(trades, date)
monthly_report = AnalyticsEngine.generate_monthly_report(trades, 2024, 1)

# Compare strategies
comparison = AnalyticsEngine.compare_strategies(trades)
```

## Configuration Templates

### Aggressive Strategy
```python
config.get_template("aggressive")
# Max position: 3%, Confirmation: 1, Drawdown: 30%
```

### Balanced Strategy
```python
config.get_template("balanced")
# Max position: 2%, Confirmation: 2, Drawdown: 20%
```

### Conservative Strategy
```python
config.get_template("conservative")
# Max position: 1%, Confirmation: 3, Drawdown: 10%
```

## Environment Variables

```bash
export TRADING_BOT_API_KEY=your_api_key
export TRADING_BOT_API_SECRET=your_api_secret
export TRADING_BOT_EXCHANGE=binance
export TRADING_BOT_SYMBOL=XAUUSD
```

## Logging

Logs are stored in `logs/` directory in JSON format:

```bash
# View logs
tail -f logs/trading_bot.json

# Parse JSON logs
cat logs/trading_bot.json | jq '.message'
```

## Database

SQLite database is stored in `trading_bot.db`:

```python
from trading_bot.core.database import DatabaseManager

db = DatabaseManager()

# Get trade history
trades = db.get_trade_history(
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 1, 31),
)

# Get open positions
positions = db.get_open_positions()

# Backup database
db.backup("backup.db")
```

## Troubleshooting

### Connection Issues
- Check API credentials in config.json
- Verify exchange is accessible
- Check network connectivity

### Insufficient Data
- Ensure at least 50 candles are available
- Check timeframe setting
- Verify symbol is correct

### Performance Issues
- Reduce number of concurrent positions
- Increase cache TTL
- Use lower timeframe for faster updates

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review configuration in `config.json`
3. Run tests to verify installation
4. Check documentation in `IMPLEMENTATION_PROGRESS.md`

## Next Steps

1. **Backtest Strategy**: Run backtests on historical data
2. **Paper Trading**: Test on demo account
3. **Live Trading**: Start with small position sizes
4. **Monitor Performance**: Track metrics and adjust parameters
5. **Optimize**: Use walk-forward analysis to optimize parameters

---

**Happy Trading! 🚀**
