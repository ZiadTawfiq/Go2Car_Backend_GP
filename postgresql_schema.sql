-- ==========================================
-- PostgreSQL DDL Schema for Go2Car Backend
-- Generated from SQLAlchemy ORM Models
-- ==========================================

CREATE TYPE reservation_status AS ENUM ('pending', 'active', 'completed', 'cancelled', 'expired');

CREATE TABLE blacklisted_tokens (
	id SERIAL NOT NULL, 
	jti VARCHAR NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id), 
	UNIQUE (jti)
);

CREATE INDEX ix_blacklisted_tokens_created_at ON blacklisted_tokens (created_at);

CREATE INDEX ix_blacklisted_tokens_id ON blacklisted_tokens (id);

CREATE TABLE parking_floors (
	id SERIAL NOT NULL, 
	floor_code VARCHAR NOT NULL, 
	floor_name VARCHAR NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX ix_parking_floors_id ON parking_floors (id);

CREATE UNIQUE INDEX ix_parking_floors_floor_code ON parking_floors (floor_code);

CREATE TABLE users (
	id SERIAL NOT NULL, 
	email VARCHAR NOT NULL, 
	name VARCHAR NOT NULL, 
	password VARCHAR NOT NULL, 
	is_admin BOOLEAN, 
	is_verified BOOLEAN, 
	verification_token VARCHAR, 
	verification_token_expires_at TIMESTAMP WITHOUT TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_users_email ON users (email);

CREATE INDEX ix_users_id ON users (id);

CREATE TABLE vehicles (
	id SERIAL NOT NULL, 
	plate_number VARCHAR NOT NULL, 
	color VARCHAR, 
	vehicle_type VARCHAR, 
	PRIMARY KEY (id)
);

CREATE INDEX ix_vehicles_id ON vehicles (id);

CREATE UNIQUE INDEX ix_vehicles_plate_number ON vehicles (plate_number);

CREATE TABLE parking_sections (
	id SERIAL NOT NULL, 
	section_code VARCHAR NOT NULL, 
	section_name VARCHAR NOT NULL, 
	floor_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(floor_id) REFERENCES parking_floors (id)
);

CREATE INDEX ix_parking_sections_id ON parking_sections (id);

CREATE INDEX ix_parking_sections_floor_id ON parking_sections (floor_id);

CREATE UNIQUE INDEX ix_parking_sections_section_code ON parking_sections (section_code);

CREATE TABLE user_vehicles (
	user_id INTEGER NOT NULL, 
	vehicle_id INTEGER NOT NULL, 
	PRIMARY KEY (user_id, vehicle_id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(vehicle_id) REFERENCES vehicles (id) ON DELETE CASCADE
);

CREATE INDEX ix_user_vehicles_vehicle_id ON user_vehicles (vehicle_id);

CREATE TABLE cameras (
	id SERIAL NOT NULL, 
	name VARCHAR NOT NULL, 
	location_description VARCHAR, 
	section_id INTEGER NOT NULL, 
	is_active BOOLEAN, 
	PRIMARY KEY (id), 
	FOREIGN KEY(section_id) REFERENCES parking_sections (id)
);

CREATE INDEX ix_cameras_id ON cameras (id);

CREATE INDEX ix_cameras_section_id ON cameras (section_id);

CREATE TABLE parking_slots (
	id SERIAL NOT NULL, 
	slot_code VARCHAR NOT NULL, 
	section_id INTEGER NOT NULL, 
	is_occupied BOOLEAN, 
	last_updated TIMESTAMP WITH TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(section_id) REFERENCES parking_sections (id)
);

CREATE UNIQUE INDEX ix_parking_slots_slot_code ON parking_slots (slot_code);

CREATE INDEX idx_available_slots ON parking_slots (section_id) WHERE is_occupied = false;

CREATE INDEX ix_parking_slots_id ON parking_slots (id);

CREATE INDEX ix_parking_slots_section_id ON parking_slots (section_id);

CREATE TABLE detection_logs (
	id SERIAL NOT NULL, 
	camera_id INTEGER NOT NULL, 
	slot_id INTEGER, 
	plate_number VARCHAR, 
	vehicle_color VARCHAR, 
	vehicle_type VARCHAR, 
	detected_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	flagged_for_review BOOLEAN, 
	PRIMARY KEY (id), 
	FOREIGN KEY(camera_id) REFERENCES cameras (id), 
	FOREIGN KEY(slot_id) REFERENCES parking_slots (id)
);

CREATE INDEX ix_detection_logs_camera_id ON detection_logs (camera_id);

CREATE INDEX ix_detection_logs_slot_id ON detection_logs (slot_id);

CREATE INDEX ix_detection_logs_id ON detection_logs (id);

CREATE INDEX ix_detection_logs_detected_at ON detection_logs (detected_at);

CREATE TABLE parking_records (
	id SERIAL NOT NULL, 
	vehicle_id INTEGER NOT NULL, 
	slot_id INTEGER NOT NULL, 
	entry_time TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	exit_time TIMESTAMP WITH TIME ZONE, 
	is_active BOOLEAN, 
	PRIMARY KEY (id), 
	FOREIGN KEY(vehicle_id) REFERENCES vehicles (id), 
	FOREIGN KEY(slot_id) REFERENCES parking_slots (id)
);

CREATE INDEX ix_parking_records_vehicle_id ON parking_records (vehicle_id);

CREATE INDEX ix_parking_records_exit_time ON parking_records (exit_time);

CREATE INDEX idx_active_parking ON parking_records (vehicle_id) WHERE is_active = true;

CREATE INDEX ix_parking_records_id ON parking_records (id);

CREATE INDEX ix_parking_records_slot_id ON parking_records (slot_id);

CREATE INDEX ix_parking_records_entry_time ON parking_records (entry_time);

CREATE TABLE reservations (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	slot_id INTEGER NOT NULL, 
	vehicle_id INTEGER, 
	start_time TIMESTAMP WITH TIME ZONE NOT NULL, 
	end_time TIMESTAMP WITH TIME ZONE NOT NULL, 
	status reservation_status NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(slot_id) REFERENCES parking_slots (id), 
	FOREIGN KEY(vehicle_id) REFERENCES vehicles (id)
);

CREATE INDEX ix_reservations_vehicle_id ON reservations (vehicle_id);

CREATE INDEX ix_reservations_end_time ON reservations (end_time);

CREATE INDEX idx_active_reservations ON reservations (user_id) WHERE status IN ('pending', 'active');

CREATE INDEX ix_reservations_slot_id ON reservations (slot_id);

CREATE INDEX ix_reservations_start_time ON reservations (start_time);

CREATE INDEX ix_reservations_user_id ON reservations (user_id);

CREATE INDEX ix_reservations_id ON reservations (id);
