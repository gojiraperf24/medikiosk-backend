# MediKiosk Backend - AI Clinical History Software Platform

## Overview
MediKiosk is an AI-powered clinical history software platform designed for Indian hospitals and AYUSH institutions. It enables patients to independently record comprehensive medical histories through voice and touch interaction, digitize existing medical documents, and generate structured clinical summaries that integrate with hospital information systems and the ABDM ecosystem.

## Problem Statement
- **Consultation Time Bottleneck**: Indian public hospital OPDs operate with 2-5 minute consultations per patient
- **Document Fragmentation**: Physical medical records from multiple providers remain unstructured and inaccessible
- **AYUSH Complexity**: Ayurvedic history taking requires extensive assessment (Dashavidha Pariksha) that cannot be captured manually within OPD time constraints
- **First-Mile Problem**: No efficient mechanism to capture structured histories before clinical encounters begin

## Solution Architecture

### Core Modules

#### Module A: Conversational Multimodal History Engine
- Natural voice conversation in Indian languages (Hindi, English, regional languages)
- Adaptive questioning based on chief complaint
- Dual-mode input: voice + touchscreen interface
- AYUSH-specific extended history capture
- Red-flag detection for emergency symptoms

#### Module B: Medical Document Digitization & Intelligence
- OCR for handwritten and printed documents (multilingual)
- Clinical entity extraction (diagnoses, medications, investigations)
- Chronological organization of medical timeline
- Abnormal value highlighting

#### Module C: Structured History Summary Generator
- AI synthesis of conversational history and digitized documents
- Standard clinical format output
- Physician-ready summaries in seconds
- Bilingual output support

#### Module D: Consent, Privacy & ABDM Integration
- DPDP 2023 compliance
- ABHA authentication
- FHIR-based ABDM integration
- Secure data processing and session management

## Technology Stack
- **Backend Framework**: Python with FastAPI
- **Database**: PostgreSQL with FHIR-compliant schema
- **AI/ML**: LLMs for dialogue, OCR, entity extraction
- **Voice**: Bhashini/AI4Bharat for Indian language ASR & TTS
- **ABDM Integration**: FHIR APIs for health records exchange
- **Security**: JWT auth, encryption at rest/transit, audit logging

## Project Structure
```
medikiosk-backend/
├── app/
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── constants.py
│   ├── models/
│   │   ├── patient.py
│   │   ├── history.py
│   │   ├── document.py
│   │   └── session.py
│   ├── schemas/
│   │   ├── patient.py
│   │   ├── history.py
│   │   ├── document.py
│   │   └── responses.py
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py
│   │   │   │   ├── patients.py
│   │   │   │   ├── history.py
│   │   │   │   ├── documents.py
│   │   │   │   └── summaries.py
│   │   │   └── router.py
│   │   └── middleware.py
│   ├── services/
│   │   ├── conversation_engine.py
│   │   ├── document_processor.py
│   │   ├── summary_generator.py
│   │   ├── abdm_integration.py
│   │   ├── asr_tts.py
│   │   └── entity_extraction.py
│   ├── utils/
│   │   ├── validators.py
│   │   ├── fhir_converter.py
│   │   ├── logger.py
│   │   └── exceptions.py
│   ├── database/
│   │   ├── base.py
│   │   ├── session.py
│   │   └── migrations/
│   └── main.py
├── tests/
├── requirements.txt
├── .env.example
├── docker-compose.yml
├── Dockerfile
└── setup.py
```

## Getting Started

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Docker & Docker Compose (optional)

### Installation

1. Clone the repository
```bash
git clone https://github.com/gojiraperf24/medikiosk-backend.git
cd medikiosk-backend
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run migrations
```bash
alembic upgrade head
```

6. Start server
```bash
uvicorn app.main:app --reload
```

### Docker Setup
```bash
docker-compose up --build
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - ABHA/Aadhaar login
- `POST /api/v1/auth/register` - New patient registration
- `POST /api/v1/auth/consent` - Consent capture

### Patient Management
- `GET /api/v1/patients/{patient_id}` - Get patient details
- `PUT /api/v1/patients/{patient_id}` - Update patient info
- `GET /api/v1/patients/{patient_id}/history` - Retrieve patient history

### History Conversation
- `POST /api/v1/history/start` - Initiate conversation session
- `POST /api/v1/history/respond` - Submit voice/touch response
- `GET /api/v1/history/session/{session_id}` - Get session status

### Document Processing
- `POST /api/v1/documents/upload` - Upload medical document
- `GET /api/v1/documents/{document_id}` - Retrieve processed document
- `GET /api/v1/documents/timeline/{patient_id}` - Get chronological document timeline

### Summary Generation
- `POST /api/v1/summaries/generate` - Generate clinical summary
- `GET /api/v1/summaries/{summary_id}` - Retrieve summary
- `POST /api/v1/summaries/{summary_id}/confirm` - Physician confirmation

### ABDM Integration
- `POST /api/v1/abdm/link-abha` - Link to ABHA ID
- `POST /api/v1/abdm/push-record` - Push to personal health record
- `GET /api/v1/abdm/consent-status` - Check consent status

## Development Workflow

### Code Style
- Follow PEP 8
- Use type hints
- Max line length: 100 characters

### Testing
```bash
pytest tests/
pytest --cov=app tests/  # With coverage
```

### Database Migrations
```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## Security Considerations
- All patient data encrypted at rest and in transit
- DPDP 2023 compliance with consent management
- ABHA authentication for patient identification
- Audit logging for all data access
- Session termination and data cleanup after submission
- Role-based access control (RBAC)

## Compliance
- Digital Personal Data Protection Act 2023
- ABDM Consent Framework
- FHIR Standards for health data interoperability
- ISO 27001 for information security

## Key Features

✅ Multilingual voice-to-text history capture (Hindi, English, regional)
✅ Adaptive clinical questioning based on patient responses
✅ AYUSH-specific Dashavidha Pariksha assessment mode
✅ Medical document OCR and intelligent extraction
✅ Chronological medical timeline generation
✅ Red-flag detection for emergency symptoms
✅ Structured clinical summary generation
✅ ABDM/FHIR integration
✅ Low-literacy & accessibility-first UI design
✅ Physician review and confirmation workflow

## Contributing
See CONTRIBUTING.md for guidelines

## License
MIT License

## Contact
For queries about this project, contact: All India Institute of Ayurveda, Ministry of Ayush

## References
- [ABDM Official Documentation](https://www.abdm.gov.in/)
- [AI4Bharat Language Models](https://ai4bharat.org/)
- [FHIR Standard](https://www.hl7.org/fhir/)
- Problem Statement: [PS 26047 - Patient Case-Taking Software](https://drive.google.com/file/d/1mQ6Qp2MKL8JXdL2kJYqV-SFqcfbxSvrd/view)
