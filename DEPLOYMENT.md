# MediKiosk Backend - Development & Deployment Guide

## Quick Start

### Using Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/gojiraperf24/medikiosk-backend.git
cd medikiosk-backend

# Create .env file
cp .env.example .env

# Start services
docker-compose up --build

# Access API
http://localhost:8000
http://localhost:8000/docs (Swagger UI)
http://localhost:8000/redoc (ReDoc)
```

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database and API keys

# Run migrations (optional)
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

## Docker Compose Services

- **app** (Port 8000): FastAPI backend application
- **db** (Port 5432): PostgreSQL database
- **redis** (Port 6379): Redis cache for sessions

## Database Migrations

### Create new migration
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback
```bash
alembic downgrade -1
```

## API Testing

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Register patient
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "phone": "9876543210",
    "email": "john@example.com",
    "preferred_language": "en"
  }'
```

### Using Python requests

```python
import requests

base_url = "http://localhost:8000/api/v1"

# Register patient
response = requests.post(f"{base_url}/auth/register", json={
    "first_name": "Jane",
    "last_name": "Smith",
    "phone": "9876543211",
    "email": "jane@example.com"
})
print(response.json())
```

## Environment Variables

Key environment variables (see `.env.example` for complete list):

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key
- `ABDM_CLIENT_ID`: ABDM gateway client ID
- `OPENAI_API_KEY`: OpenAI API key for LLM
- `BHASHINI_API_KEY`: Bhashini API key for speech recognition

## Logging

Logs are configured as JSON by default. Check `app/utils/logger.py` for configuration.

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py
```

## Project Structure

```
medikiosk-backend/
├── app/
│   ├── core/              # Configuration, security, constants
│   ├── models/            # SQLAlchemy ORM models
│   ├── schemas/           # Pydantic validation schemas
│   ├── services/          # Business logic
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/ # API route handlers
│   ├── database/          # Database utilities
│   ├── utils/             # Helper functions
│   └── main.py            # FastAPI application
├── tests/                 # Test suite
├── alembic/               # Database migrations
├── docker-compose.yml     # Container orchestration
├── Dockerfile             # Application container
└── requirements.txt       # Python dependencies
```

## Production Deployment

### Important Security Steps

1. **Change SECRET_KEY** in `.env`
2. **Set DEBUG=False** in production
3. **Use strong database passwords**
4. **Enable HTTPS/SSL**
5. **Set proper CORS origins**
6. **Use environment secrets management** (AWS Secrets Manager, HashiCorp Vault, etc.)

### Deployment with Docker

```bash
# Build image
docker build -t medikiosk-backend:latest .

# Push to registry
docker tag medikiosk-backend:latest your-registry/medikiosk-backend:latest
docker push your-registry/medikiosk-backend:latest

# Deploy on Kubernetes/Docker Swarm
# (Update docker-compose.yml for production)
docker-compose -f docker-compose.prod.yml up -d
```

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps

# Check logs
docker-compose logs db

# Recreate database
docker-compose down -v
docker-compose up
```

### Port Already in Use

```bash
# Change ports in docker-compose.yml or
# Kill process using port
lsof -i :8000
kill -9 <PID>
```

## Contributing

See CONTRIBUTING.md for guidelines.

## Support

For issues and questions, create an issue on GitHub or contact the MediKiosk team.

## License

MIT License - see LICENSE file for details
