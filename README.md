# Gold Trading Bot - Enhanced Edition

A production-grade XAUUSD (gold) trading bot with multi-strategy ensemble, advanced risk management, and real-time monitoring.

## Features

- **Multi-Strategy Ensemble**: Technical Analysis + LSTM ML + DQN RL with intelligent routing
- **Advanced Risk Management**: Kelly Criterion position sizing, drawdown protection, daily loss limits
- **Smart Position Management**: Trailing stops, partial profit-taking, trend-based exits
- **Real-Time Indicators**: 15+ technical indicators with <100ms calculation
- **ML Models**: LSTM with automatic retraining and confidence scoring
- **Backtesting**: Walk-forward analysis with Monte Carlo simulation
- **Multi-Timeframe**: 2m/5m/15m confirmation system
- **Order Execution**: Multi-exchange support with automatic failover
- **Data Persistence**: SQLite with backup/recovery
- **Error Handling**: Exponential backoff retry, crash recovery
- **GUI Dashboard**: Real-time monitoring with PyQt5
- **Comprehensive Logging**: JSON-formatted trade/signal/error logs

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure
cp config.example.json config.json
# Edit config.json with your settings

# Run bot
python -m trading_bot.bot

# Run GUI
python run_gui.py

# Run tests
pytest tests/
```

## Architecture

```
trading_bot/
├── core/          # Logger, Config, Database, State Manager
├── market/        # Data Provider, Cache
├── indicators/    # Technical Indicators Engine
├── strategies/    # Ensemble Router, Strategy Base
├── risk/          # Risk Manager, Position Sizing
├── execution/     # Order Executor, Position Manager
├── ml/            # LSTM Model, Model Manager
├── backtesting/   # Backtest Engine, Monte Carlo
├── analytics/     # Performance Metrics
├── gui/           # Dashboard, Alerts
└── utils/         # Error Handler, Memory Manager
```

## Configuration

See `config.example.json` for all available options:
- Trading parameters (risk, position size, timeframes)
- Exchange settings (API keys, symbols)
- ML model settings (retraining triggers, confidence thresholds)
- GUI preferences (alerts, notifications)

## Testing

```bash
# Unit tests
pytest tests/test_*.py -v

# Property-based tests
pytest tests/test_properties_pbt.py -v

# Coverage
pytest --cov=trading_bot tests/
```

## Documentation

- `QUICKSTART.md` - Quick start guide
- `DEPLOYMENT_GUIDE.md` - Production deployment
- `FINAL_REPORT.md` - Project completion report
- `.kiro/specs/` - Full specification and design documents

## Performance

- Signal-to-order latency: <200ms
- Indicator calculation: <100ms
- Memory usage: <500MB
- CPU usage: <50% (active trading)

## License

MIT

## Author

amirgh23
