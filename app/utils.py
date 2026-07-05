import re


arabic_to_english = str.maketrans(
    "٠١٢٣٤٥٦٧٨٩",
    "0123456789"
)

def normalize_plate(plate: str) -> str:
    plate = plate.strip().upper()
    plate = plate.translate(arabic_to_english)
    plate = re.sub(r"[\s\-]", "", plate)

    return plate