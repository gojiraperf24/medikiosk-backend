"""API v1 Clinical summary endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.database.session import get_db
from app.services.summary_generator import SummaryGenerator
from app.models.patient import ClinicalSummary
from app.schemas.common import ClinicalSummaryCreate, ClinicalSummaryResponse, SummaryConfirmation, SuccessResponse
from app.utils.logger import setup_logger

router = APIRouter(prefix="/summaries", tags=["summaries"])
logger = setup_logger(__name__)


@router.post("/generate")
async def generate_summary(
    summary_create: ClinicalSummaryCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate clinical history summary from conversation and documents"""
    logger.info(f"Generating summary for patient: {summary_create.patient_id}")
    
    try:
        generator = SummaryGenerator(language=summary_create.language)
        result = await generator.generate_summary({}, [])
        
        if result["status"] == "success":
            summary = ClinicalSummary(
                patient_id=summary_create.patient_id,
                session_id=summary_create.session_id,
                summary_text=result["summary_text"],
                summary_json=result["summary_json"],
                language=summary_create.language
            )
            
            db.add(summary)
            db.commit()
            db.refresh(summary)
            
            logger.info(f"Summary generated: {summary.id}")
            
            return SuccessResponse(
                message="Summary generated successfully",
                data={
                    "summary_id": summary.id,
                    "summary_text": result["summary_text"]
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error")
            )
    
    except Exception as e:
        logger.error(f"Summary generation error: {str(e)}")
        db.rollback()
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
    logger.info(f"Fetching summary: {summary_id}")
    
    summary = db.query(ClinicalSummary).filter(
        ClinicalSummary.id == summary_id
    ).first()
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found"
        )
    
    return summary
