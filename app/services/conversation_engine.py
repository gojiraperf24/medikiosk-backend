"""Conversational AI engine for patient history elicitation"""
import asyncio
from typing import Dict, List, Optional, Any
from app.core.constants import CLINICAL_HISTORY_COMPONENTS, DAVIDHA_PARIKSHA_PARAMS
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ConversationEngine:
    """AI-powered conversation engine for clinical history taking"""
    
    # Clinical questioning templates
    SOCRATES_FRAMEWORK = {
        "S": "Site: Where exactly is the symptom?",
        "O": "Onset: When did it start?",
        "C": "Character: What does it feel like?",
        "R": "Radiation: Does it spread anywhere?",
        "A": "Aggravating factors: What makes it worse?",
        "T": "Relieving factors: What makes it better?",
        "E": "Emesis/Severity: Any associated symptoms? How severe (1-10)?",
        "S": "Severity/System review: Any other symptoms?"
    }
    
    def __init__(self, language: str = "hi", session_type: str = "general"):
        """Initialize conversation engine
        
        Args:
            language: Patient's preferred language (hi, en, ta, te, etc.)
            session_type: 'general' for allopathic, 'ayush' for Ayurvedic
        """
        self.language = language
        self.session_type = session_type
        self.conversation_history = []
        self.extracted_history = {}
        self.current_component = None
        self.red_flags = []
        
    async def start_conversation(self) -> Dict[str, Any]:
        """Start new conversation session"""
        logger.info(f"Starting {self.session_type} conversation in {self.language}")
        
        opening_prompt = self._get_opening_prompt()
        self.conversation_history.append({
            "role": "assistant",
            "content": opening_prompt,
            "timestamp": self._get_timestamp()
        })
        
        return {
            "status": "started",
            "prompt": opening_prompt,
            "session_type": self.session_type,
            "language": self.language,
            "expected_input_type": ["voice", "text"]  # Dual-mode input
        }
    
    async def process_response(
        self,
        user_input: str,
        input_type: str = "voice",
        confidence: float = 1.0
    ) -> Dict[str, Any]:
        """Process patient response and generate next question
        
        Args:
            user_input: Patient's spoken or typed response
            input_type: 'voice' or 'text'
            confidence: ASR confidence score (0-1) for voice input
        """
        self.conversation_history.append({
            "role": "user",
            "content": user_input,
            "input_type": input_type,
            "confidence": confidence,
            "timestamp": self._get_timestamp()
        })
        
        # Extract medical information from response
        extracted = await self._extract_clinical_entities(user_input)
        self.extracted_history.update(extracted)
        
        # Check for red flags
        red_flags_detected = await self._detect_red_flags(user_input)
        if red_flags_detected:
            self.red_flags.extend(red_flags_detected)
            logger.warning(f"Red flags detected: {red_flags_detected}")
        
        # Determine next question
        next_question = await self._generate_next_question(extracted)
        
        self.conversation_history.append({
            "role": "assistant",
            "content": next_question,
            "timestamp": self._get_timestamp()
        })
        
        return {
            "status": "processing",
            "next_question": next_question,
            "extracted_entities": extracted,
            "red_flags": red_flags_detected,
            "conversation_progress": len(self.extracted_history) / len(CLINICAL_HISTORY_COMPONENTS)
        }
    
    async def _extract_clinical_entities(self, text: str) -> Dict[str, Any]:
        """Extract clinical entities from patient narration using NLP
        
        This would integrate with LLM or NER models
        """
        extracted = {}
        
        # Placeholder for actual entity extraction logic
        # In production, this would use OpenAI, LangChain, or spaCy
        text_lower = text.lower()
        
        # Simple pattern matching for demonstration
        if any(word in text_lower for word in ["chest", "heart", "pain"]):
            extracted["chief_complaint"] = "Chest pain"
        if any(word in text_lower for word in ["cough", "cold", "fever"]):
            extracted["chief_complaint"] = "Respiratory symptoms"
        if any(word in text_lower for word in ["diabetes", "sugar"]):
            extracted["past_medical_history"] = ["Diabetes"]
        
        return extracted
    
    async def _detect_red_flags(self, text: str) -> List[str]:
        """Detect emergency symptoms (red flags) in patient narration"""
        red_flags = []
        text_lower = text.lower()
        
        # Red flag keywords
        red_flag_patterns = {
            "chest_pain": ["chest pain", "heart pain", "pressure in chest"],
            "stroke_symptoms": ["weakness", "numbness", "facial droop", "speech difficulty"],
            "severe_breathing": ["difficulty breathing", "can't breathe", "shortness of breath"],
            "loss_of_consciousness": ["fainted", "lost consciousness", "blackout"],
            "severe_bleeding": ["heavy bleeding", "major bleed", "uncontrolled bleeding"],
            "acute_abdomen": ["severe abdominal pain", "acute belly pain"]
        }
        
        for flag_type, keywords in red_flag_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                red_flags.append(flag_type)
                logger.warning(f"Red flag detected: {flag_type}")
        
        return red_flags
    
    async def _generate_next_question(self, extracted: Dict[str, Any]) -> str:
        """Generate contextually appropriate next question based on SOCRATES framework
        
        Uses adaptive questioning logic to probe deeper
        """
        # If chief complaint identified, probe using SOCRATES
        if "chief_complaint" in extracted:
            if not hasattr(self, '_socrates_step'):
                self._socrates_step = 0
            
            steps = list(self.SOCRATES_FRAMEWORK.values())
            if self._socrates_step < len(steps):
                question = steps[self._socrates_step]
                self._socrates_step += 1
                return question
        
        # Default: Ask about review of systems
        return "Any other symptoms or health concerns you'd like to tell me about?"
    
    async def complete_conversation(self) -> Dict[str, Any]:
        """Complete conversation and prepare for summary generation"""
        logger.info("Completing conversation session")
        
        return {
            "status": "completed",
            "conversation_history": self.conversation_history,
            "extracted_history": self.extracted_history,
            "red_flags_detected": self.red_flags,
            "confidence_score": self._calculate_completeness()
        }
    
    def _calculate_completeness(self) -> float:
        """Calculate how complete the history is (0-1)"""
        components_captured = len(self.extracted_history)
        total_components = len(CLINICAL_HISTORY_COMPONENTS)
        return components_captured / total_components if total_components > 0 else 0.0
    
    def _get_opening_prompt(self) -> str:
        """Get session opening prompt based on language and type"""
        if self.session_type == "ayush":
            if self.language == "hi":
                return "नमस्ते! आपकी स्वास्थ्य जानकारी दर्ज करने में आपका स्वागत है। कृपया बताएं कि आज आप कैसा महसूस कर रहे हैं?"
            else:
                return "Welcome to your Ayurvedic health assessment. Please describe your current health concerns in detail."
        else:
            if self.language == "hi":
                return "नमस्ते! अपनी स्वास्थ्य समस्या के बारे में बताएं।"
            else:
                return "Hello! What brings you to the clinic today? Please describe your main health concern."
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat()


class AYUSHConversationEngine(ConversationEngine):
    """Extended conversation engine for Ayurvedic (AYUSH) history taking"""
    
    def __init__(self, language: str = "hi"):
        super().__init__(language, session_type="ayush")
        self.dashavidha_assessment = {param: None for param in DAVIDHA_PARIKSHA_PARAMS}
    
    async def get_dashavidha_questions(self) -> Dict[str, str]:
        """Generate questions for Dashavidha Pariksha assessment"""
        questions = {
            "prakriti": "आपकी मूल प्रकृति क्या है? (वात, पित्त, कफ)",
            "vikriti": "आपकी वर्तमान विषमता कौन सी है?",
            "sara": "आपकी ऊतक शक्ति कैसी है?",
            "samhanana": "आपकी शारीरिक संरचना कैसी है?",
            "pramana": "आपके शरीर का आकार कैसा है?",
            "satmya": "आपकी पाचन क्षमता कैसी है?",
            "sattva": "आपकी मानसिक शक्ति कैसी है?",
            "ahara_shakti": "आपकी भूख कैसी है?",
            "vyayama_shakti": "आपकी व्यायाम करने की क्षमता कैसी है?",
            "vaya": "आपकी उम्र किस श्रेणी में है?"
        }
        return questions
