"""Clinical history conversation endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.schemas.common import HistorySessionCreate, HistorySessionResponse, HistoryResponse
from app.database.session import get_db
from app.models.patient import HistorySession
from app.services.conversation_engine import ConversationEngine
from app.core.constants import SessionStatusEnum
from app.utils.logger import setup_logger

router = APIRouter(prefix="/history", tags=["History"])
logger = setup_logger(__name__)


@router.post("/start", response_model=HistorySessionResponse)
async def start_history_session(
    session_data: HistorySessionCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initiate new history conversation session"""
    logger.info(f"Starting history session for patient: {session_data.patient_id}")
    
    # Create database session
    db_session = HistorySession(
        patient_id=session_data.patient_id,
        session_type=session_data.session_type,
        language=session_data.language,
        status=SessionStatusEnum.INITIATED
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    # Initialize conversation engine
    conv_engine = ConversationEngine(
        language=session_data.language,
        session_type=session_data.session_type
    )
    conv_result = await conv_engine.start_conversation()
    
    # Store conversation data
    db_session.conversation_data = conv_result
    db_session.status = SessionStatusEnum.IN_PROGRESS
    db.commit()
    
    logger.info(f"History session started: {db_session.id}")
    return db_session


@router.post("/respond")
async def submit_history_response(
    response_data: HistoryResponse,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit patient response to history question"""
    logger.info(f"Processing response for session: {response_data.session_id}")
    
    # Get session
    db_session = db.query(HistorySession).filter(
        HistorySession.id == response_data.session_id
    ).first()
    
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Process response
    conv_engine = ConversationEngine(
        language=db_session.language,
        session_type=db_session.session_type
    )
    
    result = await conv_engine.process_response(
        user_input=response_data.content,
        input_type=response_data.response_type,
        confidence=response_data.confidence_score or 1.0
    )
    
    # Update session
    db_session.conversation_data = result
    if result.get("red_flags"):
        db_session.red_flags = result["red_flags"]
    db.commit()
    
    logger.info(f"Response processed for session: {response_data.session_id}")
    return result


@router.get("/session/{session_id}", response_model=HistorySessionResponse)
async def get_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get history session status and data"""
    db_session = db.query(HistorySession).filter(
        HistorySession.id == session_id
    ).first()
    
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return db_session


@router.post("/session/{session_id}/complete")
async def complete_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete history conversation session"""
    logger.info(f"Completing session: {session_id}")
    
    db_session = db.query(HistorySession).filter(
        HistorySession.id == session_id
    ).first()
    
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    from datetime import datetime
    db_session.status = SessionStatusEnum.COMPLETED
    db_session.completed_at = datetime.utcnow()
    db.commit()
    
    logger.info(f"Session completed: {session_id}")
    return {"status": "completed", "session_id": session_id}
