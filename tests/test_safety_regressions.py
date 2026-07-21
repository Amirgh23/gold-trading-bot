"""Regression tests for money-impacting defects."""

from datetime import datetime

import pytest

from trading_bot.execution.position_manager import PositionManager
from trading_bot.models.signal import Signal
from trading_bot.risk.manager import RiskManager


def _signal(direction: str) -> Signal:
    return Signal(
        timestamp=datetime.now(),
        symbol="PAXG/USDT",
        direction=direction,
        strategy="TEST",
        confidence=80,
        entry_price=2000,
        stop_loss=2010 if direction == "SELL" else 1990,
        take_profit=1980 if direction == "SELL" else 2020,
        reason="regression",
    )


def test_short_trade_profit_has_correct_sign():
    manager = PositionManager()
    position = manager.open_position(_signal("SELL"), 1)
    trade = manager.close_position(position.id, 1980, "TAKE_PROFIT")

    assert trade.side == "SHORT"
    assert trade.pnl == pytest.approx(20)
    assert trade.pnl_percent == pytest.approx(1)


def test_position_size_caps_notional_exposure():
    risk = RiskManager(
        account_equity=10_000,
        max_position_size_percent=2,
        risk_per_trade_percent=1,
    )

    units = risk.calculate_position_size(entry_price=2000, stop_loss=1990)

    assert units * 2000 <= 200 + 1e-9
    assert risk.check_risk_limits(units, 0, 0, entry_price=2000)
