"""Enhanced Network Communication for AromaSense"""
import socket
import threading
import json
import time
from PySide6.QtCore import QThread, Signal
from typing import Optional

class NetworkWorker(QThread):
    """Enhanced network worker with bidirectional communication"""
    
    data_received = Signal(dict)
    connection_status = Signal(bool)
    error_occurred = Signal(str)
    arduino_status = Signal(bool)
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8082):
        super().__init__()
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.running = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        
    def run(self):
        """Main connection loop"""
        self.running = True
        
        while self.running and self.reconnect_attempts < self.max_reconnect_attempts:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(5.0)
                print(f"🔗 Attempting to connect to {self.host}:{self.port}...")
                self.socket.connect((self.host, self.port))
                
                print(f"✅ Connected to backend at {self.host}:{self.port}")
                self.connection_status.emit(True)
                self.reconnect_attempts = 0
                
                # Start listening for data
                self._listen_for_data()
                
            except socket.timeout:
                error_msg = "Connection timeout - Backend not responding"
                self.error_occurred.emit(error_msg)
                print(f"❌ {error_msg}")
            except ConnectionRefusedError:
                error_msg = f"Backend refused connection at {self.host}:{self.port}"
                self.error_occurred.emit(error_msg)
                print(f"❌ {error_msg}")
            except Exception as e:
                error_msg = f"Connection error: {str(e)}"
                self.error_occurred.emit(error_msg)
                print(f"❌ {error_msg}")
            
            # Reconnect logic
            if self.running:
                self.reconnect_attempts += 1
                if self.reconnect_attempts < self.max_reconnect_attempts:
                    print(f"🔄 Reconnecting... attempt {self.reconnect_attempts}")
                    time.sleep(2)
        
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            final_error = "Max reconnection attempts reached - Check backend server"
            self.error_occurred.emit(final_error)
            print(f"❌ {final_error}")
            
        self.connection_status.emit(False)
        self.running = False
    
    def _listen_for_data(self):
        """Listen for incoming data from backend"""
        buffer = ""
        self.socket.settimeout(1.0)  # Shorter timeout for listening
        
        while self.running and self.socket:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    print("⚠️ Backend disconnected")
                    break
                    
                buffer += data
                lines = buffer.split('\n')
                buffer = lines[-1]  # Keep incomplete line in buffer
                
                for line in lines[:-1]:
                    line = line.strip()
                    if line:
                        self._process_received_data(line)
                        
            except socket.timeout:
                continue  # Timeout is normal, just continue listening
            except Exception as e:
                if self.running:
                    error_msg = f"Data receive error: {str(e)}"
                    self.error_occurred.emit(error_msg)
                    print(f"❌ {error_msg}")
                break
    
    def _process_received_data(self, data: str):
        """Process received JSON data"""
        try:
            json_data = json.loads(data)
            
            # Handle connection status messages
            if isinstance(json_data, dict) and json_data.get('type') == 'connection_status':
                arduino_connected = json_data.get('arduino_connected', False)
                print(f"🔌 Arduino connection status: {arduino_connected}")
                self.arduino_status.emit(arduino_connected)
                return
                
            # Handle sensor data (regular data without 'type' field)
            if isinstance(json_data, dict) and 'no2' in json_data:
                self.data_received.emit(json_data)
            
        except json.JSONDecodeError:
            print(f"⚠️ Invalid JSON received: {data}")
        except Exception as e:
            print(f"❌ Error processing data: {e}")
    
    def send_command(self, command: str):
        """Send command to backend"""
        if self.socket and self.running:
            try:
                full_command = f"{command}\n"
                self.socket.sendall(full_command.encode('utf-8'))
                print(f"📤 Sent command: {command}")
            except Exception as e:
                error_msg = f"Send command error: {str(e)}"
                self.error_occurred.emit(error_msg)
                print(f"❌ {error_msg}")
        else:
            print(f"⚠️ Cannot send command: Socket not connected")
    
    def stop(self):
        """Stop the network worker"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.wait(2000)  # Wait for thread to finish