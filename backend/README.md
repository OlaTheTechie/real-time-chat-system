# Realtime Chat Server

A FastAPI-based realtime chat server with WebSocket support, PostgreSQL database, and Redis for message broadcasting.

## Setup Instructions

### Prerequisites
- Python 3.10+
- Redis (optional for WebSocket functionality)

### Installation

1. Install dependencies using Poetry:
```bash
cd backend
poetry install --no-root
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configurations if needed
```

3. The application uses SQLite by default for development. For production, update DATABASE_URL in .env to use PostgreSQL.

4. Start the server:
```bash
python run_server.py
```

Or using uvicorn directly:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation

Once the server is running, visit:
- API Documentation: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

### Frontend (Streamlit)

To run the Streamlit frontend:
```bash
cd frontend
streamlit run main.py
```

## Project Structure

```
backend/
├── app/
│   ├── api/v1/          # API routes
│   ├── auth/            # Authentication module
│   ├── chat/            # Chat functionality
│   ├── core/            # Core configuration and security
│   ├── database/        # Database and Redis connections
│   ├── models/          # SQLAlchemy models
│   └── main.py          # FastAPI application
├── alembic/             # Database migrations
├── frontend/            # Streamlit frontend
└── requirements.txt     # Python dependencies
```