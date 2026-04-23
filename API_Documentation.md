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

**Response `201`**

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

**Response `200`**

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

Verify a user's email using the token sent to their inbox. Typically triggered via a link in the verification email.

**Query Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `token` | string | ✅ | Email verification token |

**Request Example**

```
GET /auth/verify-email?token=abc123verifytoken
```

**Response `200`** — `{}`

---

#### `POST /auth/logout` 🔒

Logs out the currently authenticated user and invalidates the session.

**Response `200`** — `{}`

---

### Vehicles

#### `GET /vehicles/search`

🔍 **Primary search** — find where a vehicle is currently parked by its license plate number.

**Query Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plate` | string | ✅ | License plate number to search for |

**Request Example**

```
GET /vehicles/search?plate=ABC-1234
```

**Response `200`**

```json
{
  "plate_number": "ABC-1234",
  "slot_code": "A-12",
  "floor": 2
}
```

---

#### `GET /vehicles/search-by-attributes`

🔍 **Fallback search** — find parked vehicles by color and/or type. Useful when the user doesn't remember their exact plate number. Returns an array of matches.

**Query Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `color` | string \| null | ❌ | Vehicle color, e.g. `white`, `red` |
| `type` | string \| null | ❌ | Vehicle type, e.g. `sedan`, `SUV` |

**Request Example**

```
GET /vehicles/search-by-attributes?color=white&type=sedan
```

**Response `200`**

```json
[
  {
    "plate_number": "ABC-1234",
    "slot_code": "A-12",
    "floor": 1
  },
  {
    "plate_number": "XYZ-5678",
    "slot_code": "B-05",
    "floor": 2
  }
]
```

---

#### `POST /vehicles/exit`

🚗 Process a vehicle exit: closes the parking record, sets the `exit_time`, and frees the slot.

**Request Body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `plate` | string | ✅ | License plate of the exiting vehicle |

**Request Example**

```json
{
  "plate": "ABC-1234"
}
```

**Response `200`** — `{}`

---

### Parking Slots

#### `GET /slots/available`

Return all currently free (unoccupied) parking slots.

**Response `200`**

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

#### `GET /slots/{slot_id}`

Return a single parking slot by its ID.

**Path Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `slot_id` | integer | ✅ | The unique slot ID |

**Response `200`** — [`ParkingSlotOut`](#parkingslotout)

---

#### `GET /slots/occupancy`

Returns real-time occupancy statistics for the entire parking facility.

**Response `200`**

```json
{
  "total_slots": 120,
  "occupied_slots": 87,
  "occupancy_percentage": 72.5
}
```

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

> ⚠️ This endpoint is called **automatically** by the internal YOLO/OCR AI module when a vehicle is detected. The frontend team does **not** need to call this directly — it is documented here for full system understanding.

#### `POST /ai/detect`

📡 Called by the AI module when a vehicle is detected.

**Flow:**
1. Create or update vehicle record
2. Guard against duplicate active sessions
3. Create parking record
4. Mark slot as occupied

**Request Body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `plate` | string | ✅ | Detected license plate number |
| `slot_code` | string | ✅ | Assigned slot code |
| `floor` | integer | ✅ | Floor number where vehicle is parked |
| `color` | string \| null | ❌ | Detected vehicle color |
| `type` | string \| null | ❌ | Detected vehicle type, e.g. `sedan`, `SUV` |

**Request Example**

```json
{
  "plate": "ABC-1234",
  "slot_code": "A-12",
  "floor": 2,
  "color": "white",
  "type": "sedan"
}
```

**Response `200`**

```json
{
  "message": "Vehicle recorded successfully",
  "plate": "ABC-1234",
  "slot_code": "A-12",
  "floor": 2
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

**Response `200`**

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

### Users (Me)

> All `/users/me` endpoints require a valid Bearer token.

#### `GET /users/me` 🔒

Returns the authenticated user's profile.

**Response `200`**

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

**Response `200`**

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

**Response `200`**

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

**Response `200`**

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

**Response `200`**

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

## Data Schemas

### `UserOut`

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique user ID |
| `name` | string | Full name |
| `email` | string | Email address |
| `is_admin` | boolean | Whether the user has admin privileges |

---

### `VehicleLocation`

| Field | Type | Description |
|-------|------|-------------|
| `plate_number` | string | License plate number |
| `slot_code` | string | Slot where the car is parked |
| `floor` | integer | Floor number |

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

### `Token`

| Field | Type | Description |
|-------|------|-------------|
| `access_token` | string | JWT access token |
| `token_type` | string | Always `"bearer"` |

---

### `LoginResponse`

| Field | Type | Description |
|-------|------|-------------|
| `token` | `Token` | JWT token object |
| `user` | `UserOut` | Authenticated user info |

---

### `AIDetectRequest`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `plate` | string | ✅ | Detected license plate number |
| `slot_code` | string | ✅ | Assigned slot code |
| `floor` | integer | ✅ | Floor number |
| `color` | string \| null | ❌ | Detected vehicle color |
| `type` | string \| null | ❌ | Detected vehicle type |

---

### `AIDetectResponse`

| Field | Type | Description |
|-------|------|-------------|
| `message` | string | Confirmation message |
| `plate` | string | Plate number stored |
| `slot_code` | string | Slot code stored |
| `floor` | integer | Floor stored |

---

### `SlotOccupancyOut`

| Field | Type | Description |
|-------|------|-------------|
| `total_slots` | integer | Total number of slots in the system |
| `occupied_slots` | integer | Number of currently occupied slots |
| `occupancy_percentage` | number | Percentage of slots that are occupied |

---

### `SlotStatusUpdate`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `is_occupied` | boolean | ✅ | New occupancy status to apply to the slot |

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

## Response Codes

| Code | Meaning |
|------|---------|
| `200 OK` | Request succeeded |
| `201 Created` | Resource created successfully |
| `422 Unprocessable Entity` | Validation error — check your request body or parameters |
| `401 Unauthorized` | Missing or invalid Bearer token |

---

*Go2Car API v1.0.0 · OpenAPI 3.1.0*
