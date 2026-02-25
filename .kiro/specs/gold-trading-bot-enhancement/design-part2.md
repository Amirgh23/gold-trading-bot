# Correctness Properties

## Acceptance Criteria Testing Prework

### Requirement 1: Multi-Strategy Ensemble

1.1 WHEN the bot receives signals from Technical Analysis, LSTM, and DQN strategies, THE System SHALL weight each signal based on historical accuracy
  Thoughts: This is a rule that should apply to all signals. We can generate random signals from each strategy with different historical accuracies, then verify that the ensemble weights them correctly.
  Testable: yes - property

1.2 WHEN a signal is generated, THE System SHALL require confirmation from at least 2 independent strategies
  Thoughts: This is a universal rule. We can generate signals from 1, 2, and 3 strategies and verify that trades only execute with 2+ confirmations.
  Testable: yes - property

1.3 WHEN market volatility is high, THE System SHALL increase the confirmation threshold to 3 strategies
  Thoughts: This is a rule about how the system should behave under different volatility conditions. We can generate high-volatility data and verify the threshold increases.
  Testable: yes - property

1.4 WHEN all strategies agree on direction, THE System SHALL increase position size by 20%
  Thoughts: This is a rule about position sizing. We can verify that when all strategies agree, position size increases by exactly 20%.
  Testable: yes - property

### Requirement 2: Risk Management

2.1 WHEN a trade is about to be placed, THE System SHALL calculate position size using Kelly Criterion
  Thoughts: This is a mathematical property. We can verify that position size follows Kelly Criterion formula: f* = (bp - q) / b
  Testable: yes - property

2.2 WHEN account equity changes, THE System SHALL recalculate position size to maintain consistent risk per trade
  Thoughts: This is an invariant. Risk per trade should remain constant regardless of account equity changes.
  Testable: yes - property

2.3 WHEN consecutive losses occur, THE System SHALL reduce position size by 10% per loss
  Thoughts: This is a rule about position sizing after losses. We can verify that each loss reduces position size by exactly 10%.
  Testable: yes - property

2.4 WHEN maximum drawdown limit is approached, THE System SHALL reduce all position sizes by 50%
  Thoughts: This is a threshold-based rule. We can verify that at 80% of drawdown limit, position sizes are reduced by 50%.
  Testable: yes - property

2.5 WHEN daily loss limit is reached, THE System SHALL stop all trading for the remainder of the day
  Thoughts: This is a state-based rule. Once daily loss limit is reached, no new trades should be opened.
  Testable: yes - property

### Requirement 3: Entry and Exit Management

3.1 WHEN a position is entered, THE System SHALL place a hard stop loss at calculated level based on ATR
  Thoughts: This is a rule about stop loss placement. We can verify that stop loss is placed at entry_price ± (ATR * multiplier).
  Testable: yes - property

3.2 WHEN price moves in favor by 1.5x initial risk, THE System SHALL activate trailing stop at breakeven
  Thoughts: This is a rule about trailing stop activation. We can verify that when profit reaches 1.5x risk, trailing stop is set to breakeven.
  Testable: yes - property

3.3 WHEN position reaches 50% of take profit, THE System SHALL close 25% of position
  Thoughts: This is a rule about partial profit-taking. We can verify that at 50% TP, exactly 25% of position is closed.
  Testable: yes - property

3.4 WHEN market conditions change (trend reversal detected), THE System SHALL close position immediately
  Thoughts: This is a rule about trend-based exits. We can verify that trend reversals trigger immediate position closure.
  Testable: yes - property

### Requirement 4: Real-Time Analysis

4.1 WHEN market data is received, THE System SHALL calculate 15+ indicators in real-time (<100ms)
  Thoughts: This is a performance requirement. We can measure calculation time and verify it's under 100ms.
  Testable: yes - property

4.2 WHEN indicators are calculated, THE System SHALL detect trend direction
  Thoughts: This is a rule about trend detection. We can verify that trend is correctly identified based on EMA positions.
  Testable: yes - property

4.3 WHEN volatility changes, THE System SHALL adjust indicator parameters dynamically
  Thoughts: This is a rule about dynamic adjustment. We can verify that parameters change when volatility changes.
  Testable: yes - property

### Requirement 5: ML Model

5.1 WHEN model is trained, THE System SHALL validate on forward data to prevent overfitting
  Thoughts: This is a rule about model validation. We can verify that validation accuracy on forward data is within acceptable range.
  Testable: yes - property

5.2 WHEN model accuracy drops below 55%, THE System SHALL automatically retrain
  Thoughts: This is a threshold-based rule. We can verify that retraining is triggered when accuracy drops below 55%.
  Testable: yes - property

5.3 WHEN confidence is below 40%, THE System SHALL not use ML signal
  Thoughts: This is a rule about signal filtering. We can verify that signals with confidence < 40% are not used.
  Testable: yes - property

### Requirement 6: Backtesting

6.1 WHEN backtesting runs, THE System SHALL simulate trades with realistic slippage and commission
  Thoughts: This is a rule about backtesting accuracy. We can verify that slippage and commission are applied to all trades.
  Testable: yes - property

6.2 WHEN optimization completes, THE System SHALL validate on out-of-sample data
  Thoughts: This is a rule about preventing overfitting. We can verify that optimized parameters perform well on unseen data.
  Testable: yes - property

### Requirement 7: UI

7.1 WHEN the GUI starts, THE System SHALL display real-time price chart
  Thoughts: This is a UI requirement that's not computationally testable.
  Testable: no

7.2 WHEN trades close, THE System SHALL update trading history with complete details
  Thoughts: This is a rule about data persistence. We can verify that all trade details are saved to database.
  Testable: yes - property

### Requirement 8: Error Handling

8.1 WHEN API connection fails, THE System SHALL attempt reconnection with exponential backoff
  Thoughts: This is a rule about retry logic. We can verify that reconnection attempts follow exponential backoff pattern.
  Testable: yes - property

8.2 WHEN system crashes, THE System SHALL save state to persistent storage
  Thoughts: This is a rule about state persistence. We can verify that state is saved before crash.
  Testable: yes - property

8.3 WHEN system restarts, THE System SHALL restore all open positions
  Thoughts: This is a round-trip property. Saving then restoring should result in identical positions.
  Testable: yes - property

### Requirement 9: Performance

9.1 WHEN indicators are calculated, THE System SHALL complete in less than 100ms
  Thoughts: This is a performance requirement. We can measure and verify calculation time.
  Testable: yes - property

9.2 WHEN signal is generated, THE System SHALL place order within 200ms
  Thoughts: This is a latency requirement. We can measure end-to-end latency.
  Testable: yes - property

### Requirement 10: Logging

10.1 WHEN trades occur, THE System SHALL log all trade details
  Thoughts: This is a rule about logging. We can verify that all required fields are logged.
  Testable: yes - property

10.2 WHEN trading day ends, THE System SHALL generate daily summary
  Thoughts: This is a rule about reporting. We can verify that daily summary contains all required metrics.
  Testable: yes - property

### Requirement 11: Configuration

11.1 WHEN user changes parameters, THE System SHALL validate before applying
  Thoughts: This is a rule about parameter validation. We can verify that invalid parameters are rejected.
  Testable: yes - property

11.2 WHEN user saves configuration, THE System SHALL persist to file
  Thoughts: This is a round-trip property. Saving then loading should result in identical configuration.
  Testable: yes - property

### Requirement 12: Data Persistence

12.1 WHEN trades are executed, THE System SHALL persist to database
  Thoughts: This is a rule about data persistence. We can verify that trades are saved to database.
  Testable: yes - property

12.2 WHEN system restarts, THE System SHALL load all historical trades
  Thoughts: This is a round-trip property. Saving then loading should result in identical trade history.
  Testable: yes - property

### Requirement 13: Live Trading

13.1 WHEN order is placed, THE System SHALL route to exchange with best price
  Thoughts: This is a rule about order routing. We can verify that orders are routed to the exchange with best price.
  Testable: yes - property

13.2 WHEN exchange connection fails, THE System SHALL switch to backup exchange
  Thoughts: This is a rule about failover. We can verify that backup exchange is used when primary fails.
  Testable: yes - property

### Requirement 14: Multi-Timeframe

14.1 WHEN signal is generated on 2-minute, THE System SHALL confirm on 5-minute
  Thoughts: This is a rule about multi-timeframe confirmation. We can verify that 5-minute confirmation is checked.
  Testable: yes - property

14.2 WHEN all timeframes align, THE System SHALL increase position size by 25%
  Thoughts: This is a rule about position sizing. We can verify that position size increases by 25% when aligned.
  Testable: yes - property

### Requirement 15: Portfolio Management

15.1 WHEN correlation is high, THE System SHALL reduce position sizes
  Thoughts: This is a rule about correlation-based sizing. We can verify that position sizes are reduced when correlation is high.
  Testable: yes - property

15.2 WHEN portfolio volatility exceeds threshold, THE System SHALL reduce all position sizes
  Thoughts: This is a rule about portfolio-level risk management. We can verify that all positions are reduced.
  Testable: yes - property

## Property Reflection

After analyzing all acceptance criteria, I've identified the following redundancies and consolidations:

- Properties 2.2 and 2.3 can be combined: "Position sizing maintains consistent risk regardless of equity changes and loss streaks"
- Properties 3.2 and 3.3 can be combined: "Trailing stop and partial profit-taking follow defined rules based on profit levels"
- Properties 4.1 and 9.1 are identical: "Indicator calculation completes within 100ms"
- Properties 8.2 and 8.3 can be combined: "State persistence and recovery is a round-trip property"
- Properties 12.1 and 12.2 can be combined: "Trade persistence is a round-trip property"
- Properties 11.2 and 12.2 can be combined: "Configuration and trade persistence are round-trip properties"

## Correctness Properties

### Property 1: Ensemble Signal Weighting
*For any* set of signals from multiple strategies with different historical accuracies, the ensemble should weight each signal proportionally to its historical accuracy, such that higher-accuracy strategies have more influence on the final decision.
**Validates: Requirements 1.1, 1.4**

### Property 2: Confirmation Threshold Enforcement
*For any* generated signal, the system should only execute a trade if confirmed by at least 2 independent strategies under normal volatility, or 3 strategies under high volatility.
**Validates: Requirements 1.2, 1.3**

### Property 3: Position Sizing Consistency
*For any* account equity level and win rate, the position size should follow Kelly Criterion formula and maintain consistent risk per trade (0.5-2% of account), regardless of equity changes or loss streaks.
**Validates: Requirements 2.1, 2.2, 2.3**

### Property 4: Drawdown Protection
*For any* account state, when maximum drawdown limit is approached (80% of threshold), all position sizes should be reduced by 50%, and when daily loss limit is reached, no new trades should be opened.
**Validates: Requirements 2.4, 2.5**

### Property 5: Stop Loss and Trailing Stop
*For any* position, a hard stop loss should be placed at entry ± (ATR * multiplier), and when price moves in favor by 1.5x initial risk, a trailing stop should be activated at breakeven.
**Validates: Requirements 3.1, 3.2**

### Property 6: Partial Profit-Taking
*For any* position reaching profit milestones (50%, 75%, 100% of take profit), the system should close corresponding percentages (25%, 25%, 50%) of the position.
**Validates: Requirements 3.3**

### Property 7: Trend-Based Exit
*For any* open position, when a trend reversal is detected, the position should be closed immediately regardless of profit/loss status.
**Validates: Requirements 3.4**

### Property 8: Indicator Calculation Performance
*For any* market data update, all 15+ technical indicators should be calculated and available within 100ms.
**Validates: Requirements 4.1, 9.1**

### Property 9: Trend Detection Accuracy
*For any* price data, the trend direction (uptrend, downtrend, sideways) should be correctly identified based on EMA positions and ADX values.
**Validates: Requirements 4.2**

### Property 10: Dynamic Parameter Adjustment
*For any* change in market volatility, indicator parameters should be adjusted dynamically to maintain signal quality.
**Validates: Requirements 4.3**

### Property 11: ML Model Validation
*For any* trained LSTM model, validation accuracy on forward data (data after training period) should be within acceptable range to prevent overfitting.
**Validates: Requirements 5.1**

### Property 12: ML Model Retraining Trigger
*For any* model with accuracy below 55%, the system should automatically trigger retraining on latest data.
**Validates: Requirements 5.2**

### Property 13: ML Signal Filtering
*For any* ML signal with confidence below 40%, the signal should not be used for trading decisions.
**Validates: Requirements 5.3**

### Property 14: Backtesting Accuracy
*For any* backtest simulation, all trades should include realistic slippage (0.5-1 pip) and commission (0.001%) in P&L calculations.
**Validates: Requirements 6.1**

### Property 15: Out-of-Sample Validation
*For any* optimized parameter set, performance on out-of-sample data should be within 10% of in-sample performance to indicate no overfitting.
**Validates: Requirements 6.2**

### Property 16: Trade History Persistence
*For any* executed trade, all trade details should be persisted to database, and reloading should produce identical trade records (round-trip property).
**Validates: Requirements 7.2, 12.1, 12.2**

### Property 17: Exponential Backoff Retry
*For any* API connection failure, reconnection attempts should follow exponential backoff pattern (1s, 2s, 4s, 8s, 16s).
**Validates: Requirements 8.1**

### Property 18: State Persistence and Recovery
*For any* system state before crash, saving and then restoring should result in identical positions and account state (round-trip property).
**Validates: Requirements 8.2, 8.3**

### Property 19: Configuration Persistence
*For any* configuration change, saving and then loading should result in identical configuration (round-trip property).
**Validates: Requirements 11.2**

### Property 20: Parameter Validation
*For any* parameter change, invalid parameters should be rejected and current configuration should remain unchanged.
**Validates: Requirements 11.1**

### Property 21: Order Routing Optimization
*For any* order placement, the system should route to the exchange with the best price and liquidity among available exchanges.
**Validates: Requirements 13.1**

### Property 22: Exchange Failover
*For any* primary exchange connection failure, the system should automatically switch to backup exchange and continue trading.
**Validates: Requirements 13.2**

### Property 23: Multi-Timeframe Confirmation
*For any* signal generated on 2-minute timeframe, the system should verify confirmation on 5-minute and 15-minute timeframes before entering trade.
**Validates: Requirements 14.1**

### Property 24: Multi-Timeframe Position Sizing
*For any* position where all timeframes align, position size should be increased by 25% (within risk limits).
**Validates: Requirements 14.2**

### Property 25: Correlation-Based Position Sizing
*For any* set of open positions with high correlation (>0.7), position sizes should be reduced to limit concentration risk.
**Validates: Requirements 15.1**

### Property 26: Portfolio Volatility Management
*For any* portfolio state where volatility exceeds threshold, all position sizes should be reduced proportionally.
**Validates: Requirements 15.2**

