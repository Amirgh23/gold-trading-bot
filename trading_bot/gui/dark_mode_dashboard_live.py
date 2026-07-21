"""Pulse Matrix desktop dashboard in a violet/cyan visual system."""

from datetime import datetime, timezone

import numpy as np
import pandas as pd
from PyQt5.QtChart import (
    QChart,
    QChartView,
    QCandlestickSeries,
    QCandlestickSet,
    QDateTimeAxis,
    QLineSeries,
    QValueAxis,
)
from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from trading_bot.gui.cyberpunk_theme import COLORS, mono_font, ui_font


class DarkModeDashboardLive(QWidget):
    """Professional paper-trading dashboard with clearly labelled demo data."""

    def __init__(self):
        super().__init__()
        self.setObjectName("DashboardRoot")
        self.data = self.generate_sample_data()
        self.feed_running = True
        self._rng = np.random.default_rng(20260722)

        self._build_ui()
        self._refresh_all()

        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start(1000)

        self.market_timer = QTimer(self)
        self.market_timer.timeout.connect(self._tick_demo_feed)
        self.market_timer.start(2200)

    # ---------- composition ----------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 14, 18, 14)
        root.setSpacing(12)

        root.addLayout(self._build_header())

        content = QHBoxLayout()
        content.setSpacing(12)

        center = QVBoxLayout()
        center.setSpacing(10)
        center.addLayout(self._build_metrics())
        center.addWidget(self._build_chart(), 1)
        center.addWidget(self._build_decision_log())
        content.addLayout(center, 5)
        content.addWidget(self._build_risk_console(), 2)

        root.addLayout(content, 1)

    def _build_header(self):
        layout = QHBoxLayout()
        layout.setSpacing(16)

        pair_stack = QVBoxLayout()
        pair_stack.setSpacing(0)
        pair_caption = QLabel("INSTRUMENT")
        pair_caption.setObjectName("Eyebrow")
        pair_stack.addWidget(pair_caption)
        pair = QLabel("PAXG / USDT")
        pair.setObjectName("Gold")
        pair.setFont(ui_font(16, 700))
        pair_stack.addWidget(pair)
        layout.addLayout(pair_stack)
        layout.addStretch()

        self.mode_badge = QLabel("  PAPER MODE  ")
        self.mode_badge.setObjectName("Cyan")
        self.mode_badge.setFont(mono_font(10, 700))
        self.mode_badge.setStyleSheet(
            f"color:{COLORS['cyan']}; background:{COLORS['cyan_soft']};"
            f"border:1px solid {COLORS['cyan']}; border-radius:4px; padding:7px 11px;"
        )
        layout.addWidget(self.mode_badge)

        self.feed_badge = QLabel("DEMO FEED  /  CONNECTED")
        self.feed_badge.setObjectName("Positive")
        self.feed_badge.setFont(mono_font(9, 600))
        layout.addWidget(self.feed_badge)

        self.clock_label = QLabel()
        self.clock_label.setObjectName("Muted")
        self.clock_label.setFont(mono_font(9))
        layout.addWidget(self.clock_label)
        self._update_clock()
        return layout

    def _build_metrics(self):
        layout = QHBoxLayout()
        layout.setSpacing(8)
        self.price_value = self._metric(layout, "LAST PRICE", "—", "Gold")
        self.change_value = self._metric(layout, "SESSION", "—", "Positive")
        self.signal_value = self._metric(layout, "STRATEGY SIGNAL", "WAIT", "Violet")
        self.confidence_value = self._metric(layout, "SIGNAL SCORE", "—", "Cyan")
        self.volatility_value = self._metric(layout, "VOLATILITY", "—", "Muted")
        return layout

    def _metric(self, parent, title, value, value_object):
        panel = QFrame()
        panel.setObjectName("Metric")
        panel.setMinimumHeight(72)
        box = QVBoxLayout(panel)
        box.setContentsMargins(12, 9, 12, 9)
        box.setSpacing(3)
        caption = QLabel(title)
        caption.setObjectName("Muted")
        caption.setFont(ui_font(8, 650))
        result = QLabel(value)
        result.setObjectName(value_object)
        result.setFont(mono_font(13, 700))
        box.addWidget(caption)
        box.addWidget(result)
        parent.addWidget(panel, 1)
        return result

    def _build_chart(self):
        container = QFrame()
        container.setObjectName("Panel")
        box = QVBoxLayout(container)
        box.setContentsMargins(12, 10, 12, 8)
        box.setSpacing(6)

        toolbar = QHBoxLayout()
        title = QLabel("MARKET STRUCTURE")
        title.setObjectName("Eyebrow")
        toolbar.addWidget(title)
        toolbar.addStretch()
        for label in ("5m", "15m", "1H", "4H"):
            button = QPushButton(label)
            button.setCheckable(True)
            button.setFixedSize(54, 28)
            button.clicked.connect(lambda checked, value=label: self._select_timeframe(value))
            button.setProperty("timeframe", label)
            if label == "5m":
                button.setChecked(True)
                button.setStyleSheet(
                    f"color:{COLORS['cyan']}; border-color:{COLORS['cyan']};"
                    f"background:{COLORS['cyan_soft']};"
                )
            toolbar.addWidget(button)
        box.addLayout(toolbar)

        self.chart = QChart()
        self.chart.setBackgroundVisible(False)
        self.chart.setPlotAreaBackgroundVisible(True)
        self.chart.setPlotAreaBackgroundBrush(QBrush(QColor(COLORS["void"])))
        self.chart.setMargins(type(self.chart.margins())(4, 4, 4, 4))
        self.chart.legend().setVisible(True)
        self.chart.legend().setLabelColor(QColor(COLORS["muted"]))
        self.chart.legend().setFont(mono_font(8))
        self.chart.legend().setAlignment(Qt.AlignTop)

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setMinimumHeight(380)
        self.chart_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.chart_view.setStyleSheet("background: transparent; border: 0;")
        box.addWidget(self.chart_view, 1)
        return container

    def _build_decision_log(self):
        panel = QFrame()
        panel.setObjectName("Panel")
        box = QVBoxLayout(panel)
        box.setContentsMargins(12, 9, 12, 10)
        box.setSpacing(6)

        heading = QHBoxLayout()
        title = QLabel("DECISION LOG")
        title.setObjectName("Eyebrow")
        heading.addWidget(title)
        heading.addStretch()
        label = QLabel("STRATEGY EVENTS  /  PAPER ONLY")
        label.setObjectName("Muted")
        label.setFont(mono_font(8))
        heading.addWidget(label)
        box.addLayout(heading)

        self.log_table = QTableWidget(5, 4)
        self.log_table.setHorizontalHeaderLabels(["TIME (UTC)", "ACTION", "CONTEXT", "OUTCOME"])
        self.log_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.log_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.log_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.log_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.log_table.verticalHeader().setVisible(False)
        self.log_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.log_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.log_table.setAlternatingRowColors(True)
        self.log_table.setMaximumHeight(188)

        entries = [
            ("15:20:14", "WAIT", "EMA band compressed; no clean edge", "NO TRADE"),
            ("15:12:03", "SKIP LONG", "RSI below trigger; momentum neutral", "FILTERED"),
            ("15:05:47", "WAIT", "Spread widened above paper threshold", "NO TRADE"),
            ("14:58:32", "RISK CHECK", "Exposure remains below configured cap", "PASSED"),
            ("14:47:18", "SESSION", "Demo market feed initialized", "READY"),
        ]
        for row, values in enumerate(entries):
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setFont(mono_font(8))
                if col == 1:
                    item.setForeground(QColor(COLORS["violet"]))
                elif col == 3:
                    item.setForeground(QColor(COLORS["cyan"]))
                self.log_table.setItem(row, col, item)
        box.addWidget(self.log_table)
        return panel

    def _build_risk_console(self):
        panel = QFrame()
        panel.setObjectName("PanelAccent")
        panel.setMinimumWidth(285)
        panel.setMaximumWidth(380)
        box = QVBoxLayout(panel)
        box.setContentsMargins(16, 14, 16, 14)
        box.setSpacing(12)

        title = QLabel("RISK CONSOLE")
        title.setObjectName("Eyebrow")
        box.addWidget(title)

        signal_panel = QFrame()
        signal_panel.setObjectName("SignalPanel")
        signal_box = QVBoxLayout(signal_panel)
        signal_box.setContentsMargins(14, 12, 14, 12)
        caption = QLabel("CURRENT STRATEGY STATE")
        caption.setObjectName("Muted")
        caption.setFont(ui_font(8, 650))
        self.risk_signal = QLabel("WAIT")
        self.risk_signal.setObjectName("Violet")
        self.risk_signal.setFont(mono_font(26, 700))
        self.signal_reason = QLabel("Waiting for a confirmed crossover")
        self.signal_reason.setWordWrap(True)
        self.signal_reason.setObjectName("Muted")
        signal_box.addWidget(caption)
        signal_box.addWidget(self.risk_signal)
        signal_box.addWidget(self.signal_reason)
        box.addWidget(signal_panel)

        box.addWidget(self._separator())
        self.equity_value = self._risk_row(box, "PAPER EQUITY", "10,000.00 USDT", "Cyan")
        self.daily_value = self._risk_row(box, "DAILY P&L", "+0.00 USDT", "Positive")
        self.drawdown_value = self._risk_row(box, "DRAWDOWN", "0.00%", "Muted")
        self.exposure_value = self._risk_row(box, "OPEN EXPOSURE", "0.00 USDT", "Muted")

        load_header = QHBoxLayout()
        load_title = QLabel("RISK LOAD")
        load_title.setObjectName("Muted")
        self.risk_load_text = QLabel("12%")
        self.risk_load_text.setObjectName("Violet")
        self.risk_load_text.setFont(mono_font(10, 700))
        load_header.addWidget(load_title)
        load_header.addStretch()
        load_header.addWidget(self.risk_load_text)
        box.addLayout(load_header)
        self.risk_bar = QProgressBar()
        self.risk_bar.setRange(0, 100)
        self.risk_bar.setValue(12)
        box.addWidget(self.risk_bar)

        breaker = QFrame()
        breaker.setObjectName("CircuitBreaker")
        breaker_box = QHBoxLayout(breaker)
        breaker_box.setContentsMargins(10, 8, 10, 8)
        breaker_title = QLabel("CIRCUIT BREAKER")
        breaker_title.setObjectName("Muted")
        self.breaker_state = QLabel("ARMED / SAFE")
        self.breaker_state.setObjectName("Positive")
        self.breaker_state.setFont(mono_font(9, 700))
        breaker_box.addWidget(breaker_title)
        breaker_box.addStretch()
        breaker_box.addWidget(self.breaker_state)
        box.addWidget(breaker)

        guardrail_title = QLabel("GUARDRAILS")
        guardrail_title.setObjectName("Eyebrow")
        box.addWidget(guardrail_title)
        self._risk_row(box, "RISK PER TRADE", "0.50%", "Cyan")
        self._risk_row(box, "DAILY LOSS LIMIT", "2.00%", "Muted")
        self._risk_row(box, "MAX DRAWDOWN", "10.00%", "Muted")
        box.addStretch()

        self.paper_button = QPushButton("OPEN PAPER TICKET")
        self.paper_button.setObjectName("PrimaryButton")
        self.paper_button.clicked.connect(self._show_paper_ticket)
        box.addWidget(self.paper_button)

        replay_button = QPushButton("REPLAY SESSION")
        replay_button.clicked.connect(self._replay_session)
        box.addWidget(replay_button)

        self.halt_button = QPushButton("HALT DEMO FEED")
        self.halt_button.setObjectName("DangerButton")
        self.halt_button.clicked.connect(self._toggle_feed)
        box.addWidget(self.halt_button)
        return panel

    def _risk_row(self, parent, title, value, value_object):
        row = QHBoxLayout()
        label = QLabel(title)
        label.setObjectName("Muted")
        label.setFont(ui_font(8, 600))
        result = QLabel(value)
        result.setObjectName(value_object)
        result.setFont(mono_font(9, 650))
        row.addWidget(label)
        row.addStretch()
        row.addWidget(result)
        parent.addLayout(row)
        return result

    def _separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"color:{COLORS['line']};")
        return line

    # ---------- live demo state ----------
    def _refresh_all(self):
        analysis = self._analyze()
        self._update_metrics(analysis)
        self._render_chart()

    def _tick_demo_feed(self):
        if not self.feed_running:
            return
        last = float(self.data["close"].iloc[-1])
        delta = float(self._rng.normal(0, 1.65))
        close = max(1.0, last + delta)
        open_ = last
        spread = abs(float(self._rng.normal(1.35, 0.4)))
        row = {
            "date": datetime.now(timezone.utc).replace(tzinfo=None),
            "open": open_,
            "high": max(open_, close) + spread,
            "low": min(open_, close) - spread,
            "close": close,
            "volume": int(self._rng.integers(700, 6800)),
        }
        self.data = pd.concat([self.data, pd.DataFrame([row])], ignore_index=True).tail(240)
        self.data["MA20"] = self.data["close"].rolling(20).mean()
        self.data["MA50"] = self.data["close"].rolling(50).mean()
        self._refresh_all()

    def _analyze(self):
        close = self.data["close"]
        current = float(close.iloc[-1])
        previous = float(close.iloc[-2])
        ma20 = float(close.rolling(20).mean().iloc[-1])
        ma50 = float(close.rolling(50).mean().iloc[-1])
        returns = close.pct_change().dropna().tail(30)
        volatility = float(returns.std() * 100)

        delta = close.diff().tail(15)
        gain = delta.clip(lower=0).mean()
        loss = -delta.clip(upper=0).mean()
        rsi = 100 if loss == 0 and gain > 0 else 50 if loss == 0 else 100 - (100 / (1 + gain / loss))

        if current > ma20 > ma50 and 48 < rsi < 68:
            signal, score, reason = "LONG BIAS", 68, "Trend aligned; waiting for crossover confirmation"
        elif current < ma20 < ma50 and 32 < rsi < 52:
            signal, score, reason = "SHORT BIAS", 65, "Downtrend aligned; waiting for crossover confirmation"
        else:
            signal, score, reason = "WAIT", 41, "No validated entry; capital remains protected"

        return {
            "price": current,
            "change": (current / previous - 1) * 100,
            "signal": signal,
            "score": score,
            "reason": reason,
            "volatility": volatility,
        }

    def _update_metrics(self, analysis):
        self.price_value.setText(f"{analysis['price']:,.2f}")
        self.change_value.setText(f"{analysis['change']:+.2f}%")
        self.change_value.setObjectName("Positive" if analysis["change"] >= 0 else "Negative")
        self.change_value.style().unpolish(self.change_value)
        self.change_value.style().polish(self.change_value)
        self.signal_value.setText(analysis["signal"])
        self.confidence_value.setText(f"{analysis['score']} / 100")
        vol_label = "ELEVATED" if analysis["volatility"] > 0.12 else "NORMAL"
        self.volatility_value.setText(vol_label)
        self.risk_signal.setText(analysis["signal"])
        self.signal_reason.setText(analysis["reason"])

    def _render_chart(self):
        self.chart.removeAllSeries()
        for axis in list(self.chart.axes()):
            self.chart.removeAxis(axis)

        frame = self.data.tail(90)
        candles = QCandlestickSeries()
        candles.setName("PAXG / USDT")
        candles.setIncreasingColor(QColor(COLORS["cyan"]))
        candles.setDecreasingColor(QColor(COLORS["red"]))
        candles.setBodyWidth(0.72)

        ma20 = QLineSeries()
        ma20.setName("EMA 20")
        ma20.setPen(QPen(QColor(COLORS["cyan"]), 1.4))
        ma50 = QLineSeries()
        ma50.setName("EMA 50")
        ma50.setPen(QPen(QColor(COLORS["violet"]), 1.4))

        for _, row in frame.iterrows():
            timestamp = int(pd.Timestamp(row["date"]).timestamp() * 1000)
            candle = QCandlestickSet(
                float(row["open"]), float(row["high"]), float(row["low"]), float(row["close"]), timestamp
            )
            candles.append(candle)
            if pd.notna(row.get("MA20")):
                ma20.append(timestamp, float(row["MA20"]))
            if pd.notna(row.get("MA50")):
                ma50.append(timestamp, float(row["MA50"]))

        self.chart.addSeries(candles)
        self.chart.addSeries(ma20)
        self.chart.addSeries(ma50)

        axis_x = QDateTimeAxis()
        axis_x.setFormat("HH:mm")
        axis_x.setLabelsColor(QColor(COLORS["muted"]))
        axis_x.setGridLineColor(QColor(COLORS["line"]))
        axis_x.setLinePenColor(QColor(COLORS["line_bright"]))
        axis_x.setLabelsFont(mono_font(7))
        axis_x.setTickCount(7)
        self.chart.addAxis(axis_x, Qt.AlignBottom)

        axis_y = QValueAxis()
        low = float(frame["low"].min())
        high = float(frame["high"].max())
        padding = max(2.0, (high - low) * 0.08)
        axis_y.setRange(low - padding, high + padding)
        axis_y.setLabelFormat("%.2f")
        axis_y.setLabelsColor(QColor(COLORS["muted"]))
        axis_y.setGridLineColor(QColor(COLORS["line"]))
        axis_y.setLinePenColor(QColor(COLORS["line_bright"]))
        axis_y.setLabelsFont(mono_font(7))
        axis_y.setTickCount(7)
        self.chart.addAxis(axis_y, Qt.AlignRight)

        for series in (candles, ma20, ma50):
            series.attachAxis(axis_x)
            series.attachAxis(axis_y)

    # ---------- actions ----------
    def _update_clock(self):
        self.clock_label.setText(datetime.now(timezone.utc).strftime("%d %b %Y  /  %H:%M:%S UTC"))

    def _show_paper_ticket(self):
        QMessageBox.information(
            self,
            "Paper order",
            "Paper execution is intentionally protected.\n\n"
            "No live order will be sent. Use the Backtest workspace to validate a strategy first.",
        )

    def _select_timeframe(self, selected):
        for button in self.findChildren(QPushButton):
            timeframe = button.property("timeframe")
            if not timeframe:
                continue
            active = timeframe == selected
            button.setChecked(active)
            button.setStyleSheet(
                f"color:{COLORS['cyan']}; border-color:{COLORS['cyan']};"
                f"background:{COLORS['cyan_soft']};" if active else ""
            )

    def _replay_session(self):
        self.data = self.generate_sample_data()
        self._refresh_all()

    def _toggle_feed(self):
        self.feed_running = not self.feed_running
        if self.feed_running:
            self.halt_button.setText("HALT DEMO FEED")
            self.feed_badge.setText("DEMO FEED  /  CONNECTED")
            self.feed_badge.setObjectName("Positive")
            self.breaker_state.setText("ARMED / SAFE")
        else:
            self.halt_button.setText("RESUME DEMO FEED")
            self.feed_badge.setText("DEMO FEED  /  HALTED")
            self.feed_badge.setObjectName("Negative")
            self.breaker_state.setText("FEED HALTED")
        for label in (self.feed_badge, self.breaker_state):
            label.style().unpolish(label)
            label.style().polish(label)

    @staticmethod
    def generate_sample_data():
        rng = np.random.default_rng(42)
        dates = pd.date_range(end=datetime.now(timezone.utc).replace(tzinfo=None), periods=240, freq="5min")
        movement = rng.normal(0.08, 1.65, 240)
        prices = 4680 + np.cumsum(movement)
        opens = np.r_[prices[0], prices[:-1]]
        wick = np.abs(rng.normal(1.25, 0.5, 240))
        data = pd.DataFrame(
            {
                "date": dates,
                "open": opens,
                "high": np.maximum(opens, prices) + wick,
                "low": np.minimum(opens, prices) - wick,
                "close": prices,
                "volume": rng.integers(700, 6800, 240),
            }
        )
        data["MA20"] = data["close"].rolling(20).mean()
        data["MA50"] = data["close"].rolling(50).mean()
        return data
