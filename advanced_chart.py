# نمودار پیشرفته با کندل استیک و اندیکاتورها
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis, QCandlestickSeries, QCandlestickSet
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter, QPen
import pandas as pd

class AdvancedChart(QWidget):
    """نمودار پیشرفته با کندل استیک"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.data_points = []
        
    def init_ui(self):
        """ساخت رابط کاربری نمودار"""
        layout = QVBoxLayout()
        
        # نمودار اصلی
        self.chart = QChart()
        self.chart.setTitle("نمودار قیمت طلا (XAU/USDT)")
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setBackgroundBrush(QColor("#1e1e1e"))
        self.chart.setTitleBrush(QColor("#ffffff"))
        
        # سری قیمت
        self.price_series = QLineSeries()
        self.price_series.setColor(QColor("#00ff00"))
        self.price_series.setName("قیمت")
        
        # سری EMA سریع
        self.ema_fast_series = QLineSeries()
        self.ema_fast_series.setColor(QColor("#ff9500"))
        self.ema_fast_series.setName("EMA 5")
        
        # سری EMA کند
        self.ema_slow_series = QLineSeries()
        self.ema_slow_series.setColor(QColor("#ff0000"))
        self.ema_slow_series.setName("EMA 13")
        
        self.chart.addSeries(self.price_series)
        self.chart.addSeries(self.ema_fast_series)
        self.chart.addSeries(self.ema_slow_series)
        
        # محورها
        self.axis_x = QValueAxis()
        self.axis_x.setTitleText("زمان")
        self.axis_x.setLabelFormat("%d")
        self.axis_x.setLabelsColor(QColor("#ffffff"))
        self.axis_x.setTitleBrush(QColor("#ffffff"))
        self.axis_x.setGridLineColor(QColor("#3d3d3d"))
        
        self.axis_y = QValueAxis()
        self.axis_y.setTitleText("قیمت ($)")
        self.axis_y.setLabelFormat("%.2f")
        self.axis_y.setLabelsColor(QColor("#ffffff"))
        self.axis_y.setTitleBrush(QColor("#ffffff"))
        self.axis_y.setGridLineColor(QColor("#3d3d3d"))
        
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        
        self.price_series.attachAxis(self.axis_x)
        self.price_series.attachAxis(self.axis_y)
        self.ema_fast_series.attachAxis(self.axis_x)
        self.ema_fast_series.attachAxis(self.axis_y)
        self.ema_slow_series.attachAxis(self.axis_x)
        self.ema_slow_series.attachAxis(self.axis_y)
        
        # نمایش نمودار
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(self.chart_view)
        
        # اطلاعات زیر نمودار
        info_layout = QHBoxLayout()
        
        self.current_price_label = QLabel("قیمت فعلی: --")
        self.current_price_label.setStyleSheet("color: #00ff00; font-size: 14pt; font-weight: bold;")
        info_layout.addWidget(self.current_price_label)
        
        self.high_label = QLabel("بالاترین: --")
        self.high_label.setStyleSheet("color: #ffffff; font-size: 12pt;")
        info_layout.addWidget(self.high_label)
        
        self.low_label = QLabel("پایین‌ترین: --")
        self.low_label.setStyleSheet("color: #ffffff; font-size: 12pt;")
        info_layout.addWidget(self.low_label)
        
        self.volume_label = QLabel("حجم: --")
        self.volume_label.setStyleSheet("color: #ffffff; font-size: 12pt;")
        info_layout.addWidget(self.volume_label)
        
        info_layout.addStretch()
        layout.addLayout(info_layout)
        
        self.setLayout(layout)
    
    def add_data_point(self, price, ema_fast=None, ema_slow=None):
        """اضافه کردن نقطه جدید به نمودار"""
        x = len(self.data_points)
        self.data_points.append(price)
        
        # اضافه کردن به سری قیمت
        self.price_series.append(x, price)
        
        # اضافه کردن EMA ها
        if ema_fast is not None:
            self.ema_fast_series.append(x, ema_fast)
        if ema_slow is not None:
            self.ema_slow_series.append(x, ema_slow)
        
        # محدود کردن تعداد نقاط
        max_points = 100
        if len(self.data_points) > max_points:
            self.price_series.remove(0)
            if self.ema_fast_series.count() > 0:
                self.ema_fast_series.remove(0)
            if self.ema_slow_series.count() > 0:
                self.ema_slow_series.remove(0)
            self.data_points.pop(0)
        
        # به‌روزرسانی محدوده محورها
        if len(self.data_points) > 0:
            min_price = min(self.data_points)
            max_price = max(self.data_points)
            margin = (max_price - min_price) * 0.1
            
            self.axis_y.setRange(min_price - margin, max_price + margin)
            self.axis_x.setRange(0, len(self.data_points))
    
    def update_info(self, price, high, low, volume):
        """به‌روزرسانی اطلاعات"""
        self.current_price_label.setText(f"قیمت فعلی: ${price:.2f}")
        self.high_label.setText(f"بالاترین: ${high:.2f}")
        self.low_label.setText(f"پایین‌ترین: ${low:.2f}")
        self.volume_label.setText(f"حجم: {volume:.2f}")
    
    def clear(self):
        """پاک کردن نمودار"""
        self.price_series.clear()
        self.ema_fast_series.clear()
        self.ema_slow_series.clear()
        self.data_points.clear()
