# Go2Car API Documentation

> Backend API for the **Go2Car AI Smart Parking System**.  
> Handles vehicle detection from the AI module, lets users find their parked car, and provides admin analytics.

---

## Table of Contents

- [Base URL](#base-url)
- [Authentication](#authentication)
- [Endpoints](#endpoints)
  - [Auth](#auth)
  - [Vehicles](#vehicles)
  - [Parking Slots](#parking-slots)
  - [AI Integration](#ai-integration)
  - [Admin](#admin)
  - [Users (Me)](#users-me)
  - [Floors](#floors)
  - [Sections](#sections)
  - [Cameras](#cameras)
  - [Health](#health)
- [Data Schemas](#data-schemas)
- [Response Codes](#response-codes)

---

## Base URL

```
https://api.go2car.app
```

---

## Authentication

Go2Car uses **JWT Bearer Token** authentication.

1. Call `POST /auth/login` with your email and password.
2. Copy the `access_token` from the response.
3. Include it in the `Authorization` header for all protected endpoints.

```
Authorization: Bearer <your_access_token>
```

> Endpoints marked with 🔒 require a valid Bearer token.

---

## Endpoints

---

### Auth

#### `POST /auth/register`

Register a new user account.

**Request Body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✅ | User's full name |
| `email` | string (email) | ✅ | User's email address |
| `password` | string | ✅ | User's password |

**Request Example**

```json
{
  "name": "Ahmed Samy",
  "email": "ahmed@example.com",
  "password": "SecurePass123"
}
```

**Response `201`** — [`UserOut`](#userout)

```json
{
  "id": 1,
  "name": "Ahmed Samy",
  "email": "ahmed@example.com",
  "is_admin": false
}
```

---

#### `POST /auth/login`

Login with email and password. Returns a JWT access token and user info.

**Request Body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string (email) | ✅ | Registered email |
| `password` | string | ✅ | Account password |

**Request Example**

```json
{
  "email": "ahmed@example.com",
  "password": "SecurePass123"
}
```

**Response `200`** — [`LoginResponse`](#loginresponse)

```json
{
  "token": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  },
  "user": {
    "id": 1,
    "name": "Ahmed Samy",
    "email": "ahmed@example.com",
    "is_admin": false
  }
}
```

---

#### `GET /auth/verify-email`

Verify a user's email using the token sent to their inbox. Typically triggered via a link in the verification email. Returns a JWT token on success, allowing immediate login.

**Query Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `token` | string | ✅ | Email verification token |

**Request Example**

```
GET /auth/verify-email?token=abc123verifytoken
```

**Response `200`** — [`LoginResponse`](#loginresponse)

---

#### `POST /auth/logout` 🔒

Logs out the currently authenticated user and invalidates the session.

**Response `200`** — `{}`

---

### Vehicles

#### `POST /vehicles/`

Register a new vehicle in the system.

**Query Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | integer | ❌ | ID of the user to assign the vehicle to (default: `1`) |

**Request Body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `plate_number` | string | ✅ | Vehicle licence plate |
| `color` | string \| null | ❌ | Vehicle color |
| `vehicle_type` | string \| null | ❌ | e.g. `sedan`, `SUV`, `truck` |

**Request Example**

```json
{
  "plate_number": "ABC-1234",
  "color": "white",
  "vehicle_type": "sedan"
}
```

**Response `200`** — `{}`

---

#### `GET /vehicles/search`

🔍 **Primary search** — find a vehicle by partial plate number.

**Query Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plate` | string | ✅ | Full or partial licence plate to search for |

**Request Example**

```
GET /vehicles/search?plate=ABC-1234
```

**Response `200`** — `{}`

---

#### `GET /vehicles/search/attributes`

🔍 **Fallback search** — find parked vehicles by color and/or vehicle type. Useful when the user doesn't remember their exact plate number.

**Query Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `color` | string \| null | ❌ | Vehicle color, e.g. `white`, `red` |
| `vehicle_type` | string \| null | ❌ | Vehicle type, e.g. `sedan`, `SUV` |

**Request Example**

```
GET /vehicles/search/attributes?color=white&vehicle_type=sedan
```

**Response `200`** — `{}`

---

#### `GET /vehicles/history`

View the full parking history of all vehicles. Optionally filter by plate number. Admin use.

**Query Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plate` | string \| null | ❌ | Filter history to a specific plate |

**Response `200`** — `{}`

---

#### `GET /vehicles/user/me`

Get all vehicles registered to the current user.

**Query Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | integer | ❌ | User ID (default: `1`) |

**Response `200`** — `{}`

---

#### `GET /vehicles/{plate}/location`

Get the slot and floor where a specific vehicle is currently parked.

**Path Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plate` | string | ✅ | Vehicle licence plate |

**Response `200`** — `{}`

---

#### `GET /vehicles/{plate}/map`

Get the map path to navigate to the vehicle's parking slot.

**Path Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plate` | string | ✅ | Vehicle licence plate |

**Response `200`** — `{}`

---

#### `POST /vehicles/{plate}/exit`

🚗 Mark a vehicle as exited and free up its parking slot.

**Path Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plate` | string | ✅ | Licence plate of the exiting vehicle |

**Response `200`** — `{}`

---

### Parking Slots

#### `GET /slots/available`

Return all currently free (unoccupied) parking slots.

**Response `200`** — array of [`ParkingSlotOut`](#parkingslotout)

```json
[
  {
    "id": 3,
    "slot_code": "A-03",
    "section": {
      "id": 1,
      "section_code": "SEC-A",
      "section_name": "Section A",
      "floor": {
        "id": 1,
        "floor_code": "F1",
        "floor_name": "Ground Floor"
      }
    },
    "is_occupied": false,
    "last_updated": "2025-04-21T10:30:00Z"
  }
]
```

---

#### `GET /slots/all`

Return all parking slots — both occupied and free.

**Response `200`** — array of [`ParkingSlotOut`](#parkingslotout)

---

#### `GET /slots/occupancy`

Returns real-time occupancy statistics for the entire parking facility.

**Response `200`** — [`SlotOccupancyOut`](#slotoccupancyout)

```json
{
  "total_slots": 120,
  "occupied_slots": 87,
  "free_slots": 33,
  "occupancy_percentage": 72.5
}
```

---

#### `GET /slots/{slot_id}`

Return a single parking slot by its ID.

**Path Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `slot_id` | integer | ✅ | The unique slot ID |

**Response `200`** — [`ParkingSlotOut`](#parkingslotout)

---

#### `PATCH /slots/{slot_id}`

Manually override the occupied status of a slot. Useful for administrative corrections.

**Path Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `slot_id` | integer | ✅ | The unique slot ID |

**Request Body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `is_occupied` | boolean | ✅ | New occupancy status for the slot |

**Request Example**

```json
{
  "is_occupied": false
}
```

**Response `200`** — [`ParkingSlotOut`](#parkingslotout)

---

#### `POST /slots/`

Admin — add a new parking slot to the system.

**Request Body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `slot_code` | string | ✅ | Unique code for the slot, e.g. `A-15` |
| `section_id` | integer | ✅ | ID of the section this slot belongs to |

**Request Example**

```json
{
  "slot_code": "A-15",
  "section_id": 2
}
```

**Response `201`** — [`ParkingSlotOut`](#parkingslotout)

---

### AI Integration

> ⚠️ This endpoint is called **automatically** by the external AI vision service after processing a camera snapshot. The frontend team does **not** need to call this directly — it is documented here for full system understanding.

#### `POST /ai/scan-result`

📡 Called by the AI module after processing a camera frame.

**Flow:**
- `has_car: false` → backend frees the slot
- `has_car: true` → backend registers the vehicle and marks the slot as occupied

**Request Body** — [`SlotScanResult`](#slotscanresult)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `slot_code` | string | ✅ | Which slot was scanned |
| `has_car` | boolean | ✅ | Whether a vehicle was detected |
| `plate` | string \| null | ❌ | Detected plate (present when `has_car: true`) |
| `color` | string \| null | ❌ | Detected color (present when `has_car: true`) |
| `vehicle_type` | string \| null | ❌ | Detected vehicle type (present when `has_car: true`) |

**Request Example — vehicle detected**

```json
{
  "slot_code": "A-12",
  "has_car": true,
  "plate": "ABC-1234",
  "color": "white",
  "vehicle_type": "sedan"
}
```

**Request Example — slot empty**

```json
{
  "slot_code": "A-12",
  "has_car": false
}
```

**Response `200`** — [`SlotScanResponse`](#slotscanresponse)

```json
{
  "message": "Vehicle recorded successfully",
  "slot_code": "A-12",
  "has_car": true,
  "plate": "ABC-1234"
}
```

---

### Admin

> All admin endpoints require a valid Bearer token from an **admin** account.

#### `GET /admin/summary` 🔒

Returns a high-level analytics summary of the parking system — occupancy rates, user counts, and other admin-level stats.

**Response `200`** — `{}`

---

#### `GET /admin/users` 🔒

Returns a list of all registered users.

**Response `200`** — array of [`UserOut`](#userout)

```json
[
  { "id": 1, "name": "Ahmed Samy", "email": "ahmed@example.com", "is_admin": false },
  { "id": 2, "name": "Sara Admin", "email": "sara@go2car.app", "is_admin": true }
]
```

---

#### `POST /admin/users` 🔒

Create a new admin user account.

**Request Body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✅ | Admin's full name |
| `email` | string (email) | ✅ | Admin's email address |
| `password` | string | ✅ | Admin's password |

**Response `200`** — [`UserOut`](#userout)

---

#### `PUT /admin/users/{user_id}` 🔒

Update any user's details or admin status.

**Path Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | integer | ✅ | Target user's ID |

**Request Body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string (email) \| null | ❌ | New email address |
| `name` | string \| null | ❌ | New full name |
| `is_admin` | boolean \| null | ❌ | Set or revoke admin privileges |

**Request Example**

```json
{
  "name": "Ahmed Updated",
  "is_admin": true
}
```

**Response `200`** — [`UserOut`](#userout)

---

#### `DELETE /admin/users/{user_id}` 🔒

Permanently delete a user account.

**Path Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | integer | ✅ | Target user's ID |

**Response `200`** — `{}`

---

#### `GET /admin/analytics/summary`

Get parking KPIs and occupancy statistics.

**Response `200`** — `{}`

---

#### `GET /admin/analytics/peak-hours`

Get hourly parking activity statistics to identify the busiest periods.

**Response `200`** — `{}`

---

#### `GET /admin/analytics/heatmap`

Per-slot usage analytics — useful for identifying consistently busy or underused areas.

**Response `200`** — `{}`

---

#### `GET /admin/analytics/history`

Get a historical timeline of parking activity.

**Response `200`** — `{}`

---

#### `GET /admin/analytics/export/pdf`

Export all parking analytics as a downloadable PDF report.

**Response `200`** — `{}`

---

### Users (Me)

> All `/users/me` endpoints require a valid Bearer token.

#### `GET /users/me` 🔒

Returns the authenticated user's profile.

**Response `200`** — [`UserOut`](#userout)

```json
{
  "id": 1,
  "name": "Ahmed Samy",
  "email": "ahmed@example.com",
  "is_admin": false
}
```

---

#### `PUT /users/me` 🔒

Update the authenticated user's name or email.

**Request Body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string (email) \| null | ❌ | New email address |
| `name` | string \| null | ❌ | New full name |

**Response `200`** — [`UserOut`](#userout)

---

#### `DELETE /users/me` 🔒

Permanently delete the authenticated user's own account.

**Response `200`** — `{}`

---

#### `PUT /users/me/password` 🔒

Change the authenticated user's password. Requires the current password for verification.

**Request Body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `old_password` | string | ✅ | Current password |
| `new_password` | string | ✅ | New desired password |

**Request Example**

```json
{
  "old_password": "OldPass123",
  "new_password": "NewPass456"
}
```

**Response `200`** — `{}`

---

### Floors

#### `GET /floors/all`

Returns all parking floors in the facility.

**Response `200`** — array of [`ParkingFloorOut`](#parkingfloorout)

```json
[
  { "id": 1, "floor_code": "F1", "floor_name": "Ground Floor" },
  { "id": 2, "floor_code": "F2", "floor_name": "First Floor" }
]
```

---

#### `GET /floors/{floor_id}`

Returns a single floor by its ID.

**Path Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `floor_id` | integer | ✅ | Floor ID |

**Response `200`** — [`ParkingFloorOut`](#parkingfloorout)

---

### Sections

#### `GET /sections/all`

Returns all parking sections across all floors.

**Response `200`** — array of [`ParkingSectionOut`](#parkingsectionout)

```json
[
  {
    "id": 1,
    "section_code": "SEC-A",
    "section_name": "Section A",
    "floor": { "id": 1, "floor_code": "F1", "floor_name": "Ground Floor" }
  }
]
```

---

#### `GET /sections/{section_id}`

Returns a single section by its ID, including its floor details.

**Path Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `section_id` | integer | ✅ | Section ID |

**Response `200`** — [`ParkingSectionOut`](#parkingsectionout)

---

### Cameras

#### `GET /cameras/all`

Returns all cameras registered in the system.

**Response `200`** — array of [`CameraOut`](#cameraout)

```json
[
  {
    "id": 1,
    "name": "Entrance Cam A",
    "location_description": "Main entrance gate, ground floor",
    "is_active": true,
    "section": {
      "id": 1,
      "section_code": "SEC-A",
      "section_name": "Section A",
      "floor": { "id": 1, "floor_code": "F1", "floor_name": "Ground Floor" }
    }
  }
]
```

---

#### `GET /cameras/active`

Returns only cameras that are currently active (`is_active: true`).

**Response `200`** — array of [`CameraOut`](#cameraout)

---

#### `GET /cameras/stats`

Returns a summary count of total, active, and inactive cameras.

**Response `200`** — [`CameraStats`](#camerastats)

```json
{
  "total": 10,
  "active": 8,
  "inactive": 2
}
```

---

#### `GET /cameras/{camera_id}`

Returns a single camera by its ID.

**Path Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `camera_id` | integer | ✅ | Camera ID |

**Response `200`** — [`CameraOut`](#cameraout)

---

#### `PATCH /cameras/{camera_id}`

Update a camera's name, location description, or active status.

**Path Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `camera_id` | integer | ✅ | Camera ID |

**Request Body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string \| null | ❌ | New camera name |
| `location_description` | string \| null | ❌ | Updated location description |
| `is_active` | boolean \| null | ❌ | Enable or disable the camera |

**Request Example**

```json
{
  "is_active": false,
  "location_description": "Side entrance, ground floor"
}
```

**Response `200`** — [`CameraOut`](#cameraout)

---

#### `POST /cameras/`

Register a new camera in the system.

**Request Body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✅ | Camera name |
| `location_description` | string | ✅ | Where the camera is physically located |
| `section_id` | integer | ✅ | ID of the section this camera monitors |
| `is_active` | boolean | ❌ | Whether the camera is active (default: `true`) |

**Request Example**

```json
{
  "name": "Floor 2 Cam B",
  "location_description": "North aisle, near elevator",
  "section_id": 3,
  "is_active": true
}
```

**Response `200`** — [`CameraOut`](#cameraout)

---

### Health

#### `GET /`

Health check — verifies the API is reachable and running.

**Response `200`** — `{}`

---

## Data Schemas

### `UserOut`

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique user ID |
| `name` | string | Full name |
| `email` | string | Email address |
| `is_admin` | boolean | Whether the user has admin privileges |

---

### `LoginResponse`

| Field | Type | Description |
|-------|------|-------------|
| `token` | `Token` | JWT token object |
| `user` | `UserOut` | Authenticated user info |

---

### `Token`

| Field | Type | Description |
|-------|------|-------------|
| `access_token` | string | JWT access token |
| `token_type` | string | Always `"bearer"` |

---

### `ParkingSlotOut`

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Slot ID |
| `slot_code` | string | Slot identifier code |
| `section` | `ParkingSectionOut` | Nested section details |
| `is_occupied` | boolean | Whether the slot is currently occupied |
| `last_updated` | datetime \| null | Last status change timestamp (ISO 8601) |

---

### `SlotOccupancyOut`

| Field | Type | Description |
|-------|------|-------------|
| `total_slots` | integer | Total number of slots in the system |
| `occupied_slots` | integer | Number of currently occupied slots |
| `free_slots` | integer | Number of currently free slots |
| `occupancy_percentage` | number | Percentage of slots that are occupied |

---

### `SlotStatusUpdate`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `is_occupied` | boolean | ✅ | New occupancy status to apply to the slot |

---

### `SlotScanResult`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `slot_code` | string | ✅ | Which slot was scanned |
| `has_car` | boolean | ✅ | Whether a vehicle was detected |
| `plate` | string \| null | ❌ | Detected plate (when `has_car: true`) |
| `color` | string \| null | ❌ | Detected color (when `has_car: true`) |
| `vehicle_type` | string \| null | ❌ | Detected vehicle type (when `has_car: true`) |

---

### `SlotScanResponse`

| Field | Type | Description |
|-------|------|-------------|
| `message` | string | Confirmation message |
| `slot_code` | string | Slot code that was processed |
| `has_car` | boolean | Reflected from scan input |
| `plate` | string \| null | Registered plate if applicable |

---

### `ParkingSectionOut`

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Section ID |
| `section_code` | string | Section identifier |
| `section_name` | string | Human-readable section name |
| `floor` | `ParkingFloorOut` | Nested floor details |

---

### `ParkingFloorOut`

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Floor ID |
| `floor_code` | string | Floor identifier code |
| `floor_name` | string | Human-readable floor name |

---

### `CameraOut`

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Camera ID |
| `name` | string | Camera name |
| `location_description` | string | Physical location description |
| `is_active` | boolean | Whether the camera is currently active |
| `section` | `ParkingSectionOut` | The section this camera monitors |

---

### `CameraCreate`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✅ | Camera name |
| `location_description` | string | ✅ | Physical location description |
| `section_id` | integer | ✅ | ID of the section this camera monitors |
| `is_active` | boolean | ❌ | Active status (default: `true`) |

---

### `CameraUpdate`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string \| null | ❌ | New camera name |
| `location_description` | string \| null | ❌ | Updated location description |
| `is_active` | boolean \| null | ❌ | Enable or disable the camera |

---

### `CameraStats`

| Field | Type | Description |
|-------|------|-------------|
| `total` | integer | Total number of cameras |
| `active` | integer | Number of active cameras |
| `inactive` | integer | Number of inactive cameras |

---

### `AdminUpdateUser`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string (email) \| null | ❌ | New email address |
| `name` | string \| null | ❌ | New full name |
| `is_admin` | boolean \| null | ❌ | Set or revoke admin privileges |

---

### `VehicleCreate`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `plate_number` | string | ✅ | Vehicle licence plate |
| `color` | string \| null | ❌ | Vehicle color |
| `vehicle_type` | string \| null | ❌ | e.g. `sedan`, `SUV`, `truck` |

---

## Response Codes

| Code | Meaning |
|------|---------|
| `200 OK` | Request succeeded |
| `201 Created` | Resource created successfully |
| `422 Unprocessable Entity` | Validation error — check your request body or parameters |
| `401 Unauthorized` | Missing or invalid Bearer token |

---

*Go2Car API v1.0.0 · OpenAPI 3.1.0*