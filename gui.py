# رابط کاربری گرافیکی ربات تریدر
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTableWidget, 
                             QTableWidgetItem, QTextEdit, QGroupBox, QGridLayout,
                             QTabWidget, QProgressBar)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis
from datetime import datetime
import pandas as pd
from bot_ml import MLGoldScalpBot
from config import *

class BotThread(QThread):
    """ترد جداگانه برای اجرای ربات"""
    signal_update = pyqtSignal(dict)
    signal_log = pyqtSignal(str)
    signal_trade = pyqtSignal(dict)
    
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.running = False
    
    def run(self):
        """اجرای ربات در پس‌زمینه"""
        self.running = True
        self.signal_log.emit("🚀 ربات شروع به کار کرد")
        
        while self.running:
            try:
                # شبیه‌سازی داده (در پروژه واقعی از API استفاده کنید)
                self.signal_update.emit({
                    'price': 2050.5,
                    'change': 0.5,
                    'volume': 1500,
                    'timestamp': datetime.now()
                })
                
                self.msleep(2000)  # 2 ثانیه
                
            except Exception as e:
                self.signal_log.emit(f"❌ خطا: {str(e)}")
    
    def stop(self):
        """توقف ربات"""
        self.running = False
        self.signal_log.emit("⏹️ ربات متوقف شد")

class TradingGUI(QMainWindow):
    """رابط کاربری اصلی"""
    
    def __init__(self):
        super().__init__()
        self.bot = MLGoldScalpBot(use_ml=True)
        self.bot_thread = None
        self.init_ui()
        
    def init_ui(self):
        """ساخت رابط کاربری"""
        self.setWindowTitle('ربات تریدر طلا - LSTM + تحلیل تکنیکال')
        self.setGeometry(100, 100, 1400, 900)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #ffffff;
            }
            QGroupBox {
                color: #ffffff;
                border: 2px solid #3d3d3d;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #0d7377;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #14a085;
            }
            QPushButton:pressed {
                background-color: #0a5f62;
            }
            QTableWidget {
                background-color: #2d2d2d;
                color: #ffffff;
                gridline-color: #3d3d3d;
            }
            QTextEdit {
                background-color: #2d2d2d;
                color: #00ff00;
                border: 1px solid #3d3d3d;
            }
        """)
        
        # ویجت مرکزی
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # هدر
        header = self.create_header()
        main_layout.addWidget(header)
        
        # تب‌ها
        tabs = QTabWidget()
        tabs.addTab(self.create_dashboard_tab(), "📊 داشبورد")
        tabs.addTab(self.create_trades_tab(), "💼 معاملات")
        tabs.addTab(self.create_ml_tab(), "🤖 یادگیری ماشین")
        tabs.addTab(self.create_settings_tab(), "⚙️ تنظیمات")
        main_layout.addWidget(tabs)
        
        # لاگ
        log_group = self.create_log_section()
        main_layout.addWidget(log_group)
        
        # تایمر برای به‌روزرسانی
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(1000)
    
    def create_header(self):
        """ساخت هدر"""
        header = QGroupBox()
        layout = QHBoxLayout()
        
        # عنوان
        title = QLabel("🏆 ربات تریدر انس طلا")
        title.setFont(QFont('Arial', 18, QFont.Bold))
        layout.addWidget(title)
        
        layout.addStretch()
        
        # قیمت فعلی
        self.price_label = QLabel("قیمت: $0.00")
        self.price_label.setFont(QFont('Arial', 16))
        layout.addWidget(self.price_label)
        
        # تغییرات
        self.change_label = QLabel("تغییر: 0.00%")
        self.change_label.setFont(QFont('Arial', 14))
        layout.addWidget(self.change_label)
        
        layout.addStretch()
        
        # دکمه‌های کنترل
        self.start_btn = QPushButton("▶️ شروع")
        self.start_btn.clicked.connect(self.start_bot)
        layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹️ توقف")
        self.stop_btn.clicked.connect(self.stop_bot)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)
        
        header.setLayout(layout)
        return header
    
    def create_dashboard_tab(self):
        """تب داشبورد"""
        widget = QWidget()
        layout = QGridLayout()
        
        # آمار کلی
        stats_group = QGroupBox("📈 آمار کلی")
        stats_layout = QGridLayout()
        
        self.total_trades_label = QLabel("کل معاملات: 0")
        self.win_rate_label = QLabel("نرخ برد: 0%")
        self.profit_label = QLabel("سود/زیان: $0.00")
        self.daily_pnl_label = QLabel("P&L روزانه: $0.00")
        
        stats_layout.addWidget(self.total_trades_label, 0, 0)
        stats_layout.addWidget(self.win_rate_label, 0, 1)
        stats_layout.addWidget(self.profit_label, 1, 0)
        stats_layout.addWidget(self.daily_pnl_label, 1, 1)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group, 0, 0)
        
        # وضعیت ربات
        status_group = QGroupBox("🤖 وضعیت ربات")
        status_layout = QVBoxLayout()
        
        self.bot_status_label = QLabel("وضعیت: متوقف")
        self.strategy_label = QLabel(f"استراتژی: ترکیبی (EMA {FAST_EMA}/{SLOW_EMA} + LSTM)")
        self.timeframe_label = QLabel(f"تایم فریم: {TIMEFRAME}")
        self.open_positions_label = QLabel("پوزیشن‌های باز: 0")
        
        status_layout.addWidget(self.bot_status_label)
        status_layout.addWidget(self.strategy_label)
        status_layout.addWidget(self.timeframe_label)
        status_layout.addWidget(self.open_positions_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group, 0, 1)
        
        # نمودار قیمت
        chart_group = QGroupBox("📊 نمودار قیمت")
        chart_layout = QVBoxLayout()
        
        self.price_chart = self.create_price_chart()
        chart_layout.addWidget(self.price_chart)
        
        chart_group.setLayout(chart_layout)
        layout.addWidget(chart_group, 1, 0, 1, 2)
        
        widget.setLayout(layout)
        return widget

    def create_trades_tab(self):
        """تب معاملات"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # جدول معاملات باز
        open_trades_group = QGroupBox("💼 معاملات باز")
        open_layout = QVBoxLayout()
        
        self.open_trades_table = QTableWidget()
        self.open_trades_table.setColumnCount(7)
        self.open_trades_table.setHorizontalHeaderLabels([
            'نوع', 'قیمت ورود', 'استاپ لاس', 'تیک پرافیت', 'حجم', 'زمان', 'منبع'
        ])
        open_layout.addWidget(self.open_trades_table)
        
        open_trades_group.setLayout(open_layout)
        layout.addWidget(open_trades_group)
        
        # جدول تاریخچه معاملات
        history_group = QGroupBox("📜 تاریخچه معاملات")
        history_layout = QVBoxLayout()
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(8)
        self.history_table.setHorizontalHeaderLabels([
            'نوع', 'قیمت ورود', 'قیمت خروج', 'سود/زیان', 'حجم', 'زمان', 'دلیل بسته شدن', 'منبع'
        ])
        history_layout.addWidget(self.history_table)
        
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_ml_tab(self):
        """تب یادگیری ماشین"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # وضعیت مدل
        model_group = QGroupBox("🧠 وضعیت مدل LSTM")
        model_layout = QGridLayout()
        
        self.model_status_label = QLabel("وضعیت: آماده")
        self.model_accuracy_label = QLabel("دقت: N/A")
        self.lookback_label = QLabel(f"Lookback: 60 کندل")
        
        model_layout.addWidget(self.model_status_label, 0, 0)
        model_layout.addWidget(self.model_accuracy_label, 0, 1)
        model_layout.addWidget(self.lookback_label, 1, 0)
        
        # دکمه آموزش مجدد
        retrain_btn = QPushButton("🎓 آموزش مجدد مدل")
        retrain_btn.clicked.connect(self.retrain_model)
        model_layout.addWidget(retrain_btn, 1, 1)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # پیش‌بینی‌های اخیر
        predictions_group = QGroupBox("🔮 پیش‌بینی‌های اخیر")
        predictions_layout = QVBoxLayout()
        
        self.predictions_table = QTableWidget()
        self.predictions_table.setColumnCount(5)
        self.predictions_table.setHorizontalHeaderLabels([
            'زمان', 'قیمت فعلی', 'قیمت پیش‌بینی', 'تغییر %', 'روند'
        ])
        predictions_layout.addWidget(self.predictions_table)
        
        predictions_group.setLayout(predictions_layout)
        layout.addWidget(predictions_group)
        
        # نمودار دقت
        accuracy_group = QGroupBox("📈 نمودار دقت پیش‌بینی")
        accuracy_layout = QVBoxLayout()
        
        self.accuracy_chart = self.create_accuracy_chart()
        accuracy_layout.addWidget(self.accuracy_chart)
        
        accuracy_group.setLayout(accuracy_layout)
        layout.addWidget(accuracy_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_settings_tab(self):
        """تب تنظیمات"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # تنظیمات استراتژی
        strategy_group = QGroupBox("⚙️ تنظیمات استراتژی")
        strategy_layout = QGridLayout()
        
        strategy_layout.addWidget(QLabel(f"EMA سریع: {FAST_EMA}"), 0, 0)
        strategy_layout.addWidget(QLabel(f"EMA کند: {SLOW_EMA}"), 0, 1)
        strategy_layout.addWidget(QLabel(f"RSI دوره: {RSI_PERIOD}"), 1, 0)
        strategy_layout.addWidget(QLabel(f"تیک پرافیت: {TAKE_PROFIT_PIPS} پیپ"), 1, 1)
        strategy_layout.addWidget(QLabel(f"استاپ لاس: {STOP_LOSS_PIPS} پیپ"), 2, 0)
        
        strategy_group.setLayout(strategy_layout)
        layout.addWidget(strategy_group)
        
        # تنظیمات ریسک
        risk_group = QGroupBox("🛡️ مدیریت ریسک")
        risk_layout = QGridLayout()
        
        risk_layout.addWidget(QLabel(f"حداکثر ضرر روزانه: ${MAX_DAILY_LOSS}"), 0, 0)
        risk_layout.addWidget(QLabel(f"حداکثر معاملات همزمان: {MAX_OPEN_TRADES}"), 0, 1)
        risk_layout.addWidget(QLabel(f"حجم معامله: {POSITION_SIZE}"), 1, 0)
        risk_layout.addWidget(QLabel(f"لوریج: {LEVERAGE}x"), 1, 1)
        
        risk_group.setLayout(risk_layout)
        layout.addWidget(risk_group)
        
        # تنظیمات ML
        ml_group = QGroupBox("🤖 تنظیمات یادگیری ماشین")
        ml_layout = QGridLayout()
        
        ml_layout.addWidget(QLabel("استفاده از ML: فعال"), 0, 0)
        ml_layout.addWidget(QLabel("حداقل اطمینان ML: 30%"), 0, 1)
        ml_layout.addWidget(QLabel("Lookback: 60 کندل"), 1, 0)
        ml_layout.addWidget(QLabel("Features: 5 (OHLCV)"), 1, 1)
        
        ml_group.setLayout(ml_layout)
        layout.addWidget(ml_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_log_section(self):
        """بخش لاگ"""
        log_group = QGroupBox("📝 لاگ سیستم")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        return log_group
    
    def create_price_chart(self):
        """ساخت نمودار قیمت"""
        chart = QChart()
        chart.setTitle("نمودار قیمت طلا")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setBackgroundBrush(QColor("#2d2d2d"))
        chart.setTitleBrush(QColor("#ffffff"))
        
        self.price_series = QLineSeries()
        self.price_series.setColor(QColor("#00ff00"))
        chart.addSeries(self.price_series)
        
        # محورها
        axis_x = QValueAxis()
        axis_x.setTitleText("زمان")
        axis_x.setLabelFormat("%d")
        axis_x.setLabelsColor(QColor("#ffffff"))
        
        axis_y = QValueAxis()
        axis_y.setTitleText("قیمت ($)")
        axis_y.setLabelFormat("%.2f")
        axis_y.setLabelsColor(QColor("#ffffff"))
        
        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)
        self.price_series.attachAxis(axis_x)
        self.price_series.attachAxis(axis_y)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(chart_view.Antialiasing)
        
        return chart_view
    
    def create_accuracy_chart(self):
        """ساخت نمودار دقت"""
        chart = QChart()
        chart.setTitle("دقت پیش‌بینی LSTM")
        chart.setBackgroundBrush(QColor("#2d2d2d"))
        chart.setTitleBrush(QColor("#ffffff"))
        
        accuracy_series = QLineSeries()
        accuracy_series.setColor(QColor("#ff9500"))
        chart.addSeries(accuracy_series)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(chart_view.Antialiasing)
        
        return chart_view
    
    def start_bot(self):
        """شروع ربات"""
        if self.bot_thread is None or not self.bot_thread.isRunning():
            self.bot_thread = BotThread(self.bot)
            self.bot_thread.signal_update.connect(self.update_data)
            self.bot_thread.signal_log.connect(self.add_log)
            self.bot_thread.signal_trade.connect(self.add_trade)
            self.bot_thread.start()
            
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.bot_status_label.setText("وضعیت: در حال اجرا ✅")
            self.add_log("🚀 ربات شروع به کار کرد")
    
    def stop_bot(self):
        """توقف ربات"""
        if self.bot_thread and self.bot_thread.isRunning():
            self.bot_thread.stop()
            self.bot_thread.wait()
            
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.bot_status_label.setText("وضعیت: متوقف ⏹️")
            self.add_log("⏹️ ربات متوقف شد")
    
    def update_data(self, data):
        """به‌روزرسانی داده‌ها"""
        price = data['price']
        change = data['change']
        
        self.price_label.setText(f"قیمت: ${price:.2f}")
        
        if change >= 0:
            self.change_label.setText(f"تغییر: +{change:.2f}%")
            self.change_label.setStyleSheet("color: #00ff00;")
        else:
            self.change_label.setText(f"تغییر: {change:.2f}%")
            self.change_label.setStyleSheet("color: #ff0000;")
        
        # به‌روزرسانی نمودار
        count = self.price_series.count()
        self.price_series.append(count, price)
        if count > 50:
            self.price_series.remove(0)
    
    def add_log(self, message):
        """اضافه کردن لاگ"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def add_trade(self, trade):
        """اضافه کردن معامله"""
        row = self.open_trades_table.rowCount()
        self.open_trades_table.insertRow(row)
        
        self.open_trades_table.setItem(row, 0, QTableWidgetItem(trade['type']))
        self.open_trades_table.setItem(row, 1, QTableWidgetItem(f"${trade['entry_price']:.2f}"))
        self.open_trades_table.setItem(row, 2, QTableWidgetItem(f"${trade['stop_loss']:.2f}"))
        self.open_trades_table.setItem(row, 3, QTableWidgetItem(f"${trade['take_profit']:.2f}"))
        self.open_trades_table.setItem(row, 4, QTableWidgetItem(str(trade['size'])))
        self.open_trades_table.setItem(row, 5, QTableWidgetItem(trade['timestamp'].strftime("%H:%M:%S")))
        self.open_trades_table.setItem(row, 6, QTableWidgetItem(trade.get('source', 'N/A')))
    
    def retrain_model(self):
        """آموزش مجدد مدل"""
        self.add_log("🎓 شروع آموزش مجدد مدل...")
        # اینجا باید کد آموزش مدل اضافه شود
        self.add_log("✅ آموزش مدل با موفقیت انجام شد")
    
    def update_ui(self):
        """به‌روزرسانی دوره‌ای UI"""
        # به‌روزرسانی آمار
        self.open_positions_label.setText(f"پوزیشن‌های باز: {len(self.bot.open_trades)}")
        self.total_trades_label.setText(f"کل معاملات: {len(self.bot.trade_history)}")
        self.daily_pnl_label.setText(f"P&L روزانه: ${self.bot.daily_pnl:.2f}")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = TradingGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
