import re

def normalize_plate(plate: str) -> str:
    plate = plate.strip().upper()
    plate = re.sub(r"[\s\-]", "", plate)
    return plate