# Quick Start Guide

## 🚀 Start the Server

### Option 1: Using the startup script (Recommended)

```bash
cd backend
./start.sh
```

This script will:
- Check if Redis is running
- Create `.env` file if needed
- Initialize the database if needed
- Start the FastAPI server

### Option 2: Manual start

```bash
cd backend
source .venv/bin/activate
python run_server.py
```

## 📦 Install Redis (Required for WebSocket)

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install redis-server
sudo service redis-server start
```

### Using Docker
```bash
docker run -d -p 6379:6379 redis:latest
```

### Verify Redis is running
```bash
redis-cli ping
# Should return: PONG
```

## 🧪 Test with Postman

1. **Import Collection**
   - Open Postman
   - Click Import
   - Select `postman_collection.json`

2. **Test Flow**
   - Health Check
   - Register User
   - Login User
   - Create Chat Room
   - Send Message
   - Get Messages

See `TESTING_GUIDE.md` for detailed instructions.

## 📚 API Documentation

Once the server is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔧 Useful Commands

```bash
# Initialize/reset database
python manage_db.py init

# Check database
sqlite3 chatserver.db ".tables"

# View logs
# Server logs appear in the terminal where you ran the server

# Stop server
# Press CTRL+C in the terminal
```

## ⚡ Quick Test (No Postman)

```bash
# Health check
curl http://localhost:8000/health

# Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"password123"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'
```

## 🐛 Troubleshooting

**Server won't start:**
- Check if port 8000 is already in use: `lsof -i :8000`
- Make sure virtual environment is activated

**Redis errors:**
- Install Redis (see above)
- Or run without Redis (WebSocket won't work)

**Database errors:**
- Delete `chatserver.db` and run `python manage_db.py init`

## 📁 Project Structure

```
backend/
├── app/
│   ├── auth/          # Authentication routes
│   ├── chat/          # Chat routes and WebSocket
│   ├── models/        # Database models
│   ├── core/          # Config and security
│   └── main.py        # FastAPI app
├── tests/             # Test files
├── run_server.py      # Server startup
├── manage_db.py       # Database management
└── postman_collection.json  # API tests
```
