"""
Advanced Professional Trading Dashboard
Complete with all charts, indicators, oscillators, and AI analysis on one screen
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
from PyQt5.QtGui import QFont, QColor, QBrush
from PyQt5.QtChart import QChart, QChartView, QCandlestickSeries, QCandlestickSet
from PyQt5.QtChart import QLineSeries, QDateTimeAxis, QValueAxis, QBarSeries, QBarSet, QBarCategoryAxis
from PyQt5.QtCore import QDateTime, QPointF


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
        """Perform comprehensive AI analysis"""
        prices = self.data['close'].values
        
        # Trend analysis
        ma20 = np.mean(prices[-20:]) if len(prices) >= 20 else np.mean(prices)
        ma50 = np.mean(prices[-50:]) if len(prices) >= 50 else np.mean(prices)
        ma200 = np.mean(prices[-200:]) if len(prices) >= 200 else np.mean(prices)
        current_price = prices[-1]
        
        trend = "UPTREND" if ma20 > ma50 > ma200 else "DOWNTREND" if ma20 < ma50 < ma200 else "SIDEWAYS"
        trend_strength = abs(ma20 - ma50) / ma50 * 100
        
        # RSI Analysis
        rsi = self.calculate_rsi(prices)
        rsi_signal = "OVERBOUGHT" if rsi > 70 else "OVERSOLD" if rsi < 30 else "NEUTRAL"
        
        # MACD Analysis
        ema12 = self.calculate_ema(prices, 12)
        ema26 = self.calculate_ema(prices, 26)
        macd = ema12 - ema26
        macd_signal = "BULLISH" if macd > 0 else "BEARISH"
        
        # Stochastic Analysis
        stoch = self.calculate_stochastic(prices)
        stoch_signal = "OVERBOUGHT" if stoch > 80 else "OVERSOLD" if stoch < 20 else "NEUTRAL"
        
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
        
        # ATR (Average True Range)
        atr = self.calculate_atr(self.data)
        volatility = "HIGH" if atr > np.mean(prices) * 0.02 else "LOW"
        
        # AI Recommendation
        signals = [
            ("BULL" if "UP" in trend else "BEAR"),
            ("BULL" if "OVERBOUGHT" not in rsi_signal else "BEAR"),
            ("BULL" if "BULLISH" in macd_signal else "BEAR"),
            ("BULL" if "OVERBOUGHT" not in stoch_signal else "BEAR"),
            ("BULL" if "OVERBOUGHT" not in bb_signal else "BEAR"),
        ]
        
        bullish_count = sum(1 for s in signals if "BULL" in s)
        bearish_count = len(signals) - bullish_count
        
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
            'stoch': stoch,
            'stoch_signal': stoch_signal,
            'bb_signal': bb_signal,
            'volatility': volatility,
            'atr': atr,
            'recommendation': recommendation,
            'confidence': confidence,
            'current_price': current_price,
            'ma20': ma20,
            'ma50': ma50,
            'ma200': ma200,
            'bb_upper': bb_upper,
            'bb_lower': bb_lower,
            'bb_middle': bb_middle
        }
    
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
    
    @staticmethod
    def calculate_ema(prices, period):
        """Calculate EMA"""
        multiplier = 2 / (period + 1)
        ema = np.mean(prices[:period])
        
        for price in prices[period:]:
            ema = price * multiplier + ema * (1 - multiplier)
        
        return ema
    
    @staticmethod
    def calculate_stochastic(prices, period=14):
        """Calculate Stochastic"""
        if len(prices) < period:
            return 50
        
        low = np.min(prices[-period:])
        high = np.max(prices[-period:])
        close = prices[-1]
        
        if high == low:
            return 50
        
        stoch = ((close - low) / (high - low)) * 100
        return stoch
    
    @staticmethod
    def calculate_atr(data, period=14):
        """Calculate ATR"""
        if len(data) < period:
            return 0
        
        high = data['high'].values[-period:]
        low = data['low'].values[-period:]
        close = data['close'].values[-period:]
        
        tr = np.maximum(
            high - low,
            np.maximum(
                np.abs(high - np.roll(close, 1)),
                np.abs(low - np.roll(close, 1))
            )
        )
        
        atr = np.mean(tr)
        return atr


class AdvancedProfessionalDashboard(QWidget):
    """Advanced professional dashboard with all indicators on one screen"""
    
    def __init__(self):
        super().__init__()
        self.data = self.generate_sample_data()
        self.analysis = None
        self.init_ui()
        self.start_ai_analysis()
        
    def init_ui(self):
        """Initialize UI"""
        main_layout = QVBoxLayout(self)
        
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
        
        # Volatility
        self.volatility_widget = self.create_metric_widget("Volatility", "MEDIUM", "orange")
        top_layout.addWidget(self.volatility_widget)
        
        main_layout.addLayout(top_layout)
        
        # Main grid layout for charts
        grid_layout = QGridLayout()
        
        # Row 1: Candlestick chart (large)
        candlestick_chart = self.create_candlestick_chart()
        grid_layout.addWidget(candlestick_chart, 0, 0, 2, 2)
        
        # Row 1, Col 3: RSI
        rsi_chart = self.create_rsi_chart()
        grid_layout.addWidget(rsi_chart, 0, 2)
        
        # Row 1, Col 4: Stochastic
        stoch_chart = self.create_stochastic_chart()
        grid_layout.addWidget(stoch_chart, 0, 3)
        
        # Row 2, Col 3: MACD
        macd_chart = self.create_macd_chart()
        grid_layout.addWidget(macd_chart, 1, 2)
        
        # Row 2, Col 4: Bollinger Bands
        bb_chart = self.create_bollinger_bands_chart()
        grid_layout.addWidget(bb_chart, 1, 3)
        
        # Row 3: AI Analysis Table (full width)
        ai_table = self.create_ai_analysis_table()
        grid_layout.addWidget(ai_table, 2, 0, 1, 4)
        
        main_layout.addLayout(grid_layout)
        
    def create_metric_widget(self, title, value, color):
        """Create metric display widget"""
        widget = QFrame()
        widget.setStyleSheet(f"background-color: #f0f0f0; border-radius: 5px; border: 2px solid {color};")
        widget.setMaximumHeight(80)
        
        layout = QVBoxLayout(widget)
        
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(9)
        title_label.setFont(title_font)
        
        value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(12)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setStyleSheet(f"color: {color};")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return widget
    
    def create_candlestick_chart(self):
        """Create main candlestick chart with all indicators"""
        chart = QChart()
        chart.setTitle("XAUUSD - Price Analysis with Indicators")
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
        
        # Add MA20
        ma20_series = QLineSeries()
        ma20_series.setName("MA20")
        for idx, row in self.data.tail(50).iterrows():
            if pd.notna(row.get('MA20')):
                ma20_series.append(int(row['date'].timestamp() * 1000), row['MA20'])
        chart.addSeries(ma20_series)
        
        # Add MA50
        ma50_series = QLineSeries()
        ma50_series.setName("MA50")
        for idx, row in self.data.tail(50).iterrows():
            if pd.notna(row.get('MA50')):
                ma50_series.append(int(row['date'].timestamp() * 1000), row['MA50'])
        chart.addSeries(ma50_series)
        
        # Axes
        axis_x = QDateTimeAxis()
        axis_x.setFormat("hh:mm")
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        ma20_series.attachAxis(axis_x)
        ma50_series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setRange(self.data['low'].min() - 5, self.data['high'].max() + 5)
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        ma20_series.attachAxis(axis_y)
        ma50_series.attachAxis(axis_y)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(chart_view.Antialiasing)
        chart_view.setMinimumHeight(300)
        
        return chart_view
    
    def create_rsi_chart(self):
        """Create RSI chart"""
        chart = QChart()
        chart.setTitle("RSI (14)")
        
        rsi_series = QLineSeries()
        rsi_series.setName("RSI")
        
        for idx, row in self.data.tail(50).iterrows():
            rsi = AIAnalysisThread.calculate_rsi(self.data['close'].values[:idx+1])
            rsi_series.append(int(row['date'].timestamp() * 1000), rsi)
        
        chart.addSeries(rsi_series)
        
        axis_x = QDateTimeAxis()
        axis_x.setFormat("hh:mm")
        chart.addAxis(axis_x, Qt.AlignBottom)
        rsi_series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setRange(0, 100)
        chart.addAxis(axis_y, Qt.AlignLeft)
        rsi_series.attachAxis(axis_y)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(chart_view.Antialiasing)
        chart_view.setMinimumHeight(200)
        
        return chart_view
    
    def create_stochastic_chart(self):
        """Create Stochastic chart"""
        chart = QChart()
        chart.setTitle("Stochastic")
        
        stoch_series = QLineSeries()
        stoch_series.setName("Stochastic")
        
        for idx, row in self.data.tail(50).iterrows():
            stoch = AIAnalysisThread.calculate_stochastic(self.data['close'].values[:idx+1])
            stoch_series.append(int(row['date'].timestamp() * 1000), stoch)
        
        chart.addSeries(stoch_series)
        
        axis_x = QDateTimeAxis()
        axis_x.setFormat("hh:mm")
        chart.addAxis(axis_x, Qt.AlignBottom)
        stoch_series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setRange(0, 100)
        chart.addAxis(axis_y, Qt.AlignLeft)
        stoch_series.attachAxis(axis_y)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(chart_view.Antialiasing)
        chart_view.setMinimumHeight(200)
        
        return chart_view
    
    def create_macd_chart(self):
        """Create MACD chart"""
        chart = QChart()
        chart.setTitle("MACD")
        
        macd_series = QLineSeries()
        macd_series.setName("MACD")
        
        for idx, row in self.data.tail(50).iterrows():
            prices = self.data['close'].values[:idx+1]
            ema12 = AIAnalysisThread.calculate_ema(prices, 12)
            ema26 = AIAnalysisThread.calculate_ema(prices, 26)
            macd = ema12 - ema26
            macd_series.append(int(row['date'].timestamp() * 1000), macd)
        
        chart.addSeries(macd_series)
        
        axis_x = QDateTimeAxis()
        axis_x.setFormat("hh:mm")
        chart.addAxis(axis_x, Qt.AlignBottom)
        macd_series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        chart.addAxis(axis_y, Qt.AlignLeft)
        macd_series.attachAxis(axis_y)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(chart_view.Antialiasing)
        chart_view.setMinimumHeight(200)
        
        return chart_view
    
    def create_bollinger_bands_chart(self):
        """Create Bollinger Bands chart"""
        chart = QChart()
        chart.setTitle("Bollinger Bands")
        
        prices = self.data['close'].values
        bb_middle = np.mean(prices[-20:])
        bb_std = np.std(prices[-20:])
        
        bb_series = QLineSeries()
        bb_series.setName("Price")
        
        for idx, row in self.data.tail(50).iterrows():
            bb_series.append(int(row['date'].timestamp() * 1000), row['close'])
        
        chart.addSeries(bb_series)
        
        axis_x = QDateTimeAxis()
        axis_x.setFormat("hh:mm")
        chart.addAxis(axis_x, Qt.AlignBottom)
        bb_series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setRange(self.data['low'].min() - 5, self.data['high'].max() + 5)
        chart.addAxis(axis_y, Qt.AlignLeft)
        bb_series.attachAxis(axis_y)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(chart_view.Antialiasing)
        chart_view.setMinimumHeight(200)
        
        return chart_view
    
    def create_ai_analysis_table(self):
        """Create AI analysis table"""
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Indicator", "Value", "Signal"])
        table.setRowCount(10)
        table.setMaximumHeight(200)
        
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
            table.setItem(i, 0, QTableWidgetItem(indicator))
            table.setItem(i, 1, QTableWidgetItem(value))
            
            signal_item = QTableWidgetItem(signal)
            
            if "BULL" in signal or "BUY" in signal or "ABOVE" in signal:
                signal_item.setBackground(QBrush(QColor("lightgreen")))
            elif "BEAR" in signal or "SELL" in signal or "BELOW" in signal:
                signal_item.setBackground(QBrush(QColor("lightcoral")))
            elif "OVERBOUGHT" in signal:
                signal_item.setBackground(QBrush(QColor("orange")))
            elif "OVERSOLD" in signal:
                signal_item.setBackground(QBrush(QColor("lightyellow")))
            
            table.setItem(i, 2, signal_item)
        
        return table
    
    def generate_sample_data(self):
        """Generate sample data"""
        dates = pd.date_range(end=datetime.now(), periods=200, freq='5min')
        
        np.random.seed(42)
        prices = 2050 + np.cumsum(np.random.randn(200) * 2)
        
        data = pd.DataFrame({
            'date': dates,
            'open': prices + np.random.randn(200) * 0.5,
            'high': prices + np.abs(np.random.randn(200) * 1.5),
            'low': prices - np.abs(np.random.randn(200) * 1.5),
            'close': prices,
            'volume': np.random.randint(1000, 10000, 200)
        })
        
        # Calculate MAs
        data['MA20'] = data['close'].rolling(20).mean()
        data['MA50'] = data['close'].rolling(50).mean()
        
        return data
    
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
        
        # Update confidence widget
        self.confidence_widget.findChild(QLabel).setText(f"{confidence:.0f}%")
        
        # Update volatility widget
        volatility = analysis['volatility']
        vol_color = "red" if volatility == "HIGH" else "green"
        self.volatility_widget.setStyleSheet(f"background-color: #f0f0f0; border-radius: 5px; border: 2px solid {vol_color};")

