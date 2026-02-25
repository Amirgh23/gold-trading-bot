#!/usr/bin/env python3
"""
Gold Trading Bot - GUI Launcher
Central hub for accessing all features: Dashboard, Backtesting, Tests, Settings
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trading_bot.gui.launcher import main

if __name__ == "__main__":
    main()
