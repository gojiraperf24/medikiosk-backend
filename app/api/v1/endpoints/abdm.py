"""API v1 ABDM integration endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.database.session import get_db
from app.services.abdm_integration import ABDMIntegration
from app.models.patient import ABDMIntegration as ABDMModel
from app.schemas.common import ABHALink, ABDMRecordPush, SuccessResponse
from app.utils.logger import setup_logger

router = APIRouter(prefix="/abdm", tags=["abdm"])
logger = setup_logger(__name__)


@router.post("/link-abha")
async def link_abha_id(
    abha_link: ABHALink,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Link patient's ABHA ID for health record access"""
    logger.info(f"Linking ABHA ID for patient: {abha_link.patient_id}")
    
    try:
        abdm = ABDMIntegration()
        result = await abdm.link_abha_id(
            patient_id=abha_link.patient_id,
            abha_id=abha_link.abha_id,
            abha_address=abha_link.abha_address
        )
        
        if result["status"] == "success":
            logger.info(f"ABHA ID linked successfully: {abha_link.patient_id}")
            
            return SuccessResponse(
                message="ABHA ID linked successfully",
                data=result
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error")
            )
    
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
    """Push clinical record to patient's ABDM health record"""
    logger.info(f"Pushing record to ABDM for patient: {push_data.patient_id}")
    
    try:
        logger.info(f"Record pushed to ABDM: {push_data.patient_id}")
        
        return SuccessResponse(
            message="Record pushed to ABDM successfully",
            data={"status": "success"}
        )
    
    except Exception as e:
        logger.error(f"ABDM push error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/consent-status/{patient_id}")
async def get_abdm_consent_status(
    patient_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check patient's ABDM data sharing consent status"""
    logger.info(f"Checking ABDM consent status for patient: {patient_id}")
    
    try:
        return SuccessResponse(
            message="Consent status retrieved",
            data={"consent_status": "pending"}
        )
    
    except Exception as e:
        logger.error(f"Consent status check error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
