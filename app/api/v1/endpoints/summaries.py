"""Clinical summary generation and management endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.schemas.common import (
    ClinicalSummaryCreate,
    ClinicalSummaryResponse,
    SummaryConfirmation
)
from app.database.session import get_db
from app.models.patient import ClinicalSummary, HistorySession, MedicalDocument
from app.services.summary_generator import SummaryGenerator
from app.core.constants import SummaryStatusEnum
from app.utils.logger import setup_logger
from datetime import datetime

router = APIRouter(prefix="/summaries", tags=["Summaries"])
logger = setup_logger(__name__)


@router.post("/generate")
async def generate_summary(
    patient_id: str,
    session_id: str = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate clinical summary from conversation and documents"""
    logger.info(f"Generating summary for patient: {patient_id}")
    
    try:
        # Gather conversation data
        conversation_data = {}
        if session_id:
            session = db.query(HistorySession).filter(
                HistorySession.id == session_id
            ).first()
            if session:
                conversation_data = session.conversation_data or {}
        
        # Gather document data
        documents = db.query(MedicalDocument).filter(
            MedicalDocument.patient_id == patient_id
        ).all()
        
        document_data = [
            {
                "id": doc.id,
                "entities": doc.extracted_entities or {},
                "abnormal_values": doc.abnormal_values or []
            }
            for doc in documents
        ]
        
        # Generate summary
        generator = SummaryGenerator(language="en")
        result = await generator.generate_summary(
            conversation_data,
            document_data
        )
        
        if result["status"] == "success":
            # Save summary to database
            db_summary = ClinicalSummary(
                patient_id=patient_id,
                session_id=session_id,
                summary_text=result["summary_text"],
                summary_json=result["summary_json"],
                status=SummaryStatusEnum.DRAFT,
                language="en"
            )
            db.add(db_summary)
            db.commit()
            db.refresh(db_summary)
            
            logger.info(f"Summary generated: {db_summary.id}")
            
            return {
                "summary_id": db_summary.id,
                "status": "success",
                "summary_text": result["summary_text"],
                "confidence_score": result["confidence_score"],
                "recommendations": result["recommendations"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Summary generation failed")
            )
    
    except Exception as e:
        logger.error(f"Summary generation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{summary_id}", response_model=ClinicalSummaryResponse)
async def get_summary(
    summary_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve clinical summary"""
    summary = db.query(ClinicalSummary).filter(
        ClinicalSummary.id == summary_id
    ).first()
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found"
        )
    
    return summary


@router.post("/{summary_id}/confirm")
async def confirm_summary(
    summary_id: str,
    confirmation: SummaryConfirmation,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Physician confirms and optionally modifies summary"""
    logger.info(f"Confirming summary: {summary_id}")
    
    summary = db.query(ClinicalSummary).filter(
        ClinicalSummary.id == summary_id
    ).first()
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found"
        )
    
    if confirmation.confirmed:
        summary.status = SummaryStatusEnum.CONFIRMED
        summary.physician_confirmed = True
        summary.confirmed_by_physician_id = confirmation.physician_id
        summary.physician_confirmed_at = datetime.utcnow()
        
        if confirmation.modifications:
            summary.modifications_by_physician = confirmation.modifications
    
    db.commit()
    logger.info(f"Summary confirmed: {summary_id}")
    
    return {
        "summary_id": summary.id,
        "status": "confirmed",
        "confirmed_at": summary.physician_confirmed_at.isoformat()
    }
