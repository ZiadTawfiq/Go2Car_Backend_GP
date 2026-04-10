# 🚗 Go2Car — AI Smart Parking System — Backend API

A clean, production-ready FastAPI backend for the Go2Car graduation project.
The system supports AI-powered vehicle detection, parking slot management, and mobile-app car search.

---

## 🏗️ Project Structure

```
app/
├── main.py              ← FastAPI entry point
├── core/
│   ├── config.py        ← Settings (reads .env)
│   └── security.py      ← JWT + password hashing
├── db/
│   └── database.py      ← SQLAlchemy engine + session
├── models/
│   ├── user.py
│   ├── vehicle.py
│   ├── parking_slot.py
│   └── parking_record.py
├── schemas/
│   ├── user.py
│   ├── vehicle.py
│   ├── parking_slot.py
│   ├── parking_record.py
│   └── ai.py
├── services/
│   ├── auth_service.py
│   ├── vehicle_service.py
│   ├── slot_service.py
│   ├── ai_service.py
│   └── admin_service.py
└── routes/
    ├── dependencies.py  ← JWT auth guards
    ├── auth.py
    ├── vehicles.py
    ├── slots.py
    ├── ai.py
    └── admin.py
```

---

## ⚡ Quick Start

### 1. Clone & enter the project
```bash
cd Go2Car_Backend_GP
```

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
copy .env.example .env      # Windows
# cp .env.example .env      # Mac/Linux
```
Edit `.env` if needed (default uses SQLite — no setup required).

### 5. Run the server
```bash
uvicorn app.main:app --reload
```

### 6. Open the interactive docs
- Swagger UI → http://127.0.0.1:8000/docs
- ReDoc      → http://127.0.0.1:8000/redoc

---

## 📡 API Reference

### 🔐 Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login → get JWT token |
| GET | `/auth/users/me` | Get current user profile |

### 🚗 Vehicles

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/vehicles/search?plate=ABC123` | **Find car by plate** |
| GET | `/vehicles/search-by-attributes?color=white&type=sedan` | Fallback search |
| POST | `/vehicles/exit` | Process vehicle exit |

### 🅿️ Parking Slots

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/slots/available` | List free slots |
| GET | `/slots/all` | List all slots |
| POST | `/slots/` | Create slot (admin only) |

### 🤖 AI Integration

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ai/detect` | **AI sends detection data** |

### 📊 Admin

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/summary` | Facility analytics (admin only) |

---

## 🔄 Example Requests (curl)

### Register
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@go2car.com", "password": "secret123"}'
```

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@go2car.com", "password": "secret123"}'
```

### AI detects a car
```bash
curl -X POST http://localhost:8000/ai/detect \
  -H "Content-Type: application/json" \
  -d '{
    "plate": "ABC123",
    "slot_code": "F2-A-05",
    "floor": 2,
    "color": "white",
    "type": "sedan"
  }'
```

### Search for a car
```bash
curl "http://localhost:8000/vehicles/search?plate=ABC123"
```

### Vehicle exits
```bash
curl -X POST http://localhost:8000/vehicles/exit \
  -H "Content-Type: application/json" \
  -d '{"plate": "ABC123"}'
```

### Search by attributes
```bash
curl "http://localhost:8000/vehicles/search-by-attributes?color=white&type=sedan"
```

### Admin summary (requires admin JWT)
```bash
curl http://localhost:8000/admin/summary \
  -H "Authorization: Bearer <your-admin-token>"
```

---

## 🗄️ Database

The project uses **SQLite by default** — the file `go2car.db` is created automatically on first run.

To switch to **PostgreSQL**, update `.env`:
```
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/go2car_db
```
Then install: `pip install psycopg2-binary`

---

## 🔐 Creating an Admin User

Register normally, then open the database and set `is_admin = 1`:
```bash
# SQLite
sqlite3 go2car.db "UPDATE users SET is_admin=1 WHERE email='admin@go2car.com';"
```

Or register with `"is_admin": true` in the request body (useful for dev).

---

## 🔄 System Flow

```
AI Camera
   │
   ▼
POST /ai/detect
   │
   ├─ Upsert vehicle record
   ├─ Create ParkingRecord (is_active=true)
   └─ Mark ParkingSlot.is_occupied=true

Mobile App
   │
   ▼
GET /vehicles/search?plate=ABC123
   │
   └─ Returns: { slot_code: "F2-A-05", floor: 2 }

Vehicle leaves
   │
   ▼
POST /vehicles/exit { "plate": "ABC123" }
   │
   ├─ ParkingRecord.is_active = false
   ├─ ParkingRecord.exit_time = now()
   └─ ParkingSlot.is_occupied = false
```
