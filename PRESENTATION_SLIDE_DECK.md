# 📊 Hackathon Pitch Deck Blueprint: Renewable Energy Predictive Maintenance (PdM) Platform

> **Target Length**: 15 Slides Max  
> **Design Platform**: Canva  
> **Style Preset**: Enterprise Light / Modern Clean Glassmorphism  
> **Color Palette**: Emerald Green (`#10B981`), Tech Cyan (`#06B6D4`), Charcoal Slate (`#1E293B`), Soft Off-White (`#F8FAFC`)

---

## 🎨 Master Design System & Canva Theme Guidelines

Before populating the slides, apply these uniform styling rules in Canva to maintain clean-cut, professional consistency:

* **Color Palette**:
  * **Primary Accent**: Emerald Green (`#10B981` / `#059669`) — Represents asset health, clean energy, & optimal operational status.
  * **Secondary Accent**: Tech Cyan (`#06B6D4`) — Represents AI engines, live SCADA streams, & IoT edge connectivity.
  * **Warning / Alert**: Amber Orange (`#F59E0B`) & Alert Red (`#EF4444`).
  * **Background**: Light Grey / Slate Off-White (`#F8FAFC`) with subtle light glass cards (`#FFFFFF` with `1px` border stroke `#E2E8F0` and `8px` drop shadow).
* **Typography**:
  * **Font Family**: Clean Sans-Serif (**Inter**, **Montserrat**, or **Plus Jakarta Sans**).
  * **Hierarchy**: Titles in **Bold 32–40pt**, Subheadings in **Semi-Bold 20–24pt**, Body text in **14–18pt**.
* **Canva Shapes & UI Components**:
  * **Cards**: Use *Rounded Rectangles* (Corner Radius: `12-16px`) with soft drop shadows for content grouping.
  * **Status Pills/Badges**: Small pill-shaped containers (`Capsule` shape) for key metrics (`AHI: 94%`, `RUL: 520h`, `RPN: 85`).
  * **Formula Containers**: Dark slate code boxes (`#1E293B`) with cyan monospace text for mathematical equations ($\Delta T$, $\Delta I$, PR, RPN).
  * **Metric Callouts**: Large bold numbers (`48-60pt`) inside shaded rectangle containers with icon headers.

---

## 📜 Slide-by-Slide Detailed Blueprint

---

### Slide 1: Title Slide & Value Proposition
* **Slide Title**: **AI-Powered Predictive Maintenance for Hybrid Renewable Fleets**
* **Subtitle**: *Preventing Unplanned Downtime in Solar PV & Wind Assets via SCADA Telemetry, NBM Machine Learning, and Domain Physics*
* **Slide Hook / Goal**: Capture immediate judge attention with high production value, clear problem domain, and strong branding.
* **Content & Key Points to Put**:
  * **Project Name**: Renewable Energy Predictive Maintenance Platform (PdM)
  * **Team / Hackathon Identifier**: HackOut 2026 Submission
  * **Core Motto**: *"Transforming Reactive SCADA Alarms into Proactive Financial & Physical Intelligence."*
  * **Key Capability Pills**: `3D Globe Fleet Map` | `Random Forest NBM` | `Physics Diagnostics` | `1-Click Repair`
* **Canva Layout & Shapes / Hooks**:
  * **Layout**: Left-aligned high-contrast typography header; right side dedicated to a large hero image container.
  * **Shapes**: Gradient accent bar (Emerald Green to Tech Cyan) at the top edge. 4 pill-shaped badges at the bottom aligned horizontally.
* **Mandatory Diagrams / Images to Add**:
  * 📸 **Hero Image**: High-resolution photorealistic render or screenshot of wind turbines and solar PV arrays during golden hour, overlaid with a subtle translucent futuristic HUD UI grid.

---

### Slide 2: The Invisible Crisis in Renewable Energy
* **Slide Title**: **The \$XX Billion Problem: Unplanned Downtime**
* **Slide Hook / Goal**: Establish the acute industrial pain point and huge financial impact of catastrophic component failures.
* **Content & Key Points to Put**:
  * **The Challenge**: Wind turbines and Solar PV arrays operate in extreme environmental conditions (desert heat, ocean salt, thermal stress).
  * **Hidden Micro-Faults**: Bearings wear down silently, solar panels suffer dust soiling and blown bypass diodes without triggering traditional static alarms until total failure.
  * **Financial Impact**:
    * Emergency Component Replacement: **\$50,000+ per catastrophic failure**.
    * Supply Chain Bottlenecks: Up to **60 days lead time** for heavy offshore gearboxes.
    * Daily Lost Generation: Up to **\$2,400/day** per offline 2MW wind turbine.
* **Canva Layout & Shapes / Hooks**:
  * **Layout**: 3-Column Pain Point Layout with stat callout boxes at the top of each column.
  * **Shapes**: Red/Amber tint rounded cards (`#FEF2F2` background with `#FCA5A5` border) to signify danger/loss.
* **Mandatory Diagrams / Images to Add**:
  * 🖼️ **Infographic / Photo**: Split visual showing a damaged wind turbine gearbox bearing vs a dust-soiled solar PV array with a thermal infrared hotspot glowing red.

---

### Slide 3: Status Quo vs. The Paradigm Shift
* **Slide Title**: **Why Traditional Maintenance Systems Fail**
* **Slide Hook / Goal**: Highlight the gap between legacy threshold alarms and true predictive physics-ML intelligence.
* **Content & Key Points to Put**:
  * **Legacy Approach (Reactive / Periodic)**:
    * Fixed threshold alarms (e.g. alarm only when temp $> 80^\circ\text{C}$) — *Too late! Damage is already done.*
    * High false-alarm rates during high-ambient weather days.
    * No financial risk weighting or supply chain lead-time context.
  * **Our Paradigm Shift (Proactive & Predictive)**:
    * **Normal Behavior Modeling (NBM)**: Learns expected thermal/power curves under actual ambient conditions.
    * **Physics-Enforced Rules**: Detects bearing friction deltas ($\Delta T > 20^\circ\text{C}$) & 3-phase current imbalance ($\Delta I > 5\%$).
    * **Financial RPN Scoring**: Prioritizes repairs by daily revenue loss $\times$ supply chain lead time risk.
* **Canva Layout & Shapes / Hooks**:
  * **Layout**: 2-Column Comparison Layout (Left: "Legacy Reactive" with Red cross headers, Right: "Our Predictive AI" with Emerald checkmark headers).
  * **Shapes**: Two contrasting full-height vertical cards. Right card highlighted with a glowing green border stroke.
* **Mandatory Diagrams / Images to Add**:
  * 📊 **Comparison Diagram**: A simple line graph showing *Legacy Fixed Alarm Threshold* (flat red line breached at total failure) vs *NBM Anomaly Score Trend* (early warning curve detecting degradation weeks prior).

---

### Slide 4: The Solution Overview
* **Slide Title**: **End-to-End Renewable Fleet Intelligence**
* **Slide Hook / Goal**: Introduce the 4 core pillars of our full-stack platform.
* **Content & Key Points to Put**:
  * **1. High-Frequency Telemetry Ingestion**: Ingests live SCADA telemetry from Wind Turbines & Solar PV physics engines.
  * **2. Hybrid AI Engine**: Combines 5 trained Random Forest Regressors with explicit domain engineering physics.
  * **3. Asset Health & Financial Engine**: Calculates real-time Asset Health Index (AHI 0-100), RUL hours, and Risk Priority Numbers (RPN).
  * **4. Actionable Technician Workflows**: Interactive 3D Globe dashboard, auto-generated PDF work orders, and 1-click repair dispatch.
* **Canva Layout & Shapes / Hooks**:
  * **Layout**: 4-Horizontal Step Process Flow across the slide.
  * **Shapes**: 4 Rounded rectangular process cards linked with directional arrow connectors (`➔`). Top icons in circular containers with cyan/emerald fills.
* **Mandatory Diagrams / Images to Add**:
  * 💻 **Platform Screenshot**: Clean high-res screenshot of the Streamlit Dashboard main header showing top fleet KPIs (Total Assets, Healthy vs At-Risk counts, Daily Financial Loss).

---

### Slide 5: System Architecture & Tier Breakdown
* **Slide Title**: **4-Tier Decentralized Platform Architecture**
* **Slide Hook / Goal**: Demonstrate enterprise-grade software engineering, modularity, and clean data flow.
* **Content & Key Points to Put**:
  * **Tier 1: IoT Edge Simulator**: Kaggle SCADA replay (Wind) & Solar irradiance geometry model (`simulator/`).
  * **Tier 2: Data Store**: MongoDB persistent database storing live SCADA, asset registries, dynamic commands, and anomaly scores (`predictive_maintenance`).
  * **Tier 3: ML & Business Engine**: Background anomaly scorer evaluating NBM models, thermal inertia EMA, health index, and financial RPN (`ml_engine/` & `business_logic/`).
  * **Tier 4: Presentation & API**: Streamlit Light Glassmorphic UI & FastAPI REST Server (`dashboard/` & `backend/`).
* **Canva Layout & Shapes / Hooks**:
  * **Layout**: Centered High-Tech Architecture Flowchart.
  * **Shapes**: Container boxes for each Tier with distinct color-coded headers (Blue for IoT, Green for DB, Purple for ML, Orange for UI/API).
* **Mandatory Diagrams / Images to Add**:
  * 📐 **Architecture Flowchart**: Insert the official System Architecture flowchart:
    * `IoT Edge Simulator` ➔ `MongoDB` ➔ `Background Scorer (ML/Physics)` ➔ `Streamlit 3D Globe / FastAPI REST`.

---

### Slide 6: IoT Telemetry & Physics Simulation Engine
* **Slide Title**: **Multi-Modal Data Ingestion & Solar Physics Engine**
* **Slide Hook / Goal**: Explain how realistic wind SCADA and solar physics streams are generated and processed.
* **Content & Key Points to Put**:
  * **Wind Turbine SCADA Replay**:
    * Replays multi-farm Kaggle SCADA telemetry (`Wind Farm A, B, C`).
    * Captures nacelle temps, generator RPM, blade pitch angles, wind speed, and 3-phase currents ($I_1, I_2, I_3$).
  * **Solar PV Physics Model**:
    * Clear-Sky Solar Geometry: $\sin(\alpha) = \sin(\text{lat})\sin(\delta) + \cos(\text{lat})\cos(\delta)\cos(\omega)$
    * Cell Thermal Model (NOCT $45^\circ\text{C}$): $T_{\text{panel}} = T_{\text{ambient}} + (45 - 20) \times \frac{\text{Irradiance}}{800}$
    * Dust Soiling Accumulation ($0.001/\text{tick}$) & Blown Diode Fault Injection (33% power loss).
* **Canva Layout & Shapes / Hooks**:
  * **Layout**: 2-Column Split (Left: Wind SCADA Specs, Right: Solar Physics Engine & Math Formulas).
  * **Shapes**: Code-snippet styled container box for mathematical formulas with dark background (`#1E293B`) and white/cyan monospace text for mathematical elegance.
* **Mandatory Diagrams / Images to Add**:
  * 📈 **Physics Curves Chart**: Plot/Graphic showing simulated Solar Irradiance curve vs Ambient and Panel Surface Temperature over a 24-hour cycle.

---

### Slide 7: Machine Learning: Normal Behavior Models (NBM)
* **Slide Title**: **Random Forest Regressors for Baseline Prediction**
* **Slide Hook / Goal**: Detail the AI model training, feature selection, and thermal residual calculation.
* **Content & Key Points to Put**:
  * **5 Trained Random Forest Models (`scikit-learn`)**:
    1. Gearbox Bearing Temperature ($R^2 > 0.94$, MAE $\sim 0.8^\circ\text{C}$)
    2. Gearbox Oil Sump Temperature ($R^2 > 0.96$, MAE $\sim 0.6^\circ\text{C}$)
    3. Generator Drive-End (DE) Bearing Temp ($R^2 > 0.93$)
    4. Generator Non-Drive-End (NDE) Bearing Temp ($R^2 > 0.93$)
    5. Solar PV Inverter AC Power Baseline ($R^2 > 0.98$)
  * **Thermal Residual Anomaly Scoring**:
    $$\text{Residual}_i = |\text{Actual}_i - \widehat{\text{Predicted}}_i|$$
    $$\text{Score}_i = \min\left(100.0, \frac{\text{Residual}_i}{10.0^\circ\text{C}} \times 100.0\right)$$
* **Canva Layout & Shapes / Hooks**:
  * **Layout**: Top summary stats bar (showing $R^2 > 0.95$ average), followed by a 2-column model detail layout.
  * **Shapes**: Green performance pills (`R² > 0.94`, `MAE < 1.0°C`) attached to each model card.
* **Mandatory Diagrams / Images to Add**:
  * 📉 **Actual vs Predicted Plot**: Dual-line graph showing Actual Bearing Temperature (red line spiking during fault) vs ML Baseline Expected Temperature (blue smooth curve).

---

### Slide 8: Domain Physics & Electrical Diagnostics
* **Slide Title**: **Beyond ML: Physics-Enforced Diagnostic Rules**
* **Slide Hook / Goal**: Prove that the system prevents false alarms by enforcing strict mechanical & electrical physical laws.
* **Content & Key Points to Put**:
  * **1. Exponential Thermal Inertia EMA ($\alpha = 0.25$)**:
    * Filters high-frequency thermal noise in mechanical nacelle housing:
    * $T_{\text{smoothed}}^{(t)} = 0.25 \cdot T_{\text{raw}}^{(t)} + 0.75 \cdot T_{\text{smoothed}}^{(t-1)}$
  * **2. Bearing-to-Oil Differential ($\Delta T$)**:
    * $\Delta T = T_{\text{bearing}} - T_{\text{oil}}$. Flags friction when $\Delta T > 20.0^\circ\text{C}$.
  * **3. 3-Phase Electrical Current Imbalance ($\Delta I$)**:
    * Evaluates stator winding health. Alarms triggered when phase divergence exceeds $5.0\%$.
  * **4. IEC 61724 Solar Performance Ratio (PR)**:
    * $PR = \frac{P_{\text{actual}}}{(\text{Irradiance}/1000) \times \text{Capacity}_{\text{kw}}}$. Flags soiling or diode failure when $PR < 0.70$.
* **Canva Layout & Shapes / Hooks**:
  * **Layout**: 4 Grid Cards (2x2 Grid) representing the 4 physics rules.
  * **Shapes**: Light blue rounded rectangle cards with custom physics icons (Thermometer, Electric Lightning, Solar Sun, Filter Wave).
* **Mandatory Diagrams / Images to Add**:
  * ⚡ **Diagnostic UI Visual**: Screenshot of the Streamlit "Asset Deep Dive" tab displaying the 3-Phase Current Imbalance graph and Bearing-to-Oil $\Delta T$ gauge.

---

### Slide 9: Asset Health Index (AHI) & RUL Estimation
* **Slide Title**: **Asset Health Index (AHI) & Remaining Useful Life**
* **Slide Hook / Goal**: Explain how raw anomaly scores are synthesized into an intuitive 0-100 AHI score and RUL in hours.
* **Content & Key Points to Put**:
  * **Asset Health Index (AHI 0-100)**:
    $$\text{AHI} = \max(0.0, \min(100.0, 100.0 - \text{Overall Anomaly Score}))$$
    * 🟢 **80 - 100**: Healthy | 🟡 **50 - 79**: Warning | 🟠 **20 - 49**: Critical | 🔴 **0 - 19**: Failure Imminent
  * **Degradation Velocity & RUL (Linear Polyfit)**:
    * Fits 1st-degree polynomial regression over historical anomaly trend to compute degradation rate ($\text{pts/hour}$).
    $$\text{RUL (Operating Hours)} = \max\left(0.5, \frac{\text{AHI}}{|\text{Degradation Rate}|}\right)$$
    * **Rapid Collapse Alert**: Triggered if degradation rate $> 5.0\text{ AHI/hour}$ or $RUL < 24\text{ hours}$.
* **Canva Layout & Shapes / Hooks**:
  * **Layout**: Left side AHI color gauge scale bar; right side RUL linear regression math breakdown.
  * **Shapes**: Vertical color gradient bar (Green ➔ Yellow ➔ Orange ➔ Red) representing health bands with threshold callout markers.
* **Mandatory Diagrams / Images to Add**:
  * 📉 **RUL Regression Trend Chart**: Scatter plot of historical AHI telemetry points with a linear trendline projecting down to 0 AHI (RUL threshold).

---

### Slide 10: Financial Risk Engine & Priority Scoring (RPN)
* **Slide Title**: **Financial Downtime Analytics & Risk Priority Number**
* **Slide Hook / Goal**: Demonstrate how maintenance is prioritized based on dollars lost and supply chain logistics.
* **Content & Key Points to Put**:
  * **Grid Curtailment Guard**: Prevents false financial alarms when operators intentionally derate assets ($\text{status\_type\_id} \in [1, 2]$).
  * **Daily Revenue Loss Calculation**:
    $$\text{Revenue Loss}_{\text{daily}} = \text{Power Loss (kW)} \times 24\text{ Hours} \times \$0.10/\text{kWh}$$
  * **Supply Chain Lead Time Weighting**:
    * Gearbox Bearing Replacement: **60 Days** | Generator Bearing: **21 Days** | Solar Diode: **2 Days**
  * **Risk Priority Number (RPN)**:
    $$\text{RPN} = \frac{(100.0 - \text{AHI}) \times \text{Revenue Loss}_{\text{daily}} \times \left(1 + \frac{\text{Lead Time (Days)}}{30}\right)}{100.0}$$
* **Canva Layout & Shapes / Hooks**:
  * **Layout**: 3 Column Cards highlighting (1) Curtailment Guard, (2) Supply Chain Lead Time Table, (3) RPN Formula Box.
  * **Shapes**: Financial dollar badge icons (`$`) on emerald cards; lead-time clock icons on blue cards.
* **Mandatory Diagrams / Images to Add**:
  * 📊 **Supply Chain Lead Time Table**: Table graphic showing Component vs Lead Time (Days) vs Risk Weighting.

---

### Slide 11: Presentation Tier: 3D Globe & Streamlit Dashboard
* **Slide Title**: **Interactive 3D Globe & Enterprise Control Room**
* **Slide Hook / Goal**: Showcase the visual interface, UX elegance, and real-time fleet map capabilities.
* **Content & Key Points to Put**:
  * **Interactive 3D Globe Map (`pydeck` orthographic projection)**:
    * Visualizes global fleet distribution (Desert, Nordic, Coastal, Temperate regions).
    * Asset Shape Coding: Solar Panels (Circles `●`) vs Wind Turbines (Triangles `▲`).
    * Health Color Coding: Dynamic status colors (Green, Yellow, Red).
    * **Focus Zoom**: 1-Click dropdown centering and zooming the 3D globe onto any specific GPS location.
  * **6 Application Tabs**:
    1. Fleet Overview | 2. Asset Deep Dive | 3. Maintenance Queue | 4. Financial Impact | 5. Asset Manager | 6. Command Center
* **Canva Layout & Shapes / Hooks**:
  * **Layout**: Large Hero UI Screenshot framing on the right; key UX features bulleted on the left inside a clean glass card.
  * **Shapes**: Soft grey mockup browser/app frame encapsulating the dashboard screenshot.
* **Mandatory Diagrams / Images to Add**:
  * 🌐 **3D Globe Screenshot**: High-resolution screenshot of the Streamlit 3D Globe UI showing wind turbines and solar arrays plotted across global locations.

---

### Slide 12: Automated Technician Workflow & PDF Work Orders
* **Slide Title**: **Closed-Loop Repair Dispatch & Audit Logging**
* **Slide Hook / Goal**: Show how the platform translates insights into real-world maintenance actions.
* **Content & Key Points to Put**:
  * **Automated PDF Work Order Generator (`ReportLab`)**:
    * Generates formal enterprise work orders complete with asset GPS, OEM hardware model, fault diagnostics, estimated downtime loss, and required replacement parts.
  * **1-Click Repair Workflow**:
    * Technician clicks "Execute Repair" in the Streamlit Command Center.
    * Sends `clear_overrides` command to MongoDB simulation queue.
    * Resets asset health to 100% baseline in real time.
  * **Permanent MongoDB Audit Trail (`repair_history`)**:
    * Logs technician timestamp, replaced component, prior AHI, and cost savings.
* **Canva Layout & Shapes / Hooks**:
  * **Layout**: 2-Column Split (Left: Repair Workflow Step-by-Step, Right: PDF Work Order Document Preview).
  * **Shapes**: PDF document border shape with shadow on the right; green checkmark badges on the left workflow list.
* **Mandatory Diagrams / Images to Add**:
  * 📄 **PDF Work Order Mockup**: Image preview of an auto-generated PDF maintenance work order document with company header, QR code, and component breakdown.

---

### Slide 13: Enterprise REST API & Multi-Farm Scalability
* **Slide Title**: **Production-Ready FastAPI & REST Microservices**
* **Slide Hook / Goal**: Demonstrate system extensibility, OpenAPI compliance, and enterprise integration capabilities.
* **Content & Key Points to Put**:
  * **FastAPI Backend Server (`backend/api.py`)**:
    * Fully decoupled REST API operating alongside the Streamlit UI.
    * Swagger UI & OpenAPI Specification available at `http://localhost:8000/docs`.
  * **Core Endpoint Suite**:
    * `GET /api/fleet/summary` ➔ Top-level fleet health KPIs & financial loss.
    * `GET /api/assets` ➔ Query active fleet filtered by region or asset type.
    * `POST /api/assets` ➔ Dynamic asset provisioning into MongoDB.
    * `GET /api/maintenance/queue` ➔ Priority queue sorted by RPN.
    * `POST /api/commands` ➔ Dispatch live overrides & repair commands.
* **Canva Layout & Shapes / Hooks**:
  * **Layout**: Left side API Endpoint table; right side interactive Swagger UI code box.
  * **Shapes**: Code block container (`#0F172A`) with syntax highlighting (HTTP verbs: `GET` in green, `POST` in blue).
* **Mandatory Diagrams / Images to Add**:
  * 💻 **FastAPI Swagger Screenshot**: Screenshot of the FastAPI `/docs` interactive Swagger UI showing endpoint execution and JSON response bodies.

---

### Slide 14: Business Impact & ROI Case Study
* **Slide Title**: **Financial Returns & Cost Savings Analysis**
* **Slide Hook / Goal**: Prove the economic value proposition to judges and potential investors.
* **Content & Key Points to Put**:
  * **Cost of Inaction vs. Preventive Servicing**:
    * Catastrophic Gearbox Failure: **\$50,000 replacement + \$30,000 lost generation** = **\$80,000 total loss**.
    * Early Preventive Maintenance (Our Platform): **\$5,000 scheduled service**.
    * **Net Savings per Event: \$75,000 (93.7% Cost Reduction)**.
  * **Fleet-Wide Metrics (100-Asset Hybrid Fleet)**:
    * Downtime Reduction: **-78%**
    * Annual Revenue Protection: **+\$450,000 / year**
    * Platform Payback Period: **$< 3$ Months**
* **Canva Layout & Shapes / Hooks**:
  * **Layout**: 3 High-Impact Big Stat Cards across the slide (`93.7% Savings`, `-78% Downtime`, `< 3 Mo Payback`).
  * **Shapes**: Massive bold text callouts (60pt) inside glowing emerald gradient rounded cards (`#ECFDF5` background with `#10B981` borders).
* **Mandatory Diagrams / Images to Add**:
  * 📊 **Financial ROI Bar Chart**: Side-by-side bar chart comparing *Reactive Maintenance Cost* vs *Predictive Maintenance Cost* over 12 months.

---

### Slide 15: Strategic Roadmap & Conclusion
* **Slide Title**: **The Future of Autonomous Energy Management**
* **Slide Hook / Goal**: End on a visionary, high-energy note summarizing future scale and tech milestones.
* **Content & Key Points to Put**:
  * **Immediate Milestones (Q3-Q4 2026)**:
    * **Edge AI Containerization**: Deploy quantized NBM models directly to ONNX / NVIDIA Jetson edge devices on nacelles.
    * **Battery Energy Storage System (BESS) Support**: Extend physics engines to lithium-ion cell degradation and thermal runaway prediction.
  * **Long-Term Vision**:
    * Fully autonomous fleet dispatch with robotic solar panel washing drone orchestration.
  * **Final Call to Action**:
    * *"Predictive Intelligence is the Key to Unlocking 100% Renewable Reliability."*
    * **Try Live Platform**: `http://localhost:8501` | **API Docs**: `http://localhost:8000/docs`
* **Canva Layout & Shapes / Hooks**:
  * **Layout**: 3 Timeline Cards horizontally (Q3 2026 ➔ Q4 2026 ➔ 2027 Vision), followed by a prominent centered Call to Action box at the bottom.
  * **Shapes**: Tech cyan timeline dots and connecting lines. Bottom CTA box with an Emerald Green button graphic ("Launch Platform ➔").
* **Mandatory Diagrams / Images to Add**:
  * 🚀 **Future Vision Image**: Futuristic visual of a smart renewable microgrid with wind turbines, solar panels, and battery storage units connected by holographic digital light streams.

---

## 📌 Summary Checklist of Visual Diagrams & Screenshots Needed

To ensure your presentation score is maximized, gather and crop the following 10 visual assets before populating Canva:

1. 📸 **Hero Photo**: Cinematic wind turbine + solar panel golden hour photo.
2. 🖼️ **Fault Infographic**: Wind turbine gearbox failure vs solar soiling/hotspot photo.
3. 📐 **Architecture Diagram**: 4-Tier System Architecture flowchart (from `PROJECT_REPORT.md`).
4. 📈 **Physics Curves Plot**: Solar clear-sky irradiance vs panel surface temperature graph.
5. 📉 **ML Residual Plot**: Actual vs Predicted Random Forest temperature residual curve.
6. ⚡ **Diagnostics UI**: Streamlit screenshot of 3-Phase Current Imbalance & $\Delta T$ gauges.
7. 📉 **RUL Trend Line**: Linear regression degradation velocity scatter plot.
8. 🌐 **3D Globe Screenshot**: Full-screen Streamlit 3D Globe map with asset markers.
9. 📄 **PDF Work Order**: Mockup of the auto-generated ReportLab maintenance work order PDF.
10. 📊 **ROI Comparison Chart**: Bar chart comparing Reactive vs Predictive financial costs.
