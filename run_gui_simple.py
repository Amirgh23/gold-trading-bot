#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
اسکریپت اجرای رابط کاربری ساده (بدون TensorFlow)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui_simple import main

if __name__ == '__main__':
    print("="*60)
    print("🚀 راه‌اندازی رابط کاربری ربات تریدر طلا")
    print("📊 نسخه ساده - بدون یادگیری ماشین")
    print("="*60)
    main()
