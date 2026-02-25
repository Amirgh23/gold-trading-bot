# Complete AI-Powered Trading GUI with All Indicators
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTableWidget, 
                             QTableWidgetItem, QTextEdit, QGroupBox, QGridLayout,
                             QTabWidget, QComboBox, QProgressBar, QSplitter)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QFont, QColor, QPainter
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis, QBarSeries, QBarSet
from datetime import datetime
import pandas as pd
import numpy as np
from market_data import MarketDataProvider
from low_capital_strategy import LowCapitalStrategy
from candlestick_chart import CandlestickChartWidget
from config import *

class AIBotThread(QThread):
    """Thread with advanced strategy"""
    signal_update = pyqtSignal(dict)
    signal_log = pyqtSignal(str)
    signal_trade = pyqtSignal(dict)
    signal_indicators = pyqtSignal(dict)
    signal_ai_prediction = pyqtSignal(dict)
    
    def __init__(self, exchange='binance'):
        super().__init__()
        self.running = False
        self.market_data = MarketDataProvider(exchange)
        self.strategy = LowCapitalStrategy(capital=100, risk_per_trade=0.005)
        self.last_signal_time = None
    
    def calculate_all_indicators(self, df):
        """Calculate all indicators"""
        # EMA
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
        df['signal_line'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['signal_line']
        
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
        
        return df
    
    def run(self):
        """Run the bot"""
        self.running = True
        
        if not self.market_data.connected:
            self.signal_log.emit("❌ Connection to exchange failed")
            return
        
        self.signal_log.emit("🚀 AI Bot started with real-time data")
        
        while self.running:
            try:
                # Get current price
                price_data = self.market_data.get_current_price()
                
                if price_data:
                    self.signal_update.emit(price_data)
                    
                    # Get OHLCV data
                    df = self.market_data.get_ohlcv(limit=200)
                    
                    if df is not None and len(df) > 50:
                        # Calculate indicators
                        df = self.calculate_all_indicators(df)
                        
                        # Send indicators for display
                        current = df.iloc[-1]
                        indicators = {
                            'rsi': current.get('rsi', 50),
                            'macd': current.get('macd', 0),
                            'signal_line': current.get('signal_line', 0),
                            'macd_histogram': current.get('macd_histogram', 0),
                            'bb_upper': current.get('bb_upper', 0),
                            'bb_middle': current.get('bb_middle', 0),
                            'bb_lower': current.get('bb_lower', 0),
                            'atr': current.get('atr', 0),
                            'stoch_k': current.get('stoch_k', 50),
                            'stoch_d': current.get('stoch_d', 50),
                            'ema_5': current.get('ema_5', 0),
                            'ema_13': current.get('ema_13', 0),
                            'ema_50': current.get('ema_50', 0),
                            'df': df  # Send full dataframe for chart
                        }
                        self.signal_indicators.emit(indicators)
                        
                        # AI prediction (simulated)
                        ai_prediction = self.simulate_ai_prediction(df)
                        self.signal_ai_prediction.emit(ai_prediction)
                        
                        # Analysis and signal generation
                        signal = self.strategy.analyze(df)
                        
                        if signal:
                            current_time = datetime.now()
                            if (self.last_signal_time is None or 
                                (current_time - self.last_signal_time).seconds > 120):
                                
                                self.signal_trade.emit({
                                    'type': signal['signal'],
                                    'entry_price': signal['price'],
                                    'stop_loss': signal['stop_loss'],
                                    'take_profit': signal['take_profit'],
                                    'size': signal['position_size'],
                                    'timestamp': current_time,
                                    'source': 'AI_STRATEGY',
                                    'confidence': signal['confidence'],
                                    'risk_reward': signal['risk_reward']
                                })
                                
                                self.last_signal_time = current_time
                                self.signal_log.emit(
                                    f"🎯 Signal {signal['signal']} | "
                                    f"Price: ${signal['price']:.2f} | "
                                    f"Confidence: {signal['confidence']*100:.0f}% | "
                                    f"R:R = 1:{signal['risk_reward']:.1f}"
                                )
                
                self.msleep(3000)  # Every 3 seconds
                
            except Exception as e:
                self.signal_log.emit(f"❌ Error: {str(e)}")
                self.msleep(5000)
    
    def simulate_ai_prediction(self, df):
        """Simulate AI prediction"""
        current_price = df['close'].iloc[-1]
        
        # Calculate trend
        ema_5 = df['ema_5'].iloc[-1]
        ema_13 = df['ema_13'].iloc[-1]
        rsi = df['rsi'].iloc[-1]
        
        # Simple prediction based on trend
        if ema_5 > ema_13 and rsi < 70:
            trend = 'BULLISH'
            predicted_change = np.random.uniform(0.1, 0.5)
        elif ema_5 < ema_13 and rsi > 30:
            trend = 'BEARISH'
            predicted_change = np.random.uniform(-0.5, -0.1)
        else:
            trend = 'NEUTRAL'
            predicted_change = np.random.uniform(-0.2, 0.2)
        
        predicted_price = current_price * (1 + predicted_change / 100)
        confidence = min(abs(ema_5 - ema_13) / current_price * 1000, 0.95)
        
        return {
            'trend': trend,
            'predicted_price': predicted_price,
            'predicted_change': predicted_change,
            'confidence': confidence,
            'timeframe': '5-10 minutes'
        }
    
    def stop(self):
        """Stop the bot"""
        self.running = False
        self.signal_log.emit("⏹️ Bot stopped")

class CompleteAIGUI(QMainWindow):
    """Complete AI-Powered GUI"""
    
    def __init__(self):
        super().__init__()
        self.bot_thread = None
        self.open_trades = []
        self.trade_history = []
        self.total_pnl = 0
        self.selected_exchange = 'binance'
        self.init_ui()

    def init_ui(self):
        """Build user interface"""
        self.setWindowTitle('🤖 Smart Gold Trading Bot - AI Trading Bot')
        self.setGeometry(50, 50, 1600, 1000)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0e27;
            }
            QLabel {
                color: #ffffff;
            }
            QGroupBox {
                color: #00d4ff;
                border: 2px solid #1e3a5f;
                border-radius: 8px;
                margin-top: 12px;
                font-weight: bold;
                background-color: #0f1729;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00d4ff, stop:1 #0099cc);
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00ffff, stop:1 #00ccff);
            }
            QPushButton:pressed {
                background: #0088aa;
            }
            QPushButton:disabled {
                background: #2d3748;
                color: #718096;
            }
            QTableWidget {
                background-color: #1a1f35;
                color: #ffffff;
                gridline-color: #2d3748;
                border: 1px solid #2d3748;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #1e3a5f;
                color: #00d4ff;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QTextEdit {
                background-color: #0f1729;
                color: #00ff00;
                border: 1px solid #1e3a5f;
                border-radius: 4px;
                font-family: 'Consolas', 'Courier New', monospace;
            }
            QTabWidget::pane {
                border: 1px solid #1e3a5f;
                background-color: #0f1729;
            }
            QTabBar::tab {
                background-color: #1a1f35;
                color: #ffffff;
                padding: 12px 20px;
                border: 1px solid #2d3748;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: #1e3a5f;
                color: #00d4ff;
            }
            QComboBox {
                background-color: #1a1f35;
                color: #ffffff;
                border: 1px solid #2d3748;
                padding: 8px;
                border-radius: 4px;
            }
            QProgressBar {
                border: 1px solid #2d3748;
                border-radius: 4px;
                text-align: center;
                background-color: #1a1f35;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00d4ff, stop:1 #00ff88);
                border-radius: 3px;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Splitter to divide the page
        splitter = QSplitter(Qt.Horizontal)
        
        # Left - Charts and Indicators
        left_widget = self.create_left_panel()
        splitter.addWidget(left_widget)
        
        # Right - Trades and AI
        right_widget = self.create_right_panel()
        splitter.addWidget(right_widget)
        
        splitter.setStretchFactor(0, 7)
        splitter.setStretchFactor(1, 3)
        
        main_layout.addWidget(splitter)
        
        # Log
        log_group = self.create_log_section()
        main_layout.addWidget(log_group)
        
        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(1000)
    
    def create_header(self):
        """Build header"""
        header = QGroupBox()
        layout = QHBoxLayout()
        
        # Title
        title = QLabel("🤖 Smart Gold Trading Bot")
        title.setFont(QFont('Arial', 20, QFont.Bold))
        title.setStyleSheet("color: #00d4ff;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Current price
        self.price_label = QLabel("Price: $0.00")
        self.price_label.setFont(QFont('Arial', 18, QFont.Bold))
        self.price_label.setStyleSheet("color: #00ff88;")
        layout.addWidget(self.price_label)
        
        # Changes
        self.change_label = QLabel("Change: 0.00%")
        self.change_label.setFont(QFont('Arial', 14))
        layout.addWidget(self.change_label)
        
        layout.addStretch()
        
        # Exchange selection
        exchange_label = QLabel("Exchange:")
        layout.addWidget(exchange_label)
        
        self.exchange_combo = QComboBox()
        self.exchange_combo.addItems(['binance', 'bybit', 'okx', 'kucoin'])
        self.exchange_combo.currentTextChanged.connect(self.on_exchange_changed)
        layout.addWidget(self.exchange_combo)
        
        # Control buttons
        self.start_btn = QPushButton("▶️ Start")
        self.start_btn.clicked.connect(self.start_bot)
        layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹️ Stop")
        self.stop_btn.clicked.connect(self.stop_bot)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)
        
        header.setLayout(layout)
        return header
    
    def create_left_panel(self):
        """Left panel - Charts"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Chart tabs
        tabs = QTabWidget()
        tabs.addTab(self.create_price_chart_tab(), "📊 Price Chart")
        tabs.addTab(self.create_indicators_tab(), "📈 Indicators")
        tabs.addTab(self.create_ai_analysis_tab(), "🤖 AI Analysis")
        
        layout.addWidget(tabs)
        widget.setLayout(layout)
        return widget
    
    def create_right_panel(self):
        """Right panel - Trades"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Statistics
        stats = self.create_stats_section()
        layout.addWidget(stats)
        
        # Trades
        trades = self.create_trades_section()
        layout.addWidget(trades)
        
        widget.setLayout(layout)
        return widget
    
    def create_price_chart_tab(self):
        """Price chart tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Candlestick chart
        self.candlestick_widget = CandlestickChartWidget()
        layout.addWidget(self.candlestick_widget)
        
        # Information
        info_layout = QHBoxLayout()
        
        self.high_label = QLabel("High: --")
        self.high_label.setStyleSheet("color: #00ff88; font-size: 12pt;")
        info_layout.addWidget(self.high_label)
        
        self.low_label = QLabel("Low: --")
        self.low_label.setStyleSheet("color: #ff4444; font-size: 12pt;")
        info_layout.addWidget(self.low_label)
        
        self.volume_label = QLabel("Volume: --")
        self.volume_label.setStyleSheet("color: #ffffff; font-size: 12pt;")
        info_layout.addWidget(self.volume_label)
        
        info_layout.addStretch()
        layout.addLayout(info_layout)
        
        widget.setLayout(layout)
        return widget
    


    def create_indicators_tab(self):
        """Indicators tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # RSI
        rsi_group = QGroupBox("📊 RSI (Relative Strength Index)")
        rsi_layout = QVBoxLayout()
        
        self.rsi_label = QLabel("RSI: --")
        self.rsi_label.setFont(QFont('Arial', 14, QFont.Bold))
        rsi_layout.addWidget(self.rsi_label)
        
        self.rsi_bar = QProgressBar()
        self.rsi_bar.setRange(0, 100)
        self.rsi_bar.setValue(50)
        self.rsi_bar.setFormat("%v")
        rsi_layout.addWidget(self.rsi_bar)
        
        self.rsi_status = QLabel("Status: Neutral")
        rsi_layout.addWidget(self.rsi_status)
        
        rsi_group.setLayout(rsi_layout)
        layout.addWidget(rsi_group)
        
        # MACD
        macd_group = QGroupBox("📈 MACD")
        macd_layout = QGridLayout()
        
        self.macd_label = QLabel("MACD: --")
        self.macd_signal_label = QLabel("Signal: --")
        self.macd_histogram_label = QLabel("Histogram: --")
        
        macd_layout.addWidget(self.macd_label, 0, 0)
        macd_layout.addWidget(self.macd_signal_label, 0, 1)
        macd_layout.addWidget(self.macd_histogram_label, 1, 0, 1, 2)
        
        macd_group.setLayout(macd_layout)
        layout.addWidget(macd_group)
        
        # Stochastic
        stoch_group = QGroupBox("📉 Stochastic Oscillator")
        stoch_layout = QVBoxLayout()
        
        self.stoch_k_label = QLabel("%K: --")
        self.stoch_d_label = QLabel("%D: --")
        self.stoch_status = QLabel("Status: --")
        
        stoch_layout.addWidget(self.stoch_k_label)
        stoch_layout.addWidget(self.stoch_d_label)
        stoch_layout.addWidget(self.stoch_status)
        
        stoch_group.setLayout(stoch_layout)
        layout.addWidget(stoch_group)
        
        # ATR
        atr_group = QGroupBox("💹 ATR (Average True Range)")
        atr_layout = QVBoxLayout()
        
        self.atr_label = QLabel("ATR: --")
        self.atr_label.setFont(QFont('Arial', 12))
        atr_layout.addWidget(self.atr_label)
        
        atr_group.setLayout(atr_layout)
        layout.addWidget(atr_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_ai_analysis_tab(self):
        """AI Analysis tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # AI prediction
        prediction_group = QGroupBox("🤖 AI Prediction")
        prediction_layout = QVBoxLayout()
        
        self.ai_trend_label = QLabel("Trend: --")
        self.ai_trend_label.setFont(QFont('Arial', 16, QFont.Bold))
        prediction_layout.addWidget(self.ai_trend_label)
        
        self.ai_predicted_price_label = QLabel("Predicted Price: --")
        self.ai_predicted_price_label.setFont(QFont('Arial', 14))
        prediction_layout.addWidget(self.ai_predicted_price_label)
        
        self.ai_change_label = QLabel("Predicted Change: --")
        prediction_layout.addWidget(self.ai_change_label)
        
        self.ai_confidence_label = QLabel("Confidence: --")
        prediction_layout.addWidget(self.ai_confidence_label)
        
        self.ai_confidence_bar = QProgressBar()
        self.ai_confidence_bar.setRange(0, 100)
        prediction_layout.addWidget(self.ai_confidence_bar)
        
        self.ai_timeframe_label = QLabel("Timeframe: --")
        prediction_layout.addWidget(self.ai_timeframe_label)
        
        prediction_group.setLayout(prediction_layout)
        layout.addWidget(prediction_group)
        
        # AI Recommendation
        recommendation_group = QGroupBox("💡 Trading Recommendation")
        recommendation_layout = QVBoxLayout()
        
        self.ai_recommendation = QLabel("Analyzing...")
        self.ai_recommendation.setWordWrap(True)
        self.ai_recommendation.setFont(QFont('Arial', 12))
        recommendation_layout.addWidget(self.ai_recommendation)
        
        recommendation_group.setLayout(recommendation_layout)
        layout.addWidget(recommendation_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_stats_section(self):
        """Statistics section"""
        stats_group = QGroupBox("📊 Trading Statistics")
        layout = QGridLayout()
        
        self.total_trades_label = QLabel("Total Trades: 0")
        self.total_trades_label.setFont(QFont('Arial', 11))
        
        self.open_positions_label = QLabel("Open Positions: 0")
        self.open_positions_label.setFont(QFont('Arial', 11))
        
        self.daily_pnl_label = QLabel("Daily P&L: $0.00")
        self.daily_pnl_label.setFont(QFont('Arial', 11))
        
        self.win_rate_label = QLabel("Win Rate: 0%")
        self.win_rate_label.setFont(QFont('Arial', 11))
        
        layout.addWidget(self.total_trades_label, 0, 0)
        layout.addWidget(self.open_positions_label, 0, 1)
        layout.addWidget(self.daily_pnl_label, 1, 0)
        layout.addWidget(self.win_rate_label, 1, 1)
        
        stats_group.setLayout(layout)
        return stats_group
    
    def create_trades_section(self):
        """Trades section"""
        trades_group = QGroupBox("💼 Recent Trades")
        layout = QVBoxLayout()
        
        self.trades_table = QTableWidget()
        self.trades_table.setColumnCount(6)
        self.trades_table.setHorizontalHeaderLabels([
            'Type', 'Price', 'SL', 'TP', 'Confidence', 'Time'
        ])
        self.trades_table.horizontalHeader().setStretchLastSection(True)
        self.trades_table.setMaximumHeight(300)
        
        layout.addWidget(self.trades_table)
        trades_group.setLayout(layout)
        return trades_group
    
    def create_log_section(self):
        """System log section"""
        log_group = QGroupBox("📝 System Log")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(120)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        return log_group
    
    def on_exchange_changed(self, exchange):
        """Change exchange"""
        self.selected_exchange = exchange
        self.add_log(f"📊 Selected exchange: {exchange}")
    
    def start_bot(self):
        """Start the bot"""
        if self.bot_thread is None or not self.bot_thread.isRunning():
            self.add_log(f"🔗 Connecting to {self.selected_exchange}...")
            self.bot_thread = AIBotThread(self.selected_exchange)
            self.bot_thread.signal_update.connect(self.update_data)
            self.bot_thread.signal_log.connect(self.add_log)
            self.bot_thread.signal_trade.connect(self.add_trade)
            self.bot_thread.signal_indicators.connect(self.update_indicators)
            self.bot_thread.signal_ai_prediction.connect(self.update_ai_prediction)
            self.bot_thread.start()
            
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.exchange_combo.setEnabled(False)
            self.add_log("🚀 AI Bot started with real-time data")
    
    def stop_bot(self):
        """Stop the bot"""
        if self.bot_thread and self.bot_thread.isRunning():
            self.bot_thread.stop()
            self.bot_thread.wait()
            
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.exchange_combo.setEnabled(True)
            self.add_log("⏹️ Bot stopped")
    
    def update_data(self, data):
        """Update data"""
        price = data['price']
        change = data.get('change', 0)
        high = data.get('high', price)
        low = data.get('low', price)
        volume = data.get('volume', 0)
        
        self.price_label.setText(f"Price: ${price:.2f}")
        
        if change >= 0:
            self.change_label.setText(f"Change: +{change:.2f}%")
            self.change_label.setStyleSheet("color: #00ff88; font-size: 14pt;")
        else:
            self.change_label.setText(f"Change: {change:.2f}%")
            self.change_label.setStyleSheet("color: #ff4444; font-size: 14pt;")
        
        self.high_label.setText(f"High: ${high:.2f}")
        self.low_label.setText(f"Low: ${low:.2f}")
        self.volume_label.setText(f"Volume: {volume:.2f}")
    
    def update_chart(self, df):
        """Update candlestick chart"""
        if df is not None and len(df) > 0:
            # Plot candlesticks
            self.candlestick_widget.plot_candlesticks(df.tail(50))
            
            # Add EMA
            self.candlestick_widget.add_ema(df.tail(50), 5, '#ff9500', 'EMA 5')
            self.candlestick_widget.add_ema(df.tail(50), 13, '#ff0066', 'EMA 13')
            
            # Add Bollinger Bands
            self.candlestick_widget.add_bollinger_bands(df.tail(50))
            
            # Add legend
            self.candlestick_widget.add_legend()
    
    def update_indicators(self, indicators):
        """Update indicators"""
        # RSI
        rsi = indicators.get('rsi', 50)
        self.rsi_label.setText(f"RSI: {rsi:.1f}")
        self.rsi_bar.setValue(int(rsi))
        
        if rsi > 70:
            self.rsi_status.setText("Status: Overbought 🔴")
            self.rsi_status.setStyleSheet("color: #ff4444;")
        elif rsi < 30:
            self.rsi_status.setText("Status: Oversold 🟢")
            self.rsi_status.setStyleSheet("color: #00ff88;")
        else:
            self.rsi_status.setText("Status: Neutral ⚪")
            self.rsi_status.setStyleSheet("color: #ffffff;")
        
        # MACD
        macd = indicators.get('macd', 0)
        signal_line = indicators.get('signal_line', 0)
        histogram = indicators.get('macd_histogram', 0)
        
        self.macd_label.setText(f"MACD: {macd:.2f}")
        self.macd_signal_label.setText(f"Signal: {signal_line:.2f}")
        self.macd_histogram_label.setText(f"Histogram: {histogram:.2f}")
        
        # Stochastic
        stoch_k = indicators.get('stoch_k', 50)
        stoch_d = indicators.get('stoch_d', 50)
        
        self.stoch_k_label.setText(f"%K: {stoch_k:.1f}")
        self.stoch_d_label.setText(f"%D: {stoch_d:.1f}")
        
        if stoch_k > 80:
            self.stoch_status.setText("Status: Overbought")
            self.stoch_status.setStyleSheet("color: #ff4444;")
        elif stoch_k < 20:
            self.stoch_status.setText("Status: Oversold")
            self.stoch_status.setStyleSheet("color: #00ff88;")
        else:
            self.stoch_status.setText("Status: Neutral")
            self.stoch_status.setStyleSheet("color: #ffffff;")
        
        # ATR
        atr = indicators.get('atr', 0)
        self.atr_label.setText(f"ATR: {atr:.2f} (Volatility: {'High' if atr > 10 else 'Low'})")
        
        # Update candlestick chart
        df = indicators.get('df')
        if df is not None:
            self.update_chart(df)
    
    def update_ai_prediction(self, prediction):
        """Update AI prediction"""
        trend = prediction['trend']
        predicted_price = prediction['predicted_price']
        predicted_change = prediction['predicted_change']
        confidence = prediction['confidence']
        timeframe = prediction['timeframe']
        
        # Trend
        if trend == 'BULLISH':
            self.ai_trend_label.setText(f"Trend: Bullish 📈")
            self.ai_trend_label.setStyleSheet("color: #00ff88; font-size: 16pt; font-weight: bold;")
        elif trend == 'BEARISH':
            self.ai_trend_label.setText(f"Trend: Bearish 📉")
            self.ai_trend_label.setStyleSheet("color: #ff4444; font-size: 16pt; font-weight: bold;")
        else:
            self.ai_trend_label.setText(f"Trend: Neutral ➡️")
            self.ai_trend_label.setStyleSheet("color: #ffffff; font-size: 16pt; font-weight: bold;")
        
        # Predicted price
        self.ai_predicted_price_label.setText(f"Predicted Price: ${predicted_price:.2f}")
        
        # Change
        if predicted_change >= 0:
            self.ai_change_label.setText(f"Predicted Change: +{predicted_change:.2f}%")
            self.ai_change_label.setStyleSheet("color: #00ff88;")
        else:
            self.ai_change_label.setText(f"Predicted Change: {predicted_change:.2f}%")
            self.ai_change_label.setStyleSheet("color: #ff4444;")
        
        # Confidence
        confidence_pct = int(confidence * 100)
        self.ai_confidence_label.setText(f"Confidence: {confidence_pct}%")
        self.ai_confidence_bar.setValue(confidence_pct)
        
        # Timeframe
        self.ai_timeframe_label.setText(f"Timeframe: {timeframe}")
        
        # Recommendation
        if confidence > 0.7:
            if trend == 'BULLISH':
                recommendation = "✅ Recommendation: Enter BUY with high confidence"
            elif trend == 'BEARISH':
                recommendation = "✅ Recommendation: Enter SELL with high confidence"
            else:
                recommendation = "⚠️ Recommendation: Wait, trend is unclear"
        elif confidence > 0.4:
            recommendation = "⚠️ Recommendation: Be careful, medium confidence"
        else:
            recommendation = "❌ Recommendation: Avoid entering trades"
        
        self.ai_recommendation.setText(recommendation)
    
    def add_trade(self, trade):
        """Add trade"""
        self.open_trades.append(trade)
        
        row = self.trades_table.rowCount()
        self.trades_table.insertRow(row)
        
        color = QColor("#00ff88") if trade['type'] == 'BUY' else QColor("#ff4444")
        
        items = [
            QTableWidgetItem(trade['type']),
            QTableWidgetItem(f"${trade['entry_price']:.2f}"),
            QTableWidgetItem(f"${trade['stop_loss']:.2f}"),
            QTableWidgetItem(f"${trade['take_profit']:.2f}"),
            QTableWidgetItem(f"{trade.get('confidence', 0)*100:.0f}%"),
            QTableWidgetItem(trade['timestamp'].strftime("%H:%M:%S"))
        ]
        
        for col, item in enumerate(items):
            if col == 0:
                item.setForeground(color)
            self.trades_table.setItem(row, col, item)
    
    def add_log(self, message):
        """Add log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def update_ui(self):
        """Periodic update"""
        self.open_positions_label.setText(f"Open Positions: {len(self.open_trades)}")
        self.total_trades_label.setText(f"Total Trades: {len(self.open_trades)}")
        self.daily_pnl_label.setText(f"Daily P&L: ${self.total_pnl:.2f}")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = CompleteAIGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
