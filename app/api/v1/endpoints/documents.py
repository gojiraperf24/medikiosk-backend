"""API v1 Medical document endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.database.session import get_db
from app.services.document_processor import DocumentProcessor
from app.models.patient import MedicalDocument
from app.schemas.common import DocumentResponse, SuccessResponse
from app.utils.logger import setup_logger

router = APIRouter(prefix="/documents", tags=["documents"])
logger = setup_logger(__name__)


@router.post("/upload")
async def upload_document(
    patient_id: str,
    document_type: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and process medical document"""
    logger.info(f"Uploading document for patient: {patient_id}")
    
    try:
        # Save uploaded file
        file_path = f"/tmp/{file.filename}"
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Process document
        processor = DocumentProcessor()
        result = await processor.process_document(file_path, document_type)
        
        if result["status"] == "success":
            # Create document record
            doc = MedicalDocument(
                patient_id=patient_id,
                document_type=document_type,
                original_filename=file.filename,
                file_path=file_path,
                file_size_mb=len(contents) / (1024 * 1024),
                extracted_text=result.get("extracted_text"),
                extracted_entities=result.get("entities"),
                abnormal_values=result.get("abnormal_values"),
                document_date=result.get("document_date"),
                processing_status="completed"
            )
            
            db.add(doc)
            db.commit()
            db.refresh(doc)
            
            logger.info(f"Document uploaded successfully: {doc.id}")
            
            return SuccessResponse(
                message="Document uploaded and processed successfully",
                data={
                    "document_id": doc.id,
                    "abnormal_values": result.get("abnormal_values", [])
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error")
            )
    
    except Exception as e:
        logger.error(f"Document upload error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve processed document details"""
    logger.info(f"Fetching document: {document_id}")
    
    doc = db.query(MedicalDocument).filter(
        MedicalDocument.id == document_id
    ).first()
    
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return doc
