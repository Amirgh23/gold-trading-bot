"""
Dark Mode Professional Trading Dashboard - LIVE DATA VERSION
Full screen main chart with real-time updates
"""

import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget,
    QTableWidget, QTableWidgetItem, QScrollArea, QFrame, QGridLayout
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QBrush, QPainter
from PyQt5.QtChart import QChart, QChartView, QCandlestickSeries, QCandlestickSet
from PyQt5.QtChart import QLineSeries, QDateTimeAxis, QValueAxis
from PyQt5.QtCore import QDateTime, QPointF
from trading_bot.gui.live_data_manager import LiveDataUpdater, LiveAnalysisUpdater


class DarkModeDashboardLive(QWidget):
    """Dark mode dashboard with LIVE DATA - Real-time updates"""
    
    def __init__(self):
        super().__init__()
        self.data = self.generate_sample_data()
        self.analysis = None
        self.chart_view = None
        self.chart = None
        self.table = None
        
        # Live data managers
        self.data_updater = LiveDataUpdater(self.data)
        self.analysis_updater = LiveAnalysisUpdater(self.data_updater)
        
        self.init_ui()
        self.apply_dark_mode()
        self.start_live_updates()
        
    def start_live_updates(self):
        """Start live data and analysis updates"""
        # Connect signals
        self.data_updater.data_updated.connect(self.on_data_updated)
        self.analysis_updater.analysis_updated.connect(self.on_analysis_updated)
        
        # Start threads
        self.data_updater.start()
        self.analysis_updater.start()
        
    def on_data_updated(self, data):
        """Handle live data update"""
        self.data = data
        self.refresh_chart()
    
    def on_analysis_updated(self, analysis):
        """Handle live analysis update"""
        self.analysis = analysis
        self.update_metrics(analysis)
        self.update_analysis_table(analysis)
    
    def refresh_chart(self):
        """Refresh chart with new data"""
        if self.chart is None or self.chart_view is None:
            return
        
        try:
            # Clear old series
            self.chart.removeAllSeries()
            
            # Create candlestick series
            series = QCandlestickSeries()
            series.setName("XAUUSD")
            
            # Add candlesticks
            for idx, row in self.data.tail(100).iterrows():
                candlestick = QCandlestickSet(
                    row['open'], row['high'], row['low'], row['close']
                )
                candlestick.setTimestamp(int(row['date'].timestamp() * 1000))
                series.append(candlestick)
            
            self.chart.addSeries(series)
            
            # Add MAs
            ma20_series = QLineSeries()
            ma20_series.setName("MA20")
            for idx, row in self.data.tail(100).iterrows():
                if pd.notna(row.get('MA20')):
                    ma20_series.append(int(row['date'].timestamp() * 1000), row['MA20'])
            self.chart.addSeries(ma20_series)
            
            ma50_series = QLineSeries()
            ma50_series.setName("MA50")
            for idx, row in self.data.tail(100).iterrows():
                if pd.notna(row.get('MA50')):
                    ma50_series.append(int(row['date'].timestamp() * 1000), row['MA50'])
            self.chart.addSeries(ma50_series)
            
            ma200_series = QLineSeries()
            ma200_series.setName("MA200")
            for idx, row in self.data.tail(100).iterrows():
                if pd.notna(row.get('MA200')):
                    ma200_series.append(int(row['date'].timestamp() * 1000), row['MA200'])
            self.chart.addSeries(ma200_series)
        except Exception as e:
            print(f"Error refreshing chart: {e}")
    
    def update_metrics(self, analysis):
        """Update top metrics"""
        if analysis:
            price = analysis.get('current_price', 0)
            confidence = analysis.get('confidence', 0)
            volatility = analysis.get('volatility', 'MEDIUM')
            
            # Update confidence
            self.confidence_widget.findChild(QLabel).setText(f"{confidence:.0f}%")
            
            # Update volatility
            vol_color = "#ff0000" if volatility == "HIGH" else "#00ff00"
            self.volatility_widget.setStyleSheet(f"""
                QFrame {{
                    background-color: #1a1a1a;
                    border: 1px solid {vol_color};
                    border-radius: 3px;
                    padding: 3px;
                }}
            """)
    
    def update_analysis_table(self, analysis):
        """Update analysis table with live data"""
        if not analysis or self.table is None:
            return
        
        try:
            indicators = [
                ("Trend", analysis.get('trend', 'N/A'), "BULLISH" if "UP" in analysis.get('trend', '') else "BEARISH"),
                ("RSI (14)", f"{analysis.get('rsi', 0):.1f}", analysis.get('rsi_signal', 'N/A')),
                ("MACD", f"{analysis.get('macd', 0):.4f}", analysis.get('macd_signal', 'N/A')),
                ("Stochastic", f"{analysis.get('stoch', 0):.1f}", analysis.get('stoch_signal', 'N/A')),
                ("Bollinger Bands", "MIDDLE", analysis.get('bb_signal', 'N/A')),
                ("MA20", f"{analysis.get('ma20', 0):.2f}", "ABOVE" if analysis.get('current_price', 0) > analysis.get('ma20', 0) else "BELOW"),
                ("MA50", f"{analysis.get('ma50', 0):.2f}", "ABOVE" if analysis.get('current_price', 0) > analysis.get('ma50', 0) else "BELOW"),
                ("Volatility", analysis.get('volatility', 'N/A'), "NORMAL"),
                ("AI Recommendation", analysis.get('recommendation', 'HOLD'), "STRONG"),
                ("Confidence Level", f"{analysis.get('confidence', 0):.0f}%", "HIGH"),
            ]
            
            for i, (indicator, value, signal) in enumerate(indicators):
                if i < self.table.rowCount():
                    self.table.setItem(i, 0, QTableWidgetItem(indicator))
                    self.table.setItem(i, 1, QTableWidgetItem(str(value)))
                    
                    signal_item = QTableWidgetItem(signal)
                    
                    if "BULL" in signal or "BUY" in signal or "ABOVE" in signal:
                        signal_item.setBackground(QBrush(QColor("#1a3a1a")))
                        signal_item.setForeground(QBrush(QColor("#00ff00")))
                    elif "BEAR" in signal or "SELL" in signal or "BELOW" in signal:
                        signal_item.setBackground(QBrush(QColor("#3a1a1a")))
                        signal_item.setForeground(QBrush(QColor("#ff0000")))
                    elif "OVERBOUGHT" in signal:
                        signal_item.setBackground(QBrush(QColor("#3a3a1a")))
                        signal_item.setForeground(QBrush(QColor("#ffff00")))
                    
                    self.table.setItem(i, 2, signal_item)
        except Exception as e:
            print(f"Error updating table: {e}")
        
    def init_ui(self):
        """Initialize UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Top section - Key metrics (compact)
        top_layout = QHBoxLayout()
        top_layout.setSpacing(5)
        
        # Current price
        price_widget = self.create_metric_widget("Price", "$2,050.25", "#00ff00")
        top_layout.addWidget(price_widget)
        
        # Change
        change_widget = self.create_metric_widget("Change", "+2.5%", "#00ff00")
        top_layout.addWidget(change_widget)
        
        # AI Signal
        self.signal_widget = self.create_metric_widget("Signal", "ANALYZING...", "#ffff00")
        top_layout.addWidget(self.signal_widget)
        
        # Confidence
        self.confidence_widget = self.create_metric_widget("Confidence", "0%", "#888888")
        top_layout.addWidget(self.confidence_widget)
        
        # Volatility
        self.volatility_widget = self.create_metric_widget("Volatility", "MEDIUM", "#ff8800")
        top_layout.addWidget(self.volatility_widget)
        
        # Live indicator
        live_widget = self.create_metric_widget("Status", "🔴 LIVE", "#ff0000")
        top_layout.addWidget(live_widget)
        
        main_layout.addLayout(top_layout, 0)
        
        # Main chart (12/12 - full width and height)
        main_chart = self.create_main_chart()
        main_layout.addWidget(main_chart, 1)
        
        # Bottom section - AI Analysis Table (compact)
        ai_table = self.create_ai_analysis_table()
        main_layout.addWidget(ai_table, 0)
        
    def create_metric_widget(self, title, value, color):
        """Create metric display widget"""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: #1a1a1a;
                border: 1px solid {color};
                border-radius: 3px;
                padding: 3px;
            }}
        """)
        widget.setMaximumHeight(50)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(3, 2, 3, 2)
        layout.setSpacing(1)
        
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(8)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #888888;")
        
        value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(10)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setStyleSheet(f"color: {color};")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return widget
    
    def create_main_chart(self):
        """Create main candlestick chart with all indicators"""
        self.chart = QChart()
        self.chart.setTitle("XAUUSD - Real-Time Price Analysis (LIVE DATA)")
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setBackgroundBrush(QBrush(QColor("#0a0a0a")))
        self.chart.setTitleBrush(QBrush(QColor("#00ff00")))
        
        # Create candlestick series
        series = QCandlestickSeries()
        series.setName("XAUUSD")
        
        # Add candlesticks
        for idx, row in self.data.tail(100).iterrows():
            candlestick = QCandlestickSet(
                row['open'], row['high'], row['low'], row['close']
            )
            candlestick.setTimestamp(int(row['date'].timestamp() * 1000))
            series.append(candlestick)
        
        self.chart.addSeries(series)
        
        # Add MA20 (Blue)
        ma20_series = QLineSeries()
        ma20_series.setName("MA20")
        for idx, row in self.data.tail(100).iterrows():
            if pd.notna(row.get('MA20')):
                ma20_series.append(int(row['date'].timestamp() * 1000), row['MA20'])
        self.chart.addSeries(ma20_series)
        
        # Add MA50 (Red)
        ma50_series = QLineSeries()
        ma50_series.setName("MA50")
        for idx, row in self.data.tail(100).iterrows():
            if pd.notna(row.get('MA50')):
                ma50_series.append(int(row['date'].timestamp() * 1000), row['MA50'])
        self.chart.addSeries(ma50_series)
        
        # Add MA200 (Yellow)
        ma200_series = QLineSeries()
        ma200_series.setName("MA200")
        for idx, row in self.data.tail(100).iterrows():
            if pd.notna(row.get('MA200')):
                ma200_series.append(int(row['date'].timestamp() * 1000), row['MA200'])
        self.chart.addSeries(ma200_series)
        
        # Axes
        axis_x = QDateTimeAxis()
        axis_x.setFormat("hh:mm")
        axis_x.setLabelsColor(QColor("#888888"))
        axis_x.setGridLineColor(QColor("#222222"))
        self.chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        ma20_series.attachAxis(axis_x)
        ma50_series.attachAxis(axis_x)
        ma200_series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setRange(self.data['low'].min() - 5, self.data['high'].max() + 5)
        axis_y.setLabelsColor(QColor("#888888"))
        axis_y.setGridLineColor(QColor("#222222"))
        self.chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        ma20_series.attachAxis(axis_y)
        ma50_series.attachAxis(axis_y)
        ma200_series.attachAxis(axis_y)
        
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setStyleSheet("background-color: #0a0a0a;")
        
        return self.chart_view
    
    def create_ai_analysis_table(self):
        """Create AI analysis table"""
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Indicator", "Value", "Signal"])
        self.table.setRowCount(10)
        self.table.setMaximumHeight(120)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1a1a1a;
                color: #00ff00;
                gridline-color: #333333;
                border: 1px solid #333333;
            }
            QHeaderView::section {
                background-color: #0a0a0a;
                color: #00ff00;
                padding: 3px;
                border: 1px solid #333333;
            }
            QTableWidget::item {
                padding: 2px;
            }
        """)
        
        indicators = [
            ("Trend", "UPTREND", "BULLISH"),
            ("RSI (14)", "65", "NEUTRAL"),
            ("MACD", "0.25", "BULLISH"),
            ("Stochastic", "75", "OVERBOUGHT"),
            ("Bollinger Bands", "MIDDLE", "NEUTRAL"),
            ("MA20", "2048.50", "ABOVE"),
            ("MA50", "2045.00", "ABOVE"),
            ("Volatility", "MEDIUM", "NORMAL"),
            ("AI Recommendation", "BUY", "STRONG"),
            ("Confidence Level", "78%", "HIGH"),
        ]
        
        for i, (indicator, value, signal) in enumerate(indicators):
            self.table.setItem(i, 0, QTableWidgetItem(indicator))
            self.table.setItem(i, 1, QTableWidgetItem(value))
            
            signal_item = QTableWidgetItem(signal)
            
            if "BULL" in signal or "BUY" in signal or "ABOVE" in signal:
                signal_item.setBackground(QBrush(QColor("#1a3a1a")))
                signal_item.setForeground(QBrush(QColor("#00ff00")))
            elif "BEAR" in signal or "SELL" in signal or "BELOW" in signal:
                signal_item.setBackground(QBrush(QColor("#3a1a1a")))
                signal_item.setForeground(QBrush(QColor("#ff0000")))
            elif "OVERBOUGHT" in signal:
                signal_item.setBackground(QBrush(QColor("#3a3a1a")))
                signal_item.setForeground(QBrush(QColor("#ffff00")))
            
            self.table.setItem(i, 2, signal_item)
        
        return self.table
    
    def generate_sample_data(self):
        """Generate sample data"""
        dates = pd.date_range(end=datetime.now(), periods=300, freq='5min')
        
        np.random.seed(42)
        prices = 2050 + np.cumsum(np.random.randn(300) * 2)
        
        data = pd.DataFrame({
            'date': dates,
            'open': prices + np.random.randn(300) * 0.5,
            'high': prices + np.abs(np.random.randn(300) * 1.5),
            'low': prices - np.abs(np.random.randn(300) * 1.5),
            'close': prices,
            'volume': np.random.randint(1000, 10000, 300)
        })
        
        # Calculate MAs
        data['MA20'] = data['close'].rolling(20).mean()
        data['MA50'] = data['close'].rolling(50).mean()
        data['MA200'] = data['close'].rolling(200).mean()
        
        return data
    
    def apply_dark_mode(self):
        """Apply dark mode to entire widget"""
        self.setStyleSheet("""
            QWidget {
                background-color: #0a0a0a;
                color: #00ff00;
            }
            QLabel {
                color: #00ff00;
            }
            QTableWidget {
                background-color: #1a1a1a;
                color: #00ff00;
                gridline-color: #333333;
            }
            QHeaderView::section {
                background-color: #0a0a0a;
                color: #00ff00;
                padding: 3px;
                border: 1px solid #333333;
            }
            QScrollBar:vertical {
                background-color: #1a1a1a;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background-color: #333333;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #555555;
            }
        """)
    
    def closeEvent(self, event):
        """Clean up when closing"""
        self.data_updater.stop()
        self.analysis_updater.stop()
        event.accept()

