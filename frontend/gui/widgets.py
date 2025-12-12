"""Custom widgets for modern AromaSense theme"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QSpinBox,
    QCheckBox, QGroupBox, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QColor, QFont, QPainter, QBrush, QLinearGradient

import pyqtgraph as pg
import numpy as np
import serial.tools.list_ports
from config.constants import SAMPLE_TYPES, PLOT_COLORS, NUM_SENSORS, SENSOR_NAMES, MAX_PLOT_POINTS

class StatusIndicator(QFrame):
    """Modern status indicator with gradient"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.status_color = QColor(108, 117, 125)  # Gray default
        self.status_text = "Disconnected"
        self.setMinimumWidth(200)
        self.setMinimumHeight(45)
        
    def set_status(self, status_text: str, color_rgb: tuple):
        """Update status with text and color"""
        self.status_text = status_text
        self.status_color = QColor(*color_rgb)
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw modern gradient background
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0, QColor(248, 249, 250))
        gradient.setColorAt(1, QColor(233, 236, 239))
        painter.setBrush(QBrush(gradient))
        painter.setPen(QColor(222, 226, 230))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 8, 8)
        
        # Draw status circle with shadow effect
        painter.setBrush(QBrush(self.status_color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(12, 12, 20, 20)
        
        # Draw inner circle for modern look
        painter.setBrush(QBrush(QColor(255, 255, 255, 100)))
        painter.drawEllipse(15, 15, 14, 14)
        
        # Draw text
        font = QFont("Segoe UI", 11)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(33, 37, 41))
        painter.drawText(45, 0, 150, 45, Qt.AlignVCenter | Qt.AlignLeft, self.status_text)


class SensorPlot(pg.PlotWidget):
    """Modern PyQtGraph plotting widget"""
    
    def __init__(self, title: str = "Herbal Analysis Data", parent=None):
        super().__init__(parent)
        
        self.plot_title = title
        self.num_sensors = NUM_SENSORS
        self.max_points = MAX_PLOT_POINTS 
        
        # Modern plot styling
        self.setTitle(self.plot_title, color='#2E8B57', size='14pt', bold=True)
        self.setBackground('#FFFFFF')
        self.showGrid(x=True, y=True, alpha=0.3)
        
        # Modern axis styling
        styles = {'color': '#495057', 'font-size': '11pt'}
        self.setLabel('left', 'Sensor Reading', **styles)
        self.setLabel('bottom', 'Time (seconds)', **styles)
        
        # Set axis colors
        self.getAxis('left').setPen('#495057')
        self.getAxis('bottom').setPen('#495057')
        
        # Data storage
        self.time_data = np.array([])
        self.sensor_data = {i: np.array([]) for i in range(self.num_sensors)}
        self.plot_lines = {}
        
        self.addLegend(offset=(10, 10))
        
        # Create modern plot lines
        for i in range(self.num_sensors):
            color = PLOT_COLORS[i % len(PLOT_COLORS)]
            pen = pg.mkPen(color=color, width=2.5, style=Qt.SolidLine)
            
            name = SENSOR_NAMES[i] if i < len(SENSOR_NAMES) else f"Sensor {i+1}"
            
            self.plot_lines[i] = self.plot([], [], pen=pen, name=name, antialias=True)
    
    def add_data_point(self, time: float, sensor_values: list):
        self.time_data = np.append(self.time_data, time)
        
        # Update data per sensor
        for i, value in enumerate(sensor_values[:self.num_sensors]):
            self.sensor_data[i] = np.append(self.sensor_data[i], value)
        
        # Update plot lines
        for i in range(self.num_sensors):
            self.plot_lines[i].setData(self.time_data, self.sensor_data[i])
    
    def clear_data(self):
        self.time_data = np.array([])
        for i in range(self.num_sensors):
            self.sensor_data[i] = np.array([])
            self.plot_lines[i].setData([], [])


class ControlPanel(QGroupBox):
    """Modern control panel for herbal analysis"""
    
    start_clicked = Signal()
    stop_clicked = Signal()
    save_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__("Herbal Analysis Control", parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(12, 15, 12, 12)
        
        # Sample information section
        sample_layout = QVBoxLayout()
        sample_layout.addWidget(QLabel("Sample Configuration"))
        
        # Sample name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Sample:"))
        self.sample_input = QLineEdit()
        self.sample_input.setPlaceholderText("Enter sample name...")
        self.sample_input.setMinimumWidth(180)
        name_layout.addWidget(self.sample_input)
        sample_layout.addLayout(name_layout)
        
        # Herbal type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Herbal Type:"))
        self.sample_type = QComboBox()
        self.sample_type.addItems(SAMPLE_TYPES)
        self.sample_type.setMinimumWidth(140)
        type_layout.addWidget(self.sample_type)
        sample_layout.addLayout(type_layout)
        
        layout.addLayout(sample_layout)
        
        # Control buttons section
        control_layout = QVBoxLayout()
        control_layout.addWidget(QLabel("Analysis Control"))
        
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("🔬 Start Analysis")
        self.start_btn.setObjectName("startButton")
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.setMinimumWidth(130)
        self.start_btn.setMinimumHeight(35)
        self.start_btn.clicked.connect(self.start_clicked.emit)
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setObjectName("stopButton")
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.setMinimumWidth(90)
        self.stop_btn.setMinimumHeight(35)
        self.stop_btn.clicked.connect(self.stop_clicked.emit)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        
        self.save_btn = QPushButton("💾 Save Data")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setMinimumWidth(110)
        self.save_btn.setMinimumHeight(35)
        self.save_btn.clicked.connect(self.save_clicked.emit)
        button_layout.addWidget(self.save_btn)
        
        control_layout.addLayout(button_layout)
        layout.addLayout(control_layout)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def enable_start(self, enabled: bool = True):
        self.start_btn.setEnabled(enabled)
    
    def enable_stop(self, enabled: bool = True):
        self.stop_btn.setEnabled(enabled)
    
    def get_sample_info(self) -> dict:
        return {
            'name': self.sample_input.text() or "Unnamed Sample",
            'type': self.sample_type.currentText(),
            'mode': "Auto FSM" 
        }


class ConnectionPanel(QGroupBox):
    """Modern connection panel"""
    
    connect_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__("System Connection", parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(10, 12, 10, 12)
        
        # Connection settings
        settings_layout = QGridLayout()
        settings_layout.setVerticalSpacing(8)
        settings_layout.setHorizontalSpacing(12)
        
        # WiFi settings
        settings_layout.addWidget(QLabel("WiFi Data Source:"), 0, 0)
        
        wifi_layout = QHBoxLayout()
        self.ip_input = QLineEdit()
        self.ip_input.setText("127.0.0.1")
        self.ip_input.setPlaceholderText("Server IP Address")
        self.ip_input.setFixedWidth(160)
        wifi_layout.addWidget(self.ip_input)
        
        port_label = QLabel("Port:")
        port_label.setStyleSheet("color: white;")
        wifi_layout.addWidget(port_label)
        
        port_value = QLabel("8082")
        port_value.setStyleSheet("""
            color: #2E8B57; 
            font-weight: bold; 
            background: white; 
            padding: 4px 8px; 
            border-radius: 3px;
        """)
        port_value.setFixedWidth(50)
        wifi_layout.addWidget(port_value)
        
        wifi_layout.addStretch()
        settings_layout.addLayout(wifi_layout, 0, 1)
        
        # USB settings
        settings_layout.addWidget(QLabel("USB Control:"), 1, 0)
        
        usb_layout = QHBoxLayout()
        self.port_selector = QComboBox()
        self.port_selector.setFixedWidth(160)
        self.port_selector.addItems(self.get_available_ports())
        usb_layout.addWidget(self.port_selector)
        
        self.refresh_btn = QPushButton("🔄 Scan")
        self.refresh_btn.setFixedSize(70, 30)
        self.refresh_btn.setToolTip("Scan for available ports")
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.clicked.connect(self.refresh_ports)
        usb_layout.addWidget(self.refresh_btn)
        
        usb_layout.addStretch()
        settings_layout.addLayout(usb_layout, 1, 1)
        
        layout.addLayout(settings_layout)
        
        # Status and connect button
        status_layout = QHBoxLayout()
        
        status_label = QLabel("Status:")
        status_label.setStyleSheet("color: white; font-weight: bold;")
        status_layout.addWidget(status_label)
        
        self.status_indicator = StatusIndicator()
        status_layout.addWidget(self.status_indicator)
        
        status_layout.addStretch()
        
        self.connect_btn = QPushButton("🚀 Connect System")
        self.connect_btn.setFixedWidth(140)
        self.connect_btn.setMinimumHeight(35)
        self.connect_btn.setCursor(Qt.PointingHandCursor)
        self.connect_btn.clicked.connect(self.connect_clicked.emit)
        status_layout.addWidget(self.connect_btn)
        
        layout.addLayout(status_layout)
        
        self.setLayout(layout)
    
    def get_available_ports(self) -> list:
        try:
            ports = [port.device for port in serial.tools.list_ports.comports()]
            return ports if ports else ["No ports available"]
        except:
            return ["Error scanning ports"]
            
    def refresh_ports(self):
        self.port_selector.clear()
        self.port_selector.addItems(self.get_available_ports())
    
    def get_connection_settings(self) -> dict:
        return {
            'host': self.ip_input.text(),
            'port': 8082, 
            'serial_port': self.port_selector.currentText(),
            'baud_rate': 9600 
        }
    
    def set_status(self, status_text: str, color_rgb: tuple):
        self.status_indicator.set_status(status_text, color_rgb)