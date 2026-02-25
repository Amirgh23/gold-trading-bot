#!/usr/bin/env python3
"""
Build EXE for Gold Trading Bot using PyInstaller
"""

import os
import sys
import shutil
from pathlib import Path

def build_exe():
    """Build standalone EXE"""
    
    print("=" * 60)
    print("Building Gold Trading Bot EXE")
    print("=" * 60)
    
    # Clean previous builds
    if os.path.exists("dist"):
        shutil.rmtree("dist")
        print("✓ Cleaned previous dist folder")
    
    if os.path.exists("build"):
        shutil.rmtree("build")
        print("✓ Cleaned previous build folder")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",  # Single EXE file
        "--windowed",  # No console window
        "--name=GoldTradingBot",  # EXE name
        "--icon=trading_bot/gui/icon.ico" if os.path.exists("trading_bot/gui/icon.ico") else "",
        "--add-data=config:config",  # Include config folder
        "--add-data=trading_bot/i18n:trading_bot/i18n",  # Include translations
        "--hidden-import=PyQt5",
        "--hidden-import=numpy",
        "--hidden-import=pandas",
        "--hidden-import=tensorflow",
        "--hidden-import=sklearn",
        "--hidden-import=sqlite3",
        "--collect-all=PyQt5",
        "run_launcher.py"
    ]
    
    # Remove empty strings
    cmd = [c for c in cmd if c]
    
    print("\nRunning PyInstaller...")
    print(f"Command: {' '.join(cmd)}\n")
    
    os.system(" ".join(cmd))
    
    # Check if build was successful
    exe_path = Path("dist/GoldTradingBot.exe")
    if exe_path.exists():
        print("\n" + "=" * 60)
        print("✓ EXE BUILD SUCCESSFUL!")
        print("=" * 60)
        print(f"\nEXE Location: {exe_path.absolute()}")
        print(f"File Size: {exe_path.stat().st_size / (1024*1024):.2f} MB")
        print("\nYou can now run: dist/GoldTradingBot.exe")
        return True
    else:
        print("\n✗ EXE build failed!")
        return False

if __name__ == "__main__":
    success = build_exe()
    sys.exit(0 if success else 1)
