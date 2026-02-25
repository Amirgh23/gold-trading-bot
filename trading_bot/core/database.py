"""Database management for trades, positions, and metrics."""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database for trading data persistence."""
    
    def __init__(self, db_path: str = "trading_bot.db"):
        self.db_path = db_path
        self.connection = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database schema."""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        cursor = self.connection.cursor()
        
        # Trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                entry_time TIMESTAMP NOT NULL,
                entry_price REAL NOT NULL,
                entry_size REAL NOT NULL,
                entry_reason TEXT,
                exit_time TIMESTAMP,
                exit_price REAL,
                exit_size REAL,
                exit_reason TEXT,
                pnl REAL,
                pnl_percent REAL,
                strategy TEXT,
                timeframe TEXT,
                stop_loss REAL,
                take_profit REAL,
                max_profit REAL,
                max_loss REAL,
                duration_seconds INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Positions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                entry_price REAL NOT NULL,
                entry_time TIMESTAMP NOT NULL,
                entry_size REAL NOT NULL,
                current_price REAL,
                current_size REAL,
                stop_loss REAL,
                take_profit REAL,
                trailing_stop REAL,
                unrealized_pnl REAL,
                unrealized_pnl_percent REAL,
                entry_reason TEXT,
                strategy TEXT,
                status TEXT DEFAULT 'OPEN',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Signals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id TEXT PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                symbol TEXT NOT NULL,
                direction TEXT NOT NULL,
                strategy TEXT NOT NULL,
                confidence REAL,
                entry_price REAL,
                stop_loss REAL,
                take_profit REAL,
                indicators TEXT,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL UNIQUE,
                total_trades INTEGER,
                winning_trades INTEGER,
                losing_trades INTEGER,
                win_rate REAL,
                profit_factor REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                recovery_factor REAL,
                daily_pnl REAL,
                cumulative_pnl REAL,
                strategy_performance TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indices for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trades_entry_time ON trades(entry_time)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_positions_symbol ON positions(symbol)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_signals_timestamp ON signals(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_date ON performance_metrics(date)')
        
        self.connection.commit()
        logger.info(f"Database initialized at {self.db_path}")
    
    def save_trade(self, trade: Dict[str, Any]) -> bool:
        """Save trade to database."""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO trades (
                    id, symbol, entry_time, entry_price, entry_size, entry_reason,
                    exit_time, exit_price, exit_size, exit_reason, pnl, pnl_percent,
                    strategy, timeframe, stop_loss, take_profit, max_profit, max_loss,
                    duration_seconds
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade.get('id'),
                trade.get('symbol'),
                trade.get('entry_time'),
                trade.get('entry_price'),
                trade.get('entry_size'),
                trade.get('entry_reason'),
                trade.get('exit_time'),
                trade.get('exit_price'),
                trade.get('exit_size'),
                trade.get('exit_reason'),
                trade.get('pnl'),
                trade.get('pnl_percent'),
                trade.get('strategy'),
                trade.get('timeframe'),
                trade.get('stop_loss'),
                trade.get('take_profit'),
                trade.get('max_profit'),
                trade.get('max_loss'),
                trade.get('duration_seconds'),
            ))
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving trade: {e}")
            return False
    
    def get_trade_history(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        symbol: str = "XAUUSD",
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Retrieve trade history with filtering."""
        try:
            cursor = self.connection.cursor()
            query = "SELECT * FROM trades WHERE symbol = ?"
            params = [symbol]
            
            if start_date:
                query += " AND entry_time >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND entry_time <= ?"
                params.append(end_date)
            
            query += " ORDER BY entry_time DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error retrieving trade history: {e}")
            return []
    
    def save_position(self, position: Dict[str, Any]) -> bool:
        """Save position to database."""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO positions (
                    id, symbol, side, entry_price, entry_time, entry_size,
                    current_price, current_size, stop_loss, take_profit,
                    trailing_stop, unrealized_pnl, unrealized_pnl_percent,
                    entry_reason, strategy, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                position.get('id'),
                position.get('symbol'),
                position.get('side'),
                position.get('entry_price'),
                position.get('entry_time'),
                position.get('entry_size'),
                position.get('current_price'),
                position.get('current_size'),
                position.get('stop_loss'),
                position.get('take_profit'),
                position.get('trailing_stop'),
                position.get('unrealized_pnl'),
                position.get('unrealized_pnl_percent'),
                position.get('entry_reason'),
                position.get('strategy'),
                position.get('status', 'OPEN'),
            ))
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving position: {e}")
            return False
    
    def get_open_positions(self, symbol: str = "XAUUSD") -> List[Dict[str, Any]]:
        """Get all open positions."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT * FROM positions WHERE symbol = ? AND status = 'OPEN'",
                (symbol,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error retrieving open positions: {e}")
            return []
    
    def save_signal(self, signal: Dict[str, Any]) -> bool:
        """Save signal to database."""
        try:
            cursor = self.connection.cursor()
            indicators_json = json.dumps(signal.get('indicators', {}))
            cursor.execute('''
                INSERT INTO signals (
                    id, timestamp, symbol, direction, strategy, confidence,
                    entry_price, stop_loss, take_profit, indicators, reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal.get('id'),
                signal.get('timestamp'),
                signal.get('symbol'),
                signal.get('direction'),
                signal.get('strategy'),
                signal.get('confidence'),
                signal.get('entry_price'),
                signal.get('stop_loss'),
                signal.get('take_profit'),
                indicators_json,
                signal.get('reason'),
            ))
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving signal: {e}")
            return False
    
    def save_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Save performance metrics."""
        try:
            cursor = self.connection.cursor()
            strategy_perf_json = json.dumps(metrics.get('strategy_performance', {}))
            cursor.execute('''
                INSERT OR REPLACE INTO performance_metrics (
                    date, total_trades, winning_trades, losing_trades, win_rate,
                    profit_factor, sharpe_ratio, max_drawdown, recovery_factor,
                    daily_pnl, cumulative_pnl, strategy_performance
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.get('date'),
                metrics.get('total_trades'),
                metrics.get('winning_trades'),
                metrics.get('losing_trades'),
                metrics.get('win_rate'),
                metrics.get('profit_factor'),
                metrics.get('sharpe_ratio'),
                metrics.get('max_drawdown'),
                metrics.get('recovery_factor'),
                metrics.get('daily_pnl'),
                metrics.get('cumulative_pnl'),
                strategy_perf_json,
            ))
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")
            return False
    
    def backup(self, backup_path: str = "trading_bot_backup.db") -> bool:
        """Create database backup."""
        try:
            backup_conn = sqlite3.connect(backup_path)
            self.connection.backup(backup_conn)
            backup_conn.close()
            logger.info(f"Database backed up to {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return False
    
    def restore(self, backup_path: str) -> bool:
        """Restore database from backup."""
        try:
            if not Path(backup_path).exists():
                logger.error(f"Backup file not found: {backup_path}")
                return False
            
            # Close current connection
            self.close()
            
            # Restore from backup
            backup_conn = sqlite3.connect(backup_path)
            restore_conn = sqlite3.connect(self.db_path)
            backup_conn.backup(restore_conn)
            restore_conn.close()
            backup_conn.close()
            
            # Reconnect
            self._initialize_database()
            
            logger.info(f"Database restored from {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Error restoring database: {e}")
            return False
    
    def verify_backup(self, backup_path: str) -> bool:
        """Verify backup integrity."""
        try:
            if not Path(backup_path).exists():
                logger.error(f"Backup file not found: {backup_path}")
                return False
            
            backup_conn = sqlite3.connect(backup_path)
            cursor = backup_conn.cursor()
            
            # Check if all tables exist
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = cursor.fetchall()
            
            required_tables = {'trades', 'positions', 'signals', 'performance_metrics'}
            existing_tables = {t[0] for t in tables}
            
            if not required_tables.issubset(existing_tables):
                logger.error(f"Backup missing tables: {required_tables - existing_tables}")
                backup_conn.close()
                return False
            
            # Check record counts
            cursor.execute("SELECT COUNT(*) FROM trades")
            trade_count = cursor.fetchone()[0]
            
            logger.info(f"Backup verified: {trade_count} trades, {len(existing_tables)} tables")
            backup_conn.close()
            return True
        except Exception as e:
            logger.error(f"Error verifying backup: {e}")
            return False
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
