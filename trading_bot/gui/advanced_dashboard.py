"""
Advanced Trading Dashboard with Charts, Indicators, and Oscillators
"""

import sys
import numpy as np
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget,
    QComboBox, QSpinBox, QCheckBox, QPushButton
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtChart import QChart, QChartView, QCandlestickSeries, QCandlestickSet
from PyQt5.QtChart import QLineSeries, QDateTimeAxis, QValueAxis
from PyQt5.QtCore import QDateTime, QPointF
import pandas as pd


class AdvancedDashboard(QWidget):
    """Advanced trading dashboard with multiple charts and indicators"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.generate_sample_data()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        
        # Control panel
        control_layout = QHBoxLayout()
        
        control_layout.addWidget(QLabel("Timeframe:"))
        timeframe_combo = QComboBox()
        timeframe_combo.addItems(["1m", "5m", "15m", "1h", "4h", "1d"])
        control_layout.addWidget(timeframe_combo)
        
        control_layout.addWidget(QLabel("Candles:"))
        candles_spin = QSpinBox()
        candles_spin.setValue(50)
        candles_spin.setMaximum(500)
        control_layout.addWidget(candles_spin)
        
        control_layout.addWidget(QLabel("Indicators:"))
        ma_check = QCheckBox("MA")
        ma_check.setChecked(True)
        control_layout.addWidget(ma_check)
        
        rsi_check = QCheckBox("RSI")
        rsi_check.setChecked(True)
        control_layout.addWidget(rsi_check)
        
        macd_check = QCheckBox("MACD")
        macd_check.setChecked(True)
        control_layout.addWidget(macd_check)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        # Tabs for different charts
        tabs = QTabWidget()
        
        # Tab 1: Candlestick Chart
        self.candlestick_chart = self.create_candlestick_chart()
        tabs.addTab(self.candlestick_chart, "📊 Candlestick Chart")
        
        # Tab 2: Price with Moving Averages
        self.ma_chart = self.create_ma_chart()
        tabs.addTab(self.ma_chart, "📈 Moving Averages")
        
        # Tab 3: RSI Oscillator
        self.rsi_chart = self.create_rsi_chart()
        tabs.addTab(self.rsi_chart, "📉 RSI Oscillator")
        
        # Tab 4: MACD
        self.macd_chart = self.create_macd_chart()
        tabs.addTab(self.macd_chart, "🔄 MACD")
        
        # Tab 5: Stochastic
        self.stoch_chart = self.create_stochastic_chart()
        tabs.addTab(self.stoch_chart, "⚡ Stochastic")
        
        # Tab 6: Bollinger Bands
        self.bb_chart = self.create_bollinger_chart()
        tabs.addTab(self.bb_chart, "🎯 Bollinger Bands")
        
        layout.addWidget(tabs)
        
    def generate_sample_data(self):
        """Generate sample OHLC data"""
        dates = pd.date_range(end=datetime.now(), periods=100, freq='5min')
        
        # Generate realistic price data
        np.random.seed(42)
        prices = 2050 + np.cumsum(np.random.randn(100) * 2)
        
        self.data = pd.DataFrame({
            'date': dates,
            'open': prices + np.random.randn(100) * 0.5,
            'high': prices + np.abs(np.random.randn(100) * 1.5),
            'low': prices - np.abs(np.random.randn(100) * 1.5),
            'close': prices,
            'volume': np.random.randint(1000, 10000, 100)
        })
        
        # Calculate indicators
        self.calculate_indicators()
        
    def calculate_indicators(self):
        """Calculate technical indicators"""
        # Moving Averages
        self.data['MA20'] = self.data['close'].rolling(20).mean()
        self.data['MA50'] = self.data['close'].rolling(50).mean()
        
        # RSI
        self.data['RSI'] = self.calculate_rsi(self.data['close'], 14)
        
        # MACD
        ema12 = self.data['close'].ewm(span=12).mean()
        ema26 = self.data['close'].ewm(span=26).mean()
        self.data['MACD'] = ema12 - ema26
        self.data['Signal'] = self.data['MACD'].ewm(span=9).mean()
        self.data['Histogram'] = self.data['MACD'] - self.data['Signal']
        
        # Stochastic
        self.data['Stoch_K'], self.data['Stoch_D'] = self.calculate_stochastic(
            self.data['high'], self.data['low'], self.data['close'], 14
        )
        
        # Bollinger Bands
        self.data['BB_Middle'] = self.data['close'].rolling(20).mean()
        bb_std = self.data['close'].rolling(20).std()
        self.data['BB_Upper'] = self.data['BB_Middle'] + (bb_std * 2)
        self.data['BB_Lower'] = self.data['BB_Middle'] - (bb_std * 2)
        
    @staticmethod
    def calculate_rsi(prices, period=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_stochastic(high, low, close, period=14):
        """Calculate Stochastic indicator"""
        lowest_low = low.rolling(window=period).min()
        highest_high = high.rolling(window=period).max()
        
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=3).mean()
        
        return k_percent, d_percent
    
    def create_candlestick_chart(self):
        """Create candlestick chart"""
        chart = QChart()
        chart.setTitle("XAUUSD - Candlestick Chart")
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
        
        # Axes
        axis_x = QDateTimeAxis()
        axis_x.setFormat("hh:mm")
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setRange(self.data['low'].min() - 5, self.data['high'].max() + 5)
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(chart_view.Antialiasing)
        
        return chart_view
    
    def create_ma_chart(self):
        """Create Moving Averages chart"""
        chart = QChart()
        chart.setTitle("Price with Moving Averages (MA20, MA50)")
        
        # Price series
        price_series = QLineSeries()
        price_series.setName("Price")
        
        # MA20 series
        ma20_series = QLineSeries()
        ma20_series.setName("MA20")
        
        # MA50 series
        ma50_series = QLineSeries()
        ma50_series.setName("MA50")
        
        for idx, row in self.data.iterrows():
            timestamp = int(row['date'].timestamp() * 1000)
            price_series.append(timestamp, row['close'])
            
            if pd.notna(row['MA20']):
                ma20_series.append(timestamp, row['MA20'])
            if pd.notna(row['MA50']):
                ma50_series.append(timestamp, row['MA50'])
        
        chart.addSeries(price_series)
        chart.addSeries(ma20_series)
        chart.addSeries(ma50_series)
        
        # Axes
        axis_x = QDateTimeAxis()
        axis_x.setFormat("hh:mm")
        chart.addAxis(axis_x, Qt.AlignBottom)
        price_series.attachAxis(axis_x)
        ma20_series.attachAxis(axis_x)
        ma50_series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setRange(self.data['close'].min() - 5, self.data['close'].max() + 5)
        chart.addAxis(axis_y, Qt.AlignLeft)
        price_series.attachAxis(axis_y)
        ma20_series.attachAxis(axis_y)
        ma50_series.attachAxis(axis_y)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(chart_view.Antialiasing)
        
        return chart_view
    
    def create_rsi_chart(self):
        """Create RSI oscillator chart"""
        chart = QChart()
        chart.setTitle("RSI (Relative Strength Index) - 14 Period")
        
        rsi_series = QLineSeries()
        rsi_series.setName("RSI")
        
        for idx, row in self.data.iterrows():
            if pd.notna(row['RSI']):
                timestamp = int(row['date'].timestamp() * 1000)
                rsi_series.append(timestamp, row['RSI'])
        
        chart.addSeries(rsi_series)
        
        # Axes
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
        
        return chart_view
    
    def create_macd_chart(self):
        """Create MACD chart"""
        chart = QChart()
        chart.setTitle("MACD (Moving Average Convergence Divergence)")
        
        macd_series = QLineSeries()
        macd_series.setName("MACD")
        
        signal_series = QLineSeries()
        signal_series.setName("Signal")
        
        for idx, row in self.data.iterrows():
            timestamp = int(row['date'].timestamp() * 1000)
            if pd.notna(row['MACD']):
                macd_series.append(timestamp, row['MACD'])
            if pd.notna(row['Signal']):
                signal_series.append(timestamp, row['Signal'])
        
        chart.addSeries(macd_series)
        chart.addSeries(signal_series)
        
        # Axes
        axis_x = QDateTimeAxis()
        axis_x.setFormat("hh:mm")
        chart.addAxis(axis_x, Qt.AlignBottom)
        macd_series.attachAxis(axis_x)
        signal_series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        chart.addAxis(axis_y, Qt.AlignLeft)
        macd_series.attachAxis(axis_y)
        signal_series.attachAxis(axis_y)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(chart_view.Antialiasing)
        
        return chart_view
    
    def create_stochastic_chart(self):
        """Create Stochastic oscillator chart"""
        chart = QChart()
        chart.setTitle("Stochastic Oscillator (%K, %D)")
        
        k_series = QLineSeries()
        k_series.setName("%K")
        
        d_series = QLineSeries()
        d_series.setName("%D")
        
        for idx, row in self.data.iterrows():
            timestamp = int(row['date'].timestamp() * 1000)
            if pd.notna(row['Stoch_K']):
                k_series.append(timestamp, row['Stoch_K'])
            if pd.notna(row['Stoch_D']):
                d_series.append(timestamp, row['Stoch_D'])
        
        chart.addSeries(k_series)
        chart.addSeries(d_series)
        
        # Axes
        axis_x = QDateTimeAxis()
        axis_x.setFormat("hh:mm")
        chart.addAxis(axis_x, Qt.AlignBottom)
        k_series.attachAxis(axis_x)
        d_series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setRange(0, 100)
        chart.addAxis(axis_y, Qt.AlignLeft)
        k_series.attachAxis(axis_y)
        d_series.attachAxis(axis_y)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(chart_view.Antialiasing)
        
        return chart_view
    
    def create_bollinger_chart(self):
        """Create Bollinger Bands chart"""
        chart = QChart()
        chart.setTitle("Bollinger Bands (20, 2)")
        
        price_series = QLineSeries()
        price_series.setName("Price")
        
        upper_series = QLineSeries()
        upper_series.setName("Upper Band")
        
        middle_series = QLineSeries()
        middle_series.setName("Middle Band")
        
        lower_series = QLineSeries()
        lower_series.setName("Lower Band")
        
        for idx, row in self.data.iterrows():
            timestamp = int(row['date'].timestamp() * 1000)
            price_series.append(timestamp, row['close'])
            
            if pd.notna(row['BB_Upper']):
                upper_series.append(timestamp, row['BB_Upper'])
            if pd.notna(row['BB_Middle']):
                middle_series.append(timestamp, row['BB_Middle'])
            if pd.notna(row['BB_Lower']):
                lower_series.append(timestamp, row['BB_Lower'])
        
        chart.addSeries(price_series)
        chart.addSeries(upper_series)
        chart.addSeries(middle_series)
        chart.addSeries(lower_series)
        
        # Axes
        axis_x = QDateTimeAxis()
        axis_x.setFormat("hh:mm")
        chart.addAxis(axis_x, Qt.AlignBottom)
        price_series.attachAxis(axis_x)
        upper_series.attachAxis(axis_x)
        middle_series.attachAxis(axis_x)
        lower_series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setRange(self.data['BB_Lower'].min() - 2, self.data['BB_Upper'].max() + 2)
        chart.addAxis(axis_y, Qt.AlignLeft)
        price_series.attachAxis(axis_y)
        upper_series.attachAxis(axis_y)
        middle_series.attachAxis(axis_y)
        lower_series.attachAxis(axis_y)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(chart_view.Antialiasing)
        
        return chart_view
