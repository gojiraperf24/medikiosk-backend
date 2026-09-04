"""Application constants and enumerations"""
from enum import Enum


class LanguageEnum(str, Enum):
    """Supported languages"""
    HINDI = "hi"
    ENGLISH = "en"
    TAMIL = "ta"
    TELUGU = "te"
    KANNADA = "kn"
    MARATHI = "mr"
    GUJARATI = "gu"
    BENGALI = "bn"


class PatientStatusEnum(str, Enum):
    """Patient status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class SessionStatusEnum(str, Enum):
    """History session status"""
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DocumentTypeEnum(str, Enum):
    """Medical document types"""
    PRESCRIPTION = "prescription"
    LAB_REPORT = "lab_report"
    DISCHARGE_SUMMARY = "discharge_summary"
    IMAGING = "imaging"
    OTHER = "other"


class SummaryStatusEnum(str, Enum):
    """Clinical summary status"""
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    ARCHIVED = "archived"


class ConsentStatusEnum(str, Enum):
    """Consent status"""
    PENDING = "pending"
    GRANTED = "granted"
    REVOKED = "revoked"


class RedFlagTypeEnum(str, Enum):
    """Red flag/emergency symptom types"""
    CHEST_PAIN = "chest_pain"
    STROKE_SYMPTOMS = "stroke_symptoms"
    SEVERE_BREATHING = "severe_breathing"
    LOSS_OF_CONSCIOUSNESS = "loss_of_consciousness"
    SEVERE_BLEEDING = "severe_bleeding"
    ACUTE_ABDOMEN = "acute_abdomen"
    OTHER_EMERGENCY = "other_emergency"


# Dashavidha Pariksha Parameters (Ayurveda)
DAVIDHA_PARIKSHA_PARAMS = [
    "prakriti",      # Constitution
    "vikriti",       # Current imbalance
    "sara",          # Tissue strength
    "samhanana",     # Body compactness
    "pramana",       # Body measurements
    "satmya",        # Metabolic capacity
    "sattva",        # Mental strength
    "ahara_shakti",  # Digestive capacity
    "vyayama_shakti",# Exercise capacity
    "vaya"           # Age classification
]

# Standard Clinical History Components
CLINICAL_HISTORY_COMPONENTS = [
    "chief_complaint",
    "history_of_present_illness",
    "past_medical_history",
    "past_surgical_history",
    "drug_history",
    "allergy_history",
    "family_history",
    "personal_history",
    "review_of_systems"
]

# HTTP Status Messages
HTTP_STATUS_MESSAGES = {
    200: "Success",
    201: "Created",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    409: "Conflict",
    500: "Internal Server Error"
}
