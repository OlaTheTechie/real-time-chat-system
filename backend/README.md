# Realtime Chat Server

A FastAPI-based realtime chat server with WebSocket support, class-based views, admin panel, PostgreSQL database, and Redis for message broadcasting.

## Key Features

✅ **Class-Based Views**: All endpoints use class-based architecture for better organization and maintainability
✅ **Admin Panel**: Web-based interface at `/admin` for managing all models
✅ **Authentication**: Complete auth system (register, login, logout, password reset, session management)
✅ **Real-time Chat**: WebSocket support for instant messaging
✅ **One-to-One & Group Chat**: Support for both chat types
✅ **Message History**: Persistent storage with pagination
✅ **REST API**: Full REST API with automatic documentation
✅ **Time/Space Complexity**: All methods documented with complexity analysis

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

### Access Points

Once the server is running:
- **API Documentation**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc
- **Admin Panel**: http://localhost:8000/admin
- **Health Check**: http://localhost:8000/health

### Frontend (React)

To run the React frontend:
```bash
cd frontend
npm install
npm start
```

## Project Structure

```
backend/
├── app/
│   ├── admin/           # Admin panel configuration
│   ├── api/v1/          # API routes and admin views
│   ├── auth/            # Authentication (views + routes)
│   ├── chat/            # Chat functionality (views + routes)
│   ├── core/            # Core configuration and security
│   ├── database/        # Database and Redis connections
│   ├── models/          # SQLAlchemy models
│   └── main.py          # FastAPI application
├── docs/                # Documentation
│   ├── CLASS_BASED_VIEWS.md
│   ├── ADMIN_PANEL.md
│   └── API_TESTING_SUMMARY.md
├── alembic/             # Database migrations
└── requirements.txt     # Python dependencies
```

## Architecture

### Class-Based Views

All API endpoints use class-based views for better organization:

- **AuthViews**: Authentication operations
- **ChatRoomViews**: Chat room management
- **MessageViews**: Message operations
- **AdminViews**: Admin operations

See [CLASS_BASED_VIEWS.md](docs/CLASS_BASED_VIEWS.md) for details.

### Admin Panel

Web-based admin interface for managing:
- Users
- Chat Rooms
- Messages
- Password Reset Tokens

See [ADMIN_PANEL.md](docs/ADMIN_PANEL.md) for details.