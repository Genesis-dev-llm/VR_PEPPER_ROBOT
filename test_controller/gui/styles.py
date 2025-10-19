"""
Qt Stylesheet (QSS) - Professional Dark Theme
Modern, clean design for Pepper Control Center
"""

DARK_THEME = """
/* ========================================================================
   MAIN WINDOW
   ======================================================================== */
QMainWindow {
    background-color: #1e1e1e;
    color: #e0e0e0;
}

/* ========================================================================
   STATUS BAR
   ======================================================================== */
QStatusBar {
    background-color: #2d2d30;
    color: #e0e0e0;
    border-top: 1px solid #3e3e42;
    padding: 5px;
    font-size: 12px;
}

QStatusBar::item {
    border: none;
}

/* ========================================================================
   PANELS & FRAMES
   ======================================================================== */
QFrame {
    background-color: #252526;
    border: 1px solid #3e3e42;
    border-radius: 8px;
    padding: 10px;
}

QGroupBox {
    background-color: #252526;
    border: 2px solid #3e3e42;
    border-radius: 8px;
    margin-top: 10px;
    padding: 15px;
    font-weight: bold;
    font-size: 14px;
    color: #e0e0e0;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 5px 10px;
    background-color: #2d2d30;
    border-radius: 4px;
}

/* ========================================================================
   BUTTONS
   ======================================================================== */
QPushButton {
    background-color: #0e639c;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: bold;
    min-height: 30px;
}

QPushButton:hover {
    background-color: #1177bb;
}

QPushButton:pressed {
    background-color: #005a9e;
}

QPushButton:disabled {
    background-color: #3e3e42;
    color: #6e6e6e;
}

/* Dance Buttons (with emojis) */
QPushButton#danceButton {
    background-color: #5a4a9f;
    font-size: 16px;
    min-width: 80px;
    min-height: 50px;
}

QPushButton#danceButton:hover {
    background-color: #6d5cb8;
}

/* Emergency Stop Button */
QPushButton#emergencyButton {
    background-color: #c42b1c;
    font-size: 16px;
    min-height: 60px;
    font-weight: bold;
}

QPushButton#emergencyButton:hover {
    background-color: #e81123;
}

QPushButton#emergencyButton:pressed {
    background-color: #a80000;
}

/* Toggle Buttons */
QPushButton#toggleButton {
    background-color: #3e3e42;
}

QPushButton#toggleButton:checked {
    background-color: #0e639c;
}

/* ========================================================================
   SLIDERS
   ======================================================================== */
QSlider::groove:horizontal {
    background: #3e3e42;
    height: 8px;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: #0e639c;
    width: 18px;
    height: 18px;
    margin: -5px 0;
    border-radius: 9px;
}

QSlider::handle:horizontal:hover {
    background: #1177bb;
}

QSlider::sub-page:horizontal {
    background: #0e639c;
    border-radius: 4px;
}

/* ========================================================================
   RADIO BUTTONS
   ======================================================================== */
QRadioButton {
    color: #e0e0e0;
    spacing: 8px;
    font-size: 13px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 9px;
    border: 2px solid #6e6e6e;
    background-color: #2d2d30;
}

QRadioButton::indicator:checked {
    background-color: #0e639c;
    border: 2px solid #0e639c;
}

QRadioButton::indicator:hover {
    border: 2px solid #1177bb;
}

/* ========================================================================
   LABELS
   ======================================================================== */
QLabel {
    color: #e0e0e0;
    font-size: 13px;
    background: transparent;
    border: none;
}

QLabel#headerLabel {
    font-size: 16px;
    font-weight: bold;
    color: #ffffff;
}

QLabel#statusLabel {
    font-size: 12px;
    padding: 5px;
    border-radius: 4px;
}

/* ========================================================================
   PROGRESS BARS
   ======================================================================== */
QProgressBar {
    border: 2px solid #3e3e42;
    border-radius: 5px;
    background-color: #2d2d30;
    text-align: center;
    color: #e0e0e0;
    font-weight: bold;
}

QProgressBar::chunk {
    background-color: #0e639c;
    border-radius: 3px;
}

/* Battery colors */
QProgressBar#batteryGood::chunk {
    background-color: #4ade80;
}

QProgressBar#batteryMedium::chunk {
    background-color: #fbbf24;
}

QProgressBar#batteryLow::chunk {
    background-color: #f87171;
}

/* ========================================================================
   SCROLLBARS
   ======================================================================== */
QScrollBar:vertical {
    background: #2d2d30;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background: #6e6e6e;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #8e8e8e;
}

QScrollBar:horizontal {
    background: #2d2d30;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background: #6e6e6e;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background: #8e8e8e;
}

/* ========================================================================
   SPLITTER
   ======================================================================== */
QSplitter::handle {
    background-color: #3e3e42;
    width: 3px;
    height: 3px;
}

QSplitter::handle:hover {
    background-color: #0e639c;
}

/* ========================================================================
   VIDEO DISPLAY
   ======================================================================== */
QLabel#videoLabel {
    background-color: #000000;
    border: 2px solid #3e3e42;
    border-radius: 8px;
}

/* ========================================================================
   DRAG & DROP ZONE
   ======================================================================== */
QLabel#dropZone {
    background-color: #2d2d30;
    border: 3px dashed #6e6e6e;
    border-radius: 10px;
    color: #8e8e8e;
    font-size: 14px;
    padding: 30px;
}

QLabel#dropZone[dragActive="true"] {
    border: 3px dashed #0e639c;
    background-color: #1e3a5f;
    color: #ffffff;
}

/* ========================================================================
   TOOLTIPS
   ======================================================================== */
QToolTip {
    background-color: #2d2d30;
    color: #e0e0e0;
    border: 1px solid #6e6e6e;
    border-radius: 4px;
    padding: 5px;
    font-size: 12px;
}
"""

def apply_theme(app):
    """Apply the dark theme to the application."""
    app.setStyleSheet(DARK_THEME)