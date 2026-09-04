"""ABDM integration endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.schemas.common import ABHALink, ABDMRecordPush, SuccessResponse
from app.database.session import get_db
from app.models.patient import Patient, ABDMIntegration, ClinicalSummary
from app.services.abdm_integration import ABDMIntegration as ABDMService
from app.utils.logger import setup_logger

router = APIRouter(prefix="/abdm", tags=["ABDM"])
logger = setup_logger(__name__)


@router.post("/link-abha")
async def link_abha_id(
    abha_link: ABHALink,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Link patient ABHA ID to MediKiosk"""
    logger.info(f"Linking ABHA ID for patient: {abha_link.patient_id}")
    
    try:
        # Update patient record
        patient = db.query(Patient).filter(
            Patient.id == abha_link.patient_id
        ).first()
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        patient.abha_id = abha_link.abha_id
        
        # Create or update ABDM integration record
        abdm_record = db.query(ABDMIntegration).filter(
            ABDMIntegration.patient_id == abha_link.patient_id
        ).first()
        
        if not abdm_record:
            abdm_record = ABDMIntegration(patient_id=abha_link.patient_id)
            db.add(abdm_record)
        
        abdm_record.abha_id = abha_link.abha_id
        abdm_record.abha_address = abha_link.abha_address
        abdm_record.gateway_status = "linked"
        
        db.commit()
        
        # Link with ABDM gateway
        abdm_service = ABDMService()
        result = await abdm_service.link_abha_id(
            abha_link.patient_id,
            abha_link.abha_id,
            abha_link.abha_address
        )
        
        logger.info(f"ABHA linked successfully: {abha_link.patient_id}")
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ABHA linking error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/push-record")
async def push_record_to_abdm(
    push_data: ABDMRecordPush,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Push clinical record to patient's ABDM personal health record"""
    logger.info(f"Pushing record to ABDM for patient: {push_data.patient_id}")
    
    try:
        # Get patient and summary
        patient = db.query(Patient).filter(
            Patient.id == push_data.patient_id
        ).first()
        
        if not patient or not patient.abha_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient or ABHA ID not found"
            )
        
        summary = db.query(ClinicalSummary).filter(
            ClinicalSummary.id == push_data.summary_id
        ).first()
        
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Summary not found"
            )
        
        # Push to ABDM
        abdm_service = ABDMService()
        result = await abdm_service.push_clinical_summary(
            push_data.patient_id,
            patient.abha_id,
            {
                "id": summary.id,
                "summary_text": summary.summary_text,
                "summary_json": summary.summary_json
            }
        )
        
        logger.info(f"Record pushed to ABDM: {push_data.patient_id}")
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ABDM push error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/consent-status/{patient_id}")
async def get_consent_status(
    patient_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check patient's ABDM data sharing consent status"""
    try:
        patient = db.query(Patient).filter(
            Patient.id == patient_id
        ).first()
        
        if not patient or not patient.abha_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient or ABHA ID not found"
            )
        
        # Check consent status with ABDM
        abdm_service = ABDMService()
        result = await abdm_service.check_consent_status(
            patient_id,
            patient.abha_id
        )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Consent check error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
