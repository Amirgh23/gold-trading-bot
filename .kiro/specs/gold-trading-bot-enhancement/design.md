# Gold Trading Bot Enhancement - Design Document

## Overview

The enhanced Gold Trading Bot is a production-grade, multi-strategy trading system for XAUUSD (gold) on 2-minute timeframes. The system intelligently combines Technical Analysis, LSTM Machine Learning, and DQN Reinforcement Learning strategies with advanced risk management, real-time monitoring, and comprehensive analytics.

**Key Design Principles:**
- Profitability through intelligent signal confirmation and ensemble methods
- Reliability through robust error handling and automatic recovery
- Adaptability through dynamic parameter adjustment and market regime detection
- Transparency through comprehensive logging and analytics
- Performance through optimized code and low-latency execution

## Architecture

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Trading Bot System                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Market Data Layer                           │  │
│  │  - Real-time price feeds (2-min candles)               │  │
│  │  - Multiple exchange support (Binance, etc.)           │  │
│  │  - Data caching and fallback mechanisms                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Indicator Calculation Engine                  │  │
│  │  - 15+ technical indicators (EMA, RSI, MACD, etc.)     │  │
│  │  - Real-time calculation (<100ms)                      │  │
│  │  - Support/Resistance detection                        │  │
│  │  - Trend and volatility analysis                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Multi-Strategy Signal Generation                │  │
│  │  ┌─────────────────┐  ┌─────────────────┐              │  │
│  │  │ Technical       │  │ LSTM ML         │              │  │
│  │  │ Analysis        │  │ Prediction      │              │  │
│  │  │ Strategy        │  │ Strategy        │              │  │
│  │  └─────────────────┘  └─────────────────┘              │  │
│  │  ┌─────────────────┐  ┌─────────────────┐              │  │
│  │  │ DQN RL          │  │ Multi-Timeframe │              │  │
│  │  │ Strategy        │  │ Confirmation    │              │  │
│  │  └─────────────────┘  └─────────────────┘              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Ensemble Signal Router                          │  │
│  │  - Weighted voting based on strategy accuracy          │  │
│  │  - Confirmation threshold (2-3 strategies)             │  │
│  │  - Conflict detection and resolution                   │  │
│  │  - Confidence scoring                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Risk Management & Position Sizing               │  │
│  │  - Kelly Criterion calculation                         │  │
│  │  - Dynamic position sizing based on equity             │  │
│  │  - Drawdown protection                                 │  │
│  │  - Volatility adjustment                               │  │
│  │  - Correlation analysis                                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Order Execution Engine                          │  │
│  │  - Multi-exchange routing                              │  │
│  │  - Slippage estimation                                 │  │
│  │  - Partial fill handling                               │  │
│  │  - Order status tracking                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Position Management                            │  │
│  │  - Entry/exit execution                                │  │
│  │  - Stop loss and take profit management                │  │
│  │  - Trailing stop implementation                        │  │
│  │  - Partial profit-taking                               │  │
│  │  - Time-based exits                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Data Persistence Layer                          │  │
│  │  - Trade history database                              │  │
│  │  - Performance metrics storage                         │  │
│  │  - Configuration persistence                           │  │
│  │  - Backup and recovery                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Analytics & Reporting                          │  │
│  │  - Real-time dashboard                                 │  │
│  │  - Performance metrics calculation                     │  │
│  │  - Trade analysis and reporting                        │  │
│  │  - Backtesting and optimization                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

```
Market Data → Indicators → Strategies → Ensemble Router → Risk Management 
→ Order Execution → Position Management → Data Persistence → Analytics
```

## Components and Interfaces

### 1. Market Data Layer

**Purpose:** Fetch and manage real-time market data from exchanges

**Key Components:**
- `MarketDataProvider`: Fetches OHLCV data from exchanges
- `DataCache`: Caches recent data for fast access
- `FallbackManager`: Handles connection failures with automatic retry

**Interface:**
```python
class MarketDataProvider:
    def get_ohlcv(symbol: str, timeframe: str, limit: int) -> DataFrame
    def get_current_price(symbol: str) -> float
    def get_bid_ask(symbol: str) -> Tuple[float, float]
    def subscribe_to_updates(callback: Callable) -> None
```

**Responsibilities:**
- Connect to exchange API with authentication
- Fetch 2-minute OHLCV candles
- Handle connection failures with exponential backoff
- Cache data in memory for fast access
- Provide fallback data during outages

### 2. Indicator Calculation Engine

**Purpose:** Calculate 15+ technical indicators in real-time

**Key Indicators:**
- Trend: EMA (5, 13, 50, 200), ADX
- Momentum: RSI, MACD, Stochastic, CCI
- Volatility: Bollinger Bands, ATR, Standard Deviation
- Volume: OBV, Volume Rate of Change
- Support/Resistance: Swing highs/lows, Pivot points

**Interface:**
```python
class IndicatorEngine:
    def calculate_all(df: DataFrame) -> DataFrame
    def detect_trend(df: DataFrame) -> str  # 'uptrend', 'downtrend', 'sideways'
    def find_support_resistance(df: DataFrame) -> Dict[str, List[float]]
    def calculate_volatility(df: DataFrame) -> float
    def detect_divergence(df: DataFrame) -> Dict[str, bool]
```

**Responsibilities:**
- Calculate indicators efficiently (<100ms)
- Detect market regime (trend, consolidation, breakout)
- Identify support and resistance levels
- Calculate volatility and momentum
- Detect technical divergences

### 3. Multi-Strategy Signal Generation

**Purpose:** Generate trading signals from multiple strategies

**Strategies:**
1. **Technical Analysis Strategy**: EMA crossover + RSI confirmation
2. **LSTM ML Strategy**: Neural network price prediction
3. **DQN RL Strategy**: Reinforcement learning agent
4. **Multi-Timeframe Strategy**: Confirmation across timeframes

**Interface:**
```python
class Strategy:
    def generate_signal(df: DataFrame) -> Optional[Signal]
    def get_confidence() -> float  # 0-100%
    def get_performance_metrics() -> Dict[str, float]

class Signal:
    direction: str  # 'BUY', 'SELL'
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float
    strategy_name: str
    timestamp: datetime
```

**Responsibilities:**
- Generate BUY/SELL signals based on strategy logic
- Provide confidence scores
- Track historical accuracy
- Adapt parameters based on market conditions

### 4. Ensemble Signal Router

**Purpose:** Intelligently combine signals from multiple strategies

**Logic:**
- Weighted voting based on strategy accuracy
- Confirmation threshold (2-3 strategies)
- Conflict detection and resolution
- Confidence scoring

**Interface:**
```python
class EnsembleRouter:
    def route_signal(signals: List[Signal]) -> Optional[EnsembleSignal]
    def update_strategy_weights(performance: Dict[str, float]) -> None
    def get_confirmation_status(signals: List[Signal]) -> Dict[str, Any]

class EnsembleSignal:
    direction: str
    confidence: float
    confirming_strategies: List[str]
    conflicting_strategies: List[str]
    recommendation: str  # 'STRONG_BUY', 'BUY', 'HOLD', 'SELL', 'STRONG_SELL'
```

**Responsibilities:**
- Combine signals from multiple strategies
- Weight signals based on historical accuracy
- Require confirmation from multiple strategies
- Detect and handle conflicting signals
- Provide ensemble confidence score

### 5. Risk Management & Position Sizing

**Purpose:** Calculate position size and enforce risk limits

**Algorithms:**
- Kelly Criterion for optimal position sizing
- Dynamic sizing based on account equity
- Drawdown protection
- Volatility adjustment
- Correlation analysis

**Interface:**
```python
class RiskManager:
    def calculate_position_size(
        entry_price: float,
        stop_loss: float,
        account_equity: float,
        win_rate: float,
        risk_reward_ratio: float
    ) -> float
    
    def check_risk_limits(
        position_size: float,
        account_equity: float,
        current_drawdown: float
    ) -> bool
    
    def adjust_for_volatility(
        position_size: float,
        volatility: float
    ) -> float
    
    def calculate_correlation_adjustment(
        open_positions: List[Position],
        new_position: Position
    ) -> float
```

**Responsibilities:**
- Calculate optimal position size using Kelly Criterion
- Enforce maximum position size (2% of account)
- Enforce maximum concurrent positions (5)
- Protect against drawdown (reduce size at 80% of limit)
- Adjust for volatility and correlation
- Track daily loss and stop trading if limit reached

### 6. Order Execution Engine

**Purpose:** Execute orders on exchanges with optimal routing

**Features:**
- Multi-exchange support
- Price comparison and best execution
- Slippage estimation
- Partial fill handling
- Order status tracking

**Interface:**
```python
class OrderExecutor:
    def place_order(
        symbol: str,
        side: str,  # 'BUY', 'SELL'
        size: float,
        order_type: str = 'MARKET'
    ) -> Order
    
    def get_order_status(order_id: str) -> OrderStatus
    def cancel_order(order_id: str) -> bool
    def get_best_price(symbol: str, side: str) -> float

class Order:
    id: str
    symbol: str
    side: str
    size: float
    filled_size: float
    average_price: float
    status: str
    timestamp: datetime
```

**Responsibilities:**
- Connect to exchange API
- Place market orders with optimal routing
- Handle partial fills
- Track order status
- Estimate and handle slippage
- Retry failed orders

### 7. Position Management

**Purpose:** Manage open positions with smart exits

**Features:**
- Entry/exit execution
- Stop loss and take profit management
- Trailing stop implementation
- Partial profit-taking
- Time-based exits

**Interface:**
```python
class PositionManager:
    def open_position(signal: Signal, size: float) -> Position
    def close_position(position: Position, reason: str) -> Trade
    def update_trailing_stop(position: Position, current_price: float) -> None
    def take_partial_profit(position: Position, percentage: float) -> None
    def check_exit_conditions(position: Position, current_price: float) -> Optional[str]

class Position:
    id: str
    symbol: str
    side: str  # 'LONG', 'SHORT'
    entry_price: float
    entry_time: datetime
    size: float
    stop_loss: float
    take_profit: float
    trailing_stop: Optional[float]
    current_price: float
    unrealized_pnl: float
    entry_reason: str
```

**Responsibilities:**
- Open positions based on signals
- Manage stop loss and take profit
- Implement trailing stops
- Execute partial profit-taking
- Close positions based on exit conditions
- Track position P&L

### 8. Data Persistence Layer

**Purpose:** Store and retrieve trading data

**Storage:**
- SQLite database for trades and performance metrics
- JSON files for configuration
- CSV exports for analysis

**Interface:**
```python
class DataPersistence:
    def save_trade(trade: Trade) -> None
    def get_trade_history(start_date: datetime, end_date: datetime) -> List[Trade]
    def save_performance_metrics(metrics: Dict[str, float]) -> None
    def get_performance_metrics(date: datetime) -> Dict[str, float]
    def backup_database() -> str
    def restore_database(backup_path: str) -> None
```

**Responsibilities:**
- Persist all trades to database
- Store performance metrics
- Maintain configuration
- Provide data export functionality
- Implement backup and recovery

### 9. Analytics & Reporting

**Purpose:** Calculate performance metrics and generate reports

**Metrics:**
- Win rate, profit factor, Sharpe ratio
- Maximum drawdown, recovery factor
- Monthly and daily returns
- Strategy performance comparison

**Interface:**
```python
class Analytics:
    def calculate_metrics(trades: List[Trade]) -> Dict[str, float]
    def generate_daily_report(date: datetime) -> Report
    def generate_monthly_report(year: int, month: int) -> Report
    def compare_strategies(start_date: datetime, end_date: datetime) -> Dict[str, Dict[str, float]]
    def generate_equity_curve(trades: List[Trade]) -> List[float]
```

**Responsibilities:**
- Calculate performance metrics
- Generate daily/monthly reports
- Compare strategy performance
- Generate equity curves and drawdown charts
- Provide analytics dashboard data

## Data Models

### Trade Model

```python
class Trade:
    id: str
    symbol: str
    entry_time: datetime
    entry_price: float
    entry_size: float
    entry_reason: str
    exit_time: datetime
    exit_price: float
    exit_size: float
    exit_reason: str
    pnl: float
    pnl_percent: float
    strategy: str
    timeframe: str
    stop_loss: float
    take_profit: float
    max_profit: float
    max_loss: float
    duration: timedelta
```

### Position Model

```python
class Position:
    id: str
    symbol: str
    side: str  # 'LONG', 'SHORT'
    entry_price: float
    entry_time: datetime
    entry_size: float
    current_price: float
    current_size: float
    stop_loss: float
    take_profit: float
    trailing_stop: Optional[float]
    unrealized_pnl: float
    unrealized_pnl_percent: float
    entry_reason: str
    strategy: str
```

### Signal Model

```python
class Signal:
    id: str
    timestamp: datetime
    symbol: str
    direction: str  # 'BUY', 'SELL'
    strategy: str
    confidence: float  # 0-100%
    entry_price: float
    stop_loss: float
    take_profit: float
    indicators: Dict[str, float]
    reason: str
```

### Performance Metrics Model

```python
class PerformanceMetrics:
    date: datetime
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    sharpe_ratio: float
    max_drawdown: float
    recovery_factor: float
    daily_pnl: float
    cumulative_pnl: float
    strategy_performance: Dict[str, Dict[str, float]]
```

## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

