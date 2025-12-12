"""Main application window - Modern Layout"""

import serial
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QMessageBox, QTabWidget, QTableWidget,
    QTableWidgetItem, QLabel, QGroupBox, QSplitter,
    QFrame, QProgressBar
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont

from gui.widgets import ControlPanel, ConnectionPanel, SensorPlot
from gui.styles import STYLESHEET, STATUS_COLORS
from utils.network_comm import NetworkWorker
from config.constants import (
    APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, 
    UPDATE_INTERVAL, SENSOR_NAMES, NUM_SENSORS
)

import numpy as np
import csv
from datetime import datetime
from pathlib import Path

# Mapping state dari Arduino
STATE_NAMES = {
    0: "IDLE",
    1: "PRE-COND",
    2: "RAMP_UP",
    3: "HOLD", 
    4: "PURGE",
    5: "RECOVERY",
    6: "DONE"
}

class MainWindow(QMainWindow):
    """Main application window - Modern Layout"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize variables
        self.is_sampling = False
        self.sampling_data = {i: [] for i in range(NUM_SENSORS)}
        self.sampling_times = []
        self.current_state = "IDLE"
        self.arduino_connected = False
        self.backend_connected = False
        
        # Workers
        self.network_worker = None
        self.serial_connection = None 
        
        # Setup UI
        self.setWindowTitle(APP_NAME)
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setStyleSheet(STYLESHEET)
        
        # Create central widget with modern layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main horizontal layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left sidebar (30% width)
        left_sidebar = self.create_left_sidebar()
        left_sidebar.setMaximumWidth(400)
        main_layout.addWidget(left_sidebar)
        
        # Right content area (70% width)
        right_content = self.create_right_content()
        main_layout.addWidget(right_content)
        
        # Status bar
        self.statusBar().showMessage("AromaSense Ready - Herbal Analysis System")
        
        self.update_interval = UPDATE_INTERVAL
        
        # Setup connection
        self.setup_network_connection()
        
    def setup_network_connection(self):
        """Setup network connection to backend"""
        if self.network_worker:
            self.network_worker.stop()
            self.network_worker.wait()
        
        self.network_worker = NetworkWorker()
        self.network_worker.data_received.connect(self.on_data_received)
        self.network_worker.connection_status.connect(self.on_connection_status)
        self.network_worker.error_occurred.connect(self.handle_network_error)
        self.network_worker.arduino_status.connect(self.on_arduino_status)
        self.network_worker.start()
        
    def create_left_sidebar(self):
        """Create modern left sidebar"""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        layout = QVBoxLayout(sidebar)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 15, 10, 15)
        
        # Header
        header = QLabel("AromaSense 🌿")
        header.setStyleSheet("""
            font-size: 22px; 
            font-weight: bold; 
            color: #FFFFFF;
            padding: 15px;
            background-color: rgba(255,255,255,0.1);
            border-radius: 8px;
            text-align: center;
        """)
        layout.addWidget(header)
        
        # Connection panel
        self.connection_panel = ConnectionPanel()
        self.connection_panel.connect_clicked.connect(self.on_connect)
        layout.addWidget(self.connection_panel)
        
        # System status
        status_group = QGroupBox("System Status")
        status_layout = QVBoxLayout()
        
        # State indicator
        state_frame = QHBoxLayout()
        state_frame.addWidget(QLabel("Current State:"))
        self.state_label = QLabel("IDLE")
        self.state_label.setStyleSheet("""
            color: #FFFFFF; 
            background-color: #6c757d; 
            padding: 5px 10px; 
            border-radius: 4px;
            font-weight: bold;
        """)
        state_frame.addWidget(self.state_label)
        state_frame.addStretch()
        status_layout.addLayout(state_frame)
        
        # Progress bar
        status_layout.addWidget(QLabel("Operation Progress:"))
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        status_layout.addWidget(self.progress_bar)
        
        # Connection status
        status_layout.addWidget(QLabel("Connection Status:"))
        connection_grid = QGridLayout()
        
        connection_grid.addWidget(QLabel("Backend:"), 0, 0)
        self.backend_status_label = QLabel("● Disconnected")
        self.backend_status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        connection_grid.addWidget(self.backend_status_label, 0, 1)
        
        connection_grid.addWidget(QLabel("Arduino:"), 1, 0)
        self.arduino_status_label = QLabel("● Disconnected")
        self.arduino_status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        connection_grid.addWidget(self.arduino_status_label, 1, 1)
        
        status_layout.addLayout(connection_grid)
        
        # Sensor status
        status_layout.addWidget(QLabel("Sensor Status:"))
        sensor_grid = QGridLayout()
        self.sensor_status_labels = {}
        
        # Create 2 columns for sensor status
        for i in range(NUM_SENSORS):
            row = i // 2
            col = (i % 2) * 2
            name = SENSOR_NAMES[i] if i < len(SENSOR_NAMES) else f"Sensor {i+1}"
            sensor_grid.addWidget(QLabel(f"• {name}:"), row, col)
            status_label = QLabel("● Ready")
            status_label.setStyleSheet("color: #90EE90; font-weight: bold;")
            sensor_grid.addWidget(status_label, row, col + 1)
            self.sensor_status_labels[i] = status_label
        
        status_layout.addLayout(sensor_grid)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Quick actions
        quick_group = QGroupBox("Quick Actions")
        quick_layout = QVBoxLayout()
        
        self.export_btn = QPushButton("📤 Quick Export CSV")
        self.export_btn.clicked.connect(self.on_export_csv)
        quick_layout.addWidget(self.export_btn)
        
        self.clear_btn = QPushButton("🗑️ Clear All Data")
        self.clear_btn.clicked.connect(self.on_clear_plot)
        quick_layout.addWidget(self.clear_btn)
        
        quick_group.setLayout(quick_layout)
        layout.addWidget(quick_group)
        
        layout.addStretch()
        return sidebar
        
    def create_right_content(self):
        """Create modern right content area"""
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Control panel
        self.control_panel = ControlPanel()
        self.control_panel.start_clicked.connect(self.on_start_sampling)
        self.control_panel.stop_clicked.connect(self.on_stop_sampling)
        self.control_panel.save_clicked.connect(self.on_save_data)
        layout.addWidget(self.control_panel)
        
        # Create splitter for plot and data
        splitter = QSplitter(Qt.Vertical)
        
        # Top: Plot
        plot_group = QGroupBox("Real-Time Herbal Analysis")
        plot_layout = QVBoxLayout()
        self.plot_widget = SensorPlot("Herbal Volatile Organic Compounds")
        plot_layout.addWidget(self.plot_widget)
        plot_group.setLayout(plot_layout)
        splitter.addWidget(plot_group)
        
        # Bottom: Data tabs
        data_tabs = QTabWidget()
        
        # Tab 1: Statistics
        stats_tab = QWidget()
        stats_layout = QVBoxLayout()
        self.stats_table = QTableWidget(NUM_SENSORS, 5)
        self.stats_table.setHorizontalHeaderLabels([
            "Sensor", "Min", "Max", "Mean", "Std Dev"
        ])
        for i in range(5):
            self.stats_table.setColumnWidth(i, 120)
        self.populate_stats_table()
        stats_layout.addWidget(self.stats_table)
        stats_tab.setLayout(stats_layout)
        data_tabs.addTab(stats_tab, "📊 Statistics")
        
        # Tab 2: Sample Info
        info_tab = QWidget()
        info_layout = QVBoxLayout()
        self.info_table = QTableWidget(6, 2)
        self.info_table.setHorizontalHeaderLabels(["Parameter", "Value"])
        self.info_table.setColumnWidth(0, 150)
        self.info_table.setColumnWidth(1, 200)
        self.populate_info_table()
        info_layout.addWidget(self.info_table)
        info_tab.setLayout(info_layout)
        data_tabs.addTab(info_tab, "📋 Sample Info")
        
        splitter.addWidget(data_tabs)
        splitter.setSizes([500, 200])
        
        layout.addWidget(splitter)
        return content
        
    def populate_info_table(self):
        info = {
            "Sample Name": "Not Set",
            "Herbal Type": "Not Selected", 
            "Operation Mode": "Auto FSM",
            "Data Points": "0",
            "Duration": "0.00 s",
            "Sample Quality": "Pending"
        }
        for row, (key, value) in enumerate(info.items()):
            self.info_table.setItem(row, 0, QTableWidgetItem(key))
            self.info_table.setItem(row, 1, QTableWidgetItem(value))
    
    def populate_stats_table(self):
        for row in range(NUM_SENSORS):
            sensor_name = SENSOR_NAMES[row] if row < len(SENSOR_NAMES) else f"Sensor {row+1}"
            self.stats_table.setItem(row, 0, QTableWidgetItem(sensor_name))
            for col in range(1, 5):
                self.stats_table.setItem(row, col, QTableWidgetItem("0.00"))
    
    def update_system_status(self, state: str, progress: int = 0):
        """Update system status display"""
        self.current_state = state
        self.state_label.setText(state)
        
        # Update color based on state
        color_map = {
            "IDLE": "#6c757d",
            "PRE-COND": "#17a2b8", 
            "RAMP_UP": "#ffc107",
            "HOLD": "#28a745",
            "PURGE": "#fd7e14",
            "RECOVERY": "#20c997",
            "DONE": "#6610f2"
        }
        color = color_map.get(state, "#6c757d")
        self.state_label.setStyleSheet(f"""
            color: #FFFFFF; 
            background-color: {color}; 
            padding: 5px 10px; 
            border-radius: 4px;
            font-weight: bold;
        """)
        
        self.progress_bar.setValue(progress)
    
    def on_connect(self):
        """Handle connection button click"""
        try:
            settings = self.connection_panel.get_connection_settings()
            
            # Stop existing connection
            if self.network_worker:
                self.network_worker.stop()
                self.network_worker.wait()
                self.network_worker = None

            self.statusBar().showMessage(f"🔗 Connecting to {settings['host']}...")
            self.connection_panel.set_status("Connecting...", STATUS_COLORS['connecting'])
            
            self.connection_panel.connect_btn.setEnabled(False)
            self.connection_panel.connect_btn.setText("Connecting...")
            
            # Create new network worker with settings
            self.network_worker = NetworkWorker(host=settings['host'], port=settings['port'])
            self.network_worker.data_received.connect(self.on_data_received)
            self.network_worker.connection_status.connect(self.on_connection_status)
            self.network_worker.error_occurred.connect(self.handle_network_error)
            self.network_worker.arduino_status.connect(self.on_arduino_status)
            self.network_worker.start()

            # Setup serial connection for motor control
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()
                
            if settings['serial_port'] != "No ports available" and settings['serial_port'] != "No Ports":
                try:
                    self.serial_connection = serial.Serial(
                        settings['serial_port'], 
                        settings['baud_rate'], 
                        timeout=1
                    )
                    print(f"✅ Serial Connected: {settings['serial_port']}")
                except Exception as e:
                    print(f"⚠️ Serial connection failed: {e}")
                    # Continue without serial - it's optional for motor control
            else:
                print("⚠️ No Serial Port selected. Motor control will not work!")

        except Exception as e:
            self.handle_network_error(f"Connection setup failed: {str(e)}")

    def handle_network_error(self, msg: str):
        """Handle network errors"""
        print(f"❌ Network Error: {msg}")
        self.statusBar().showMessage(f"❌ {msg}")
        self.connection_panel.set_status("Error", STATUS_COLORS['error'])
        self.connection_panel.connect_btn.setEnabled(True)
        self.connection_panel.connect_btn.setText("Connect System")

    def on_connection_status(self, connected: bool):
        """Handle backend connection status"""
        self.backend_connected = connected
        if connected:
            self.connection_panel.set_status("Backend Connected", STATUS_COLORS['connected'])
            self.backend_status_label.setText("● Connected")
            self.backend_status_label.setStyleSheet("color: #90EE90; font-weight: bold;")
            self.statusBar().showMessage("✅ Backend Connected - Waiting for Arduino...")
            self.connection_panel.connect_btn.setText("Connected")
            self.connection_panel.connect_btn.setEnabled(False)
        else:
            self.connection_panel.set_status("Disconnected", STATUS_COLORS['disconnected'])
            self.backend_status_label.setText("● Disconnected")
            self.backend_status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
            self.control_panel.enable_start(False)
            self.statusBar().showMessage("❌ Disconnected from Backend")
            self.connection_panel.connect_btn.setText("Connect System")
            self.connection_panel.connect_btn.setEnabled(True)

    def on_arduino_status(self, connected: bool):
        """Handle Arduino connection status"""
        self.arduino_connected = connected
        if connected:
            self.arduino_status_label.setText("● Connected")
            self.arduino_status_label.setStyleSheet("color: #90EE90; font-weight: bold;")
            self.control_panel.enable_start(True)
            self.statusBar().showMessage("✅ Arduino Connected - Ready for Herbal Analysis")
            
            # Update sensor status
            for i in range(NUM_SENSORS):
                self.sensor_status_labels[i].setText("● Active")
                self.sensor_status_labels[i].setStyleSheet("color: #90EE90; font-weight: bold;")
        else:
            self.arduino_status_label.setText("● Disconnected")
            self.arduino_status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
            self.control_panel.enable_start(False)
            self.statusBar().showMessage("❌ Arduino Disconnected - Check Connection")
            
            # Update sensor status
            for i in range(NUM_SENSORS):
                self.sensor_status_labels[i].setText("● Offline")
                self.sensor_status_labels[i].setStyleSheet("color: #ff6b6b; font-weight: bold;")

    def send_arduino_command(self, command: str):
        """Send command to Arduino via backend"""
        if self.network_worker and self.backend_connected:
            self.network_worker.send_command(command)
            print(f"📤 Command sent to Arduino: {command}")
        else:
            print(f"⚠️ Cannot send command: Backend not connected")

    def on_start_sampling(self):
        """Handle start sampling"""
        if not self.arduino_connected:
            QMessageBox.warning(self, "Warning", "Arduino not connected! Please check connection.")
            return
            
        sample_info = self.control_panel.get_sample_info()
        if not sample_info['name'] or sample_info['name'] == "Unnamed Sample":
            QMessageBox.warning(self, "Warning", "Please enter a sample name!")
            return
        
        # Update info table
        self.info_table.setItem(0, 1, QTableWidgetItem(sample_info['name']))
        self.info_table.setItem(1, 1, QTableWidgetItem(sample_info['type']))
        self.info_table.setItem(5, 1, QTableWidgetItem("Analyzing..."))
        
        # Reset data
        self.sampling_data = {i: [] for i in range(NUM_SENSORS)}
        self.sampling_times = []
        self.plot_widget.clear_data()
        
        self.is_sampling = True
        self.start_time = 0
        
        self.control_panel.enable_start(False)
        self.control_panel.enable_stop(True)
        
        # Update system status
        self.update_system_status("PRE-COND", 10)
        
        # Send start command to Arduino
        self.send_arduino_command("START_SAMPLING")
        
        self.statusBar().showMessage("🔬 Herbal Analysis Started - Sampling in Progress")
        self.connection_panel.set_status("Sampling...", STATUS_COLORS['sampling'])
    
    def on_data_received(self, data: dict):
        """Handle data received from Backend"""
        try:
            # Extract sensor values from JSON data
            sensor_values = [
                float(data.get('no2', 0.0)),
                float(data.get('eth', 0.0)), 
                float(data.get('voc', 0.0)),
                float(data.get('co', 0.0)),
                float(data.get('co_mics', 0.0)),
                float(data.get('eth_mics', 0.0)),
                float(data.get('voc_mics', 0.0))
            ]
            
            state_idx = int(data.get('state', 0))
            state_name = STATE_NAMES.get(state_idx, "UNKNOWN")
            level = data.get('level', 0)
            
            # Update system status
            progress = int((state_idx / 6) * 100) if state_idx <= 6 else 100
            self.update_system_status(state_name, progress)
            
            # Update status bar
            self.statusBar().showMessage(f"🔬 {state_name} | Level: {level+1}/5 | Points: {len(self.sampling_times)}")
            
            if self.is_sampling:
                self.process_new_data(sensor_values)
                
                # Auto-stop when done
                if state_idx == 6: # DONE
                    self.on_stop_sampling()
                    self.info_table.setItem(5, 1, QTableWidgetItem("✅ Excellent"))
                    QMessageBox.information(self, "Analysis Complete", 
                                         "Herbal analysis completed successfully!\n\n"
                                         f"Sample: {self.control_panel.get_sample_info()['name']}\n"
                                         f"Data Points: {len(self.sampling_times)}")
                    
        except Exception as e:
            print(f"❌ Error parsing data: {e}")

    def process_new_data(self, sensor_values: list):
        """Process new sensor data"""
        if not self.sampling_times:
            self.start_time = 0.0
        else:
            self.start_time += self.update_interval / 1000.0
            
        self.plot_widget.add_data_point(self.start_time, sensor_values)
        
        # Save data
        for i, val in enumerate(sensor_values[:NUM_SENSORS]):
            self.sampling_data[i].append(val)
        self.sampling_times.append(self.start_time)
        
        # Update info table
        self.info_table.setItem(3, 1, QTableWidgetItem(str(len(self.sampling_times))))
        self.info_table.setItem(4, 1, QTableWidgetItem(f"{self.start_time:.2f} s"))
        
        self.update_statistics()

    def on_stop_sampling(self):
        """Handle stop sampling"""
        self.is_sampling = False
        
        # Send stop command to Arduino
        self.send_arduino_command("STOP_SAMPLING")
        
        self.control_panel.enable_start(True)
        self.control_panel.enable_stop(False)
        self.connection_panel.set_status("Connected", STATUS_COLORS['connected'])
        self.update_system_status("IDLE", 0)
        
        points_count = len(self.sampling_times)
        self.statusBar().showMessage(f"⏹️ Analysis stopped. Collected {points_count} data points.")
    
    def update_statistics(self):
        """Update statistics table"""
        for sensor_id in range(NUM_SENSORS):
            if self.sampling_data[sensor_id]:
                data = np.array(self.sampling_data[sensor_id])
                self.stats_table.setItem(sensor_id, 1, QTableWidgetItem(f"{data.min():.2f}"))
                self.stats_table.setItem(sensor_id, 2, QTableWidgetItem(f"{data.max():.2f}"))
                self.stats_table.setItem(sensor_id, 3, QTableWidgetItem(f"{data.mean():.2f}"))
                self.stats_table.setItem(sensor_id, 4, QTableWidgetItem(f"{data.std():.2f}"))
    
    def on_save_data(self):
        """Save data to CSV file"""
        if not self.sampling_times:
            QMessageBox.warning(self, "Warning", "No herbal data to save!")
            return
        
        sample_info = self.control_panel.get_sample_info()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/{sample_info['name'].replace(' ', '_')}_{timestamp}.csv"
        
        try:
            Path("data").mkdir(exist_ok=True)
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["AromaSense Herbal Analysis Data"])
                writer.writerow(["Sample Name", sample_info['name']])
                writer.writerow(["Herbal Type", sample_info['type']])
                writer.writerow(["Export Date", datetime.now().isoformat()])
                writer.writerow(["Analysis Mode", "Auto FSM"])
                writer.writerow(["Total Data Points", len(self.sampling_times)])
                writer.writerow(["Final Duration", f"{self.start_time:.2f} s"])
                writer.writerow([])
                headers = ["Time (s)"] + [SENSOR_NAMES[i] for i in range(NUM_SENSORS)]
                writer.writerow(headers)
                for t_idx, t in enumerate(self.sampling_times):
                    row = [f"{t:.3f}"]
                    for s_idx in range(NUM_SENSORS):
                        if t_idx < len(self.sampling_data[s_idx]):
                            row.append(f"{self.sampling_data[s_idx][t_idx]:.2f}")
                        else:
                            row.append("0")
                    writer.writerow(row)
            QMessageBox.information(self, "Export Successful", f"Herbal data exported to:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to save data: {str(e)}")
    
    def on_clear_plot(self):
        """Clear all plot data"""
        reply = QMessageBox.question(self, "Confirm Clear", 
                                   "Clear all herbal analysis data?\nThis action cannot be undone.", 
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.plot_widget.clear_data()
            self.sampling_data = {i: [] for i in range(NUM_SENSORS)}
            self.sampling_times = []
            self.populate_info_table()
            self.populate_stats_table()
            self.update_system_status("IDLE", 0)
            self.statusBar().showMessage("✅ All data cleared - Ready for new analysis")
    
    def on_export_csv(self):
        """Quick export CSV"""
        self.on_save_data()
    
    def closeEvent(self, event):
        """Handle application close"""
        if self.is_sampling:
            reply = QMessageBox.question(self, "Confirm Exit", 
                                       "Herbal analysis in progress.\nExit anyway?", 
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                event.ignore()
                return
                
        if self.network_worker:
            self.network_worker.stop()
            self.network_worker.wait()
            
        if self.serial_connection:
            self.serial_connection.close()
            
        event.accept()