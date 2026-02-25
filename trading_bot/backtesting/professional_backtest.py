"""
Professional Backtesting Engine with Advanced Analytics
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json


class ProfessionalBacktester:
    """Professional backtesting engine"""
    
    def __init__(self, initial_capital: float = 10000, risk_per_trade: float = 0.02):
        self.initial_capital = initial_capital
        self.risk_per_trade = risk_per_trade
        self.trades = []
        self.equity_curve = []
        self.drawdown_curve = []
        
    def generate_price_data(self, n_candles: int = 500) -> pd.DataFrame:
        """Generate realistic price data"""
        np.random.seed(42)
        
        dates = pd.date_range(end=datetime.now(), periods=n_candles, freq='1H')
        prices = 2050 + np.cumsum(np.random.randn(n_candles) * 2)
        
        data = pd.DataFrame({
            'date': dates,
            'open': prices + np.random.randn(n_candles) * 0.5,
            'high': prices + np.abs(np.random.randn(n_candles) * 1.5),
            'low': prices - np.abs(np.random.randn(n_candles) * 1.5),
            'close': prices,
            'volume': np.random.randint(1000, 10000, n_candles)
        })
        
        return data
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        # Moving Averages
        data['MA20'] = data['close'].rolling(20).mean()
        data['MA50'] = data['close'].rolling(50).mean()
        
        # RSI
        data['RSI'] = self.calculate_rsi(data['close'], 14)
        
        # MACD
        ema12 = data['close'].ewm(span=12).mean()
        ema26 = data['close'].ewm(span=26).mean()
        data['MACD'] = ema12 - ema26
        data['Signal'] = data['MACD'].ewm(span=9).mean()
        
        # Bollinger Bands
        data['BB_Middle'] = data['close'].rolling(20).mean()
        bb_std = data['close'].rolling(20).std()
        data['BB_Upper'] = data['BB_Middle'] + (bb_std * 2)
        data['BB_Lower'] = data['BB_Middle'] - (bb_std * 2)
        
        return data
    
    @staticmethod
    def calculate_rsi(prices, period=14):
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals"""
        data['Signal'] = 0
        
        # Buy signal: MA20 > MA50 and RSI < 70
        buy_condition = (data['MA20'] > data['MA50']) & (data['RSI'] < 70)
        data.loc[buy_condition, 'Signal'] = 1
        
        # Sell signal: MA20 < MA50 and RSI > 30
        sell_condition = (data['MA20'] < data['MA50']) & (data['RSI'] > 30)
        data.loc[sell_condition, 'Signal'] = -1
        
        return data
    
    def run_backtest(self, data: pd.DataFrame = None) -> Dict:
        """Run complete backtest"""
        if data is None:
            data = self.generate_price_data()
        
        # Calculate indicators
        data = self.calculate_indicators(data)
        
        # Generate signals
        data = self.generate_signals(data)
        
        # Simulate trading
        capital = self.initial_capital
        position = 0
        entry_price = 0
        
        for idx, row in data.iterrows():
            if pd.isna(row['Signal']):
                continue
            
            # Buy signal
            if row['Signal'] == 1 and position == 0:
                position_size = (capital * self.risk_per_trade) / (row['close'] * 0.02)
                position = position_size
                entry_price = row['close']
                
                self.trades.append({
                    'date': row['date'],
                    'type': 'BUY',
                    'price': entry_price,
                    'size': position_size,
                    'capital': capital
                })
            
            # Sell signal
            elif row['Signal'] == -1 and position > 0:
                exit_price = row['close']
                profit = (exit_price - entry_price) * position
                capital += profit
                
                self.trades.append({
                    'date': row['date'],
                    'type': 'SELL',
                    'price': exit_price,
                    'size': position,
                    'profit': profit,
                    'capital': capital
                })
                
                position = 0
            
            # Update equity curve
            if position > 0:
                current_equity = capital + (row['close'] - entry_price) * position
            else:
                current_equity = capital
            
            self.equity_curve.append(current_equity)
        
        # Calculate metrics
        metrics = self.calculate_metrics(data)
        
        return metrics
    
    def calculate_metrics(self, data: pd.DataFrame) -> Dict:
        """Calculate performance metrics"""
        equity_array = np.array(self.equity_curve)
        
        # Returns
        total_return = (equity_array[-1] - self.initial_capital) / self.initial_capital
        
        # Sharpe Ratio
        returns = np.diff(equity_array) / equity_array[:-1]
        sharpe_ratio = np.mean(returns) / (np.std(returns) + 1e-6) * np.sqrt(252)
        
        # Max Drawdown
        cummax = np.maximum.accumulate(equity_array)
        drawdown = (equity_array - cummax) / cummax
        max_drawdown = np.min(drawdown)
        
        # Win Rate
        winning_trades = sum(1 for t in self.trades if t.get('profit', 0) > 0)
        total_trades = len([t for t in self.trades if t['type'] == 'SELL'])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # Profit Factor
        gross_profit = sum(t.get('profit', 0) for t in self.trades if t.get('profit', 0) > 0)
        gross_loss = abs(sum(t.get('profit', 0) for t in self.trades if t.get('profit', 0) < 0))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        metrics = {
            'total_return': float(total_return),
            'total_return_pct': float(total_return * 100),
            'sharpe_ratio': float(sharpe_ratio),
            'max_drawdown': float(max_drawdown),
            'max_drawdown_pct': float(max_drawdown * 100),
            'win_rate': float(win_rate),
            'win_rate_pct': float(win_rate * 100),
            'profit_factor': float(profit_factor),
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': total_trades - winning_trades,
            'final_capital': float(equity_array[-1]),
            'initial_capital': float(self.initial_capital)
        }
        
        return metrics
    
    def get_trade_log(self) -> List[Dict]:
        """Get detailed trade log"""
        return self.trades
    
    def export_results(self, filename: str = 'backtest_results.json'):
        """Export backtest results"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'initial_capital': self.initial_capital,
            'risk_per_trade': self.risk_per_trade,
            'trades': self.trades,
            'equity_curve': self.equity_curve
        }
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"✓ Results exported to {filename}")


def run_professional_backtest():
    """Run professional backtest"""
    backtester = ProfessionalBacktester(initial_capital=10000, risk_per_trade=0.02)
    
    print("=" * 60)
    print("📊 Professional Backtesting Engine")
    print("=" * 60)
    
    # Run backtest
    metrics = backtester.run_backtest()
    
    # Print results
    print("\n📈 Backtest Results:")
    print("-" * 60)
    print(f"Initial Capital:     ${metrics['initial_capital']:,.2f}")
    print(f"Final Capital:       ${metrics['final_capital']:,.2f}")
    print(f"Total Return:        {metrics['total_return_pct']:.2f}%")
    print(f"Sharpe Ratio:        {metrics['sharpe_ratio']:.2f}")
    print(f"Max Drawdown:        {metrics['max_drawdown_pct']:.2f}%")
    print(f"Win Rate:            {metrics['win_rate_pct']:.2f}%")
    print(f"Profit Factor:       {metrics['profit_factor']:.2f}")
    print(f"Total Trades:        {metrics['total_trades']}")
    print(f"Winning Trades:      {metrics['winning_trades']}")
    print(f"Losing Trades:       {metrics['losing_trades']}")
    print("-" * 60)
    
    # Export results
    backtester.export_results()
    
    return backtester, metrics


if __name__ == "__main__":
    backtester, metrics = run_professional_backtest()
