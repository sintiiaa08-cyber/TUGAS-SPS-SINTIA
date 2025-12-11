# 💻 **Electronic Nose (E-Nose) — Integrated Smart Gas Sensing System**
### *Course Project — Signal Processing Systems, Department of Instrumentation Engineering, Institut Teknologi Sepuluh Nopember (ITS)*

---

## 👩‍💻 **Prepared by**
* **Sintia Ompusunggu** (2042241113)
* **galen zahid wajendra** (2042241044)
* **Rijal Difaul Haq** (2042241097)
   
Department of Instrumentation Engineering  
Institut Teknologi Sepuluh Nopember

---

# 📘 **Project Overview**
This project presents the development of a fully integrated **Electronic Nose (E-Nose)** system designed for multi-gas sensing, real-time acquisition, and structured time-series data management. The system implements a modular architecture consisting of:

1. **Frontend GUI (Python + Qt):**  
   Provides real-time visualization, sampling control, graphical plotting, and dataset export.

2. **Backend TCP Server (Rust):**  
   Serves as a high-performance communication bridge between Arduino hardware, the database, and the GUI.

3. **Time-Series Database (InfluxDB via Docker):**  
   Ensures consistent, lossless, long-term storage of sensor measurements.

4. **Embedded System (Arduino Uno R4 WiFi):**  
   Performs gas sensor readings and controls actuators (fan & pump) to execute sampling phases.

The platform is optimized for reliability, deterministic timing behavior, and seamless integration with downstream AI/ML pipelines (e.g., Edge Impulse).

---

# 🧩 **System Architecture**

```
┌────────────────────────┐
│     Frontend GUI       │  Python + Qt
│  (Visualization & Control) 
└─────────────┬──────────┘
              │ TCP
┌─────────────▼──────────┐
│     Backend Server      │  Rust
│   (Data Communication)  │
└─────────────┬──────────┘
      InfluxDB│Write API
┌─────────────▼──────────┐
│    Time-Series DB       │  Docker (InfluxDB)
└─────────────┬──────────┘
              │ UART/WiFi
┌─────────────▼──────────┐
│      Arduino R4         │  Embedded System
│ (Gas Sensors + Actuator)│
└────────────────────────┘
```

---

# ⚙️ **System Requirements**

Please ensure the following tools are installed:

- ✔ **Docker Desktop** — Required for running InfluxDB  
- ✔ **Rust Toolchain** — Required to compile and run the Backend  
- ✔ **Python 3.8+** — Required for the GUI Frontend  
- ✔ **Gnuplot** — Required for high-resolution data visualization  
- ✔ **Arduino IDE** — Required for uploading the E-Nose firmware  

> **Important:** During Gnuplot installation, enable **“Add application directory to PATH”**.

---

# 🛠️ **Setup & Installation (One-Time Only)**

## **1️⃣ Initialize Database (InfluxDB with Docker)**

From the project root directory, run:

```bash
docker-compose up -d
```

Ensure the container appears as **Running** in Docker Desktop.

---

## **2️⃣ Build Backend (Rust)**

```bash
cd backend
cargo build
```

The first build will fetch all required dependencies.

---

## **3️⃣ Configure Frontend (Python Virtual Environment)**

### Windows
```bash
cd frontend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Linux / macOS
```bash
cd frontend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## **4️⃣ Upload Firmware to Arduino**

1. Open `embedded/main.ino` in Arduino IDE  
2. Modify this line:

```cpp
const char* RUST_IP = "...";
```

Replace with the IPv4 address of your laptop (`ipconfig`).  
3. Upload to **Arduino Uno R4 WiFi**.

---

# ▶️ **Running the System (Performed Each Session)**

Three terminals are required.

---

## **🖥️ Terminal 1 — Backend (Rust)**

```bash
cd backend
cargo run
```

Backend ready message:

```
Listening for Arduino on port 8081...
```

---

## **🖥️ Terminal 2 — Frontend GUI**

```bash
cd frontend
venv\Scripts\activate
python main.py
```

---

## **🔌 Terminal 3 — Hardware (Arduino)**

- Connect Arduino to USB/power  
- Ensure both Arduino and laptop are on the **same WiFi network**  

---

# 🎮 **Application Usage Guide**

## **A. Data Sampling Procedure**

1. Enter **Sample Name**  
2. Choose **Sample Category**  
3. Press **▶ Start**  
4. The system automatically performs sequential phases:
   - Pre-Condition  
   - Ramp-Up  
   - Hold  
   - Purge  
5. Real-time data will be displayed on the GUI.

---

## **B. Save Data & Visualization**

Press **💾 Save Data** → A `.csv` file is stored in:

```
frontend/data/
```

A prompt will appear:
> **“Open graph in Gnuplot?”**

Selecting **Yes** opens the high-resolution graph automatically.

---

## **C. Export for Edge Impulse (AI/ML)**

1. Click **🚀 Export to Edge Impulse**  
2. A dataset `.json` file is generated  
3. The browser automatically opens Edge Impulse Studio  
4. Upload the JSON dataset to begin the ML pipeline  

---

# 📊 **Monitoring Database (InfluxDB UI)**

Access InfluxDB dashboard:

```
http://localhost:8086
```

Default credentials:

- **Username:** admin  
- **Password:** adminpassword  

Navigate to:

**Data Explorer → Bucket: electronic_nose → sensor_reading → Submit**

---

# 🛠️ **Troubleshooting**

### ❗ 1. Python: `ModuleNotFoundError`
Cause: Virtual environment not activated  
Solution:

```bash
venv\Scripts\activate
```

---

### ❗ 2. Gnuplot Not Detected  
Reinstall and check **Add to PATH**.

---

### ❗ 3. InfluxDB Login Error (401 Unauthorized)
Reset database:

```bash
docker-compose down -v
docker-compose up -d
```

---

### ❗ 4. Real-Time Graph Not Updating
Verify:
- Arduino Serial Monitor shows `"Connected to Backend"`  
- Laptop IP changed? → Update IP in `main.ino`  

---

# 📁 **Project Directory Structure**

```
project/
│── backend/            # Rust TCP Server
│── frontend/           # Qt-based Python GUI
│   ├── data/           # Stored CSV outputs
│   ├── assets/         # Icons & resources
│   └── main.py
│── embedded/           # Arduino Firmware
│── docker-compose.yml
└── README.md
```

---

# 🏁 **Project Status**
- ✔ Fully operational  
- ✔ Stable and deterministic  
- ✔ Integrated end-to-end  
- ✔ Ready for academic presentation and demonstration  
- ✔ Supports AI/ML workflows  

---

# 🎓 **Application Context**
This platform is suitable for:
- Analysis of volatile compounds  
- Aroma classification via machine learning  
- Multi-gas research environments  
- Real-time laboratory instrumentation  

---

