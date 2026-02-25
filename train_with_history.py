# آموزش مدل با تاریخچه بازار
import pandas as pd
import numpy as np
from market_history import MarketHistory
from low_capital_strategy import LowCapitalStrategy
import matplotlib.pyplot as plt

def prepare_data_for_training(df):
    """آماده‌سازی داده‌ها برای آموزش"""
    print("Preparing data for training...")
    
    # محاسبه اندیکاتورها
    df['ema_5'] = df['close'].ewm(span=5, adjust=False).mean()
    df['ema_13'] = df['close'].ewm(span=13, adjust=False).mean()
    df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # MACD
    df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = df['ema_12'] - df['ema_26']
    df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    
    # Bollinger Bands
    df['bb_middle'] = df['close'].rolling(window=20).mean()
    df['bb_std'] = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * 2)
    df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * 2)
    
    # ATR
    df['tr'] = np.maximum(
        df['high'] - df['low'],
        np.maximum(
            abs(df['high'] - df['close'].shift()),
            abs(df['low'] - df['close'].shift())
        )
    )
    df['atr'] = df['tr'].rolling(window=14).mean()
    
    # Stochastic
    df['lowest_low'] = df['low'].rolling(window=14).min()
    df['highest_high'] = df['high'].rolling(window=14).max()
    df['stoch_k'] = 100 * (df['close'] - df['lowest_low']) / (df['highest_high'] - df['lowest_low'])
    df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()
    
    # حذف NaN
    df = df.dropna()
    
    return df

def backtest_strategy(df):
    """تست استراتژی روی داده‌های تاریخی"""
    print("\nBacktesting strategy on historical data...")
    
    strategy = LowCapitalStrategy(capital=100, risk_per_trade=0.005)
    
    trades = []
    balance = 100
    position = None
    
    for i in range(len(df)):
        current_df = df.iloc[:i+1]
        
        signal = strategy.analyze(current_df)
        
        if signal and position is None:
            # ورود به معامله
            position = {
                'type': signal['signal'],
                'entry_price': signal['price'],
                'entry_index': i,
                'stop_loss': signal['stop_loss'],
                'take_profit': signal['take_profit']
            }
        
        elif position is not None:
            current_price = df['close'].iloc[i]
            
            # بررسی خروج
            if position['type'] == 'BUY':
                if current_price >= position['take_profit']:
                    profit = current_price - position['entry_price']
                    balance += profit
                    trades.append({
                        'entry': position['entry_index'],
                        'exit': i,
                        'type': 'BUY',
                        'entry_price': position['entry_price'],
                        'exit_price': current_price,
                        'profit': profit,
                        'reason': 'TP'
                    })
                    position = None
                elif current_price <= position['stop_loss']:
                    loss = current_price - position['entry_price']
                    balance += loss
                    trades.append({
                        'entry': position['entry_index'],
                        'exit': i,
                        'type': 'BUY',
                        'entry_price': position['entry_price'],
                        'exit_price': current_price,
                        'profit': loss,
                        'reason': 'SL'
                    })
                    position = None
            
            elif position['type'] == 'SELL':
                if current_price <= position['take_profit']:
                    profit = position['entry_price'] - current_price
                    balance += profit
                    trades.append({
                        'entry': position['entry_index'],
                        'exit': i,
                        'type': 'SELL',
                        'entry_price': position['entry_price'],
                        'exit_price': current_price,
                        'profit': profit,
                        'reason': 'TP'
                    })
                    position = None
                elif current_price >= position['stop_loss']:
                    loss = position['entry_price'] - current_price
                    balance += loss
                    trades.append({
                        'entry': position['entry_index'],
                        'exit': i,
                        'type': 'SELL',
                        'entry_price': position['entry_price'],
                        'exit_price': current_price,
                        'profit': loss,
                        'reason': 'SL'
                    })
                    position = None
    
    return trades, balance

def plot_backtest_results(df, trades):
    """رسم نتایج backtest"""
    print("Plotting backtest results...")
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), facecolor='#0a0e27')
    
    # نمودار قیمت
    ax1.set_facecolor('#0f1729')
    ax1.plot(range(len(df)), df['close'], color='#00ff88', linewidth=2, label='Price')
    ax1.plot(range(len(df)), df['ema_5'], color='#ff9500', linewidth=1.5, label='EMA 5', alpha=0.7)
    ax1.plot(range(len(df)), df['ema_13'], color='#ff0066', linewidth=1.5, label='EMA 13', alpha=0.7)
    
    # نمایش معاملات
    for trade in trades:
        entry_idx = trade['entry']
        exit_idx = trade['exit']
        entry_price = trade['entry_price']
        exit_price = trade['exit_price']
        
        color = '#00ff88' if trade['profit'] > 0 else '#ff4444'
        
        ax1.plot([entry_idx, exit_idx], [entry_price, exit_price], 
                color=color, linewidth=2, alpha=0.7)
        ax1.scatter([entry_idx], [entry_price], color='#00d4ff', s=100, marker='^', zorder=5)
        ax1.scatter([exit_idx], [exit_price], color=color, s=100, marker='v', zorder=5)
    
    ax1.set_title('Backtest Results - Price Chart', color='#00d4ff', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Price ($)', color='#00d4ff', fontweight='bold')
    ax1.legend(loc='upper left', framealpha=0.9, facecolor='#0f1729', edgecolor='#1e3a5f', labelcolor='#ffffff')
    ax1.grid(True, alpha=0.2, color='#1e3a5f')
    ax1.tick_params(colors='#ffffff')
    
    # نمودار تراکمی سود
    cumulative_profit = [0]
    for trade in trades:
        cumulative_profit.append(cumulative_profit[-1] + trade['profit'])
    
    ax2.set_facecolor('#0f1729')
    ax2.bar(range(len(cumulative_profit)), cumulative_profit, 
           color=['#00ff88' if x >= 0 else '#ff4444' for x in cumulative_profit], alpha=0.7)
    ax2.set_title('Cumulative Profit', color='#00d4ff', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Profit ($)', color='#00d4ff', fontweight='bold')
    ax2.set_xlabel('Trade Number', color='#00d4ff', fontweight='bold')
    ax2.grid(True, alpha=0.2, color='#1e3a5f', axis='y')
    ax2.tick_params(colors='#ffffff')
    
    plt.tight_layout()
    plt.savefig('backtest_results.png', facecolor='#0a0e27', dpi=150, bbox_inches='tight')
    print("✅ Backtest chart saved to backtest_results.png")
    plt.show()

def main():
    print("="*70)
    print("Training Model with Market History")
    print("="*70)
    
    # دریافت تاریخچه بازار
    history = MarketHistory()
    df = history.fetch_and_save(limit=500)
    
    if df is None or len(df) < 50:
        print("❌ Not enough data")
        return
    
    # آماده‌سازی داده‌ها
    df = prepare_data_for_training(df)
    
    # نمایش آمار
    stats = history.get_stats()
    print("\nMarket Statistics:")
    print(f"Total Candles: {stats['total_candles']}")
    print(f"Price Range: ${stats['min_price']:.2f} - ${stats['max_price']:.2f}")
    print(f"Average Price: ${stats['avg_price']:.2f}")
    
    # Backtest
    trades, final_balance = backtest_strategy(df)
    
    # نتایج
    print("\n" + "="*70)
    print("Backtest Results")
    print("="*70)
    print(f"Initial Balance: $100.00")
    print(f"Final Balance: ${final_balance:.2f}")
    print(f"Total Profit/Loss: ${final_balance - 100:.2f}")
    print(f"Total Trades: {len(trades)}")
    
    if len(trades) > 0:
        winning_trades = sum(1 for t in trades if t['profit'] > 0)
        win_rate = (winning_trades / len(trades)) * 100
        avg_profit = sum(t['profit'] for t in trades) / len(trades)
        
        print(f"Win Rate: {win_rate:.1f}%")
        print(f"Average Profit per Trade: ${avg_profit:.2f}")
        print(f"Best Trade: ${max(t['profit'] for t in trades):.2f}")
        print(f"Worst Trade: ${min(t['profit'] for t in trades):.2f}")
    
    # رسم نتایج
    if len(trades) > 0:
        plot_backtest_results(df, trades)

if __name__ == "__main__":
    main()
