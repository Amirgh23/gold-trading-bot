#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
اسکریپت اجرای رابط کاربری گرافیکی
"""

import sys
import os

# اضافه کردن مسیر پروژه به PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui import main

if __name__ == '__main__':
    print("="*60)
    print("🚀 راه‌اندازی رابط کاربری ربات تریدر طلا")
    print("="*60)
    main()
