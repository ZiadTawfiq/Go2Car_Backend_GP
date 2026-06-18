# 🚗 Go2Car — AI-Powered Smart Parking System

A production-grade REST API backend for an AI-powered smart parking facility. Built as a graduation project, Go2Car bridges computer-vision vehicle detection with a mobile app, enabling users to locate their parked car in seconds.

The system receives real-time scan results from an external AI vision service (license plate recognition, color & type classification), automatically manages parking slot occupancy, and exposes search endpoints for the companion mobile app.

---

## ✨ Key Features

| Category | Details |
|----------|---------|
| **AI Vision Integration** | Receives scan results from cameras, auto-registers vehicles on arrival and frees slots on departure |
| **Vehicle Search** | Fuzzy plate search + attribute-based search (color, type) for when users forget their plate |
| **Multi-Level Parking Model** | Hierarchical Floor → Section → Slot structure with camera-to-section mapping |
| **Admin Analytics** | Occupancy summary, peak-hour analysis, per-slot usage heatmap, historical timeline, and PDF report export |
| **Auth & Security** | JWT with token blacklisting (secure logout), bcrypt password hashing, email verification via SendGrid |
| **Role-Based Access** | Public, authenticated, and admin-only endpoint tiers |
| **Vehicle Ownership** | Users register vehicles and view parking history for their own cars |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | **FastAPI** 0.135 + **Uvicorn** |
| Database | **SQLAlchemy** 2.0 ORM — SQLite (default) / PostgreSQL |
| Auth | **python-jose** (JWT HS256) + **Passlib** (bcrypt) |
| Validation | **Pydantic** 2 + **pydantic-settings** |
| Email | **SendGrid** SDK |
| PDF Export | **ReportLab** |
| Language | Python 3.10+ |

---

## 🏗️ Architecture

```mermaid
flowchart LR
    CAM["📷 AI Vision\nService"] -- "POST /ai/scan-result\n(arrival / departure)" --> API
    APP["📱 Mobile\nApp"] -- "Search · History\nRegister · Auth" --> API
    DASH["🖥️ Admin\nDashboard"] -- "Analytics · Users\nCameras · Slots" --> API

    subgraph API["FastAPI Backend"]
        direction TB
        R[Routes] --> S[Services]
        S --> M[Models / ORM]
        M --> DB[(SQLite / PostgreSQL)]
    end
```

### System Flow

```mermaid
sequenceDiagram
    participant AI as AI Vision Service
    participant API as FastAPI Backend
    participant DB as Database
    participant App as Mobile App

    Note over AI,API: Vehicle Arrives
    AI->>API: POST /ai/scan-result (event_type: arrival)
    API->>DB: Upsert vehicle + create ParkingRecord
    API->>DB: Mark slot occupied

    Note over App,API: User Searches
    App->>API: GET /vehicles/search?plate=ABC123
    API->>DB: Fuzzy match plate
    API-->>App: slot, section, floor

    Note over AI,API: Vehicle Departs
    AI->>API: POST /ai/scan-result (event_type: departure)
    API->>DB: Close ParkingRecord + free slot
```

---

## 📁 Project Structure

```
app/
├── main.py                  # FastAPI entry point, router registration
├── core/
│   ├── config.py            # Pydantic-settings (reads .env)
│   └── security.py          # JWT creation/decode, bcrypt hashing
├── db/
│   └── database.py          # SQLAlchemy engine + session factory
├── models/                  # ORM models
│   ├── user.py              # User (with email verification fields)
│   ├── vehicle.py           # Vehicle (plate, color, type, owner FK)
│   ├── parking_floor.py     # Floor → has many Sections
│   ├── parking_section.py   # Section → has many Slots & Cameras
│   ├── parking_slot.py      # Slot (occupied flag, section FK)
│   ├── parking_record.py    # Parking session (entry/exit times)
│   ├── camera.py            # Camera (active flag, section FK)
│   ├── detection_log.py     # Raw AI detection log
│   └── blacklist_token.py   # Revoked JWT tokens
├── schemas/                 # Pydantic request/response models
├── services/                # Business logic layer
│   ├── ai_service.py        # Arrival/departure pipeline
│   ├── vehicle_service.py   # Search, exit, history, map
│   ├── auth_service.py      # Register, login, email verification
│   ├── admin_service.py     # Analytics, user CRUD, PDF export
│   ├── slot_service.py      # Slot CRUD + occupancy stats
│   ├── camera_service.py    # Camera management
│   ├── floor_service.py     # Floor queries
│   ├── section_service.py   # Section queries
│   └── user_service.py      # Profile update, password change
└── routes/                  # API routers
    ├── dependencies.py      # JWT guard + admin guard
    ├── auth.py, user.py, vehicles.py, slots.py
    ├── ai.py, admin.py, floor.py, section.py, camera.py
```

---

## ⚡ Getting Started

### Prerequisites

- Python 3.10+
- pip

### 1. Clone & enter the project

```bash
git clone https://github.com/<your-org>/Go2Car_Backend_GP.git
cd Go2Car_Backend_GP
```

### 2. Create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
copy .env.example .env         # Windows
# cp .env.example .env         # macOS / Linux
```

Edit `.env` to set your own `SECRET_KEY`, `SENDGRID_API_KEY`, and optionally switch to PostgreSQL.

### 5. Run the server

```bash
uvicorn app.main:app --reload
```

The database file (`go2car.db`) is created automatically on first run — no manual migration needed.

### 6. Explore the API docs

| Interface | URL |
|-----------|-----|
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |

---

## 📡 API Endpoints

### Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | — | Register a new user (sends verification email) |
| POST | `/auth/login` | — | Login → returns JWT + user profile |
| GET | `/auth/verify-email?token=` | — | Verify email address |
| POST | `/auth/logout` | JWT | Revoke current token |

### Users

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/users/me` | JWT | Get current user profile |
| PUT | `/users/me` | JWT | Update profile |
| PUT | `/users/me/password` | JWT | Change password |
| DELETE | `/users/me` | JWT | Delete own account |

### Vehicles

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/vehicles/` | JWT | Register a vehicle |
| GET | `/vehicles/search?plate=` | — | Fuzzy search by plate |
| GET | `/vehicles/search/attributes?color=&vehicle_type=` | — | Search by color / type |
| GET | `/vehicles/user/me` | JWT | List my vehicles |
| GET | `/vehicles/history?plate=` | JWT | Parking history |
| GET | `/vehicles/{plate}/location` | JWT | Current slot location |
| GET | `/vehicles/{plate}/map` | JWT | Floor map path |
| POST | `/vehicles/{plate}/exit` | Admin | Mark vehicle as exited |

### Parking Slots

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/slots/available` | — | List free slots |
| GET | `/slots/all` | JWT | List all slots |
| GET | `/slots/occupancy` | JWT | Occupancy summary |
| GET | `/slots/{slot_id}` | JWT | Get one slot |
| POST | `/slots/` | Admin | Create a slot |
| PATCH | `/slots/{slot_id}` | Admin | Override slot status |

### AI Integration

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/ai/scan-result` | — | Receive scan from AI vision service |

### Floors & Sections

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/floors/all` | JWT | List all floors |
| GET | `/floors/{floor_id}` | JWT | Get one floor |
| GET | `/sections/all` | JWT | List all sections |
| GET | `/sections/{section_id}` | JWT | Get one section |

### Cameras

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/cameras/all` | Admin | List all cameras |
| GET | `/cameras/active` | Admin | List active cameras |
| GET | `/cameras/stats` | Admin | Camera statistics |
| GET | `/cameras/{camera_id}` | Admin | Get one camera |
| POST | `/cameras/` | Admin | Register a camera |
| PATCH | `/cameras/{camera_id}` | Admin | Update a camera |

### Admin & Analytics

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/admin/summary` | Admin | Facility overview |
| GET | `/admin/users` | Admin | List all users |
| POST | `/admin/users` | Admin | Create admin account |
| PUT | `/admin/users/{user_id}` | Admin | Update user |
| DELETE | `/admin/users/{user_id}` | Admin | Delete user |
| GET | `/admin/analytics/summary` | Admin | Occupancy KPIs |
| GET | `/admin/analytics/peak-hours` | Admin | Hourly entry stats |
| GET | `/admin/analytics/heatmap` | Admin | Per-slot usage heatmap |
| GET | `/admin/analytics/history` | Admin | Full parking timeline |
| GET | `/admin/analytics/export/pdf` | Admin | Download PDF report |

---

## 🔑 Example Usage

### Register a new user

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Ali", "email": "ali@example.com", "password": "Secret@123"}'
```

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "ali@example.com", "password": "Secret@123"}'
```

### AI service reports a vehicle arrival

```bash
curl -X POST http://localhost:8000/ai/scan-result \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "arrival",
    "slot_id": "F2-A-05",
    "plate_text": "ABC1234",
    "color": "white",
    "car_type": "sedan",
    "plate_confidence": 0.97
  }'
```

### Search for a car

```bash
curl "http://localhost:8000/vehicles/search?plate=ABC1234"
```

### Admin — get analytics summary

```bash
curl http://localhost:8000/admin/analytics/summary \
  -H "Authorization: Bearer <admin-token>"
```

---

## 🗄️ Database

**SQLite** is used by default — the file `go2car.db` is created automatically.

To switch to **PostgreSQL**, update `.env`:

```
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/go2car_db
```

Then install the driver:

```bash
pip install psycopg2-binary
```

---

## 🔮 Future Improvements

- [ ] Real-time slot updates via WebSocket
- [ ] Rate limiting and API key auth for the AI service endpoint
- [ ] Alembic database migrations
- [ ] Dockerized deployment with Docker Compose
- [ ] Unit and integration test suite
- [ ] Image storage for detection snapshots
- [ ] Push notifications for parking session events

---

## 📄 License

This project was built as a graduation project.
