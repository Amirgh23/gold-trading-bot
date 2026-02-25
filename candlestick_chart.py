# Candlestick Chart
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle
import pandas as pd
import numpy as np
from datetime import datetime

# Configure font for charts
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class CandlestickChart:
    """Candlestick Chart"""
    
    def __init__(self, figsize=(14, 7)):
        self.figsize = figsize
        self.fig = None
        self.ax = None
        self.data = []
        
    def create_figure(self):
        """Create figure"""
        self.fig, self.ax = plt.subplots(figsize=self.figsize, facecolor='#0a0e27')
        self.ax.set_facecolor('#0f1729')
        
        # Settings
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_color('#1e3a5f')
        self.ax.spines['bottom'].set_color('#1e3a5f')
        
        self.ax.tick_params(colors='#ffffff', labelsize=9)
        self.ax.grid(True, alpha=0.2, color='#1e3a5f', linestyle='--')
        
        self.ax.set_xlabel('Time', color='#00d4ff', fontsize=11, fontweight='bold')
        self.ax.set_ylabel('Price ($)', color='#00d4ff', fontsize=11, fontweight='bold')
        self.ax.set_title('Candlestick Chart - Gold (XAU/USDT)', 
                         color='#00d4ff', fontsize=14, fontweight='bold', pad=20)
        
        return self.fig, self.ax
    
    def plot_candlesticks(self, df, width=0.6):
        """Plot candlesticks"""
        if self.fig is None:
            self.create_figure()
        
        for idx, (i, row) in enumerate(df.iterrows()):
            open_price = row['open']
            close_price = row['close']
            high_price = row['high']
            low_price = row['low']
            
            # Color based on bullish/bearish
            if close_price >= open_price:
                color = '#00ff88'  # Green - Bullish
                body_color = '#00ff88'
                edge_color = '#00ff88'
            else:
                color = '#ff4444'  # Red - Bearish
                body_color = '#ff4444'
                edge_color = '#ff4444'
            
            # Wick (high-low lines)
            self.ax.plot([idx, idx], [low_price, high_price], 
                        color=edge_color, linewidth=1.5, zorder=2)
            
            # Body (open-close rectangle)
            body_height = abs(close_price - open_price)
            body_bottom = min(open_price, close_price)
            
            rect = Rectangle((idx - width/2, body_bottom), width, body_height,
                           facecolor=body_color, edgecolor=edge_color, 
                           linewidth=1.5, zorder=3, alpha=0.8)
            self.ax.add_patch(rect)
        
        # Set axes
        self.ax.set_xlim(-1, len(df))
        self.ax.set_ylim(df['low'].min() * 0.99, df['high'].max() * 1.01)
        
        # X-axis labels
        if len(df) > 0:
            step = max(1, len(df) // 10)
            x_ticks = range(0, len(df), step)
            x_labels = []
            for i in x_ticks:
                if hasattr(df.index[i], 'strftime'):
                    x_labels.append(df.index[i].strftime('%H:%M'))
                else:
                    x_labels.append(str(i))
            self.ax.set_xticks(x_ticks)
            self.ax.set_xticklabels(x_labels, rotation=45, ha='right')
        
        return self.fig, self.ax
    
    def add_ema(self, df, period, color, label, linewidth=2):
        """Add EMA"""
        if f'ema_{period}' not in df.columns:
            df[f'ema_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
        
        self.ax.plot(range(len(df)), df[f'ema_{period}'], 
                    color=color, linewidth=linewidth, label=label, zorder=4, alpha=0.8)
    
    def add_bollinger_bands(self, df, period=20, std_dev=2):
        """Add Bollinger Bands"""
        if 'bb_middle' not in df.columns:
            df['bb_middle'] = df['close'].rolling(window=period).mean()
            df['bb_std'] = df['close'].rolling(window=period).std()
            df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * std_dev)
            df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * std_dev)
        
        # Lines
        self.ax.plot(range(len(df)), df['bb_upper'], 
                    color='#00d4ff', linewidth=1, linestyle='--', alpha=0.5, label='BB Upper')
        self.ax.plot(range(len(df)), df['bb_middle'], 
                    color='#00d4ff', linewidth=1.5, alpha=0.7, label='BB Middle')
        self.ax.plot(range(len(df)), df['bb_lower'], 
                    color='#00d4ff', linewidth=1, linestyle='--', alpha=0.5, label='BB Lower')
        
        # Fill between bands
        self.ax.fill_between(range(len(df)), df['bb_upper'], df['bb_lower'], 
                            color='#00d4ff', alpha=0.05)
    
    def add_volume(self, df, ax_volume=None):
        """Add volume chart"""
        if ax_volume is None:
            return
        
        colors = ['#00ff88' if df['close'].iloc[i] >= df['open'].iloc[i] 
                 else '#ff4444' for i in range(len(df))]
        
        ax_volume.bar(range(len(df)), df['volume'], color=colors, alpha=0.6, width=0.8)
        ax_volume.set_facecolor('#0f1729')
        ax_volume.set_ylabel('Volume', color='#00d4ff', fontsize=10, fontweight='bold')
        ax_volume.tick_params(colors='#ffffff', labelsize=8)
        ax_volume.grid(True, alpha=0.2, color='#1e3a5f', linestyle='--')
        ax_volume.spines['top'].set_visible(False)
        ax_volume.spines['right'].set_visible(False)
        ax_volume.spines['left'].set_color('#1e3a5f')
        ax_volume.spines['bottom'].set_color('#1e3a5f')
    
    def add_legend(self):
        """Add legend"""
        self.ax.legend(loc='upper left', framealpha=0.9, 
                      facecolor='#0f1729', edgecolor='#1e3a5f',
                      labelcolor='#ffffff', fontsize=9)
    
    def show(self):
        """Show chart"""
        plt.tight_layout()
        plt.show()
    
    def save(self, filename):
        """Save chart"""
        plt.tight_layout()
        plt.savefig(filename, facecolor='#0a0e27', dpi=150, bbox_inches='tight')
        print(f"✅ Chart saved: {filename}")

# Candlestick chart in PyQt5
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtGui import QPainter
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class CandlestickChartWidget(QWidget):
    """Candlestick Chart Widget for PyQt5"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(14, 7), facecolor='#0a0e27')
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
        self.ax = None
        self.data = []
    
    def plot_candlesticks(self, df, width=0.6):
        """Plot candlesticks"""
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        
        # Settings
        self.ax.set_facecolor('#0f1729')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_color('#1e3a5f')
        self.ax.spines['bottom'].set_color('#1e3a5f')
        
        self.ax.tick_params(colors='#ffffff', labelsize=9)
        self.ax.grid(True, alpha=0.2, color='#1e3a5f', linestyle='--')
        
        self.ax.set_xlabel('Time', color='#00d4ff', fontsize=11, fontweight='bold')
        self.ax.set_ylabel('Price ($)', color='#00d4ff', fontsize=11, fontweight='bold')
        self.ax.set_title('Candlestick Chart - Gold (XAU/USDT)', 
                         color='#00d4ff', fontsize=14, fontweight='bold', pad=20)
        
        # Plot candlesticks
        for idx, (i, row) in enumerate(df.iterrows()):
            open_price = row['open']
            close_price = row['close']
            high_price = row['high']
            low_price = row['low']
            
            # Color
            if close_price >= open_price:
                color = '#00ff88'
                edge_color = '#00ff88'
            else:
                color = '#ff4444'
                edge_color = '#ff4444'
            
            # Wick
            self.ax.plot([idx, idx], [low_price, high_price], 
                        color=edge_color, linewidth=1.5, zorder=2)
            
            # Body
            body_height = abs(close_price - open_price)
            body_bottom = min(open_price, close_price)
            
            rect = patches.Rectangle((idx - width/2, body_bottom), width, body_height,
                                    facecolor=color, edgecolor=edge_color, 
                                    linewidth=1.5, zorder=3, alpha=0.8)
            self.ax.add_patch(rect)
        
        # Axes
        self.ax.set_xlim(-1, len(df))
        self.ax.set_ylim(df['low'].min() * 0.99, df['high'].max() * 1.01)
        
        # X-axis labels
        if len(df) > 0:
            step = max(1, len(df) // 10)
            x_ticks = range(0, len(df), step)
            x_labels = []
            for i in x_ticks:
                if hasattr(df.index[i], 'strftime'):
                    x_labels.append(df.index[i].strftime('%H:%M'))
                else:
                    x_labels.append(str(i))
            self.ax.set_xticks(x_ticks)
            self.ax.set_xticklabels(x_labels, rotation=45, ha='right')
        
        self.canvas.draw()
    
    def add_ema(self, df, period, color, label):
        """Add EMA"""
        if f'ema_{period}' not in df.columns:
            df[f'ema_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
        
        self.ax.plot(range(len(df)), df[f'ema_{period}'], 
                    color=color, linewidth=2, label=label, zorder=4, alpha=0.8)
        self.canvas.draw()
    
    def add_bollinger_bands(self, df, period=20, std_dev=2):
        """Add Bollinger Bands"""
        if 'bb_middle' not in df.columns:
            df['bb_middle'] = df['close'].rolling(window=period).mean()
            df['bb_std'] = df['close'].rolling(window=period).std()
            df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * std_dev)
            df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * std_dev)
        
        self.ax.plot(range(len(df)), df['bb_upper'], 
                    color='#00d4ff', linewidth=1, linestyle='--', alpha=0.5, label='BB Upper')
        self.ax.plot(range(len(df)), df['bb_middle'], 
                    color='#00d4ff', linewidth=1.5, alpha=0.7, label='BB Middle')
        self.ax.plot(range(len(df)), df['bb_lower'], 
                    color='#00d4ff', linewidth=1, linestyle='--', alpha=0.5, label='BB Lower')
        
        self.ax.fill_between(range(len(df)), df['bb_upper'], df['bb_lower'], 
                            color='#00d4ff', alpha=0.05)
        self.canvas.draw()
    
    def add_legend(self):
        """Add legend"""
        self.ax.legend(loc='upper left', framealpha=0.9, 
                      facecolor='#0f1729', edgecolor='#1e3a5f',
                      labelcolor='#ffffff', fontsize=9)
        self.canvas.draw()
