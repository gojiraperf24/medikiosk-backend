"""Custom application exceptions"""


class MediKioskException(Exception):
    """Base exception for MediKiosk application"""
    pass


class AuthenticationException(MediKioskException):
    """Authentication related exceptions"""
    pass


class AuthorizationException(MediKioskException):
    """Authorization related exceptions"""
    pass


class PatientNotFoundException(MediKioskException):
    """Patient not found exception"""
    pass


class SessionNotFoundException(MediKioskException):
    """Session not found exception"""
    pass


class DocumentProcessingException(MediKioskException):
    """Document processing exception"""
    pass


class ABDMIntegrationException(MediKioskException):
    """ABDM integration exception"""
    pass


class ConsentException(MediKioskException):
    """Consent related exception"""
    pass


class ASRException(MediKioskException):
    """Automatic Speech Recognition exception"""
    pass


class TTSException(MediKioskException):
    """Text-to-Speech exception"""
    pass


class ConversationEngineException(MediKioskException):
    """Conversation engine exception"""
    pass
