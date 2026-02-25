"""Monte Carlo simulation for strategy robustness testing."""

import random
import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime
import logging
from trading_bot.models.trade import Trade

logger = logging.getLogger(__name__)


class MonteCarloSimulation:
    """Performs Monte Carlo simulations on trading strategies."""
    
    @staticmethod
    def run_simulation(
        trades: List[Trade],
        num_simulations: int = 1000,
        confidence_level: float = 0.95,
    ) -> Dict:
        """
        Run Monte Carlo simulation with random trade order.
        
        Args:
            trades: List of historical trades
            num_simulations: Number of simulations to run
            confidence_level: Confidence level for intervals (0.95 = 95%)
        
        Returns:
            Dictionary with simulation results and confidence intervals
        """
        if not trades or len(trades) < 2:
            logger.warning("Insufficient trades for Monte Carlo simulation")
            return {}
        
        # Extract P&L from trades
        pnls = [trade.pnl for trade in trades]
        
        # Run simulations
        simulation_results = []
        for _ in range(num_simulations):
            # Randomly shuffle trade order
            shuffled_pnls = random.sample(pnls, len(pnls))
            
            # Calculate cumulative P&L
            cumulative_pnl = 0
            max_dd = 0
            peak = 0
            
            for pnl in shuffled_pnls:
                cumulative_pnl += pnl
                
                if cumulative_pnl > peak:
                    peak = cumulative_pnl
                
                drawdown = peak - cumulative_pnl
                if drawdown > max_dd:
                    max_dd = drawdown
            
            simulation_results.append({
                'total_pnl': cumulative_pnl,
                'max_drawdown': max_dd,
                'final_equity': cumulative_pnl,
            })
        
        # Calculate confidence intervals
        pnls_array = np.array([r['total_pnl'] for r in simulation_results])
        dds_array = np.array([r['max_drawdown'] for r in simulation_results])
        
        alpha = 1 - confidence_level
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100
        
        return {
            'num_simulations': num_simulations,
            'confidence_level': confidence_level,
            'pnl_stats': {
                'mean': float(np.mean(pnls_array)),
                'std': float(np.std(pnls_array)),
                'min': float(np.min(pnls_array)),
                'max': float(np.max(pnls_array)),
                'lower_ci': float(np.percentile(pnls_array, lower_percentile)),
                'upper_ci': float(np.percentile(pnls_array, upper_percentile)),
            },
            'drawdown_stats': {
                'mean': float(np.mean(dds_array)),
                'std': float(np.std(dds_array)),
                'min': float(np.min(dds_array)),
                'max': float(np.max(dds_array)),
                'lower_ci': float(np.percentile(dds_array, lower_percentile)),
                'upper_ci': float(np.percentile(dds_array, upper_percentile)),
            },
            'probability_of_profit': float(np.sum(pnls_array > 0) / len(pnls_array) * 100),
            'probability_of_loss': float(np.sum(pnls_array < 0) / len(pnls_array) * 100),
        }
    
    @staticmethod
    def run_walk_forward_simulation(
        trades: List[Trade],
        window_size: int = 50,
        num_simulations: int = 100,
    ) -> Dict:
        """
        Run walk-forward Monte Carlo simulation.
        
        Args:
            trades: List of historical trades
            window_size: Number of trades per window
            num_simulations: Simulations per window
        
        Returns:
            Dictionary with walk-forward results
        """
        if len(trades) < window_size:
            logger.warning("Insufficient trades for walk-forward simulation")
            return {}
        
        results = []
        
        # Walk forward through trades
        for i in range(0, len(trades) - window_size, window_size // 2):
            window_trades = trades[i:i + window_size]
            
            sim_result = MonteCarloSimulation.run_simulation(
                window_trades,
                num_simulations=num_simulations,
            )
            
            if sim_result:
                sim_result['window_start'] = i
                sim_result['window_end'] = i + window_size
                results.append(sim_result)
        
        return {
            'windows': results,
            'total_windows': len(results),
            'window_size': window_size,
        }
    
    @staticmethod
    def calculate_robustness_score(
        trades: List[Trade],
        num_simulations: int = 1000,
    ) -> float:
        """
        Calculate strategy robustness score (0-100).
        
        Based on:
        - Consistency of results across simulations
        - Probability of profit
        - Drawdown stability
        
        Args:
            trades: List of historical trades
            num_simulations: Number of simulations
        
        Returns:
            Robustness score (0-100)
        """
        if not trades:
            return 0.0
        
        sim_result = MonteCarloSimulation.run_simulation(
            trades,
            num_simulations=num_simulations,
        )
        
        if not sim_result:
            return 0.0
        
        # Calculate components
        pnl_stats = sim_result['pnl_stats']
        dd_stats = sim_result['drawdown_stats']
        prob_profit = sim_result['probability_of_profit']
        
        # Consistency score (lower std = higher consistency)
        consistency = max(0, 100 - (pnl_stats['std'] / max(abs(pnl_stats['mean']), 1) * 100))
        
        # Profitability score
        profitability = prob_profit
        
        # Drawdown stability (lower max drawdown = higher stability)
        stability = max(0, 100 - (dd_stats['max'] / max(abs(pnl_stats['mean']), 1) * 100))
        
        # Weighted robustness score
        robustness = (consistency * 0.3 + profitability * 0.4 + stability * 0.3)
        
        return min(100, max(0, robustness))
