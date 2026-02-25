#!/usr/bin/env python3
"""
Bilingual GUI launcher for Gold Trading Bot (English & Persian).
Supports language switching at runtime.
"""

import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from trading_bot.i18n.translations import Language, get_translator
from trading_bot.gui.language_switcher import get_language_switcher, set_app_language

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_bilingual_gui():
    """Create bilingual GUI with language switcher."""
    try:
        from PyQt5.QtWidgets import (
            QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
            QComboBox, QLabel, QPushButton, QTabWidget, QTableWidget,
            QTableWidgetItem, QTextEdit, QSpinBox, QDoubleSpinBox,
            QFormLayout, QGroupBox, QMessageBox
        )
        from PyQt5.QtCore import Qt, pyqtSignal, QObject
        from PyQt5.QtGui import QFont
        
        from trading_bot.gui.dashboard import TradingDashboard
        from trading_bot.gui.alerts import AlertManager
        
        class LanguageChangeSignal(QObject):
            """Signal emitter for language changes."""
            language_changed = pyqtSignal(Language)
        
        class BilingualTradingGUI(QMainWindow):
            """Main GUI with bilingual support."""
            
            def __init__(self):
                super().__init__()
                self.translator = get_translator()
                self.language_switcher = get_language_switcher()
                self.signal_emitter = LanguageChangeSignal()
                
                # Initialize components
                self.dashboard = TradingDashboard(language=Language.ENGLISH)
                self.alert_manager = AlertManager(language=Language.ENGLISH)
                
                # Register language change listener
                self.language_switcher.register_listener(self._on_language_changed)
                
                self.init_ui()
            
            def init_ui(self):
                """Initialize UI."""
                self.setWindowTitle(self.translator.t("dashboard"))
                self.setGeometry(100, 100, 1500, 950)
                
                # Create central widget
                central_widget = QWidget()
                self.setCentralWidget(central_widget)
                
                # Create main layout
                main_layout = QVBoxLayout()
                
                # Language selector
                lang_layout = QHBoxLayout()
                lang_label = QLabel(self.translator.t("language", "Language") + ":")
                self.language_combo = QComboBox()
                self.language_combo.addItem("English", Language.ENGLISH)
                self.language_combo.addItem("فارسی (Persian)", Language.PERSIAN)
                self.language_combo.currentIndexChanged.connect(self._on_language_selected)
                
                lang_layout.addWidget(lang_label)
                lang_layout.addWidget(self.language_combo)
                lang_layout.addStretch()
                
                main_layout.addLayout(lang_layout)
                
                # Create tabs
                self.tabs = QTabWidget()
                
                # Dashboard tab
                dashboard_tab = self._create_dashboard_tab()
                self.tabs.addTab(dashboard_tab, self.translator.t("dashboard"))
                
                # Positions tab
                positions_tab = self._create_positions_tab()
                self.tabs.addTab(positions_tab, self.translator.t("positions"))
                
                # Trades tab
                trades_tab = self._create_trades_tab()
                self.tabs.addTab(trades_tab, self.translator.t("trades"))
                
                # Settings tab
                settings_tab = self._create_settings_tab()
                self.tabs.addTab(settings_tab, self.translator.t("settings"))
                
                # Logs tab
                logs_tab = self._create_logs_tab()
                self.tabs.addTab(logs_tab, self.translator.t("logs"))
                
                main_layout.addWidget(self.tabs)
                central_widget.setLayout(main_layout)
            
            def _create_dashboard_tab(self):
                """Create dashboard tab."""
                widget = QWidget()
                layout = QVBoxLayout()
                
                # Status section
                status_group = QGroupBox(self.translator.t("status"))
                status_layout = QFormLayout()
                
                self.status_label = QLabel(self.translator.t("stopped"))
                self.equity_label = QLabel("$0.00")
                self.pnl_label = QLabel("$0.00")
                self.drawdown_label = QLabel("0.00%")
                self.positions_label = QLabel("0")
                
                status_layout.addRow(self.translator.t("status") + ":", self.status_label)
                status_layout.addRow(self.translator.t("account_equity") + ":", self.equity_label)
                status_layout.addRow(self.translator.t("total_pnl") + ":", self.pnl_label)
                status_layout.addRow(self.translator.t("drawdown") + ":", self.drawdown_label)
                status_layout.addRow(self.translator.t("open_positions") + ":", self.positions_label)
                
                status_group.setLayout(status_layout)
                layout.addWidget(status_group)
                
                # Metrics section
                metrics_group = QGroupBox(self.translator.t("performance_metrics"))
                metrics_layout = QFormLayout()
                
                self.win_rate_label = QLabel("0.00%")
                self.profit_factor_label = QLabel("0.00")
                self.sharpe_label = QLabel("0.00")
                self.trades_label = QLabel("0")
                
                metrics_layout.addRow(self.translator.t("win_rate") + ":", self.win_rate_label)
                metrics_layout.addRow(self.translator.t("profit_factor") + ":", self.profit_factor_label)
                metrics_layout.addRow(self.translator.t("sharpe_ratio") + ":", self.sharpe_label)
                metrics_layout.addRow(self.translator.t("total_trades") + ":", self.trades_label)
                
                metrics_group.setLayout(metrics_layout)
                layout.addWidget(metrics_group)
                
                # Control buttons
                button_layout = QHBoxLayout()
                
                self.start_button = QPushButton(self.translator.t("start_bot"))
                self.stop_button = QPushButton(self.translator.t("stop_bot"))
                self.stop_button.setEnabled(False)
                
                button_layout.addWidget(self.start_button)
                button_layout.addWidget(self.stop_button)
                
                layout.addLayout(button_layout)
                layout.addStretch()
                
                widget.setLayout(layout)
                return widget
            
            def _create_positions_tab(self):
                """Create positions tab."""
                widget = QWidget()
                layout = QVBoxLayout()
                
                self.positions_table = QTableWidget()
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
                widget = QWidget()
                layout = QVBoxLayout()
                
                self.trades_table = QTableWidget()
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
                widget = QWidget()
                layout = QVBoxLayout()
                
                # Risk settings
                risk_group = QGroupBox(self.translator.t("risk_management"))
                risk_layout = QFormLayout()
                
                self.max_position_spinbox = QDoubleSpinBox()
                self.max_position_spinbox.setValue(2.0)
                self.max_position_spinbox.setMaximum(10.0)
                
                self.max_drawdown_spinbox = QDoubleSpinBox()
                self.max_drawdown_spinbox.setValue(20.0)
                self.max_drawdown_spinbox.setMaximum(50.0)
                
                risk_layout.addRow(self.translator.t("position_size") + " (%):", self.max_position_spinbox)
                risk_layout.addRow(self.translator.t("max_drawdown") + " (%):", self.max_drawdown_spinbox)
                
                risk_group.setLayout(risk_layout)
                layout.addWidget(risk_group)
                
                # Strategy settings
                strategy_group = QGroupBox(self.translator.t("strategy_settings"))
                strategy_layout = QFormLayout()
                
                self.confidence_spinbox = QSpinBox()
                self.confidence_spinbox.setValue(2)
                self.confidence_spinbox.setMaximum(3)
                
                strategy_layout.addRow(self.translator.t("confidence_threshold") + ":", self.confidence_spinbox)
                
                strategy_group.setLayout(strategy_layout)
                layout.addWidget(strategy_group)
                
                # Save button
                save_button = QPushButton(self.translator.t("save_settings"))
                layout.addWidget(save_button)
                
                layout.addStretch()
                widget.setLayout(layout)
                return widget
            
            def _create_logs_tab(self):
                """Create logs tab."""
                widget = QWidget()
                layout = QVBoxLayout()
                
                self.logs_text = QTextEdit()
                self.logs_text.setReadOnly(True)
                
                layout.addWidget(self.logs_text)
                widget.setLayout(layout)
                return widget
            
            def _on_language_selected(self, index):
                """Handle language selection."""
                language = self.language_combo.itemData(index)
                set_app_language(language)
            
            def _on_language_changed(self, language: Language):
                """Handle language change."""
                self.translator.set_language(language)
                self.dashboard.set_language(language)
                self.alert_manager.set_language(language)
                self._update_ui_text()
            
            def _update_ui_text(self):
                """Update all UI text after language change."""
                self.setWindowTitle(self.translator.t("dashboard"))
                
                # Update tab titles
                self.tabs.setTabText(0, self.translator.t("dashboard"))
                self.tabs.setTabText(1, self.translator.t("positions"))
                self.tabs.setTabText(2, self.translator.t("trades"))
                self.tabs.setTabText(3, self.translator.t("settings"))
                self.tabs.setTabText(4, self.translator.t("logs"))
                
                # Update button texts
                self.start_button.setText(self.translator.t("start_bot"))
                self.stop_button.setText(self.translator.t("stop_bot"))
                
                logger.info(f"UI updated to {self.translator.get_language().value}")
        
        # Create and run application
        app = QApplication(sys.argv)
        gui = BilingualTradingGUI()
        gui.show()
        
        logger.info("Bilingual Trading GUI started")
        sys.exit(app.exec_())
        
    except ImportError as e:
        logger.error(f"PyQt5 not installed: {e}")
        print("Please install PyQt5: pip install PyQt5")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error starting GUI: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    create_bilingual_gui()
