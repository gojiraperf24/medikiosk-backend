"""Authentication and authorization endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    get_current_user
)
from app.schemas.common import (
    PatientCreate,
    PatientResponse,
    ConsentCreate,
    ConsentResponse,
    SuccessResponse,
    ErrorResponse
)
from app.database.session import get_db
from app.models.patient import Patient, ConsentRecord
from app.core.constants import ConsentStatusEnum
from app.utils.logger import setup_logger

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = setup_logger(__name__)


@router.post("/register", response_model=PatientResponse)
async def register_patient(
    patient_data: PatientCreate,
    db: Session = Depends(get_db)
):
    """Register new patient"""
    logger.info(f"Registering new patient: {patient_data.first_name}")
    
    # Check if patient already exists (by phone or email)
    if patient_data.phone:
        existing = db.query(Patient).filter(Patient.phone == patient_data.phone).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Patient with this phone number already exists"
            )
    
    # Create new patient
    db_patient = Patient(**patient_data.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    
    logger.info(f"Patient registered successfully: {db_patient.id}")
    return db_patient


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Patient login via ABHA ID or phone"""
    logger.info(f"Login attempt: {form_data.username}")
    
    # Find patient by ABHA ID or phone
    patient = db.query(Patient).filter(
        (Patient.abha_id == form_data.username) |
        (Patient.phone == form_data.username)
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": patient.id, "patient_id": patient.id}
    )
    refresh_token = create_refresh_token(
        data={"sub": patient.id, "patient_id": patient.id}
    )
    
    logger.info(f"Login successful for patient: {patient.id}")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "patient_id": patient.id
    }


@router.post("/consent", response_model=ConsentResponse)
async def grant_consent(
    consent_data: ConsentCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Patient grants consent for data capture and sharing"""
    logger.info(f"Consent requested: {consent_data.consent_type}")
    
    # Create consent record
    db_consent = ConsentRecord(
        patient_id=consent_data.patient_id,
        consent_type=consent_data.consent_type,
        consent_text=consent_data.consent_text,
        status=ConsentStatusEnum.GRANTED,
        accepted_at=__import__('datetime').datetime.utcnow()
    )
    db.add(db_consent)
    db.commit()
    db.refresh(db_consent)
    
    logger.info(f"Consent granted: {db_consent.id}")
    return db_consent


@router.get("/me", response_model=PatientResponse)
async def get_current_patient(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current authenticated patient details"""
    patient_id = current_user.get("patient_id")
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    return patient
