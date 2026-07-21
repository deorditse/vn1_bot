from enum import Enum, StrEnum


class AsMinutes(int, Enum):
    MINUTE = 1
    HOUR = 60
    DAY = 60 * 24
    YEAR = 60 * 24 * 365


class AuthMethod(Enum):
    UNDEFINED = 0
    TEST = 1
    DEMO = 2


class ApiMode(Enum):
    UNDEFINED = 0
    DEV = 1
    PROD = 9


class AiDescriptionProductType(StrEnum):
    MEDICINE = "medicine"
    NON_MEDICINE = "non_medicine"


class NonMedicineCategory(StrEnum):
    DIETARY_SUPPLEMENT = "dietary_supplement"
    MEDICAL_NUTRITION = "medical_nutrition"
    MEDICAL_DEVICE = "medical_device"
    HYGIENE = "hygiene"
    COSMETICS = "cosmetics"
