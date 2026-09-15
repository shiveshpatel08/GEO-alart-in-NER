# GeoAlert-NER — Team Leader Quick Run Guide 🚀

> **Disaster Early Warning System for North Eastern Region (NER), India**  
> Complete stack verified & ready for presentation/evaluation.

---

## ⚡ Quick Start (1-Click Run)

If this is your first time running the project on a new laptop:

1. **Setup Environment**:
   - Double-click **`setup_environment.bat`**  
   - This automatically configures PostgreSQL 16 + PostGIS 3.6, applies Alembic database migrations, seeds monitoring stations, and installs frontend npm packages.

2. **Start the System**:
   - Double-click **`start_all.bat`**  
   - This starts PostgreSQL, launches the FastAPI backend, launches the React/Vite dashboard, and automatically opens your web browser to `http://localhost:5173`.

3. **Stop the System**:
   - Double-click **`stop_all.bat`** when you are done.

---

## 🌐 System Endpoints & URLs

| Component | URL | Description |
| :--- | :--- | :--- |
| **Interactive Dashboard** | [http://localhost:5173](http://localhost:5173) | Leaflet GIS map with color-coded risk markers, dynamic 3 km PostGIS danger zones, and live telemetry feeds |
| **Backend API Docs** | [http://localhost:8000/docs](http://localhost:8000/docs) | Interactive Swagger UI for testing all REST endpoints |
| **System Health Check** | [http://localhost:8000/health](http://localhost:8000/health) | Real-time database & backend health probe |
| **Realtime SSE Alert Feed** | [http://localhost:8000/api/v1/realtime/sse/alerts](http://localhost:8000/api/v1/realtime/sse/alerts) | Live Server-Sent Events stream for emergency alerts |
| **ML Model Status** | [http://localhost:8000/api/v1/ml/status](http://localhost:8000/api/v1/ml/status) | Inspect active Random Forest ML classifier weights and metrics |

---

## 🛠️ Step-by-Step Manual Commands (Optional)

If you prefer running components individually in PowerShell or Command Prompt:

### 1. Database Start (PostgreSQL + PostGIS)
```powershell
# Start PostgreSQL daemon
& "$env:USERPROFILE\pgsql\pgsql\bin\pg_ctl.exe" -D "$env:USERPROFILE\pgsql\data" -l "$env:USERPROFILE\pgsql\server.log" start
```

### 2. Run Database Migrations & Seeds
```powershell
# Apply schema migrations
alembic upgrade head

# Seed sensor stations and historical landslides
python scripts/seed_data.py
python scripts/import_real_landslides.py
```

### 3. Start FastAPI Backend
```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. Start Vite Frontend
```powershell
cd frontend
npm run dev
```

---

## ✅ Verified Verification Checklist

All 19 requirements have been tested and verified operational:

- [x] **PostgreSQL 16 + PostGIS 3.6**: Running on port `5432` with spatial extensions enabled (`ST_MakePoint`, `ST_Distance`, `ST_Buffer`, `ST_AsGeoJSON`, `ST_DWithin`).
- [x] **Alembic Migrations**: Fully synced with PostgreSQL schema (`20260913_0001`).
- [x] **FastAPI Backend**: Serving live requests on port `8000`.
- [x] **Vite React Frontend**: Serving compiled responsive UI on port `5173` with reverse proxy to backend.
- [x] **Machine Learning Model**: `RandomForestClassifier` loaded from `app/models_ml/landslide_risk_model.joblib` computing calibrated risk scores from multi-sensor feature vectors.
- [x] **Live Open-Meteo Integration**: Live hourly rainfall and soil moisture ingestion working for North East coordinates (Shillong, Cherrapunji, Gangtok, etc.).
- [x] **Satellite Weather Fallback**: Automatic failover to Open-Meteo precipitation if sensor nodes go offline.
- [x] **Crowdsourced Incident Reports**: Public field reporting with media uploads and PostGIS geographic proximity search.
- [x] **Real-time Streaming (SSE)**: Server-Sent Events streaming alert events to dashboard clients without page reloads.
- [x] **Security & Access Control**: JWT Bearer authentication and role-based access control (RBAC) protecting critical command endpoints.

---

## 🧪 Running Automated Test Suite

To run the complete automated verification suite:

```powershell
python scripts/test_api.py
```

**Expected output:**
```text
============================================================
[SUCCESS] All API tests executed successfully!
============================================================
```
