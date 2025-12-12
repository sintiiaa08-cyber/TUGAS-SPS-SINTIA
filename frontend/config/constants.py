"""Application constants and configuration"""

# Application settings
APP_NAME = "AromaSense - Herbal Analysis System"
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
UPDATE_INTERVAL = 250  # milliseconds

# Sensor configuration
NUM_SENSORS = 7
SENSOR_NAMES = [
    "NO2 Sensor",          # ← PERBAIKAN: '₂' menjadi '2'
    "Ethanol Sensor", 
    "VOC Sensor", 
    "CO Sensor",
    "MiCS CO",
    "MiCS Ethanol", 
    "MiCS VOC"
]

# Sample types
SAMPLE_TYPES = [
    "jahe",
    "kencur", 
    "kunyit",
    "lengkuas"
]

# Plot colors
PLOT_COLORS = [
    '#FF6B6B',  # Red
    '#4ECDC4',  # Teal
    '#45B7D1',  # Blue
    '#96CEB4',  # Green
    '#FFEAA7',  # Yellow
    '#DDA0DD',  # Plum
    '#98D8C8'   # Mint
]

# Data settings
MAX_PLOT_POINTS = 1000
DATA_SAVE_PATH = "data/"