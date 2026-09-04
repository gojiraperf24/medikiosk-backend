"""Medical document processing and OCR service"""
import io
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class DocumentProcessor:
    """Process medical documents - OCR, extraction, structuring"""
    
    # Supported file types
    SUPPORTED_FORMATS = ["pdf", "jpg", "jpeg", "png", "tiff"]
    
    # Clinical entity types to extract
    ENTITY_TYPES = [
        "diagnosis",
        "medication",
        "investigation",
        "procedure",
        "allergies",
        "dosage"
    ]
    
    def __init__(self):
        """Initialize document processor"""
        self.extracted_data = {}
        self.processing_errors = []
    
    async def process_document(
        self,
        file_path: str,
        document_type: str
    ) -> Dict[str, Any]:
        """Process medical document
        
        Args:
            file_path: Path to uploaded document
            document_type: Type of document (prescription, lab_report, etc.)
        """
        logger.info(f"Processing document: {file_path}, type: {document_type}")
        
        try:
            # Step 1: Validate file
            file_valid = await self._validate_file(file_path)
            if not file_valid:
                return {"status": "failed", "error": "Invalid file format"}
            
            # Step 2: Extract text using OCR
            extracted_text = await self._extract_text_via_ocr(file_path)
            if not extracted_text:
                return {"status": "failed", "error": "OCR extraction failed"}
            
            # Step 3: Extract clinical entities
            entities = await self._extract_clinical_entities(
                extracted_text,
                document_type
            )
            
            # Step 4: Detect abnormal values
            abnormal_values = await self._detect_abnormal_values(entities)
            
            # Step 5: Extract document date
            doc_date = await self._extract_document_date(extracted_text)
            
            return {
                "status": "success",
                "extracted_text": extracted_text,
                "entities": entities,
                "abnormal_values": abnormal_values,
                "document_date": doc_date,
                "document_type": document_type
            }
        
        except Exception as e:
            logger.error(f"Document processing error: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    async def _validate_file(self, file_path: str) -> bool:
        """Validate file format and size"""
        try:
            path = Path(file_path)
            
            # Check extension
            if path.suffix.lower().lstrip(".") not in self.SUPPORTED_FORMATS:
                logger.error(f"Unsupported file format: {path.suffix}")
                return False
            
            # Check file exists
            if not path.exists():
                logger.error(f"File not found: {file_path}")
                return False
            
            # Check file size (max 50MB)
            file_size_mb = path.stat().st_size / (1024 * 1024)
            if file_size_mb > 50:
                logger.error(f"File too large: {file_size_mb}MB")
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"File validation error: {str(e)}")
            return False
    
    async def _extract_text_via_ocr(self, file_path: str) -> str:
        """Extract text from document using OCR
        
        Integrates with Tesseract or Google Vision API
        """
        try:
            logger.info(f"Starting OCR for: {file_path}")
            
            # Placeholder for actual OCR implementation
            # In production, would use:
            # - pytesseract for local OCR
            # - Google Cloud Vision API for multilingual support
            # - AWS Textract for handwritten documents
            
            # For now, return placeholder text
            extracted_text = "[OCR extracted text would appear here]\n"
            extracted_text += "Patient: John Doe\n"
            extracted_text += "Date: 2024-01-15\n"
            extracted_text += "Diagnosis: Type 2 Diabetes Mellitus\n"
            extracted_text += "Medications: Metformin 500mg BD, Glipizide 5mg OD\n"
            extracted_text += "Lab Values: HbA1c 7.2%, FBS 145 mg/dL\n"
            
            logger.info("OCR extraction completed")
            return extracted_text
        
        except Exception as e:
            logger.error(f"OCR extraction error: {str(e)}")
            return ""
    
    async def _extract_clinical_entities(
        self,
        text: str,
        document_type: str
    ) -> Dict[str, List[Dict[str, str]]]:
        """Extract clinical entities from OCR text
        
        Uses NER or rule-based pattern matching
        """
        entities = {entity_type: [] for entity_type in self.ENTITY_TYPES}
        
        try:
            # Parse text and identify entities
            # Placeholder logic - in production would use spaCy NER or LLM
            
            if "diagnosis" in text.lower() or document_type == "discharge_summary":
                entities["diagnosis"].append({
                    "name": "Type 2 Diabetes Mellitus",
                    "icd10_code": "E11",
                    "status": "confirmed"
                })
            
            if "medication" in text.lower() or "mg" in text.lower():
                entities["medication"].append({
                    "name": "Metformin",
                    "dosage": "500mg",
                    "frequency": "Twice daily",
                    "route": "Oral"
                })
            
            if document_type == "lab_report":
                entities["investigation"].append({
                    "test_name": "HbA1c",
                    "value": "7.2",
                    "unit": "%",
                    "reference_range": "<5.7"
                })
            
            logger.info(f"Extracted {len(entities)} entity types")
            return entities
        
        except Exception as e:
            logger.error(f"Entity extraction error: {str(e)}")
            return entities
    
    async def _detect_abnormal_values(
        self,
        entities: Dict[str, List[Dict[str, str]]]
    ) -> List[Dict[str, Any]]:
        """Detect and flag abnormal lab values"""
        abnormal_values = []
        
        # Reference ranges for common tests
        reference_ranges = {
            "HbA1c": {"normal_high": 5.7, "unit": "%"},
            "FBS": {"normal_high": 100, "unit": "mg/dL"},
            "Creatinine": {"normal_high": 1.2, "unit": "mg/dL"},
            "TSH": {"normal_low": 0.4, "normal_high": 4.0, "unit": "mIU/L"}
        }
        
        for investigation in entities.get("investigation", []):
            test_name = investigation.get("test_name")
            if test_name in reference_ranges:
                try:
                    value = float(investigation.get("value", 0))
                    ref_range = reference_ranges[test_name]
                    
                    if value > ref_range.get("normal_high", float('inf')):
                        abnormal_values.append({
                            "test": test_name,
                            "value": value,
                            "status": "HIGH",
                            "normal_range": ref_range
                        })
                    elif value < ref_range.get("normal_low", 0):
                        abnormal_values.append({
                            "test": test_name,
                            "value": value,
                            "status": "LOW",
                            "normal_range": ref_range
                        })
                except ValueError:
                    pass
        
        logger.info(f"Detected {len(abnormal_values)} abnormal values")
        return abnormal_values
    
    async def _extract_document_date(self, text: str) -> Optional[str]:
        """Extract document creation date from text
        
        Uses regex pattern matching for common date formats
        """
        import re
        from datetime import datetime
        
        # Common date patterns (DD/MM/YYYY, MM/DD/YYYY, etc.)
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{4}-\d{1,2}-\d{1,2}',
            r'\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s\d{4}'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0]  # Return first match
        
        return None
    
    async def organize_timeline(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Organize documents chronologically"""
        try:
            from datetime import datetime
            
            # Sort by document date
            sorted_docs = sorted(
                documents,
                key=lambda x: datetime.fromisoformat(x.get("document_date", "1900-01-01"))
            )
            
            logger.info(f"Organized {len(sorted_docs)} documents chronologically")
            return sorted_docs
        
        except Exception as e:
            logger.error(f"Timeline organization error: {str(e)}")
            return documents
