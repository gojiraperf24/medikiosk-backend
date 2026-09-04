"""Pydantic schemas for API request/response validation"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.core.constants import PatientStatusEnum, SessionStatusEnum, ConsentStatusEnum


# Patient Schemas
class PatientBase(BaseModel):
    """Base patient schema"""
    first_name: str
    last_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    preferred_language: str = "hi"


class PatientCreate(PatientBase):
    """Schema for creating patient"""
    abha_id: Optional[str] = None
    aadhaar_number: Optional[str] = None


class PatientUpdate(BaseModel):
    """Schema for updating patient"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    preferred_language: Optional[str] = None


class PatientResponse(PatientBase):
    """Schema for patient response"""
    id: str
    abha_id: Optional[str] = None
    status: PatientStatusEnum
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# History Session Schemas
class HistorySessionCreate(BaseModel):
    """Schema for creating history session"""
    patient_id: str
    session_type: str = "general"  # 'general' or 'ayush'
    language: str = "hi"


class HistorySessionResponse(BaseModel):
    """Schema for history session response"""
    id: str
    patient_id: str
    session_type: str
    status: SessionStatusEnum
    language: str
    conversation_data: Optional[Dict[str, Any]] = None
    red_flags: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class HistoryResponse(BaseModel):
    """Schema for submitting history response"""
    session_id: str
    response_type: str  # 'voice', 'touch', 'text'
    content: str
    confidence_score: Optional[float] = None


# Medical Document Schemas
class DocumentMetadata(BaseModel):
    """Document metadata"""
    original_filename: str
    document_type: str
    document_date: Optional[datetime] = None


class DocumentResponse(BaseModel):
    """Schema for document response"""
    id: str
    patient_id: str
    document_type: str
    original_filename: str
    extracted_text: Optional[str] = None
    extracted_entities: Optional[Dict[str, Any]] = None
    abnormal_values: Optional[List[Dict[str, Any]]] = None
    processing_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Clinical Summary Schemas
class SummaryComponent(BaseModel):
    """Individual summary component"""
    component_type: str  # chief_complaint, hpi, past_history, etc.
    content: str
    source: Optional[str] = None  # 'conversation', 'document'


class ClinicalSummaryCreate(BaseModel):
    """Schema for creating clinical summary"""
    patient_id: str
    session_id: Optional[str] = None
    summary_text: str
    summary_json: Optional[Dict[str, Any]] = None
    language: str = "en"


class ClinicalSummaryResponse(BaseModel):
    """Schema for clinical summary response"""
    id: str
    patient_id: str
    summary_text: str
    summary_json: Optional[Dict[str, Any]] = None
    status: str
    language: str
    physician_confirmed: bool
    confirmed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class SummaryConfirmation(BaseModel):
    """Schema for physician confirming summary"""
    summary_id: str
    physician_id: str
    modifications: Optional[Dict[str, Any]] = None
    confirmed: bool = True


# Consent Schemas
class ConsentCreate(BaseModel):
    """Schema for creating consent record"""
    patient_id: str
    consent_type: str  # 'data_capture', 'abdm_sharing', 'document_upload'
    consent_text: str


class ConsentResponse(BaseModel):
    """Schema for consent response"""
    id: str
    patient_id: str
    consent_type: str
    status: ConsentStatusEnum
    accepted_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ConsentGrant(BaseModel):
    """Schema for granting consent"""
    patient_id: str
    consent_type: str
    consent_id: str
    accepted: bool = True


# ABDM Integration Schemas
class ABHALink(BaseModel):
    """Schema for linking ABHA ID"""
    patient_id: str
    abha_id: str
    abha_address: Optional[str] = None


class ABDMRecordPush(BaseModel):
    """Schema for pushing record to ABDM"""
    patient_id: str
    summary_id: str
    record_type: str  # 'summary', 'document'


# Error Schemas
class ErrorResponse(BaseModel):
    """Standard error response"""
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Success Schemas
class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
