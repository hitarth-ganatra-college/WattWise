# Renewable Energy Predictive Maintenance Platform (PdM)

A scalable, full-stack Predictive Maintenance (PdM) platform designed for Solar PV arrays and Wind Turbines. The system ingests high-frequency SCADA telemetry, calculates ML thermal residual anomalies using Random Forest Regressors, evaluates engineering physics metrics (thermal inertia, 3-phase current imbalance, IEC 61724 solar performance ratio), estimates financial downtime losses, and visualizes fleet status on an interactive 3D Globe.

---

## Architecture Overview

The system operates across a 4-tier modular architecture:

1. **IoT Edge Simulator (`simulator/`)**: Pushes SCADA telemetry streams for Wind Turbines (from Kaggle Wind SCADA datasets) and Solar Panels (synthetic solar physics engine with soiling & diode faults).
2. **Data Layer (`MongoDB`)**: Stores raw telemetry streams, asset registries, dynamic commands, and ML anomaly scores in `predictive_maintenance`.
3. **ML & Physics Engine (`ml_engine/` & `business_logic/`)**: 
   - Evaluates 5 trained Random Forest Regressors (NBM) to predict expected baseline temperatures & solar power output.
   - Computes Asset Health Index (AHI 0-100), Remaining Useful Life (RUL hours), 3-phase current imbalance ($\Delta I$), Bearing-to-Oil temperature deltas ($\Delta T$), and financial Risk Priority Numbers (RPN).
4. **Presentation Dashboard (`dashboard/`)**: A clean enterprise Streamlit light dashboard featuring an interactive 3D Globe map with asset focus zoom, component diagnostics, maintenance queue, financial analytics, and a technician command center.

---

## Project Structure

```
HackOut/
├── config.py                 # Central platform configurations & regional modifiers
├── requirements.txt           # Python dependency specifications
├── README.md                  # Project documentation & execution guide
├── .gitignore                 # Version control exclusion rules
├── backend/                   # FastAPI / REST endpoints (optional API access)
│   └── api.py
├── business_logic/            # Physics & Financial calculation modules
│   ├── health_index.py        # AHI, RUL estimation, and degradation velocity
│   └── financial_engine.py    # Revenue loss, repair costs, RPN, & curtailment guards
├── dashboard/                 # Streamlit presentation UI & theme
│   ├── app.py                 # Main Streamlit application
│   └── glass_theme.py         # Crisp enterprise light CSS design system
├── ml_engine/                 # Machine Learning pipeline
│   ├── train_wind_nbm.py      # Random Forest trainer for wind turbine components
│   ├── train_solar_nbm.py     # Random Forest trainer for solar panel AC output
│   └── anomaly_scorer.py      # Background worker for continuous anomaly scoring
├── models/                    # Saved joblib model artifacts
└── simulator/                 # IoT SCADA telemetry stream engine
    ├── base_asset.py          # Base asset state and command handler
    ├── wind_turbine.py        # Wind SCADA dataset replay engine
    ├── solar_panel.py         # Solar irradiance physics simulator
    ├── fleet_manager.py       # Fleet orchestration manager
    └── run_simulation.py      # Simulation launcher script
```

---

## Prerequisites

Before running the platform, ensure you have:

- **Python**: Version 3.10 or 3.11 installed.
- **MongoDB**: Community Edition or MongoDB Atlas instance running on `mongodb://localhost:27017`.

---

## Quick Start Guide

### Step 1: Clone Repository & Setup Environment

```bash
# Navigate to the project root directory
cd HackOut

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
.\venv\Scripts\activate.bat
# Linux / macOS:
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Ensure MongoDB Service is Running

Make sure MongoDB is running locally on port 27017:
```bash
# Windows (PowerShell as Admin):
net start MongoDB

# Linux / macOS:
sudo systemctl start mongod
```

### Step 4: (Optional) Train ML Models

Pre-trained models are included in `models/`. To retrain models from dataset source files:

```bash
# Train Wind Turbine Normal Behavior Models (NBM)
python -m ml_engine.train_wind_nbm

# Train Solar Panel Normal Behavior Model (NBM)
python -m ml_engine.train_solar_nbm
```

### Step 5: Start the IoT SCADA Simulator

In a dedicated terminal, launch the IoT simulator to seed assets and stream telemetry into MongoDB:

```bash
python simulator/run_simulation.py --seed-defaults
```

### Step 6: Start the Background Anomaly Scorer

In a second terminal, launch the background ML scorer to process incoming telemetry:

```bash
python -m ml_engine.anomaly_scorer
```

### Step 7: Launch the Streamlit Dashboard

In a third terminal, launch the Streamlit frontend dashboard:

```bash
streamlit run dashboard/app.py
```

Open your browser and navigate to: **`http://localhost:8501`**

---

## Features & Features Overview

### 1. Interactive 3D Globe Map
- **3D Globe Mode (`orthographic`)**: Visualizes global fleet distribution on a rotatable 3D earth projection.
- **Asset Differentiation**: Visual distinction between **Solar Panels** (Circles) and **Wind Turbines** (Triangles).
- **Focus Zoom**: Select any asset from the map controls dropdown to center and zoom the globe onto its exact GPS coordinates.

### 2. Physical & Electrical Diagnostics
- **Thermal Inertia (EMA)**: Exponential Moving Average smoothing ($\alpha=0.25$) on nacelle and bearing temperatures.
- **Bearing-to-Oil $\Delta T$**: Flags friction degradation when $T_{\text{bearing}} - T_{\text{oil}} > 20^\circ\text{C}$.
- **3-Phase Current Imbalance ($\Delta I$)**: Triggers alarms when phase current divergence exceeds $5\%$.
- **IEC 61724 Performance Ratio (PR)**: Tracks solar array efficiency normalized against solar irradiance.

### 3. Fault Latching & Technician Repair
- Thermal anomalies and diode faults persist irreversibly across simulation ticks until explicitly serviced.
- **1-Click Repair Workflow**: Technicians can dispatch repair commands from the **Command Center** tab to reset asset health back to 100% baseline.

---

## Configuration

System settings, electricity pricing, replacement costs, and regional climate modifiers can be adjusted in `config.py`:

- `MONGO_URI`: Default `mongodb://localhost:27017/`
- `ELECTRICITY_PRICE_PER_KWH`: Default `$0.10` USD
- `EMERGENCY_REPLACEMENT_COST`: Default `$50,000` USD
- `PREVENTIVE_MAINTENANCE_COST`: Default `$5,000` USD
- `TICK_INTERVAL_SECONDS`: Default `2` seconds
