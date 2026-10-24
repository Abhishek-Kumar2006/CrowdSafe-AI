# CrowdSafe AI 🛡️
### AI-Powered Crowd Monitoring & Stampede Early-Warning System (Hackathon Prototype)

> **Important Operational Disclaimer:**
> **CrowdSafe AI** is an AI-assisted decision-support prototype designed for security personnel and event operators. It identifies potential crowd-safety risks (such as localized bottleneck congestion, sustained high occupancy, and sudden density surges) rather than predicting stampedes with absolute certainty. All decisions should involve human-in-the-loop verification.

---

## 🚀 Overview

**CrowdSafe AI** is a functional, end-to-end computer vision and risk analytics prototype designed for high-density public venues (stadium concourses, transit terminals, pilgrimage corridors, and festival entrances).

The system divides surveillance cameras into configurable tactical zones, detects individuals in real time using **YOLOv8** and **OpenCV**, evaluates density against configurable thresholds and congestion duration, and alerts operators through visual indicators, audio chimes, and persistent SQLite records.

---

## 🌟 Core Features

1. **Tactical Security Operations Dashboard**
   - Dark-themed control room UI with real-time HUD overlays.
   - Live telemetry: Detected people count, active alerts, overall risk level, and AI engine status.
   - Low-latency MJPEG video streaming with bounding boxes and zone tints.
   - Interactive 2D Spatial Density Heat Matrix.

2. **Real YOLOv8 Person Detection**
   - Real-time person detection powered by Ultralytics **YOLOv8 nano** (`yolov8n.pt`).
   - Computes tactical bounding boxes, confidence tags, and center/foot coordinate tracking.
   - Graceful offline fallback to OpenCV's built-in HOG People Detector if YOLO weights are missing.
   - **Truth-in-AI Guarantee**: Real AI detections are explicitly badged (`[REAL YOLOv8 INFERENCE]`), and simulated data is clearly labeled (`[SIMULATED DEMO DATA]`).

3. **Zone-Based Crowd Risk Analysis**
   - Monitored cameras are divided into configurable zones (e.g., Ingress Chokepoint, Central Plaza, Escalator Lane, Egress Route).
   - **4-Tier Risk Assessment:**
     - 🟢 **Green (Normal):** Nominal pedestrian flow.
     - 🟡 **Yellow (Increasing):** Rising density, cautionary monitoring.
     - 🟠 **Orange (High):** Heavy congestion approaching physical capacity limits.
     - 🔴 **Red (Critical):** Excessive density sustained beyond safe duration limits.
   - **Congestion Duration Tracking:** Alerts evaluate not just instantaneous spikes, but whether dangerous density persists continuously (e.g., > 4.0 seconds) to prevent false alarms while catching dangerous bottlenecks.

4. **Alerts & Operator Acknowledgment**
   - Automatically generates alerts containing timestamp, affected zone, severity level, occupancy count, and cause.
   - Audio warning chimes synthesized via the Web Audio API for Critical alerts.
   - In-app **Acknowledge** button with operator signature logging.

5. **Persistent SQLite Database**
   - Automatically initializes and manages SQLite storage (`backend/data/crowdsafe.db`).
   - Stores camera profiles, configurable zone definitions, time-series observations, and complete historical alert audit logs.
   - Searchable alert history viewer with JSON export capability.

6. **Judge Demo Mode & 1-Click Testing**
   - **Demo Simulation Feed**: When no live camera or custom video is connected, provides realistic simulated crowd movements and fluctuating zone occupancy.
   - **"TEST SURGE" Button**: Instantly triggers a simulated crowd surge scenario to demonstrate how the system transitions from Green -> Yellow -> Orange -> Red and raises critical alarms.
   - **1-Click Real YOLO Sample**: Pre-bundled with the Intel IoT Pedestrian dataset (`sample_data/crowd_sample.mp4`), allowing judges and users to test real YOLO detection with a single click without searching for a video file.

---

## 🛠️ Tech Stack

- **Frontend:** React 18, TypeScript, Tailwind CSS, Lucide Icons, Vite
- **Backend:** Python 3.10+, FastAPI, Uvicorn, SQLite3, NumPy
- **AI & Computer Vision:** Ultralytics YOLOv8 nano, OpenCV (`cv2`)
- **Audio:** Web Audio API (zero external sound file dependencies)

---

## 📂 Project Structure

```
crowdsafe-ai/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI endpoints & static frontend mounting
│   │   ├── config.py            # Risk tiers, color definitions, directory paths
│   │   ├── database.py          # SQLite schema, default seeds & CRUD queries
│   │   ├── detector.py          # YOLOv8 & OpenCV person detector & HUD renderer
│   │   ├── risk_analyzer.py     # Zone occupancy & congestion duration tracker
│   │   ├── video_processor.py   # Real video ingestion, frame extraction & looping
│   │   └── simulator.py         # Realistic demo simulation generator & surge mode
│   ├── data/
│   │   └── crowdsafe.db         # SQLite database
│   ├── sample_data/
│   │   └── crowd_sample.mp4     # Pre-bundled Intel pedestrian benchmark video
│   ├── uploads/                 # Storage for user-uploaded videos
│   ├── yolov8n.pt               # Pre-cached YOLOv8 nano model weights
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DisclaimerBanner.tsx       # Safety disclaimer banner
│   │   │   ├── Navbar.tsx                 # Header with status, mode, & surge button
│   │   │   ├── MetricsBar.tsx             # 4 key telemetry KPI cards
│   │   │   ├── VideoPlayer.tsx            # Live stream player with tactical HUD
│   │   │   ├── ZoneRiskGrid.tsx           # Zone occupancy cards & duration meters
│   │   │   ├── DensityHeatmap.tsx         # 2D spatial density matrix
│   │   │   ├── AlertFeed.tsx              # Real-time alert list & acknowledge button
│   │   │   ├── ThresholdSettingsModal.tsx # Zone threshold & duration tuner
│   │   │   ├── AlertHistoryModal.tsx      # SQLite audit log search & JSON export
│   │   │   └── VideoUploaderModal.tsx     # Video drag-and-drop & sample loader
│   │   ├── services/
│   │   │   └── api.ts                     # REST client with polling & fetch handlers
│   │   ├── utils/
│   │   │   └── audioAlert.ts              # Web Audio API chime synthesizer
│   │   ├── types/
│   │   │   └── index.ts                   # TypeScript interfaces
│   │   ├── App.tsx                        # Master dashboard view
│   │   ├── main.tsx
│   │   └── index.css                      # Tailwind styling & dark tactical scrollbars
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
└── README.md
```

---

## ⚡ Quick Start Guide

### Prerequisites
- **Python 3.10+** (tested up to Python 3.14)
- **Node.js 18+** & `npm`

---

### Method 1: Unified Run Mode (Recommended for Quick Demo)

The FastAPI server can serve both the API and the pre-built React frontend simultaneously on a single port:

1. **Build the Frontend (one-time):**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **Start the Backend Server:**
   ```bash
   cd ../backend
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

3. **Open in Browser:**
   Navigate to **`http://localhost:8000`**. The full interactive dashboard will load immediately!

---

### Method 2: Split Development Mode (Hot Reload)

If you wish to make live frontend modifications with Vite HMR:

1. **Terminal 1 - Backend:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

2. **Terminal 2 - Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open in Browser:**
   Navigate to **`http://localhost:5173`** (Vite proxies all `/api` requests to port 8000).

---

## 🎬 How to Test and Present at a Hackathon

### Step 1: Explore Demo Simulation Mode
1. Upon loading, select **"Gate 4 Main Concourse"** from the camera dropdown.
2. Observe the simulated crowd particles moving across the 4 zones.
3. Click the red **"TEST SURGE"** button in the navbar.
4. Watch how the occupancy spikes, the risk level escalates from **Normal -> Increasing -> High -> Critical**, and a **Safety Alert** is logged.
5. Click **"Acknowledge"** on the alert in the alert feed to see the active alert count update.

### Step 2: Test Real YOLOv8 AI Detection (1-Click)
1. Click the **"SAMPLE YOLO"** button in the navbar (or open the Upload modal and click "Load Sample").
2. The system switches to **"Pedestrian Concourse (Real YOLO Feed)"**.
3. Notice the green **`[REAL YOLOv8 INFERENCE]`** badge.
4. Watch the YOLOv8 model detect walking pedestrians frame-by-frame, draw tactical HUD bounding boxes with percentage confidence, and calculate zone occupancy.

### Step 3: Upload Your Own Prerecorded Video
1. Click **"UPLOAD VIDEO"** in the top navbar.
2. Drag and drop any `.mp4`, `.avi`, or `.mov` crowd video (e.g., mall, festival, subway footage).
3. Enter a camera label (e.g. *"Station South Exit"*).
4. Click **"Start Detection"**.
5. The backend automatically partitions the video into 4 quadrants, runs YOLO person detection, tracks congestion duration, and alerts you if thresholds are breached!

### Step 4: Adjust Safety Thresholds in Real Time
1. Click the **Sliders icon** (or edit button on any zone card).
2. Tune the Normal, Increasing, High, or Critical thresholds and the congestion duration slider (e.g., lower the critical threshold to 2 people).
3. Click **"Save Configuration"**.
4. The database is updated immediately, and the live risk calculation dynamically updates without refreshing the page!

### Step 5: Audit Log & Export
1. Click the **History** (clock) icon in the navbar.
2. Search through past alerts by zone or risk level.
3. Click **"Export"** to download the SQLite alert audit log as a JSON file.

---

## 📡 REST API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/status` | `GET` | System health, model name, and operational disclaimer |
| `/api/cameras` | `GET` | List all cameras (status: active, analyzing, simulated) |
| `/api/cameras/{id}/live-metrics` | `GET` | Real-time polling endpoint: counts, risk level, zone breakdown, alerts |
| `/api/cameras/{id}/stream` | `GET` | MJPEG video feed with HUD overlays and bounding boxes |
| `/api/zones/{id}` | `PUT` | Update zone thresholds and congestion duration |
| `/api/videos/upload` | `POST` | Upload prerecorded video and begin real YOLO detection |
| `/api/videos/load-sample` | `POST` | 1-click load of the bundled Intel pedestrian crowd sample |
| `/api/alerts` | `GET` | List historical alerts from SQLite with filtering |
| `/api/alerts/{id}/acknowledge` | `POST` | Acknowledge an active safety alert |
| `/api/demo/trigger-surge` | `POST` | Trigger a simulated 30-second crowd surge for judge demonstration |

---

## ⚖️ Ethics & Privacy Note

- CrowdSafe AI detects bounding boxes and spatial density only; it **does not perform facial recognition, identity tracking, or biometric profiling**.
- System logs record crowd counts, density ratios, and timestamps without storing personally identifiable information (PII).
