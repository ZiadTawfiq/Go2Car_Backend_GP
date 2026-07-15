<p align="center">
  <h1 align="center">🚗 Go2Car — AI-Powered Smart Parking System</h1>
  <p align="center">
    <strong>A production-grade REST API that bridges computer-vision vehicle detection with a mobile app,<br>enabling drivers to locate their parked car in seconds.</strong>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/python-3.10+-blue?logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/FastAPI-0.135-009688?logo=fastapi&logoColor=white" alt="FastAPI">
    <img src="https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white" alt="SQLAlchemy">
    <img src="https://img.shields.io/badge/PostgreSQL-SQLite-336791?logo=postgresql&logoColor=white" alt="Database">
    <img src="https://img.shields.io/badge/JWT-Auth-orange?logo=jsonwebtokens&logoColor=white" alt="JWT">
    <img src="https://img.shields.io/badge/Railway-Deployed-0B0D0E?logo=railway&logoColor=white" alt="Railway">
    <img src="https://img.shields.io/badge/License-GP%20Project-lightgrey" alt="License">
  </p>
</p>

---

## 📋 Table of Contents

- [The Problem](#-the-problem)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [AI Pipeline & Communication](#-ai-pipeline--communication)
- [Parking Workflow](#-parking-workflow)
- [Project Structure](#-project-structure)
- [Technology Stack](#-technology-stack)
- [Database Design](#-database-design)
- [API Reference](#-api-reference)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [Screenshots](#-screenshots)
- [Engineering Practices](#-engineering-practices)
- [Why This Project Is Interesting](#-why-this-project-is-interesting)
- [Future Improvements](#-future-improvements)

---

## 🎯 The Problem

In large multi-level parking garages, drivers waste an average of **8 minutes** searching for their parked car. Go2Car solves this by integrating an AI computer-vision pipeline with a backend API that:

1. **Detects vehicles** via camera-equipped parking sections  
2. **Recognizes license plates**, vehicle colors, and types automatically  
3. **Tracks occupancy** in real time across floors, sections, and individual slots  
4. **Enables instant search** — users find their car by plate number, color, or vehicle type  

The backend serves as the central nervous system, receiving AI scan results from edge cameras, managing the parking state machine, and exposing search/analytics APIs to the companion mobile app and admin dashboard.

---

## ✨ Key Features

| Category | Details |
|----------|---------|
| **AI Vision Integration** | Receives per-slot scan results from cameras, auto-registers vehicles on arrival and frees slots on departure |
| **Vehicle Search** | Fuzzy plate search, attribute-based search (color, type), and multi-filter advanced search with floor/section filtering |
| **Multi-Level Parking Model** | Hierarchical `Floor → Section → Slot` structure with camera-to-section mapping |
| **Slot Reservations** | Users book slots in advance with overlap protection; admins approve/reject bookings |
| **Admin Analytics** | Occupancy KPIs, peak-hour analysis, per-slot usage heatmap, historical timeline, and PDF report export |
| **Detection Logging** | Every AI scan is logged for audit trails with admin-reviewable flagged entries |
| **Auth & Security** | JWT with JTI-based token blacklisting (secure logout), bcrypt password hashing, email verification via SendGrid |
| **Guest Access** | Short-lived guest tokens for anonymous browsing without registration |
| **Role-Based Access** | Public, authenticated, and admin-only endpoint tiers |
| **Vehicle Ownership** | Many-to-many user–vehicle relationship; users register, update, and transfer vehicle ownership |
| **Image Storage** | Base64 image uploads from AI cameras saved to static storage and linked to parking records |
| **Arabic Plate Normalization** | Transliterates Arabic numerals (٠–٩) to English for consistent plate matching |
| **Floor Maps** | Section-aware map image paths returned for mobile app navigation |

---

## 🏗️ System Architecture

```mermaid
flowchart LR
    CAM["📷 AI Vision<br>Service"] -- "POST /ai/scan-result<br>(arrival / departure)" --> API
    APP["📱 Mobile<br>App"] -- "Search · History<br>Reserve · Auth" --> API
    DASH["🖥️ Admin<br>Dashboard"] -- "Analytics · Users<br>Cameras · Slots" --> API

    subgraph API["FastAPI Backend"]
        direction TB
        R["Routes<br><i>API Layer</i>"] --> S["Services<br><i>Business Logic</i>"]
        S --> M["Models<br><i>ORM Layer</i>"]
        M --> DB[("SQLite / PostgreSQL")]
        R --> D["Dependencies<br><i>Auth Guards</i>"]
    end

    API -- "Static Files" --> FS[("📁 File System<br>Maps · Uploads")]
    API -- "Email" --> SG["📧 SendGrid"]
```

### Component Responsibilities

| Component | Role |
|-----------|------|
| **Routes** | HTTP endpoint handlers — input parsing, auth enforcement, response formatting |
| **Dependencies** | JWT extraction, token blacklist checking, role-based guards (`get_current_user`, `get_current_admin`) |
| **Services** | Business logic — parking state machine, search algorithms, analytics aggregation |
| **Models** | SQLAlchemy ORM definitions with relationships, indexes, and computed properties |
| **Schemas** | Pydantic v2 models for request validation and response serialization |
| **Core** | Configuration management (`pydantic-settings`) and security utilities (JWT, bcrypt) |
| **Database** | SQLAlchemy engine + session factory with per-request lifecycle via FastAPI `Depends` |

---

## 🤖 AI Pipeline & Communication

The AI vision service runs independently (edge device / separate server) and communicates with the backend via a single REST endpoint.

### How It Works

```mermaid
sequenceDiagram
    participant Camera as 📷 Camera Sensor
    participant AI as 🧠 AI Vision Service
    participant API as ⚡ FastAPI Backend
    participant DB as 🗄️ Database

    Note over Camera,AI: Camera captures frame
    Camera->>AI: Image frame
    
    Note over AI: AI Pipeline Processes:
    Note over AI: 1. Vehicle Detection (present/absent)
    Note over AI: 2. License Plate OCR
    Note over AI: 3. Color Classification
    Note over AI: 4. Vehicle Type Classification

    AI->>API: POST /ai/scan-result
    Note right of AI: {event_type, slot_id,<br>plate_text, color, car_type,<br>plate_confidence, image_base64}

    alt event_type = "arrival"
        API->>DB: Log detection entry
        API->>DB: Upsert Vehicle (create or enrich)
        API->>DB: Guard duplicate active sessions
        API->>DB: Create ParkingRecord (active)
        API->>DB: Mark slot as occupied
        API-->>AI: ✅ Vehicle parked
    else event_type = "departure"
        API->>DB: Log detection entry
        API->>DB: Close ParkingRecord (set exit_time)
        API->>DB: Free slot (is_occupied = false)
        API-->>AI: ✅ Slot freed
    else event_type = "error:*"
        API->>DB: Log detection (flagged for review)
        API->>DB: Register vehicle with available data
        API-->>AI: ⚠️ Processed with flag
    end
```

### AI Payload Schema

```json
{
  "event_type": "arrival",
  "camera_id": "F1_A1",
  "slot_id": "F1_A1_3",
  "plate_text": "ABC1234",
  "plate_confidence": 0.97,
  "color": "white",
  "color_confidence": 0.92,
  "car_type": "sedan",
  "car_type_confidence": 0.88,
  "image_base64": "/9j/4AAQSkZJRg..."
}
```

### Key Design Decisions

- **Detection Logging**: Every inbound scan is logged to `detection_logs` *before* business logic, ensuring a complete audit trail regardless of processing outcome
- **Idempotent Arrivals**: Re-scanning an already-parked vehicle is a no-op; scanning the same slot with a different plate updates the record (handles LPR refinement)
- **Unknown Plates**: When OCR fails, a placeholder `UNKNOWN-{slot_code}` is generated so occupancy tracking remains accurate; admins can correct it later
- **Image Persistence**: Base64 images from the AI are decoded and saved to `static/uploads/` with timestamped filenames, then linked to the parking record

---

## 🔄 Parking Workflow

### Complete Vehicle Lifecycle

```mermaid
stateDiagram-v2
    [*] --> SlotAvailable: Slot exists in system

    SlotAvailable --> SlotBooked: User creates reservation
    SlotBooked --> SlotAvailable: Reservation cancelled/rejected

    SlotAvailable --> SlotOccupied: AI sends arrival scan
    SlotBooked --> SlotOccupied: AI sends arrival scan

    SlotOccupied --> SlotOccupied: AI re-scans (idempotent)
    SlotOccupied --> PlateRefined: AI sends updated plate
    PlateRefined --> SlotOccupied: Record updated

    SlotOccupied --> SlotAvailable: AI sends departure scan
    SlotOccupied --> SlotAvailable: Admin triggers exit

    note right of SlotOccupied
        ParkingRecord is_active = true
        Vehicle linked to slot
        Image stored if provided
    end note
```

### Step-by-Step Flow

| Step | Actor | Action | Backend Response |
|------|-------|--------|-----------------|
| 1 | 📷 AI Camera | Detects vehicle entering slot `F1_A1_3` | — |
| 2 | 🧠 AI Service | Runs LPR + classification pipeline | — |
| 3 | 🧠 AI Service | `POST /ai/scan-result` with arrival data | — |
| 4 | ⚡ Backend | Logs raw detection to `detection_logs` | — |
| 5 | ⚡ Backend | Creates/retrieves `Vehicle` record | — |
| 6 | ⚡ Backend | Creates `ParkingRecord` (active) | — |
| 7 | ⚡ Backend | Marks `ParkingSlot` as occupied | `"Vehicle parked successfully"` |
| 8 | 📱 User | `GET /vehicles/search?plate=ABC` | Returns slot, section, floor |
| 9 | 📱 User | `GET /vehicles/{plate}/map` | Returns floor map image path |
| 10 | 📷 AI Camera | Detects slot is empty (departure) | — |
| 11 | ⚡ Backend | Closes `ParkingRecord`, frees slot | `"Slot freed"` |

---

## 📁 Project Structure

```
Go2Car_Backend_GP/
├── app/
│   ├── main.py                    # FastAPI app, CORS, router registration, table init
│   ├── utils.py                   # Plate normalization (Arabic→English transliteration)
│   ├── core/
│   │   ├── config.py              # Pydantic-settings (reads .env)
│   │   └── security.py            # JWT create/decode, bcrypt hashing, JTI generation
│   ├── db/
│   │   └── database.py            # SQLAlchemy engine, session factory, get_db dependency
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── user.py                # User (email verification, admin flag, user_type)
│   │   ├── vehicle.py             # Vehicle (plate, color, type) + M2M user_vehicles
│   │   ├── parking_floor.py       # Floor → has many Sections
│   │   ├── parking_section.py     # Section → has many Slots & Cameras
│   │   ├── parking_slot.py        # Slot (occupied, type, status property incl. "booked")
│   │   ├── parking_record.py      # Parking session (entry/exit, image_path, partial index)
│   │   ├── camera.py              # Camera (name, active flag, section FK)
│   │   ├── detection_log.py       # Raw AI detection audit log
│   │   ├── reservation.py         # Slot reservation (status enum, time range, user/vehicle)
│   │   └── blacklist_token.py     # Revoked JWT tokens (JTI-based)
│   ├── schemas/                   # Pydantic v2 request/response models
│   │   ├── ai.py                  # SlotScanResult, ParkVehicleRequest (property mapping)
│   │   ├── user.py                # Register, Login, Token, LoginResponse, AdminUpdate
│   │   ├── vehicle.py             # VehicleCreate, VehicleSearchRequest (advanced filters)
│   │   ├── parking_slot.py        # ParkingSlotOut, SlotOccupancyOut, SlotTypeUpdate
│   │   ├── parking_floor.py       # ParkingFloorOut
│   │   ├── parking_section.py     # ParkingSectionOut (nested floor)
│   │   ├── parking_record.py      # ParkingRecordOut
│   │   ├── camera.py              # CameraOut, CameraCreate, CameraStats
│   │   ├── detection_log.py       # DetectionLogOut
│   │   └── reservation.py         # ReservationCreate, ReservationResponse
│   ├── services/                  # Business logic layer
│   │   ├── ai_service.py          # Scan handler, vehicle-slot assignment, image upload
│   │   ├── vehicle_service.py     # Search (fuzzy/attribute/advanced), history, CRUD
│   │   ├── auth_service.py        # Register, login, email verification, logout
│   │   ├── admin_service.py       # Analytics, user CRUD, PDF export (ReportLab)
│   │   ├── slot_service.py        # Slot CRUD, occupancy stats, map lookup
│   │   ├── reservation_service.py # Booking lifecycle, overlap protection, approval flow
│   │   ├── camera_service.py      # Camera CRUD + statistics
│   │   ├── detection_log_service.py # Detection log queries (all, flagged)
│   │   ├── floor_service.py       # Floor queries
│   │   ├── section_service.py     # Section queries
│   │   └── user_service.py        # Profile update, password change, account deletion
│   └── routes/                    # API routers
│       ├── dependencies.py        # get_db, get_current_user (JWT + blacklist), get_current_admin
│       ├── auth.py                # /auth/* — register, login, verify-email, logout, guest
│       ├── user.py                # /users/* — profile CRUD
│       ├── vehicles.py            # /vehicles/* — CRUD, search (3 modes), history, map, exit
│       ├── slots.py               # /slots/* — available, all, occupancy, map, CRUD
│       ├── ai.py                  # /ai/* — scan-result receiver
│       ├── admin.py               # /admin/* — summary, users, analytics, PDF export
│       ├── reservations.py        # /reservations/* — create, cancel, approve, reject
│       ├── detection_log.py       # /detection-logs/* — all logs, flagged logs
│       ├── floor.py               # /floors/* — list, get by ID
│       ├── section.py             # /sections/* — list, get by ID
│       └── camera.py              # /cameras/* — CRUD, active, stats
├── migrations/                    # Alembic migration scripts
│   └── env.py                     # Alembic environment configuration
├── static/
│   ├── maps/                      # Section map images (served via /static/maps/)
│   └── uploads/                   # AI camera snapshots (saved from base64)
├── seed_parking_structure.py      # Idempotent garage seeder (parses garage_structure.txt)
├── seed_users.py                  # Default user/admin seeder
├── garage_structure.txt           # Multi-level garage hierarchy definition
├── alembic.ini                    # Alembic configuration
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variable template
└── postgresql_schema.sql          # PostgreSQL DDL for manual setup
```

---

## 🛠️ Technology Stack

### Backend

| Technology | Purpose |
|-----------|---------|
| **FastAPI** 0.135 | Async-capable web framework with auto-generated OpenAPI docs |
| **Uvicorn** | ASGI server |
| **Pydantic** v2 | Request/response validation with `from_attributes` ORM mode |
| **pydantic-settings** | Typed configuration from `.env` files |
| **Starlette** | CORS middleware, static file serving, `FileResponse` |

### Database

| Technology | Purpose |
|-----------|---------|
| **SQLAlchemy** 2.0 | ORM with relationship mapping, eager loading, partial indexes |
| **SQLite** | Default development database (zero-config) |
| **PostgreSQL** | Production database (swap via `DATABASE_URL`) |
| **psycopg2-binary** | PostgreSQL adapter |
| **Alembic** | Database migration framework (configured) |

### Authentication & Security

| Technology | Purpose |
|-----------|---------|
| **python-jose** | JWT token creation/verification (HS256) |
| **Passlib** + **bcrypt** | Password hashing |
| **Cryptography** | Underlying crypto primitives |

### External Services

| Technology | Purpose |
|-----------|---------|
| **SendGrid** SDK | Transactional email (verification emails with branded HTML templates) |
| **Railway** | Cloud deployment platform |

### Reporting & Media

| Technology | Purpose |
|-----------|---------|
| **ReportLab** | PDF analytics report generation |
| **Pillow** | Image processing support |

### Development Tools

| Technology | Purpose |
|-----------|---------|
| **python-dotenv** | Environment variable loading |
| **email-validator** | Email format validation in Pydantic schemas |
| **python-multipart** | Form/file upload handling |

---

## 🗄️ Database Design

### Entity Relationship Diagram

```mermaid
erDiagram
    User ||--o{ user_vehicles : owns
    Vehicle ||--o{ user_vehicles : owned_by
    Vehicle ||--o{ ParkingRecord : has
    Vehicle ||--o{ Reservation : reserved_for

    ParkingFloor ||--o{ ParkingSection : contains
    ParkingSection ||--o{ ParkingSlot : contains
    ParkingSection ||--o{ Camera : monitors

    ParkingSlot ||--o{ ParkingRecord : tracks
    ParkingSlot ||--o{ Reservation : booked_for

    Camera ||--o{ DetectionLog : generates
    ParkingSlot ||--o{ DetectionLog : scanned

    User ||--o{ Reservation : creates

    User {
        int id PK
        string email UK
        string name
        string password
        bool is_admin
        string user_type
        bool is_verified
        string verification_token
        datetime created_at
    }

    Vehicle {
        int id PK
        string plate_number UK
        string color
        string vehicle_type
    }

    ParkingFloor {
        int id PK
        string floor_code UK
        string floor_name
    }

    ParkingSection {
        int id PK
        string section_code UK
        string section_name
        int floor_id FK
    }

    ParkingSlot {
        int id PK
        string slot_code UK
        string slot_type
        int section_id FK
        bool is_occupied
        datetime last_updated
    }

    ParkingRecord {
        int id PK
        int vehicle_id FK
        int slot_id FK
        datetime entry_time
        datetime exit_time
        bool is_active
        string image_path
    }

    Camera {
        int id PK
        string name
        string location_description
        int section_id FK
        bool is_active
    }

    DetectionLog {
        int id PK
        int camera_id FK
        int slot_id FK
        string plate_number
        string vehicle_color
        string vehicle_type
        datetime detected_at
        bool flagged_for_review
    }

    Reservation {
        int id PK
        int user_id FK
        int slot_id FK
        int vehicle_id FK
        datetime start_time
        datetime end_time
        enum status
        datetime created_at
    }

    BlacklistedToken {
        int id PK
        string jti UK
        datetime created_at
    }
```

### Key Design Notes

- **Many-to-Many Ownership**: Users and Vehicles share an association table (`user_vehicles`), allowing multiple users to own the same vehicle
- **Partial Indexes** (PostgreSQL): `idx_active_parking` on `parking_records` filters on `is_active = true`; `idx_available_slots` on `parking_slots` filters on `is_occupied = false` — optimizing the most frequent queries
- **Reservation Status Enum**: `pending → active → completed/cancelled/expired` lifecycle managed by the service layer
- **Slot Status Property**: Computed dynamically — checks `is_occupied` first, then active reservations for "booked" status

---

## 📡 API Reference

> **Interactive docs**: Launch the server and visit [`/docs`](http://127.0.0.1:8000/docs) (Swagger UI) or [`/redoc`](http://127.0.0.1:8000/redoc) (ReDoc).

<details>
<summary><strong>🔐 Authentication</strong> — <code>/auth</code></summary>

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/auth/register` | — | Register new user (sends verification email) |
| `POST` | `/auth/login` | — | Login → returns JWT + user profile |
| `POST` | `/auth/login/guest` | — | Guest login → short-lived 24h token, no DB required |
| `GET` | `/auth/verify-email?token=` | — | Verify email address via token |
| `POST` | `/auth/logout` | JWT | Revoke current token (JTI blacklisting) |

</details>

<details>
<summary><strong>👤 Users</strong> — <code>/users</code></summary>

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/users/me` | JWT | Get current user profile |
| `PUT` | `/users/me` | JWT | Update name or email |
| `PUT` | `/users/me/password` | JWT | Change password (requires old password) |
| `DELETE` | `/users/me` | JWT | Delete own account |

</details>

<details>
<summary><strong>🚘 Vehicles</strong> — <code>/vehicles</code></summary>

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/vehicles/` | JWT | Register a vehicle (creates or links ownership) |
| `GET` | `/vehicles/search?plate=` | — | Fuzzy search by partial plate |
| `GET` | `/vehicles/search/plate?plate=` | — | Search parked vehicles by plate (returns location) |
| `GET` | `/vehicles/search/attributes?color=&vehicle_type=` | — | Search by color and/or type |
| `GET` | `/vehicles/search/advanced?plate_number=&color=&type=&floor=&section=` | — | Multi-filter advanced search with ranking |
| `GET` | `/vehicles/user/me` | JWT | List my vehicles |
| `GET` | `/vehicles/history?plate=` | JWT | Parking history (own vehicles only) |
| `GET` | `/vehicles/{plate}/map` | — | Floor map image path for vehicle location |
| `PATCH` | `/vehicles/{plate}` | JWT | Update vehicle color or type (owner only) |
| `DELETE` | `/vehicles/{plate}` | JWT | Remove ownership (deletes if last owner) |
| `POST` | `/vehicles/{plate}/exit` | Admin | Mark vehicle as exited, free slot |

</details>

<details>
<summary><strong>🅿️ Parking Slots</strong> — <code>/slots</code></summary>

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/slots/available` | — | List free slots (excludes booked slots) |
| `GET` | `/slots/all` | JWT | List all slots with status |
| `GET` | `/slots/occupancy` | JWT | Occupancy summary (total, occupied, free, %) |
| `GET` | `/slots/{slot_id}` | JWT | Get one slot details |
| `GET` | `/slots/{slot_id}/map` | — | Map image path for a specific slot |
| `POST` | `/slots/` | Admin | Create a new parking slot |
| `PATCH` | `/slots/{slot_id}` | Admin | Update slot type |

</details>

<details>
<summary><strong>📅 Reservations</strong> — <code>/reservations</code></summary>

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/reservations/` | JWT | Create reservation (auto-registers vehicle) |
| `GET` | `/reservations/me` | JWT | Get my reservations |
| `POST` | `/reservations/{id}/cancel` | JWT | Cancel own reservation |
| `GET` | `/reservations/all` | Admin | Get all reservations |
| `POST` | `/reservations/{id}/approve` | Admin | Approve pending reservation |
| `POST` | `/reservations/{id}/reject` | Admin | Reject/cancel reservation |

</details>

<details>
<summary><strong>📷 AI Integration</strong> — <code>/ai</code></summary>

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/ai/scan-result` | — | Receive slot scan from AI vision service |

</details>

<details>
<summary><strong>🏢 Floors & Sections</strong> — <code>/floors</code>, <code>/sections</code></summary>

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/floors/all` | — | List all floors |
| `GET` | `/floors/{floor_id}` | JWT | Get one floor |
| `GET` | `/sections/all` | — | List all sections |
| `GET` | `/sections/{section_id}` | JWT | Get one section |

</details>

<details>
<summary><strong>📹 Cameras</strong> — <code>/cameras</code></summary>

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/cameras/all` | Admin | List all cameras |
| `GET` | `/cameras/active` | Admin | List active cameras |
| `GET` | `/cameras/stats` | Admin | Camera statistics (total, active, inactive) |
| `GET` | `/cameras/{camera_id}` | Admin | Get one camera |
| `POST` | `/cameras/` | Admin | Register a camera |
| `PATCH` | `/cameras/{camera_id}` | Admin | Update camera details |

</details>

<details>
<summary><strong>🔍 Detection Logs</strong> — <code>/detection-logs</code></summary>

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/detection-logs/` | Admin | All detection logs (newest first) |
| `GET` | `/detection-logs/flagged` | Admin | Flagged logs for review |

</details>

<details>
<summary><strong>⚙️ Admin & Analytics</strong> — <code>/admin</code></summary>

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/admin/summary` | Admin | Facility overview (slots, occupancy rate) |
| `GET` | `/admin/users` | Admin | List all users |
| `POST` | `/admin/users` | Admin | Create admin account |
| `PUT` | `/admin/users/{user_id}` | Admin | Update user (name, email, admin status) |
| `DELETE` | `/admin/users/{user_id}` | Admin | Delete user |
| `GET` | `/admin/analytics/summary` | Admin | Occupancy KPIs + active vehicles count |
| `GET` | `/admin/analytics/peak-hours` | Admin | Hourly entry statistics |
| `GET` | `/admin/analytics/heatmap` | Admin | Per-slot usage heatmap |
| `GET` | `/admin/analytics/history` | Admin | Full parking timeline |
| `GET` | `/admin/analytics/export/pdf` | Admin | Download PDF analytics report |

</details>

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- pip
- PostgreSQL *(optional — SQLite works out of the box)*

### 1. Clone & enter the project

```bash
git clone https://github.com/ZiadTawfiq/Go2Car_Backend_GP.git
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

Edit `.env` to set your own `SECRET_KEY` and `SENDGRID_API_KEY`.

### 5. Run the server

```bash
uvicorn app.main:app --reload
```

> The SQLite database (`go2car.db`) is created automatically on first run — no manual migration needed.

### 6. Seed the parking structure *(optional)*

```bash
python seed_parking_structure.py    # Requires PostgreSQL
python seed_users.py                # Seeds default admin/user accounts
```

### 7. Explore the API docs

| Interface | URL |
|-----------|-----|
| **Swagger UI** | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) |
| **ReDoc** | [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) |
| **Health Check** | [http://127.0.0.1:8000/](http://127.0.0.1:8000/) |

---

## 🔐 Environment Variables

```env
# Application
APP_NAME=Go2Car
APP_VERSION=1.0.0
DEBUG=true
ENVIRONMENT=development

# Database
DATABASE_URL=sqlite:///./go2car.db
# DATABASE_URL=postgresql://user:password@localhost:5432/go2car

# JWT
SECRET_KEY=your-super-secret-key-change-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# Admin Defaults
FIRST_ADMIN_EMAIL=admin@go2car.com
FIRST_ADMIN_PASSWORD=Admin@123456

# SendGrid (Email Verification)
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxx

# AI Service
AI_API_KEY=your-ai-service-api-key

# Redis (Optional)
REDIS_URL=redis://localhost:6379/0
USE_REDIS=false
```

---

## 🏛️ Engineering Practices

This project demonstrates several software engineering principles relevant to backend development:

<details>
<summary><strong>Architecture & Design Patterns</strong></summary>

| Practice | Implementation |
|----------|---------------|
| **Layered Architecture** | Strict separation: `Routes → Services → Models → Database` |
| **Service Layer Pattern** | Business logic isolated in service modules, not in route handlers |
| **Dependency Injection** | FastAPI's `Depends()` for DB sessions, auth guards, and role checks |
| **Repository Pattern** | Service functions encapsulate all database queries |
| **RESTful API Design** | Proper HTTP methods, status codes, resource-oriented URLs |

</details>

<details>
<summary><strong>Security & Auth</strong></summary>

| Practice | Implementation |
|----------|---------------|
| **JWT with JTI** | Unique token identifiers enable per-token revocation |
| **Token Blacklisting** | `BlacklistedToken` table checked on every authenticated request |
| **Password Hashing** | bcrypt via Passlib with automatic algorithm deprecation handling |
| **Role-Based Access Control** | Three-tier: public, authenticated (`get_current_user`), admin (`get_current_admin`) |
| **Email Verification** | Time-limited UUID tokens with branded HTML email templates |
| **Input Validation** | Pydantic v2 schemas enforce types, constraints, and email format |

</details>

<details>
<summary><strong>Database & Performance</strong></summary>

| Practice | Implementation |
|----------|---------------|
| **Partial Indexes** | PostgreSQL conditional indexes on `is_active` and `is_occupied` for fast lookups |
| **Eager Loading** | `joinedload()` prevents N+1 queries on related Floor/Section/Slot data |
| **Computed Properties** | `slot.status` and `slot.slot_number` derived at ORM level |
| **Idempotent Operations** | Re-scanning an occupied slot is a safe no-op |
| **Transaction Safety** | `db.rollback()` in error handlers; detection logging isolated from business flow |
| **Dual Database Support** | SQLite for development, PostgreSQL for production via single config change |

</details>

<details>
<summary><strong>Code Quality</strong></summary>

| Practice | Implementation |
|----------|---------------|
| **Configuration Management** | `pydantic-settings` with typed env vars and defaults |
| **Structured Logging** | Python `logging` module with formatted output |
| **Error Handling** | HTTPException with specific status codes and descriptive messages |
| **Data Normalization** | Arabic numeral transliteration, whitespace/dash stripping for plates |
| **Schema Separation** | Distinct Pydantic models for create, update, and response operations |
| **Seed Scripts** | Idempotent seeders for reproducible development setup |

</details>

---

## 💡 Why This Project Is Interesting

<table>
<tr>
<td width="50%">

### Engineering Challenges Solved

- **State Machine Design**: Managing the `available → booked → occupied → available` slot lifecycle with concurrent access from AI cameras and user reservations
- **AI ↔ Backend Contract**: Designing a flexible schema that handles missing OCR data, confidence scores, and image uploads while keeping the endpoint idempotent
- **Fuzzy + Ranked Search**: Multi-strategy vehicle search combining exact match, substring (ILIKE), and trigram similarity with intelligent result ranking
- **Overlap Protection**: Time-range collision detection for slot reservations preventing double-booking
- **Graceful Degradation**: When plate OCR fails, the system still tracks occupancy via placeholder plates

</td>
<td width="50%">

### Technical Depth

- **11 ORM models** with relationships, computed properties, and partial indexes
- **12 service modules** implementing distinct business domains
- **50+ REST endpoints** across 11 route groups
- **3 search strategies**: fuzzy plate, attribute-based, and multi-filter advanced with ranking
- **Complete audit trail**: Every AI scan logged independently from business processing
- **PDF report generation** with ReportLab for exportable analytics
- **Multi-tenant vehicle ownership** via many-to-many relationships
- **Arabic ↔ English numeral transliteration** for Middle Eastern plate formats

</td>
</tr>
</table>

---

## 🔮 Future Improvements

- [ ] Real-time slot updates via WebSocket  
- [ ] Rate limiting and API key authentication for the AI endpoint  
- [ ] Dockerized deployment with Docker Compose  
- [ ] Comprehensive unit and integration test suite  
- [ ] Push notifications for parking session events  
- [ ] Reservation expiry cron job  
- [ ] Image thumbnail generation for detection snapshots  
- [ ] Multi-garage support with facility-level hierarchy  
- [ ] Swagger API versioning (v1, v2)  

---

## 📄 License

This project was built as a graduation project at the Faculty of Computers and Information.

---

<p align="center">
  <sub>Built with ❤️ by the Go2Car Team</sub>
</p>
