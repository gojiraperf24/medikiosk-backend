"""Medical document management endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.schemas.common import DocumentResponse
from app.database.session import get_db
from app.models.patient import MedicalDocument
from app.services.document_processor import DocumentProcessor
from app.utils.logger import setup_logger
import uuid
from pathlib import Path

router = APIRouter(prefix="/documents", tags=["Documents"])
logger = setup_logger(__name__)

# Document storage directory
DOC_STORAGE_DIR = Path("uploads/documents")
DOC_STORAGE_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_document(
    patient_id: str,
    document_type: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload medical document for processing"""
    logger.info(f"Document upload started: {file.filename}")
    
    try:
        # Save file
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = DOC_STORAGE_DIR / unique_filename
        
        with open(file_path, "wb") as f:
            contents = await file.read()
            f.write(contents)
        
        file_size_mb = len(contents) / (1024 * 1024)
        
        # Create document record
        db_document = MedicalDocument(
            patient_id=patient_id,
            document_type=document_type,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size_mb=file_size_mb,
            processing_status="processing"
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        # Process document asynchronously
        processor = DocumentProcessor()
        result = await processor.process_document(
            str(file_path),
            document_type
        )
        
        # Update document record with processing results
        if result["status"] == "success":
            db_document.extracted_text = result.get("extracted_text")
            db_document.extracted_entities = result.get("entities")
            db_document.abnormal_values = result.get("abnormal_values")
            db_document.processing_status = "completed"
        else:
            db_document.processing_status = "failed"
            db_document.processing_error = result.get("error")
        
        db.commit()
        logger.info(f"Document processed: {db_document.id}")
        
        return {
            "document_id": db_document.id,
            "status": result["status"],
            "processing_result": result
        }
    
    except Exception as e:
        logger.error(f"Document upload error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document upload failed: {str(e)}"
        )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve processed document"""
    document = db.query(MedicalDocument).filter(
        MedicalDocument.id == document_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return document


@router.get("/timeline/{patient_id}")
async def get_document_timeline(
    patient_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chronologically organized medical document timeline"""
    documents = db.query(MedicalDocument).filter(
        MedicalDocument.patient_id == patient_id
    ).order_by(MedicalDocument.created_at).all()
    
    if not documents:
        return {"patient_id": patient_id, "timeline": []}
    
    # Organize chronologically
    processor = DocumentProcessor()
    organized = await processor.organize_timeline(
        [doc.__dict__ for doc in documents]
    )
    
    return {
        "patient_id": patient_id,
        "total_documents": len(documents),
        "timeline": organized
    }
