# API Testing Guide

This guide will help you test the Realtime Chat Server API using Postman.

## Prerequisites

1. **Redis** - Make sure Redis is running on `localhost:6379`
2. **Python Environment** - Virtual environment with dependencies installed
3. **Database** - SQLite database will be created automatically

## Quick Start

### 1. Start Redis (if not already running)

```bash
# On Ubuntu/Debian
sudo service redis-server start

# Or using Docker
docker run -d -p 6379:6379 redis:latest

# Verify Redis is running
redis-cli ping
# Should return: PONG
```

### 2. Set up Environment Variables

```bash
cd backend
cp .env.example .env
```

The default `.env` file uses SQLite, which is perfect for testing.

### 3. Initialize the Database

```bash
# Activate virtual environment
source .venv/bin/activate

# Initialize database
python manage_db.py init
```

### 4. Start the Server

```bash
# From the backend directory
python run_server.py
```

The server will start on `http://localhost:8000`

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 5. Verify Server is Running

Open your browser and go to:
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Health Check**: http://localhost:8000/health

## Testing with Postman

### Import the Collection

1. Open Postman
2. Click **Import** button
3. Select the `postman_collection.json` file from the backend directory
4. The collection "Realtime Chat Server API" will be imported

### Test Flow

Follow this sequence to test the complete flow:

#### 1. Health Check
- Run the **Health Check** request
- Should return: `{"status": "healthy"}`

#### 2. Register a User
- Run **Authentication > Register User**
- This will automatically save the `user_id` to collection variables
- Expected response:
```json
{
  "id": 1,
  "email": "testuser@example.com",
  "username": "testuser",
  "is_online": false,
  "created_at": "2024-01-01T12:00:00"
}
```

#### 3. Login
- Run **Authentication > Login User**
- This will automatically save the `access_token` to collection variables
- Expected response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

#### 4. Get Current User
- Run **Authentication > Get Current User**
- Should return your user details

#### 5. Create a Chat Room
- Run **Chat Rooms > Create Chat Room**
- This will automatically save the `room_id` to collection variables
- Expected response:
```json
{
  "id": 1,
  "name": "Test Chat Room",
  "room_type": "group",
  "created_by": 1,
  "created_at": "2024-01-01T12:00:00",
  "members": [...]
}
```

#### 6. Get All Chat Rooms
- Run **Chat Rooms > Get All Chat Rooms**
- Should return a list of rooms you're a member of

#### 7. Send a Message
- Run **Messages > Send Message (REST)**
- Expected response:
```json
{
  "id": 1,
  "room_id": 1,
  "sender_id": 1,
  "sender_username": "testuser",
  "content": "Hello from Postman!",
  "timestamp": "2024-01-01T12:00:00",
  "message_type": "text",
  "is_edited": false
}
```

#### 8. Get Room Messages
- Run **Messages > Get Room Messages**
- Should return all messages in the room

#### 9. Admin Endpoints (Optional)
- Run **Admin > Get All Users**
- Run **Admin > Get All Rooms**
- Run **Admin > Get All Messages**

## Testing WebSocket Connections

WebSocket connections cannot be tested directly in Postman, but you can use these tools:

### Option 1: Browser Console

Open browser console and run:

```javascript
// Replace with your actual token from Postman
const token = "YOUR_ACCESS_TOKEN_HERE";
const roomId = 1;

const ws = new WebSocket(`ws://localhost:8000/ws/chat/${roomId}?token=${token}`);

ws.onopen = () => {
  console.log("Connected!");
  
  // Send a message
  ws.send(JSON.stringify({
    type: "message",
    content: "Hello from WebSocket!"
  }));
};

ws.onmessage = (event) => {
  console.log("Received:", JSON.parse(event.data));
};

ws.onerror = (error) => {
  console.error("WebSocket error:", error);
};
```

### Option 2: wscat (Command Line)

```bash
# Install wscat
npm install -g wscat

# Connect to chat room (replace TOKEN and ROOM_ID)
wscat -c "ws://localhost:8000/ws/chat/1?token=YOUR_TOKEN"

# Send a message
{"type": "message", "content": "Hello from wscat!"}
```

### Option 3: Postman WebSocket (Beta)

Postman now supports WebSocket connections:
1. Create a new WebSocket request
2. URL: `ws://localhost:8000/ws/chat/1?token=YOUR_TOKEN`
3. Click Connect
4. Send JSON messages in the message panel

## Common Issues

### Redis Connection Error
```
redis.exceptions.ConnectionError: Error connecting to Redis
```
**Solution**: Make sure Redis is running on port 6379

### Database Locked Error
```
sqlite3.OperationalError: database is locked
```
**Solution**: Close any other connections to the database and restart the server

### Authentication Error
```
{"detail": "Could not validate credentials"}
```
**Solution**: Make sure you're using a valid access token. Re-run the Login request.

### Room Not Found
```
{"detail": "Chat room not found"}
```
**Solution**: Make sure the room_id variable is set. Create a room first.

## API Documentation

For detailed API documentation, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Collection Variables

The Postman collection uses these variables (automatically set by test scripts):
- `base_url`: http://localhost:8000
- `access_token`: JWT token from login
- `user_id`: Current user ID
- `room_id`: Current room ID

You can view/edit these in Postman:
1. Click on the collection name
2. Go to the **Variables** tab

## Next Steps

Once you've verified the API works:
1. Create multiple users to test one-to-one chat
2. Test group chat with multiple members
3. Test WebSocket real-time messaging
4. Start building the React frontend!

## Troubleshooting

If you encounter any issues:
1. Check server logs in the terminal
2. Verify Redis is running: `redis-cli ping`
3. Check database exists: `ls -la chatserver.db`
4. Restart the server
5. Check the FastAPI docs at http://localhost:8000/docs
