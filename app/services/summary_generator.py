"""Clinical summary generation service"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class SummaryGenerator:
    """Generate physician-ready clinical history summaries"""
    
    # Standard clinical history format sections
    SUMMARY_SECTIONS = [
        "chief_complaint",
        "history_of_present_illness",
        "past_medical_history",
        "past_surgical_history",
        "drug_history",
        "allergy_history",
        "family_history",
        "personal_history",
        "review_of_systems"
    ]
    
    def __init__(self, language: str = "en"):
        """Initialize summary generator
        
        Args:
            language: Output language ('en' or 'hi')
        """
        self.language = language
        self.summary_components = {}
    
    async def generate_summary(
        self,
        conversation_data: Dict[str, Any],
        document_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive clinical summary
        
        Args:
            conversation_data: Extracted data from conversation
            document_data: Extracted data from scanned documents
        """
        logger.info("Starting summary generation")
        
        try:
            # Synthesize conversation and document data
            synthesized_data = await self._synthesize_data(
                conversation_data,
                document_data or []
            )
            
            # Generate text summary
            text_summary = await self._generate_text_summary(synthesized_data)
            
            # Generate structured JSON summary
            json_summary = await self._generate_json_summary(synthesized_data)
            
            # Generate physician recommendations
            recommendations = await self._generate_recommendations(synthesized_data)
            
            summary = {
                "status": "success",
                "summary_text": text_summary,
                "summary_json": json_summary,
                "recommendations": recommendations,
                "generated_at": datetime.utcnow().isoformat(),
                "confidence_score": await self._calculate_confidence(synthesized_data)
            }
            
            logger.info("Summary generation completed successfully")
            return summary
        
        except Exception as e:
            logger.error(f"Summary generation error: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _synthesize_data(
        self,
        conversation_data: Dict[str, Any],
        document_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Synthesize data from conversation and documents"""
        synthesized = {}
        
        # Merge conversation and document data
        # Document data takes precedence over conversation data
        for section in self.SUMMARY_SECTIONS:
            synthesized[section] = None
            
            # Get from conversation
            if section in conversation_data:
                synthesized[section] = conversation_data[section]
            
            # Enhance/override with document data
            for doc in document_data:
                entities = doc.get("entities", {})
                if section == "past_medical_history" and entities.get("diagnosis"):
                    synthesized[section] = entities["diagnosis"]
                elif section == "drug_history" and entities.get("medication"):
                    synthesized[section] = entities["medication"]
                elif section == "allergy_history" and entities.get("allergies"):
                    synthesized[section] = entities["allergies"]
        
        return synthesized
    
    async def _generate_text_summary(self, data: Dict[str, Any]) -> str:
        """Generate human-readable text summary"""
        sections = []
        
        # Chief Complaint
        if data.get("chief_complaint"):
            sections.append(f"CHIEF COMPLAINT:\n{data['chief_complaint']}\n")
        
        # History of Present Illness
        if data.get("history_of_present_illness"):
            sections.append(
                f"HISTORY OF PRESENT ILLNESS:\n{data['history_of_present_illness']}\n"
            )
        
        # Past Medical History
        if data.get("past_medical_history"):
            pmd_text = self._format_list_items(data["past_medical_history"])
            sections.append(f"PAST MEDICAL HISTORY:\n{pmd_text}\n")
        
        # Past Surgical History
        if data.get("past_surgical_history"):
            psh_text = self._format_list_items(data["past_surgical_history"])
            sections.append(f"PAST SURGICAL HISTORY:\n{psh_text}\n")
        
        # Drug History
        if data.get("drug_history"):
            drugs_text = self._format_medication_list(data["drug_history"])
            sections.append(f"MEDICATIONS:\n{drugs_text}\n")
        
        # Allergies
        if data.get("allergy_history"):
            allergies_text = self._format_list_items(data["allergy_history"])
            sections.append(f"ALLERGIES:\n{allergies_text}\n")
        
        # Family History
        if data.get("family_history"):
            sections.append(f"FAMILY HISTORY:\n{data['family_history']}\n")
        
        # Personal History
        if data.get("personal_history"):
            sections.append(f"PERSONAL HISTORY:\n{data['personal_history']}\n")
        
        # Review of Systems
        if data.get("review_of_systems"):
            sections.append(f"REVIEW OF SYSTEMS:\n{data['review_of_systems']}\n")
        
        return "\n".join(sections)
    
    async def _generate_json_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured JSON summary"""
        return {
            "chief_complaint": data.get("chief_complaint"),
            "hpi": data.get("history_of_present_illness"),
            "past_medical_history": data.get("past_medical_history", []),
            "past_surgical_history": data.get("past_surgical_history", []),
            "medications": data.get("drug_history", []),
            "allergies": data.get("allergy_history", []),
            "family_history": data.get("family_history"),
            "personal_history": data.get("personal_history"),
            "review_of_systems": data.get("review_of_systems")
        }
    
    async def _generate_recommendations(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Generate clinical recommendations based on extracted data
        
        AI-assisted recommendations for physician review
        """
        recommendations = {
            "investigations": [],
            "consultations": [],
            "follow_up": []
        }
        
        # Placeholder recommendation logic
        # In production would use clinical decision support rules
        
        # Example: If diabetes suspected
        pmd = data.get("past_medical_history", [])
        if isinstance(pmd, list) and any("diabetes" in str(d).lower() for d in pmd):
            recommendations["investigations"].extend([
                "HbA1c",
                "Fasting Blood Sugar",
                "Renal Function Tests"
            ])
            recommendations["follow_up"].append("Endocrinology review")
        
        return recommendations
    
    async def _calculate_confidence(self, data: Dict[str, Any]) -> float:
        """Calculate confidence score of summary completeness (0-1)"""
        completed_sections = sum(
            1 for section in self.SUMMARY_SECTIONS
            if data.get(section) is not None
        )
        return completed_sections / len(self.SUMMARY_SECTIONS)
    
    @staticmethod
    def _format_list_items(items: List[Any]) -> str:
        """Format list of items for text output"""
        if isinstance(items, list):
            return "\n".join(f"- {item}" for item in items)
        return str(items)
    
    @staticmethod
    def _format_medication_list(medications: List[Dict[str, str]]) -> str:
        """Format medication list for text output"""
        lines = []
        for med in medications if isinstance(medications, list) else []:
            if isinstance(med, dict):
                line = f"- {med.get('name', 'Unknown')}"
                if med.get('dosage'):
                    line += f" {med.get('dosage')}"
                if med.get('frequency'):
                    line += f" {med.get('frequency')}"
                lines.append(line)
            else:
                lines.append(f"- {med}")
        return "\n".join(lines) if lines else "None reported"
