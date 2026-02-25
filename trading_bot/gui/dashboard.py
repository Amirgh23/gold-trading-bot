"""Real-time trading dashboard with multi-language support."""

import sys
from datetime import datetime
from typing import Optional, List, Dict
import logging
from trading_bot.i18n.translations import get_translator, Language

logger = logging.getLogger(__name__)


class TradingDashboard:
    """Real-time trading dashboard with bilingual support."""
    
    def __init__(self, bot=None, language: Language = Language.ENGLISH):
        self.bot = bot
        self.is_running = False
        self.update_interval = 1000  # milliseconds
        self.translator = get_translator()
        self.translator.set_language(language)
        
        try:
            from PyQt5.QtWidgets import (
                QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                QTableWidget, QTableWidgetItem, QLabel, QPushButton,
                QTabWidget, QTextEdit, QSpinBox, QDoubleSpinBox,
                QComboBox, QFormLayout, QGroupBox
            )
            from PyQt5.QtCore import Qt, QTimer
            from PyQt5.QtGui import QColor, QFont
            
            self.QMainWindow = QMainWindow
            self.QWidget = QWidget
            self.QVBoxLayout = QVBoxLayout
            self.QHBoxLayout = QHBoxLayout
            self.QTableWidget = QTableWidget
            self.QTableWidgetItem = QTableWidgetItem
            self.QLabel = QLabel
            self.QPushButton = QPushButton
            self.QTabWidget = QTabWidget
            self.QTextEdit = QTextEdit
            self.QSpinBox = QSpinBox
            self.QDoubleSpinBox = QDoubleSpinBox
            self.QComboBox = QComboBox
            self.QFormLayout = QFormLayout
            self.QGroupBox = QGroupBox
            self.Qt = Qt
            self.QTimer = QTimer
            self.QColor = QColor
            self.QFont = QFont
            
            self.has_pyqt = True
        except ImportError:
            logger.warning("PyQt5 not installed, using text-based dashboard")
            self.has_pyqt = False
    
    def set_language(self, language: Language):
        """Change dashboard language."""
        self.translator.set_language(language)
    
    def create_window(self):
        """Create main window."""
        if not self.has_pyqt:
            logger.warning(self.translator.t("warning"))
            return None
        
        window = self.QMainWindow()
        window.setWindowTitle(self.translator.t("dashboard"))
        window.setGeometry(100, 100, 1400, 900)
        
        # Create central widget
        central_widget = self.QWidget()
        window.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = self.QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Create tabs
        tabs = self.QTabWidget()
        main_layout.addWidget(tabs)
        
        # Dashboard tab
        dashboard_tab = self._create_dashboard_tab()
        tabs.addTab(dashboard_tab, self.translator.t("dashboard"))
        
        # Positions tab
        positions_tab = self._create_positions_tab()
        tabs.addTab(positions_tab, self.translator.t("positions"))
        
        # Trades tab
        trades_tab = self._create_trades_tab()
        tabs.addTab(trades_tab, self.translator.t("trades"))
        
        # Settings tab
        settings_tab = self._create_settings_tab()
        tabs.addTab(settings_tab, self.translator.t("settings"))
        
        # Logs tab
        logs_tab = self._create_logs_tab()
        tabs.addTab(logs_tab, self.translator.t("logs"))
        
        return window
    
    def _create_dashboard_tab(self):
        """Create dashboard tab."""
        widget = self.QWidget()
        layout = self.QVBoxLayout()
        
        # Status section
        status_group = self.QGroupBox(self.translator.t("status"))
        status_layout = self.QFormLayout()
        
        self.status_label = self.QLabel(self.translator.t("stopped"))
        self.equity_label = self.QLabel("$0.00")
        self.pnl_label = self.QLabel("$0.00")
        self.drawdown_label = self.QLabel("0.00%")
        self.positions_label = self.QLabel("0")
        
        status_layout.addRow(self.translator.t("status") + ":", self.status_label)
        status_layout.addRow(self.translator.t("account_equity") + ":", self.equity_label)
        status_layout.addRow(self.translator.t("total_pnl") + ":", self.pnl_label)
        status_layout.addRow(self.translator.t("drawdown") + ":", self.drawdown_label)
        status_layout.addRow(self.translator.t("open_positions") + ":", self.positions_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Metrics section
        metrics_group = self.QGroupBox(self.translator.t("performance_metrics"))
        metrics_layout = self.QFormLayout()
        
        self.win_rate_label = self.QLabel("0.00%")
        self.profit_factor_label = self.QLabel("0.00")
        self.sharpe_label = self.QLabel("0.00")
        self.trades_label = self.QLabel("0")
        
        metrics_layout.addRow(self.translator.t("win_rate") + ":", self.win_rate_label)
        metrics_layout.addRow(self.translator.t("profit_factor") + ":", self.profit_factor_label)
        metrics_layout.addRow(self.translator.t("sharpe_ratio") + ":", self.sharpe_label)
        metrics_layout.addRow(self.translator.t("total_trades") + ":", self.trades_label)
        
        metrics_group.setLayout(metrics_layout)
        layout.addWidget(metrics_group)
        
        # Control buttons
        button_layout = self.QHBoxLayout()
        
        self.start_button = self.QPushButton(self.translator.t("start_bot"))
        self.stop_button = self.QPushButton(self.translator.t("stop_bot"))
        self.stop_button.setEnabled(False)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def _create_positions_tab(self):
        """Create positions tab."""
        widget = self.QWidget()
        layout = self.QVBoxLayout()
        
        # Positions table
        self.positions_table = self.QTableWidget()
        self.positions_table.setColumnCount(8)
        self.positions_table.setHorizontalHeaderLabels([
            self.translator.t("id"),
            self.translator.t("side"),
            self.translator.t("entry_price"),
            self.translator.t("current_price"),
            self.translator.t("size"),
            self.translator.t("pnl"),
            self.translator.t("pnl_percent"),
            self.translator.t("stop_loss")
        ])
        
        layout.addWidget(self.positions_table)
        widget.setLayout(layout)
        return widget
    
    def _create_trades_tab(self):
        """Create trades tab."""
        widget = self.QWidget()
        layout = self.QVBoxLayout()
        
        # Trades table
        self.trades_table = self.QTableWidget()
        self.trades_table.setColumnCount(9)
        self.trades_table.setHorizontalHeaderLabels([
            self.translator.t("entry_time"),
            self.translator.t("entry_price"),
            self.translator.t("exit_time"),
            self.translator.t("exit_price"),
            self.translator.t("size"),
            self.translator.t("pnl"),
            self.translator.t("pnl_percent"),
            self.translator.t("duration"),
            self.translator.t("strategy")
        ])
        
        layout.addWidget(self.trades_table)
        widget.setLayout(layout)
        return widget
    
    def _create_settings_tab(self):
        """Create settings tab."""
        widget = self.QWidget()
        layout = self.QVBoxLayout()
        
        # Risk settings
        risk_group = self.QGroupBox(self.translator.t("risk_management"))
        risk_layout = self.QFormLayout()
        
        self.max_position_spinbox = self.QDoubleSpinBox()
        self.max_position_spinbox.setValue(2.0)
        self.max_position_spinbox.setMaximum(10.0)
        
        self.max_drawdown_spinbox = self.QDoubleSpinBox()
        self.max_drawdown_spinbox.setValue(20.0)
        self.max_drawdown_spinbox.setMaximum(50.0)
        
        risk_layout.addRow(self.translator.t("position_size") + " (%):", self.max_position_spinbox)
        risk_layout.addRow(self.translator.t("max_drawdown") + " (%):", self.max_drawdown_spinbox)
        
        risk_group.setLayout(risk_layout)
        layout.addWidget(risk_group)
        
        # Strategy settings
        strategy_group = self.QGroupBox(self.translator.t("strategy_settings"))
        strategy_layout = self.QFormLayout()
        
        self.confirmation_spinbox = self.QSpinBox()
        self.confirmation_spinbox.setValue(2)
        self.confirmation_spinbox.setMaximum(3)
        
        strategy_layout.addRow(self.translator.t("confidence_threshold") + ":", self.confirmation_spinbox)
        
        strategy_group.setLayout(strategy_layout)
        layout.addWidget(strategy_group)
        
        # Save button
        save_button = self.QPushButton(self.translator.t("save_settings"))
        layout.addWidget(save_button)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_logs_tab(self):
        """Create logs tab."""
        widget = self.QWidget()
        layout = self.QVBoxLayout()
        
        self.logs_text = self.QTextEdit()
        self.logs_text.setReadOnly(True)
        
        layout.addWidget(self.logs_text)
        widget.setLayout(layout)
        return widget
    
    def update_dashboard(self, bot_status: Dict):
        """Update dashboard with bot status."""
        if not self.has_pyqt:
            self._print_text_dashboard(bot_status)
            return
        
        try:
            status_text = self.translator.t("running") if bot_status.get('is_running') else self.translator.t("stopped")
            self.status_label.setText(status_text)
            self.equity_label.setText(
                f"${bot_status.get('account_equity', 0):.2f}"
            )
            self.pnl_label.setText(
                f"${bot_status.get('unrealized_pnl', 0):.2f}"
            )
            self.drawdown_label.setText(
                f"{bot_status.get('drawdown', 0):.2f}%"
            )
            self.positions_label.setText(
                str(bot_status.get('open_positions', 0))
            )
        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")
    
    def update_positions(self, positions: List[Dict]):
        """Update positions table."""
        if not self.has_pyqt:
            return
        
        try:
            self.positions_table.setRowCount(len(positions))
            
            for row, position in enumerate(positions):
                self.positions_table.setItem(
                    row, 0, self.QTableWidgetItem(position.get('id', '')[:8])
                )
                self.positions_table.setItem(
                    row, 1, self.QTableWidgetItem(position.get('side', ''))
                )
                self.positions_table.setItem(
                    row, 2, self.QTableWidgetItem(f"{position.get('entry_price', 0):.2f}")
                )
                self.positions_table.setItem(
                    row, 3, self.QTableWidgetItem(f"{position.get('current_price', 0):.2f}")
                )
                self.positions_table.setItem(
                    row, 4, self.QTableWidgetItem(f"{position.get('current_size', 0):.4f}")
                )
                
                pnl = position.get('unrealized_pnl', 0)
                pnl_item = self.QTableWidgetItem(f"${pnl:.2f}")
                if pnl > 0:
                    pnl_item.setForeground(self.QColor("green"))
                elif pnl < 0:
                    pnl_item.setForeground(self.QColor("red"))
                self.positions_table.setItem(row, 5, pnl_item)
                
                self.positions_table.setItem(
                    row, 6, self.QTableWidgetItem(f"{position.get('unrealized_pnl_percent', 0):.2f}%")
                )
                self.positions_table.setItem(
                    row, 7, self.QTableWidgetItem(f"{position.get('stop_loss', 0):.2f}")
                )
        except Exception as e:
            logger.error(f"Error updating positions: {e}")
    
    def update_trades(self, trades: List[Dict]):
        """Update trades table."""
        if not self.has_pyqt:
            return
        
        try:
            self.trades_table.setRowCount(len(trades))
            
            for row, trade in enumerate(trades):
                self.trades_table.setItem(
                    row, 0, self.QTableWidgetItem(str(trade.get('entry_time', '')))
                )
                self.trades_table.setItem(
                    row, 1, self.QTableWidgetItem(f"{trade.get('entry_price', 0):.2f}")
                )
                self.trades_table.setItem(
                    row, 2, self.QTableWidgetItem(str(trade.get('exit_time', '')))
                )
                self.trades_table.setItem(
                    row, 3, self.QTableWidgetItem(f"{trade.get('exit_price', 0):.2f}")
                )
                self.trades_table.setItem(
                    row, 4, self.QTableWidgetItem(f"{trade.get('entry_size', 0):.4f}")
                )
                
                pnl = trade.get('pnl', 0)
                pnl_item = self.QTableWidgetItem(f"${pnl:.2f}")
                if pnl > 0:
                    pnl_item.setForeground(self.QColor("green"))
                elif pnl < 0:
                    pnl_item.setForeground(self.QColor("red"))
                self.trades_table.setItem(row, 5, pnl_item)
                
                self.trades_table.setItem(
                    row, 6, self.QTableWidgetItem(f"{trade.get('pnl_percent', 0):.2f}%")
                )
                self.trades_table.setItem(
                    row, 7, self.QTableWidgetItem(str(trade.get('duration_seconds', 0)))
                )
                self.trades_table.setItem(
                    row, 8, self.QTableWidgetItem(trade.get('strategy', ''))
                )
        except Exception as e:
            logger.error(f"Error updating trades: {e}")
    
    def add_log(self, message: str):
        """Add message to logs."""
        if not self.has_pyqt:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
            return
        
        try:
            timestamp = datetime.now().strftime('%H:%M:%S')
            self.logs_text.append(f"[{timestamp}] {message}")
        except Exception as e:
            logger.error(f"Error adding log: {e}")
    
    def _print_text_dashboard(self, bot_status: Dict):
        """Print text-based dashboard."""
        print("\n" + "="*60)
        print(self.translator.t("dashboard").upper())
        print("="*60)
        status_text = self.translator.t("running") if bot_status.get('is_running') else self.translator.t("stopped")
        print(f"{self.translator.t('status')}: {status_text}")
        print(f"{self.translator.t('account_equity')}: ${bot_status.get('account_equity', 0):.2f}")
        print(f"{self.translator.t('total_pnl')}: ${bot_status.get('unrealized_pnl', 0):.2f}")
        print(f"{self.translator.t('drawdown')}: {bot_status.get('drawdown', 0):.2f}%")
        print(f"{self.translator.t('open_positions')}: {bot_status.get('open_positions', 0)}")
        print("="*60 + "\n")
    
    def show(self):
        """Show dashboard."""
        if not self.has_pyqt:
            logger.info("Text-based dashboard mode (PyQt5 not installed)")
            return
        
        try:
            from PyQt5.QtWidgets import QApplication
            
            app = QApplication(sys.argv)
            window = self.create_window()
            
            if window:
                window.show()
                sys.exit(app.exec_())
        except Exception as e:
            logger.error(f"Error showing dashboard: {e}")
