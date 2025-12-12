# === Modern AromaSense Theme ===
STYLESHEET = """
/* Modern AromaSense Theme - Green & Teal */
QMainWindow {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                               stop: 0 #F8F9FA, stop: 1 #E9ECEF);
}

QWidget {
    background-color: transparent;
    color: #495057;
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 13px;
}

/* Sidebar Styling */
QFrame#sidebar {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                               stop: 0 #2E8B57, stop: 1 #3CB371);
    border-radius: 0px;
    border: none;
}

#sidebar QLabel {
    color: #FFFFFF;
    font-weight: 500;
}

#sidebar QGroupBox {
    color: #FFFFFF;
    font-weight: bold;
    font-size: 13px;
    border: 2px solid #FFFFFF;
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 10px;
    background-color: rgba(255, 255, 255, 0.1);
}

#sidebar QGroupBox::title {
    color: #FFFFFF;
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 8px;
    background-color: transparent;
}

#sidebar QPushButton {
    background-color: #FFFFFF;
    color: #2E8B57;
    border: none;
    padding: 10px 15px;
    border-radius: 6px;
    font-weight: bold;
    font-size: 12px;
    min-height: 25px;
}

#sidebar QPushButton:hover {
    background-color: #F8F9FA;
    color: #228B22;
}

#sidebar QPushButton:pressed {
    background-color: #E9ECEF;
}

/* Main Content Styling */
QGroupBox {
    font-weight: bold;
    font-size: 13px;
    color: #2E8B57;
    border: 2px solid #CED4DA;
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 10px;
    background-color: #FFFFFF;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 8px;
    background-color: #FFFFFF;
    color: #2E8B57;
}

/* Button Styling */
QPushButton {
    background-color: #2E8B57;
    color: #FFFFFF;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: bold;
    font-size: 12px;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #228B22;
}

QPushButton:pressed {
    background-color: #006400;
}

QPushButton:disabled {
    background-color: #6c757d;
    color: #adb5bd;
}

/* Special Buttons */
QPushButton#startButton {
    background-color: #28a745;
    color: white;
    font-weight: bold;
}

QPushButton#startButton:hover {
    background-color: #218838;
}

QPushButton#stopButton {
    background-color: #dc3545;
    color: white;
    font-weight: bold;
}

QPushButton#stopButton:hover {
    background-color: #c82333;
}

/* Table Styling */
QTableWidget {
    background-color: #FFFFFF;
    gridline-color: #DEE2E6;
    selection-background-color: #2E8B57;
    border: 1px solid #DEE2E6;
    border-radius: 6px;
    alternate-background-color: #F8F9FA;
}

QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #E9ECEF;
}

QTableWidget::item:selected {
    background-color: #2E8B57;
    color: white;
}

QHeaderView::section {
    background-color: #2E8B57;
    color: white;
    padding: 10px;
    border: none;
    font-weight: bold;
    font-size: 12px;
}

/* Tab Widget Styling */
QTabWidget::pane {
    border: 2px solid #CED4DA;
    border-radius: 8px;
    background: #FFFFFF;
    margin-top: 2px;
}

QTabWidget::tab-bar {
    alignment: center;
}

QTabBar::tab {
    background: #E9ECEF;
    color: #495057;
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: bold;
    min-width: 120px;
}

QTabBar::tab:selected {
    background: #2E8B57;
    color: white;
    border-bottom: 3px solid #228B22;
}

QTabBar::tab:hover:!selected {
    background: #DEE2E6;
}

/* Progress Bar */
QProgressBar {
    border: 2px solid #CED4DA;
    border-radius: 6px;
    background-color: #F8F9FA;
    text-align: center;
    color: #495057;
}

QProgressBar::chunk {
    background-color: #2E8B57;
    border-radius: 4px;
}

/* Line Edit & Combo Box */
QLineEdit, QComboBox {
    background-color: #FFFFFF;
    border: 2px solid #CED4DA;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
    color: #495057;
    min-height: 20px;
}

QLineEdit:focus, QComboBox:focus {
    border-color: #2E8B57;
}

QComboBox::drop-down {
    border: none;
    width: 25px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #495057;
    width: 0px;
    height: 0px;
}

/* Splitter */
QSplitter::handle {
    background-color: #CED4DA;
    border: 1px solid #ADB5BD;
}

QSplitter::handle:hover {
    background-color: #2E8B57;
}

/* Status Bar */
QStatusBar {
    background-color: #2E8B57;
    color: #FFFFFF;
    font-weight: bold;
    padding: 8px;
    border-top: 2px solid #228B22;
}

/* Scrollbars */
QScrollBar:vertical {
    background: #F8F9FA;
    width: 15px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #2E8B57;
    border-radius: 7px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #228B22;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}
"""

STATUS_COLORS = {
    'disconnected': (108, 117, 125),    # Gray
    'connecting': (23, 162, 184),       # Cyan
    'connected': (40, 167, 69),         # Green
    'sampling': (255, 193, 7),          # Yellow
    'error': (220, 53, 69)              # Red
}