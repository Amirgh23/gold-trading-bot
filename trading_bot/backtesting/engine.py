"""Comprehensive backtesting framework with realistic simulation."""

from typing import List, Dict, Optional, Callable
from datetime import datetime
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class BacktestEngine:
    """Backtests trading strategies with realistic simulation."""
    
    def __init__(
        self,
        initial_equity: float = 10000,
        slippage_pips: float = 0.75,
        commission_percent: float = 0.001,
    ):
        self.initial_equity = initial_equity
        self.current_equity = initial_equity
        self.slippage_pips = slippage_pips
        self.commission_percent = commission_percent
        
        self.trades = []
        self.equity_curve = [initial_equity]
        self.drawdown_curve = []
        self.peak_equity = initial_equity
    
    def run_backtest(
        self,
        df: pd.DataFrame,
        signal_generator: Callable,
        position_manager,
        risk_manager,
    ) -> Dict:
        """
        Run backtest on historical data.
        
        Args:
            df: DataFrame with OHLCV data
            signal_generator: Function to generate signals
            position_manager: Position manager instance
            risk_manager: Risk manager instance
        
        Returns:
            Backtest results dictionary
        """
        logger.info(f"Starting backtest with {len(df)} candles")
        
        for idx, (timestamp, row) in enumerate(df.iterrows()):
            current_price = row['close']
            
            # Update position prices
            for position in position_manager.get_open_positions():
                position_manager.update_position_price(position.id, current_price)
            
            # Check exit conditions
            for position in position_manager.get_open_positions():
                exit_reason = position_manager.check_exit_conditions(
                    position.id,
                    current_price,
                )
                
                if exit_reason:
                    # Apply slippage
                    exit_price = self._apply_slippage(
                        current_price,
                        position.side,
                        is_exit=True
                    )
                    
                    # Close position
                    trade = position_manager.close_position(
                        position.id,
                        exit_price,
                        exit_reason,
                    )
                    
                    if trade:
                        # Apply commission
                        trade_pnl = trade.pnl - (trade.entry_size * trade.entry_price * self.commission_percent / 100)
                        self.current_equity += trade_pnl
                        self.trades.append(trade)
            
            # Generate signals
            signals = signal_generator(df.iloc[:idx+1])
            
            if signals:
                for signal in signals:
                    # Calculate position size
                    position_size = risk_manager.calculate_position_size(
                        signal.entry_price,
                        signal.stop_loss,
                    )
                    
                    # Check risk limits
                    if not risk_manager.check_risk_limits(
                        position_size,
                        risk_manager.get_current_drawdown(),
                        len(position_manager.get_open_positions()),
                    ):
                        continue
                    
                    # Apply slippage to entry
                    entry_price = self._apply_slippage(
                        signal.entry_price,
                        signal.direction,
                        is_exit=False
                    )
                    
                    # Open position
                    position_manager.open_position(signal, position_size)
            
            # Update equity curve
            total_unrealized = position_manager.get_total_unrealized_pnl()
            equity = self.current_equity + total_unrealized
            self.equity_curve.append(equity)
            
            # Update peak and drawdown
            if equity > self.peak_equity:
                self.peak_equity = equity
            
            drawdown = ((self.peak_equity - equity) / self.peak_equity * 100) if self.peak_equity > 0 else 0
            self.drawdown_curve.append(max(0, drawdown))
            
            # Update risk manager
            risk_manager.update_equity(equity)
        
        return self._generate_report()
    
    def _apply_slippage(
        self,
        price: float,
        direction: str,
        is_exit: bool = False,
    ) -> float:
        """Apply realistic slippage to price."""
        slippage = self.slippage_pips / 10000  # Convert pips to decimal
        
        if direction == "BUY" or (is_exit and direction == "SHORT"):
            # Slippage against us (higher price)
            return price * (1 + slippage)
        else:
            # Slippage against us (lower price)
            return price * (1 - slippage)
    
    def _generate_report(self) -> Dict:
        """Generate backtest report."""
        if not self.trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'total_pnl': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'recovery_factor': 0,
            }
        
        # Calculate metrics
        total_trades = len(self.trades)
        winning_trades = sum(1 for t in self.trades if t.is_profitable)
        losing_trades = total_trades - winning_trades
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        total_pnl = sum(t.pnl for t in self.trades)
        gross_profit = sum(t.pnl for t in self.trades if t.is_profitable)
        gross_loss = abs(sum(t.pnl for t in self.trades if not t.is_profitable))
        
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 0
        
        # Sharpe ratio
        returns = np.diff(self.equity_curve) / np.array(self.equity_curve[:-1])
        sharpe_ratio = (np.mean(returns) / np.std(returns) * np.sqrt(252)) if np.std(returns) > 0 else 0
        
        # Drawdown
        max_drawdown = max(self.drawdown_curve) if self.drawdown_curve else 0
        
        # Recovery factor
        recovery_factor = (total_pnl / max_drawdown) if max_drawdown > 0 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_pnl': total_pnl,
            'final_equity': self.current_equity,
            'return_percent': ((self.current_equity - self.initial_equity) / self.initial_equity * 100),
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'recovery_factor': recovery_factor,
            'equity_curve': self.equity_curve,
            'drawdown_curve': self.drawdown_curve,
        }
    
    def walk_forward_analysis(
        self,
        df: pd.DataFrame,
        signal_generator: Callable,
        position_manager,
        risk_manager,
        train_period: int = 252,
        test_period: int = 63,
    ) -> List[Dict]:
        """
        Perform walk-forward analysis.
        
        Args:
            df: Full historical data
            signal_generator: Signal generation function
            position_manager: Position manager
            risk_manager: Risk manager
            train_period: Training period in candles
            test_period: Testing period in candles
        
        Returns:
            List of backtest results for each window
        """
        results = []
        
        for i in range(train_period, len(df), test_period):
            train_end = i
            test_end = min(i + test_period, len(df))
            
            train_data = df.iloc[:train_end]
            test_data = df.iloc[train_end:test_end]
            
            logger.info(
                f"Walk-forward window: "
                f"Train {len(train_data)} candles, "
                f"Test {len(test_data)} candles"
            )
            
            # Run backtest on test data
            result = self.run_backtest(
                test_data,
                signal_generator,
                position_manager,
                risk_manager,
            )
            
            results.append(result)
        
        return results
    
    def monte_carlo_simulation(
        self,
        trades: List,
        num_simulations: int = 1000,
    ) -> Dict:
        """
        Run Monte Carlo simulation on trades.
        
        Args:
            trades: List of trades
            num_simulations: Number of simulations
        
        Returns:
            Simulation results with confidence intervals
        """
        if not trades:
            return {}
        
        pnl_list = [t.pnl for t in trades]
        final_equities = []
        
        for _ in range(num_simulations):
            # Randomly shuffle trades
            shuffled_pnl = np.random.permutation(pnl_list)
            
            # Calculate final equity
            final_equity = self.initial_equity + np.sum(shuffled_pnl)
            final_equities.append(final_equity)
        
        final_equities = np.array(final_equities)
        
        return {
            'mean_final_equity': np.mean(final_equities),
            'std_final_equity': np.std(final_equities),
            'percentile_5': np.percentile(final_equities, 5),
            'percentile_25': np.percentile(final_equities, 25),
            'percentile_50': np.percentile(final_equities, 50),
            'percentile_75': np.percentile(final_equities, 75),
            'percentile_95': np.percentile(final_equities, 95),
        }
    
    def optimize_parameters(
        self,
        df: pd.DataFrame,
        signal_generator: Callable,
        position_manager,
        risk_manager,
        param_ranges: Dict,
    ) -> Dict:
        """
        Optimize strategy parameters.
        
        Args:
            df: Historical data
            signal_generator: Signal generation function
            position_manager: Position manager
            risk_manager: Risk manager
            param_ranges: Dictionary of parameter ranges to test
        
        Returns:
            Best parameters and their performance
        """
        best_result = None
        best_params = None
        best_sharpe = -np.inf
        
        # Generate parameter combinations
        param_combinations = self._generate_param_combinations(param_ranges)
        
        for params in param_combinations:
            logger.info(f"Testing parameters: {params}")
            
            # Run backtest with these parameters
            result = self.run_backtest(
                df,
                signal_generator,
                position_manager,
                risk_manager,
            )
            
            # Check if this is the best
            if result.get('sharpe_ratio', -np.inf) > best_sharpe:
                best_sharpe = result['sharpe_ratio']
                best_result = result
                best_params = params
        
        return {
            'best_params': best_params,
            'best_result': best_result,
            'best_sharpe_ratio': best_sharpe,
        }
    
    def _generate_param_combinations(self, param_ranges: Dict) -> List[Dict]:
        """Generate all parameter combinations."""
        import itertools
        
        keys = param_ranges.keys()
        values = param_ranges.values()
        
        combinations = []
        for combo in itertools.product(*values):
            combinations.append(dict(zip(keys, combo)))
        
        return combinations
