use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::net::TcpListener;
use tokio::sync::{broadcast, Mutex};
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader};
use std::collections::HashMap;

// Struktur data Sensor
#[derive(Debug, Serialize, Deserialize, Clone)]
struct SensorData {
    timestamp: DateTime<Utc>,
    no2: f64,
    eth: f64,
    voc: f64,
    co: f64,
    co_mics: f64,
    eth_mics: f64,
    voc_mics: f64,
    state: i32,
    level: i32,
}

#[derive(Debug, Clone)]
struct ConnectionState {
    pub arduino_connected: bool,
    pub frontend_connected: bool,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("🚀 Starting E-Nose Backend System (Bidirectional - No DB)...");

    // Channel untuk komunikasi
    let (tx_sensor, _rx_sensor) = broadcast::channel::<String>(100);
    let (tx_cmd, _rx_cmd) = broadcast::channel::<String>(100);
    
    // State management
    let connection_state = Arc::new(Mutex::new(ConnectionState {
        arduino_connected: false,
        frontend_connected: false,
    }));

    let arduino_listener = TcpListener::bind("0.0.0.0:8081").await?;
    let frontend_listener = TcpListener::bind("0.0.0.0:8082").await?;

    println!("📡 Listening for Arduino on port 8081");
    println!("💻 Listening for Frontend on port 8082");

    // Clone resources untuk task
    let tx_sensor_frontend = tx_sensor.clone();
    let tx_cmd_arduino = tx_cmd.clone();
    let state_clone = connection_state.clone();

    // FRONTEND HANDLER
    tokio::spawn(async move {
        let mut frontend_connections = HashMap::new();
        
        loop {
            match frontend_listener.accept().await {
                Ok((socket, addr)) => {
                    println!("💻 Frontend Connected: {}", addr);
                    
                    // Update connection state
                    {
                        let mut state = state_clone.lock().await;
                        state.frontend_connected = true;
                    }

                    let mut tx_sensor = tx_sensor_frontend.subscribe(); // <- TAMBAH 'mut' DI SINI
                    let tx_cmd = tx_cmd_arduino.clone();
                    let state = state_clone.clone();

                    let connection_id = addr.to_string();
                    
                    let handle = tokio::spawn(async move {
                        let (reader, mut writer) = socket.into_split();
                        let mut line_reader = BufReader::new(reader).lines();

                        // Send initial connection status to frontend
                        let connection_msg = serde_json::json!({
                            "type": "connection_status",
                            "arduino_connected": false,
                            "backend_connected": true
                        });
                        
                        if let Ok(msg) = serde_json::to_string(&connection_msg) {
                            let _ = writer.write_all(msg.as_bytes()).await;
                            let _ = writer.write_all(b"\n").await;
                        }

                        loop {
                            tokio::select! {
                                // 1. Kirim Data Sensor ke Frontend
                                Ok(msg) = tx_sensor.recv() => { // <- SEKARID 'recv()' BISA DIPANGGIL
                                    if writer.write_all(msg.as_bytes()).await.is_err() || writer.write_all(b"\n").await.is_err() {
                                        break;
                                    }
                                }
                                // 2. Baca Command dari Frontend
                                Ok(Some(line)) = line_reader.next_line() => {
                                    println!("🔧 Command from UI: {}", line);
                                    if line.starts_with("START_SAMPLING") || line.starts_with("STOP_SAMPLING") {
                                        let _ = tx_cmd.send(line);
                                    }
                                }
                                else => break,
                            }
                        }
                        
                        // Update connection state on disconnect
                        {
                            let mut state = state.lock().await;
                            state.frontend_connected = false;
                        }
                        println!("💻 Frontend Disconnected: {}", addr);
                    });
                    
                    frontend_connections.insert(connection_id, handle);
                }
                Err(e) => {
                    eprintln!("❌ Error accepting frontend connection: {}", e);
                }
            }
        }
    });

    // ARDUINO HANDLER
    let tx_sensor_arduino = tx_sensor.clone();
    let state_arduino = connection_state.clone();
    
    loop {
        match arduino_listener.accept().await {
            Ok((socket, addr)) => {
                println!("🔌 Arduino Connected: {}", addr);
                
                // Update connection state
                {
                    let mut state = state_arduino.lock().await;
                    state.arduino_connected = true;
                }

                let tx_sensor = tx_sensor_arduino.clone();
                let mut rx_cmd = tx_cmd.subscribe(); // <- 'mut' sudah ada di sini
                let state = state_arduino.clone();

                tokio::spawn(async move {
                    let (reader, mut writer) = socket.into_split();
                    let mut line_reader = BufReader::new(reader).lines();

                    // Send connection status to all frontends
                    let connection_msg = serde_json::json!({
                        "type": "connection_status",
                        "arduino_connected": true,
                        "backend_connected": true
                    });
                    
                    if let Ok(msg) = serde_json::to_string(&connection_msg) {
                        let _ = tx_sensor.send(msg);
                    }

                    loop {
                        tokio::select! {
                            // 1. Baca Data Sensor dari Arduino
                            Ok(Some(line)) = line_reader.next_line() => {
                                if line.starts_with("SENSOR:") {
                                    process_sensor_data(&line, &tx_sensor).await;
                                } else if line.contains("CONNECTED") || line.contains("Connected") {
                                    println!("✅ Arduino ready: {}", line);
                                }
                            }
                            // 2. Kirim Command ke Arduino (Jika ada dari UI)
                            Ok(cmd) = rx_cmd.recv() => {
                                println!("📤 Forwarding to Arduino: {}", cmd);
                                if writer.write_all(cmd.as_bytes()).await.is_err() || writer.write_all(b"\n").await.is_err() {
                                    break;
                                }
                            }
                            else => break,
                        }
                    }
                    
                    // Update connection state on disconnect
                    {
                        let mut state = state.lock().await;
                        state.arduino_connected = false;
                    }
                    
                    // Notify frontends about disconnection
                    let disconnect_msg = serde_json::json!({
                        "type": "connection_status", 
                        "arduino_connected": false,
                        "backend_connected": true
                    });
                    
                    if let Ok(msg) = serde_json::to_string(&disconnect_msg) {
                        let _ = tx_sensor.send(msg);
                    }
                    
                    println!("🔌 Arduino Disconnected: {}", addr);
                });
            }
            Err(e) => {
                eprintln!("❌ Error accepting arduino connection: {}", e);
            }
        }
    }
}

async fn process_sensor_data(line: &str, tx: &broadcast::Sender<String>) {
    let content = line.trim_start_matches("SENSOR:");
    let parts: Vec<&str> = content.split(',').collect();

    if parts.len() >= 9 {
        let data = SensorData {
            timestamp: Utc::now(),
            no2: parts[0].parse().unwrap_or(-1.0),
            eth: parts[1].parse().unwrap_or(-1.0),
            voc: parts[2].parse().unwrap_or(-1.0),
            co: parts[3].parse().unwrap_or(-1.0),
            co_mics: parts[4].parse().unwrap_or(0.0),
            eth_mics: parts[5].parse().unwrap_or(0.0),
            voc_mics: parts[6].parse().unwrap_or(0.0),
            state: parts[7].parse().unwrap_or(0),
            level: parts[8].parse().unwrap_or(0),
        };

        // Kirim data sensor ke Frontend
        if let Ok(json_str) = serde_json::to_string(&data) {
            let _ = tx.send(json_str);
            println!("📊 Sensor data sent to GUI");
        }
    } else {
        eprintln!("⚠️ Invalid sensor data format: {}", line);
    }
}