# Models package — import all models so that Base.metadata knows about them
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.parking_floor import ParkingFloor
from app.models.parking_section import ParkingSection
from app.models.parking_slot import ParkingSlot
from app.models.camera import Camera
from app.models.parking_record import ParkingRecord
from app.models.detection_log import DetectionLog
from app.models.blacklist_token import BlacklistedToken