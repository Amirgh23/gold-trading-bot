# رابط کاربری با داده‌های واقعی از Binance
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTableWidget, 
                             QTableWidgetItem, QTextEdit, QGroupBox, QGridLayout,
                             QTabWidget, QComboBox)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QFont, QColor
from datetime import datetime
from market_data import MarketDataProvider
from strategy import FastScalpStrategy
from advanced_chart import AdvancedChart
from config import *

class BotThread(QThread):
    """ترد برای دریافت داده‌های واقعی"""
    signal_update = pyqtSignal(dict)
    signal_log = pyqtSignal(str)
    signal_trade = pyqtSignal(dict)
    
    def __init__(self, exchange='binance'):
        super().__init__()
        self.running = False
        self.market_data = MarketDataProvider(exchange)
        self.strategy = FastScalpStrategy()
        self.last_signal_time = None
    
    def run(self):
        """دریافت داده‌های واقعی"""
        self.running = True
        
        if not self.market_data.connected:
            self.signal_log.emit("❌ اتصال به صرافی برقرار نشد")
            return
        
        self.signal_log.emit("🚀 ربات با داده‌های واقعی شروع به کار کرد")
        
        while self.running:
            try:
                # دریافت قیمت فعلی
                price_data = self.market_data.get_current_price()
                
                if price_data:
                    self.signal_update.emit(price_data)
                    
                    # دریافت داده‌های OHLCV برای تحلیل
                    df = self.market_data.get_ohlcv(limit=100)
                    
                    if df is not None and len(df) > 0:
                        # محاسبه EMA برای نمودار
                        df['ema_fast'] = df['close'].ewm(span=FAST_EMA, adjust=False).mean()
                        df['ema_slow'] = df['close'].ewm(span=SLOW_EMA, adjust=False).mean()
                        
                        # ارسال داده‌ها با EMA
                        price_data['ema_fast'] = df['ema_fast'].iloc[-1]
                        price_data['ema_slow'] = df['ema_slow'].iloc[-1]
                        price_data['df'] = df  # ارسال کل دیتافریم
                        
                        # تحلیل و دریافت سیگنال
                        signal = self.strategy.analyze(df)
                        
                        if signal:
                            # جلوگیری از سیگنال‌های تکراری
                            current_time = datetime.now()
                            if (self.last_signal_time is None or 
                                (current_time - self.last_signal_time).seconds > 60):
                                
                                self.signal_trade.emit({
                                    'type': signal['signal'],
                                    'entry_price': signal['price'],
                                    'stop_loss': signal['stop_loss'],
                                    'take_profit': signal['take_profit'],
                                    'size': POSITION_SIZE,
                                    'timestamp': current_time,
                                    'source': 'TECHNICAL_LIVE'
                                })
                                
                                self.last_signal_time = current_time
                                self.signal_log.emit(
                                    f"🎯 سیگنال {signal['signal']} در قیمت ${signal['price']:.2f}"
                                )
                
                # هر 2 ثانیه به‌روزرسانی
                self.msleep(2000)
                
            except Exception as e:
                self.signal_log.emit(f"❌ خطا: {str(e)}")
                self.msleep(5000)
    
    def stop(self):
        """توقف ربات"""
        self.running = False
        self.signal_log.emit("⏹️ ربات متوقف شد")

class TradingGUI(QMainWindow):
    """رابط کاربری اصلی"""
    
    def __init__(self):
        super().__init__()
        self.bot_thread = None
        self.open_trades = []
        self.trade_history = []
        self.total_pnl = 0
        self.selected_exchange = 'binance'
        self.init_ui()
        
    def init_ui(self):
        """ساخت رابط کاربری"""
        self.setWindowTitle('ربات تریدر طلا - داده‌های واقعی (Live)')
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
            QPushButton:disabled {
                background-color: #555555;
            }
            QTableWidget {
                background-color: #2d2d2d;
                color: #ffffff;
                gridline-color: #3d3d3d;
            }
            QHeaderView::section {
                background-color: #3d3d3d;
                color: #ffffff;
                padding: 5px;
                border: 1px solid #555555;
            }
            QTextEdit {
                background-color: #2d2d2d;
                color: #00ff00;
                border: 1px solid #3d3d3d;
            }
            QTabWidget::pane {
                border: 1px solid #3d3d3d;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 10px;
                border: 1px solid #3d3d3d;
            }
            QTabBar::tab:selected {
                background-color: #0d7377;
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
        self.price_label = QLabel("قیمت: $2050.00")
        self.price_label.setFont(QFont('Arial', 16))
        layout.addWidget(self.price_label)
        
        # تغییرات
        self.change_label = QLabel("تغییر: 0.00%")
        self.change_label.setFont(QFont('Arial', 14))
        layout.addWidget(self.change_label)
        
        layout.addStretch()
        
        # انتخاب صرافی
        exchange_label = QLabel("صرافی:")
        layout.addWidget(exchange_label)
        
        self.exchange_combo = QComboBox()
        self.exchange_combo.addItems(['binance', 'bybit', 'okx', 'kucoin'])
        self.exchange_combo.currentTextChanged.connect(self.on_exchange_changed)
        layout.addWidget(self.exchange_combo)
        
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
        self.total_trades_label.setFont(QFont('Arial', 12))
        self.open_positions_label = QLabel("پوزیشن‌های باز: 0")
        self.open_positions_label.setFont(QFont('Arial', 12))
        self.daily_pnl_label = QLabel("P&L روزانه: $0.00")
        self.daily_pnl_label.setFont(QFont('Arial', 12))
        
        stats_layout.addWidget(self.total_trades_label, 0, 0)
        stats_layout.addWidget(self.open_positions_label, 0, 1)
        stats_layout.addWidget(self.daily_pnl_label, 1, 0)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group, 0, 0)
        
        # وضعیت ربات
        status_group = QGroupBox("🤖 وضعیت ربات")
        status_layout = QVBoxLayout()
        
        self.bot_status_label = QLabel("وضعیت: متوقف ⏹️")
        self.bot_status_label.setFont(QFont('Arial', 12))
        self.strategy_label = QLabel(f"استراتژی: فست اسکلپ (EMA {FAST_EMA}/{SLOW_EMA} + RSI)")
        self.strategy_label.setFont(QFont('Arial', 10))
        self.timeframe_label = QLabel(f"تایم فریم: {TIMEFRAME}")
        self.timeframe_label.setFont(QFont('Arial', 10))
        self.symbol_label = QLabel(f"نماد: {SYMBOL}")
        self.symbol_label.setFont(QFont('Arial', 10))
        
        status_layout.addWidget(self.bot_status_label)
        status_layout.addWidget(self.strategy_label)
        status_layout.addWidget(self.timeframe_label)
        status_layout.addWidget(self.symbol_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group, 0, 1)
        
        # نمودار قیمت پیشرفته
        chart_group = QGroupBox("📊 نمودار قیمت زنده با اندیکاتورها")
        chart_layout = QVBoxLayout()
        
        self.price_chart = AdvancedChart()
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
        self.open_trades_table.horizontalHeader().setStretchLastSection(True)
        open_layout.addWidget(self.open_trades_table)
        
        open_trades_group.setLayout(open_layout)
        layout.addWidget(open_trades_group)
        
        # جدول تاریخچه معاملات
        history_group = QGroupBox("📜 تاریخچه معاملات")
        history_layout = QVBoxLayout()
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            'نوع', 'قیمت ورود', 'زمان ورود', 'منبع', 'وضعیت', 'سود/زیان'
        ])
        self.history_table.horizontalHeader().setStretchLastSection(True)
        history_layout.addWidget(self.history_table)
        
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
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
    
    def on_exchange_changed(self, exchange):
        """تغییر صرافی"""
        self.selected_exchange = exchange
        self.add_log(f"📊 صرافی انتخاب شده: {exchange}")
    
    def start_bot(self):
        """شروع ربات"""
        if self.bot_thread is None or not self.bot_thread.isRunning():
            self.add_log(f"🔗 اتصال به {self.selected_exchange}...")
            self.bot_thread = BotThread(self.selected_exchange)
            self.bot_thread.signal_update.connect(self.update_data)
            self.bot_thread.signal_log.connect(self.add_log)
            self.bot_thread.signal_trade.connect(self.add_trade)
            self.bot_thread.start()
            
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.exchange_combo.setEnabled(False)
            self.bot_status_label.setText("وضعیت: در حال اجرا ✅ (Live Data)")
            self.add_log("🚀 ربات با داده‌های واقعی شروع شد")
    
    def stop_bot(self):
        """توقف ربات"""
        if self.bot_thread and self.bot_thread.isRunning():
            self.bot_thread.stop()
            self.bot_thread.wait()
            
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.exchange_combo.setEnabled(True)
            self.bot_status_label.setText("وضعیت: متوقف ⏹️")
            self.add_log("⏹️ ربات متوقف شد")
    
    def update_data(self, data):
        """به‌روزرسانی داده‌ها"""
        price = data['price']
        change = data.get('change', 0)
        high = data.get('high', price)
        low = data.get('low', price)
        volume = data.get('volume', 0)
        
        self.price_label.setText(f"قیمت: ${price:.2f}")
        
        if change >= 0:
            self.change_label.setText(f"تغییر: +{change:.2f}%")
            self.change_label.setStyleSheet("color: #00ff00; font-size: 14pt;")
        else:
            self.change_label.setText(f"تغییر: {change:.2f}%")
            self.change_label.setStyleSheet("color: #ff0000; font-size: 14pt;")
        
        # به‌روزرسانی نمودار پیشرفته
        ema_fast = data.get('ema_fast')
        ema_slow = data.get('ema_slow')
        self.price_chart.add_data_point(price, ema_fast, ema_slow)
        self.price_chart.update_info(price, high, low, volume)
    
    def add_log(self, message):
        """اضافه کردن لاگ"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def add_trade(self, trade):
        """اضافه کردن معامله"""
        self.open_trades.append(trade)
        
        row = self.open_trades_table.rowCount()
        self.open_trades_table.insertRow(row)
        
        # رنگ‌بندی بر اساس نوع معامله
        color = QColor("#00ff00") if trade['type'] == 'BUY' else QColor("#ff0000")
        
        items = [
            QTableWidgetItem(trade['type']),
            QTableWidgetItem(f"${trade['entry_price']:.2f}"),
            QTableWidgetItem(f"${trade['stop_loss']:.2f}"),
            QTableWidgetItem(f"${trade['take_profit']:.2f}"),
            QTableWidgetItem(str(trade['size'])),
            QTableWidgetItem(trade['timestamp'].strftime("%H:%M:%S")),
            QTableWidgetItem(trade.get('source', 'N/A'))
        ]
        
        for col, item in enumerate(items):
            if col == 0:  # ستون نوع
                item.setForeground(color)
            self.open_trades_table.setItem(row, col, item)
        
        # اضافه به تاریخچه
        self.add_to_history(trade)
    
    def add_to_history(self, trade):
        """اضافه کردن به تاریخچه"""
        row = self.history_table.rowCount()
        self.history_table.insertRow(row)
        
        items = [
            QTableWidgetItem(trade['type']),
            QTableWidgetItem(f"${trade['entry_price']:.2f}"),
            QTableWidgetItem(trade['timestamp'].strftime("%H:%M:%S")),
            QTableWidgetItem(trade.get('source', 'N/A')),
            QTableWidgetItem('باز'),
            QTableWidgetItem('--')
        ]
        
        for col, item in enumerate(items):
            self.history_table.setItem(row, col, item)
    
    def update_ui(self):
        """به‌روزرسانی دوره‌ای UI"""
        self.open_positions_label.setText(f"پوزیشن‌های باز: {len(self.open_trades)}")
        self.total_trades_label.setText(f"کل معاملات: {len(self.open_trades)}")
        self.daily_pnl_label.setText(f"P&L روزانه: ${self.total_pnl:.2f}")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = TradingGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
