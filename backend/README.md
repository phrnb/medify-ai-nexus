
# Medify AI Nexus Backend

A RESTful API built with FastAPI and PostgreSQL for a medical diagnosis system with AI integration.

## Features

- RESTful API with FastAPI
- PostgreSQL database
- JWT + 2FA Authentication
- Patient management
- Medical image upload and management
- Neural network analysis integration
- Report generation (HTML & PDF)
- Analytics and statistics
- Integration capabilities with EHR systems

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL
- Poetry (for dependency management)

### Installation

1. Clone the repository
2. Install dependencies with Poetry:
   ```
   cd backend
   poetry install
   ```
3. Set up environment variables in `.env` file:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/medify
   SECRET_KEY=your-secret-key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```
4. Run database migrations:
   ```
   poetry run alembic upgrade head
   ```
5. Start the server:
   ```
   poetry run uvicorn app.main:app --reload
   ```

### API Documentation

Once the server is running, access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
