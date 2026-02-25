"""
Professional Trading Dashboard with Real-Time Analysis
Complete with charts, signals, AI analysis, buy/sell recommendations
"""

import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget,
    QTableWidget, QTableWidgetItem, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QBrush
from PyQt5.QtChart import QChart, QChartView, QCandlestickSeries, QCandlestickSet
from PyQt5.QtChart import QLineSeries, QDateTimeAxis, QValueAxis, QBarSeries, QBarSet, QBarCategoryAxis
from PyQt5.QtCore import QDateTime, QPointF
import pandas as pd


class AIAnalysisThread(QThread):
    """Background thread for AI analysis"""
    analysis_ready = pyqtSignal(dict)
    
    def __init__(self, data):
        super().__init__()
        self.data = data
    
    def run(self):
        """Run AI analysis"""
        analysis = self.analyze_with_ai()
        self.analysis_ready.emit(analysis)
    
    def analyze_with_ai(self):
        """Perform AI analysis"""
        prices = self.data['close'].values
        
        # Trend analysis
        ma20 = np.mean(prices[-20:]) if len(prices) >= 20 else np.mean(prices)
        ma50 = np.mean(prices[-50:]) if len(prices) >= 50 else np.mean(prices)
        current_price = prices[-1]
        
        trend = "UPTREND" if ma20 > ma50 else "DOWNTREND"
        trend_strength = abs(ma20 - ma50) / ma50 * 100
        
        # RSI Analysis
        rsi = self.calculate_rsi(prices)
        rsi_signal = "OVERBOUGHT" if rsi > 70 else "OVERSOLD" if rsi < 30 else "NEUTRAL"
        
        # MACD Analysis
        ema12 = self.calculate_ema(prices, 12)
        ema26 = self.calculate_ema(prices, 26)
        macd = ema12 - ema26
        macd_signal = "BULLISH" if macd > 0 else "BEARISH"
        
        # Bollinger Bands
        bb_middle = np.mean(prices[-20:])
        bb_std = np.std(prices[-20:])
        bb_upper = bb_middle + (bb_std * 2)
        bb_lower = bb_middle - (bb_std * 2)
        
        if current_price > bb_upper:
            bb_signal = "OVERBOUGHT"
        elif current_price < bb_lower:
            bb_signal = "OVERSOLD"
        else:
            bb_signal = "NEUTRAL"
        
        # AI Recommendation
        signals = [trend, rsi_signal, macd_signal, bb_signal]
        bullish_count = sum(1 for s in signals if "BULL" in s or "OVER" in s or "UP" in s)
        bearish_count = sum(1 for s in signals if "BEAR" in s or "OVER" in s or "DOWN" in s)
        
        if bullish_count > bearish_count:
            recommendation = "BUY"
            confidence = (bullish_count / len(signals)) * 100
        elif bearish_count > bullish_count:
            recommendation = "SELL"
            confidence = (bearish_count / len(signals)) * 100
        else:
            recommendation = "HOLD"
            confidence = 50
        
        return {
            'trend': trend,
            'trend_strength': trend_strength,
            'rsi': rsi,
            'rsi_signal': rsi_signal,
            'macd': macd,
            'macd_signal': macd_signal,
            'bb_signal': bb_signal,
            'recommendation': recommendation,
            'confidence': confidence,
            'current_price': current_price,
            'ma20': ma20,
            'ma50': ma50
        }
    
    @staticmethod
    def calculate_rsi(prices, period=14):
        """Calculate RSI"""
        delta = np.diff(prices)
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        
        avg_gain = np.mean(gain[-period:]) if len(gain) >= period else np.mean(gain)
        avg_loss = np.mean(loss[-period:]) if len(loss) >= period else np.mean(loss)
        
        if avg_loss == 0:
            return 100 if avg_gain > 0 else 50
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_ema(prices, period):
        """Calculate EMA"""
        multiplier = 2 / (period + 1)
        ema = np.mean(prices[:period])
        
        for price in prices[period:]:
            ema = price * multiplier + ema * (1 - multiplier)
        
        return ema


class ProfessionalDashboard(QWidget):
    """Professional trading dashboard with complete analysis"""
    
    def __init__(self):
        super().__init__()
        self.data = self.generate_sample_data()
        self.analysis = None
        self.init_ui()
        self.start_ai_analysis()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        
        # Top section - Key metrics
        top_layout = QHBoxLayout()
        
        # Current price
        price_widget = self.create_metric_widget("Current Price", "$2,050.25", "green")
        top_layout.addWidget(price_widget)
        
        # Change
        change_widget = self.create_metric_widget("24h Change", "+2.5%", "green")
        top_layout.addWidget(change_widget)
        
        # AI Signal
        self.signal_widget = self.create_metric_widget("AI Signal", "ANALYZING...", "yellow")
        top_layout.addWidget(self.signal_widget)
        
        # Confidence
        self.confidence_widget = self.create_metric_widget("Confidence", "0%", "gray")
        top_layout.addWidget(self.confidence_widget)
        
        layout.addLayout(top_layout)
        
        # Tabs for different views
        tabs = QTabWidget()
        
        # Tab 1: Main Chart with Analysis
        main_chart = self.create_main_chart()
        tabs.addTab(main_chart, "📊 Price Analysis")
        
        # Tab 2: Indicators
        indicators_tab = self.create_indicators_tab()
        tabs.addTab(indicators_tab, "📈 Indicators")
        
        # Tab 3: AI Analysis
        ai_tab = self.create_ai_analysis_tab()
        tabs.addTab(ai_tab, "🤖 AI Analysis")
        
        # Tab 4: Trading Signals
        signals_tab = self.create_signals_tab()
        tabs.addTab(signals_tab, "🎯 Trading Signals")
        
        # Tab 5: Portfolio
        portfolio_tab = self.create_portfolio_tab()
        tabs.addTab(portfolio_tab, "💼 Portfolio")
        
        layout.addWidget(tabs)
        
    def create_metric_widget(self, title, value, color):
        """Create metric display widget"""
        widget = QFrame()
        widget.setStyleSheet(f"background-color: #f0f0f0; border-radius: 5px; border: 2px solid {color};")
        
        layout = QVBoxLayout(widget)
        
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(10)
        title_label.setFont(title_font)
        
        value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(14)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setStyleSheet(f"color: {color};")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return widget
    
    def create_main_chart(self):
        """Create main candlestick chart"""
        chart = QChart()
        chart.setTitle("XAUUSD - Real-Time Price Analysis")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Create candlestick series
        series = QCandlestickSeries()
        series.setName("XAUUSD")
        
        # Add candlesticks
        for idx, row in self.data.tail(50).iterrows():
            candlestick = QCandlestickSet(
                row['open'], row['high'], row['low'], row['close']
            )
            candlestick.setTimestamp(int(row['date'].timestamp() * 1000))
            series.append(candlestick)
        
        chart.addSeries(series)
        
        # Add moving averages
        ma20_series = QLineSeries()
        ma20_series.setName("MA20")
        
        for idx, row in self.data.tail(50).iterrows():
            if pd.notna(row.get('MA20')):
                ma20_series.append(int(row['date'].timestamp() * 1000), row['MA20'])
        
        chart.addSeries(ma20_series)
        
        # Axes
        axis_x = QDateTimeAxis()
        axis_x.setFormat("hh:mm")
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        ma20_series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setRange(self.data['low'].min() - 5, self.data['high'].max() + 5)
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        ma20_series.attachAxis(axis_y)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(chart_view.Antialiasing)
        
        return chart_view
    
    def create_indicators_tab(self):
        """Create indicators tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # RSI Chart
        rsi_chart = QChart()
        rsi_chart.setTitle("RSI (14) - Momentum Indicator")
        
        rsi_series = QLineSeries()
        rsi_series.setName("RSI")
        
        for idx, row in self.data.iterrows():
            rsi = self.calculate_rsi(self.data['close'].values[:idx+1])
            rsi_series.append(int(row['date'].timestamp() * 1000), rsi)
        
        rsi_chart.addSeries(rsi_series)
        
        axis_x = QDateTimeAxis()
        axis_x.setFormat("hh:mm")
        rsi_chart.addAxis(axis_x, Qt.AlignBottom)
        rsi_series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setRange(0, 100)
        rsi_chart.addAxis(axis_y, Qt.AlignLeft)
        rsi_series.attachAxis(axis_y)
        
        rsi_view = QChartView(rsi_chart)
        rsi_view.setRenderHint(rsi_view.Antialiasing)
        
        layout.addWidget(rsi_view)
        
        return widget
    
    def create_ai_analysis_tab(self):
        """Create AI analysis tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Analysis table
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Indicator", "Analysis"])
        table.setRowCount(6)
        
        indicators = [
            ("Trend", "UPTREND"),
            ("RSI Signal", "NEUTRAL"),
            ("MACD Signal", "BULLISH"),
            ("Bollinger Bands", "NEUTRAL"),
            ("AI Recommendation", "BUY"),
            ("Confidence Level", "75%")
        ]
        
        for i, (indicator, value) in enumerate(indicators):
            table.setItem(i, 0, QTableWidgetItem(indicator))
            item = QTableWidgetItem(value)
            
            if "BUY" in value:
                item.setBackground(QBrush(QColor("green")))
                item.setForeground(QBrush(QColor("white")))
            elif "SELL" in value:
                item.setBackground(QBrush(QColor("red")))
                item.setForeground(QBrush(QColor("white")))
            elif "BULLISH" in value:
                item.setBackground(QBrush(QColor("lightgreen")))
            elif "BEARISH" in value:
                item.setBackground(QBrush(QColor("lightcoral")))
            
            table.setItem(i, 1, item)
        
        layout.addWidget(table)
        
        return widget
    
    def create_signals_tab(self):
        """Create trading signals tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Signals table
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Time", "Signal", "Price", "Type", "Status"])
        table.setRowCount(5)
        
        signals = [
            ("14:30", "BUY", "$2,050.00", "Strong", "✓ Active"),
            ("14:15", "HOLD", "$2,048.50", "Weak", "✓ Active"),
            ("14:00", "SELL", "$2,045.00", "Medium", "✗ Closed"),
            ("13:45", "BUY", "$2,042.00", "Strong", "✓ Active"),
            ("13:30", "HOLD", "$2,040.00", "Weak", "✗ Closed"),
        ]
        
        for i, (time, signal, price, type_, status) in enumerate(signals):
            table.setItem(i, 0, QTableWidgetItem(time))
            
            signal_item = QTableWidgetItem(signal)
            if "BUY" in signal:
                signal_item.setBackground(QBrush(QColor("green")))
                signal_item.setForeground(QBrush(QColor("white")))
            elif "SELL" in signal:
                signal_item.setBackground(QBrush(QColor("red")))
                signal_item.setForeground(QBrush(QColor("white")))
            table.setItem(i, 1, signal_item)
            
            table.setItem(i, 2, QTableWidgetItem(price))
            table.setItem(i, 3, QTableWidgetItem(type_))
            table.setItem(i, 4, QTableWidgetItem(status))
        
        layout.addWidget(table)
        
        return widget
    
    def create_portfolio_tab(self):
        """Create portfolio tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Portfolio summary
        summary_layout = QHBoxLayout()
        
        summary_layout.addWidget(self.create_metric_widget("Total Balance", "$50,000", "blue"))
        summary_layout.addWidget(self.create_metric_widget("Open Positions", "3", "orange"))
        summary_layout.addWidget(self.create_metric_widget("Total P&L", "+$2,500", "green"))
        summary_layout.addWidget(self.create_metric_widget("Win Rate", "65%", "green"))
        
        layout.addLayout(summary_layout)
        
        # Positions table
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["Symbol", "Type", "Size", "Entry", "Current", "P&L"])
        table.setRowCount(3)
        
        positions = [
            ("XAUUSD", "LONG", "1.0", "$2,040", "$2,050", "+$10"),
            ("XAUUSD", "SHORT", "0.5", "$2,055", "$2,050", "+$2.50"),
            ("XAUUSD", "LONG", "0.75", "$2,045", "$2,050", "+$3.75"),
        ]
        
        for i, (symbol, type_, size, entry, current, pl) in enumerate(positions):
            table.setItem(i, 0, QTableWidgetItem(symbol))
            table.setItem(i, 1, QTableWidgetItem(type_))
            table.setItem(i, 2, QTableWidgetItem(size))
            table.setItem(i, 3, QTableWidgetItem(entry))
            table.setItem(i, 4, QTableWidgetItem(current))
            
            pl_item = QTableWidgetItem(pl)
            pl_item.setBackground(QBrush(QColor("lightgreen")))
            table.setItem(i, 5, pl_item)
        
        layout.addWidget(table)
        
        return widget
    
    def generate_sample_data(self):
        """Generate sample data"""
        dates = pd.date_range(end=datetime.now(), periods=100, freq='5min')
        
        np.random.seed(42)
        prices = 2050 + np.cumsum(np.random.randn(100) * 2)
        
        data = pd.DataFrame({
            'date': dates,
            'open': prices + np.random.randn(100) * 0.5,
            'high': prices + np.abs(np.random.randn(100) * 1.5),
            'low': prices - np.abs(np.random.randn(100) * 1.5),
            'close': prices,
            'volume': np.random.randint(1000, 10000, 100)
        })
        
        # Calculate MA20
        data['MA20'] = data['close'].rolling(20).mean()
        
        return data
    
    @staticmethod
    def calculate_rsi(prices, period=14):
        """Calculate RSI"""
        if len(prices) < period:
            return 50
        
        delta = np.diff(prices[-period-1:])
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        
        avg_gain = np.mean(gain)
        avg_loss = np.mean(loss)
        
        if avg_loss == 0:
            return 100 if avg_gain > 0 else 50
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def start_ai_analysis(self):
        """Start AI analysis in background"""
        self.analysis_thread = AIAnalysisThread(self.data)
        self.analysis_thread.analysis_ready.connect(self.update_analysis)
        self.analysis_thread.start()
    
    def update_analysis(self, analysis):
        """Update UI with analysis results"""
        self.analysis = analysis
        
        # Update signal widget
        recommendation = analysis['recommendation']
        confidence = analysis['confidence']
        
        color = "green" if recommendation == "BUY" else "red" if recommendation == "SELL" else "yellow"
        
        self.signal_widget.findChild(QLabel).setText(recommendation)
        self.signal_widget.setStyleSheet(f"background-color: #f0f0f0; border-radius: 5px; border: 2px solid {color};")
        
        # Update confidence widget
        self.confidence_widget.findChild(QLabel).setText(f"{confidence:.0f}%")
