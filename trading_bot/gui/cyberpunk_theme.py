"""Shared violet/cyan visual system for the desktop application."""

from PyQt5.QtGui import QColor, QFont, QPalette


COLORS = {
    "void": "#050611",
    "base": "#090B18",
    "surface": "#0D1022",
    "surface_raised": "#12162D",
    "line": "#252B4A",
    "line_bright": "#3A4775",
    "text": "#E8ECFF",
    "muted": "#858EAD",
    "cyan": "#20D9FF",
    "cyan_soft": "#112F45",
    "violet": "#9564FF",
    "violet_soft": "#251A4A",
    "gold": "#F4C55C",
    "green": "#2BE6A6",
    "red": "#FF4F7B",
    "amber": "#FFB454",
}


def ui_font(size: int = 10, weight: int = QFont.Normal) -> QFont:
    """Return a clean Windows UI font with consistent sizing."""
    font = QFont("Segoe UI", size)
    font.setWeight(weight)
    return font


def mono_font(size: int = 10, weight: int = QFont.Normal) -> QFont:
    """Return the numeric/data font used across the terminal UI."""
    font = QFont("Cascadia Mono", size)
    font.setStyleHint(QFont.Monospace)
    font.setWeight(weight)
    return font


def apply_application_palette(app) -> None:
    """Set palette defaults for native dialogs and fallback widgets."""
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(COLORS["base"]))
    palette.setColor(QPalette.WindowText, QColor(COLORS["text"]))
    palette.setColor(QPalette.Base, QColor(COLORS["void"]))
    palette.setColor(QPalette.AlternateBase, QColor(COLORS["surface"]))
    palette.setColor(QPalette.Text, QColor(COLORS["text"]))
    palette.setColor(QPalette.Button, QColor(COLORS["surface_raised"]))
    palette.setColor(QPalette.ButtonText, QColor(COLORS["text"]))
    palette.setColor(QPalette.Highlight, QColor(COLORS["violet"]))
    palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
    app.setPalette(palette)


def application_stylesheet() -> str:
    """Global stylesheet. Object names provide intentional hierarchy."""
    return f"""
    * {{
        font-family: "Segoe UI";
        outline: none;
    }}
    QMainWindow, QWidget#AppRoot {{
        background: {COLORS['void']};
        color: {COLORS['text']};
    }}
    QWidget {{
        color: {COLORS['text']};
        background: transparent;
    }}
    QWidget#Sidebar {{
        background: {COLORS['base']};
        border-right: 1px solid {COLORS['line']};
    }}
    QLabel#Brand {{
        color: {COLORS['text']};
        font-size: 20px;
        font-weight: 700;
        letter-spacing: 2px;
    }}
    QLabel#BrandAccent, QLabel#Eyebrow {{
        color: {COLORS['cyan']};
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 2px;
    }}
    QLabel#PageTitle {{
        color: {COLORS['text']};
        font-size: 22px;
        font-weight: 650;
    }}
    QLabel#Muted {{ color: {COLORS['muted']}; }}
    QLabel#Gold {{ color: {COLORS['gold']}; }}
    QLabel#Cyan {{ color: {COLORS['cyan']}; }}
    QLabel#Violet {{ color: {COLORS['violet']}; }}
    QLabel#Positive {{ color: {COLORS['green']}; }}
    QLabel#Negative {{ color: {COLORS['red']}; }}
    QPushButton {{
        min-height: 34px;
        padding: 0 14px;
        color: {COLORS['text']};
        background: {COLORS['surface_raised']};
        border: 1px solid {COLORS['line']};
        border-radius: 5px;
        font-weight: 600;
    }}
    QPushButton:hover {{
        color: #FFFFFF;
        background: #171C38;
        border-color: {COLORS['violet']};
    }}
    QPushButton:pressed {{ background: {COLORS['violet_soft']}; }}
    QPushButton:disabled {{ color: #555D78; border-color: #1B2037; }}
    QPushButton#NavButton {{
        min-height: 44px;
        padding: 0 16px;
        text-align: left;
        color: {COLORS['muted']};
        background: transparent;
        border: 0;
        border-left: 2px solid transparent;
        border-radius: 0;
    }}
    QPushButton#NavButton:hover {{
        color: {COLORS['text']};
        background: {COLORS['surface']};
        border-left-color: {COLORS['violet']};
    }}
    QPushButton#NavButton[active="true"] {{
        color: {COLORS['cyan']};
        background: {COLORS['cyan_soft']};
        border-left-color: {COLORS['cyan']};
    }}
    QPushButton#PrimaryButton {{
        min-height: 42px;
        color: #07101A;
        background: {COLORS['cyan']};
        border: 1px solid #77EAFF;
        font-weight: 750;
    }}
    QPushButton#PrimaryButton:hover {{ background: #6BE8FF; }}
    QPushButton#DangerButton {{
        color: {COLORS['red']};
        background: #24101F;
        border-color: #6B2946;
    }}
    QPushButton#DangerButton:hover {{ background: #381426; border-color: {COLORS['red']}; }}
    QFrame#Panel, QGroupBox {{
        background: {COLORS['surface']};
        border: 1px solid {COLORS['line']};
        border-radius: 7px;
    }}
    QFrame#PanelAccent {{
        background: {COLORS['surface']};
        border: 1px solid {COLORS['violet']};
        border-radius: 7px;
    }}
    QFrame#SignalPanel {{
        background: {COLORS['violet_soft']};
        border: 1px solid {COLORS['violet']};
        border-radius: 6px;
    }}
    QFrame#CircuitBreaker {{
        background: #0B1D1C;
        border: 1px solid #1D6B58;
        border-radius: 5px;
    }}
    QFrame#Metric {{
        background: {COLORS['surface']};
        border: 1px solid {COLORS['line']};
        border-radius: 6px;
    }}
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {{
        min-height: 34px;
        color: {COLORS['text']};
        background: {COLORS['base']};
        border: 1px solid {COLORS['line']};
        border-radius: 5px;
        padding: 0 9px;
        selection-background-color: {COLORS['violet']};
    }}
    QTextEdit {{ padding: 9px; }}
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus,
    QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {{
        border-color: {COLORS['cyan']};
    }}
    QComboBox::drop-down {{ border: 0; width: 22px; }}
    QComboBox QAbstractItemView {{
        color: {COLORS['text']};
        background: {COLORS['surface_raised']};
        border: 1px solid {COLORS['line_bright']};
        selection-background-color: {COLORS['violet_soft']};
    }}
    QTableWidget {{
        color: {COLORS['text']};
        background: {COLORS['surface']};
        alternate-background-color: #0A0D1D;
        border: 1px solid {COLORS['line']};
        border-radius: 6px;
        gridline-color: {COLORS['line']};
        selection-background-color: {COLORS['violet_soft']};
    }}
    QTableWidget::item {{ padding: 6px; border: 0; }}
    QHeaderView::section {{
        color: {COLORS['muted']};
        background: {COLORS['base']};
        border: 0;
        border-bottom: 1px solid {COLORS['line']};
        padding: 7px;
        font-size: 10px;
        font-weight: 650;
    }}
    QProgressBar {{
        min-height: 6px;
        max-height: 6px;
        background: #171B31;
        border: 0;
        border-radius: 3px;
        text-align: center;
        color: transparent;
    }}
    QProgressBar::chunk {{ background: {COLORS['violet']}; border-radius: 3px; }}
    QTabWidget::pane {{ border: 1px solid {COLORS['line']}; border-radius: 6px; }}
    QTabBar::tab {{
        color: {COLORS['muted']};
        background: transparent;
        border: 0;
        border-bottom: 2px solid transparent;
        padding: 10px 16px;
    }}
    QTabBar::tab:selected {{ color: {COLORS['cyan']}; border-bottom-color: {COLORS['cyan']}; }}
    QStatusBar {{
        color: {COLORS['muted']};
        background: {COLORS['base']};
        border-top: 1px solid {COLORS['line']};
    }}
    QScrollBar:vertical {{ background: transparent; width: 8px; margin: 2px; }}
    QScrollBar::handle:vertical {{ background: {COLORS['line_bright']}; border-radius: 4px; min-height: 24px; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    QSplitter::handle {{ background: {COLORS['line']}; width: 1px; }}
    """
