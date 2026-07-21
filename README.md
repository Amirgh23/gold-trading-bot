# Gold Trading Bot

A risk-first Python research and paper-trading system for a liquid gold proxy
(`PAXG/USDT` by default). It includes validated market-data ingestion, technical
signals, position/risk management, backtesting components, persistence, and a
desktop dashboard.

> Trading is risky. No strategy or software can guarantee profit. Treat results
> as research until they survive out-of-sample, walk-forward, fee/slippage, and
> paper-trading validation. The main orchestrator currently manages simulated
> positions; it does **not** place live orders.

## Safety improvements

- Paper/sandbox configuration by default; no credentials are committed.
- Position size is based on stop distance and capped by notional exposure.
- Daily-loss and maximum-drawdown circuit breakers block new entries.
- Fresh-candle gating prevents duplicate entries while polling.
- Signals require a fresh EMA crossover, a slower-trend filter, RSI bounds, and
  ATR-based stop/target levels.
- Market data is validated, retried with bounded backoff, cached, and returned in
  UTC chronological order.
- Long and short P&L are calculated with the correct sign.
- Unimplemented LSTM/DQN paths are disabled instead of being presented as active.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
copy config.example.json config.json
python -m pytest tests -q
python -m trading_bot.bot
```

For a broker other than Binance, choose a symbol and timeframe supported by that
broker. `XAUUSD` is not a Binance spot symbol; `PAXG/USDT` is used as the default
gold-backed crypto proxy.

## Configuration

The only supported top-level sections are `risk`, `strategy`, and `exchange`.
Start from `config.example.json`; unknown keys fail during dataclass loading so
configuration mistakes are visible immediately.

Recommended initial process:

1. Keep `sandbox_mode` enabled and risk at 0.25–0.5% per trade.
2. Backtest on clean data with realistic spread, fees, and slippage.
3. Select parameters only on training windows, then evaluate untouched test
   windows and multiple market regimes.
4. Paper trade for several weeks and compare fills against the simulation.
5. Consider live execution only after defining broker-specific contract size,
   tick value, minimum quantity, and an external kill switch.

## Architecture

```text
trading_bot/
  market/        validated provider and bounded cache
  indicators/    vectorized technical indicators
  strategies/    confidence filtering and ensemble routing
  risk/          stop-distance sizing and circuit breakers
  execution/     order and position lifecycle
  backtesting/   simulation, walk-forward, and Monte Carlo tools
  core/          config, database, logging, and state
  gui/           monitoring dashboards
```

Run all tests with `python -m pytest tests -q`.

## License

Proprietary. See `LICENSE`.
