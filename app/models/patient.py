"""Database models for MediKiosk"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, Enum as SQLEnum, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.constants import (
    PatientStatusEnum,
    SessionStatusEnum,
    DocumentTypeEnum,
    SummaryStatusEnum,
    ConsentStatusEnum
)

Base = declarative_base()


class Patient(Base):
    """Patient model"""
    __tablename__ = "patients"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    abha_id = Column(String, unique=True, nullable=True, index=True)
    aadhaar_number = Column(String, nullable=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    gender = Column(String, nullable=True)
    phone = Column(String, nullable=True, unique=True)
    email = Column(String, nullable=True, unique=True)
    preferred_language = Column(String, default="hi")
    status = Column(SQLEnum(PatientStatusEnum), default=PatientStatusEnum.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sessions = relationship("HistorySession", back_populates="patient")
    documents = relationship("MedicalDocument", back_populates="patient")
    summaries = relationship("ClinicalSummary", back_populates="patient")
    consents = relationship("ConsentRecord", back_populates="patient")


class HistorySession(Base):
    """Patient history conversation session"""
    __tablename__ = "history_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False, index=True)
    session_type = Column(String, default="general")  # 'general' or 'ayush'
    status = Column(SQLEnum(SessionStatusEnum), default=SessionStatusEnum.INITIATED)
    language = Column(String, default="hi")
    conversation_data = Column(JSON, nullable=True)  # Stores conversation flow
    red_flags = Column(JSON, nullable=True)  # Detected emergency symptoms
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="sessions")


class MedicalDocument(Base):
    """Scanned and processed medical documents"""
    __tablename__ = "medical_documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False, index=True)
    document_type = Column(SQLEnum(DocumentTypeEnum), nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size_mb = Column(Integer, nullable=False)
    document_date = Column(DateTime, nullable=True)  # When document was created
    extracted_text = Column(Text, nullable=True)  # OCR extracted text
    extracted_entities = Column(JSON, nullable=True)  # Diagnoses, medications, investigations
    abnormal_values = Column(JSON, nullable=True)  # Flagged lab values
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed
    processing_error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="documents")


class ClinicalSummary(Base):
    """Generated clinical history summary"""
    __tablename__ = "clinical_summaries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False, index=True)
    session_id = Column(String, ForeignKey("history_sessions.id"), nullable=True)
    summary_text = Column(Text, nullable=False)  # Full clinical summary
    summary_json = Column(JSON, nullable=True)  # Structured summary components
    status = Column(SQLEnum(SummaryStatusEnum), default=SummaryStatusEnum.DRAFT)
    language = Column(String, default="en")  # Language of summary
    physician_confirmed = Column(Boolean, default=False)
    physician_confirmed_at = Column(DateTime, nullable=True)
    confirmed_by_physician_id = Column(String, nullable=True)  # Physician's identifier
    modifications_by_physician = Column(JSON, nullable=True)  # Edits made by physician
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="summaries")


class ConsentRecord(Base):
    """Patient consent for data capture and sharing"""
    __tablename__ = "consent_records"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False, index=True)
    consent_type = Column(String, nullable=False)  # 'data_capture', 'abdm_sharing', 'document_upload'
    status = Column(SQLEnum(ConsentStatusEnum), default=ConsentStatusEnum.PENDING)
    consent_text = Column(Text, nullable=False)
    accepted_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    ip_address = Column(String, nullable=True)
    device_info = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="consents")


class ABDMIntegration(Base):
    """ABDM integration and health record linkage"""
    __tablename__ = "abdm_integrations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False, index=True, unique=True)
    abha_address = Column(String, nullable=True)  # username@abdm
    health_id = Column(String, unique=True, nullable=True)  # ABDM Health ID
    gateway_status = Column(String, default="pending")  # pending, linked, unlinked
    last_sync_at = Column(DateTime, nullable=True)
    sync_status = Column(String, default="pending")  # pending, syncing, synced, failed
    sync_error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLog(Base):
    """Audit trail for data access and modifications"""
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, nullable=True, index=True)
    actor_id = Column(String, nullable=True)  # User/system performing action
    action = Column(String, nullable=False)  # view, edit, delete, export
    resource_type = Column(String, nullable=False)  # patient, history, document, summary
    resource_id = Column(String, nullable=False)
    old_values = Column(JSON, nullable=True)  # For audit trail
    new_values = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
