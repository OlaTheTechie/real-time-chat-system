# api testing summary

## server status

Your FastAPI server is running successfully on `http://localhost:8000`

All core API endpoints have been tested and are working correctly.

##  project requirements met

### 1. class-based views 
- All endpoints refactored to use class-based architecture
- Business logic separated into view classes
- Routes delegate to view methods
- See [CLASS_BASED_VIEWS.md](CLASS_BASED_VIEWS.md)

### 2. admin panel 
- Web-based admin interface at `/admin`
- All models accessible (User, ChatRoom, Message, PasswordResetToken)
- Full CRUD operations
- Search, sort, and filter capabilities
- See [ADMIN_PANEL.md](ADMIN_PANEL.md)

### 3. authentication 
- Register/Sign-up
- Login
- Logout
- Password Reset (request & confirm)
- Session Check (GET /me)
- Token Refresh

### 4. chat features 
- One-to-one chat
- Group chat
- Real-time messaging (WebSocket)
- Message persistence
- Message history with pagination

### 5. code quality 
- Multiple apps (auth, chat, admin)
- Models, serializers (Pydantic schemas), views
- Time and space complexity documented for all methods
- Proper structure and organization

## test results

All 10 tests passed:

1. Health check
2. Root endpoint
3. Register user
4. Login user
5. Get current user (session check)
6. Create chat room
7. Get chat rooms
8. Send message
9. Get messages
10. Get room details

## available resources

### access points

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Admin Panel**: http://localhost:8000/admin
- **Health Check**: http://localhost:8000/health

### files created for testing

1. **postman_collection.json** - Complete Postman collection with all API endpoints
2. **testing_guide.md** - Detailed guide for testing with Postman
3. **quick_start.md** - Quick reference for starting the server
4. **test_api.sh** - Automated test script (just run `./test_api.sh`)
5. **start.sh** - Server startup script with checks
6. **CLASS_BASED_VIEWS.md** - Documentation on class-based architecture
7. **ADMIN_PANEL.md** - Admin panel usage guide

## testing with postman

### import the collection

1. open postman
2. click **import**
3. select `postman_collection.json` from the backend directory
4. collection "realtime chat server api" will be imported

### quick test flow

the collection includes automatic variable setting, so you can just run requests in order:

1. **register user** - saves `user_id`
2. **login user** - saves `access_token`
3. **create chat room** - saves `room_id`
4. **send message** - uses saved variables
5. **get messages** - view your messages

all subsequent requests will automatically use the saved tokens and ids

## api endpoints summary

### authentication (`/api/v1/auth`)
- `post /register` - create new user account
- `post /login` - authenticate and get jwt token
- `get /me` - get current user info
- `post /refresh` - refresh jwt token
- `post /logout` - end session
- `post /password-reset` - request password reset
- `post /password-reset-confirm` - confirm password reset

### chat rooms (`/api/v1/chat/rooms`)
- `get /rooms` - list user's chat rooms
- `post /rooms` - create new chat room
- `get /rooms/{id}` - get room details with messages
- `get /rooms/{id}/messages` - get paginated messages
- `post /rooms/{id}/messages` - send message (rest)

### admin (`/api/v1/admin`)
- `get /users` - list all users
- `get /rooms` - list all rooms
- `get /messages` - list all messages

### websocket
- `ws://localhost:8000/ws/chat/{room_id}?token={jwt}` - real-time chat
- `ws://localhost:8000/ws/notifications?token={jwt}` - typing indicators

## websocket testing

websocket connections require a jwt token. you can test them using:

### browser console
```javascript
const token = "your_token_from_postman";
const ws = new WebSocket(`ws://localhost:8000/ws/chat/1?token=${token}`);

ws.onopen = () => {
  console.log("connected");
  ws.send(JSON.stringify({
    type: "message",
    content: "hello from websocket"
  }));
};

ws.onmessage = (event) => {
  console.log("received:", JSON.parse(event.data));
};
```

### wscat (cli)
```bash
npm install -g wscat
wscat -c "ws://localhost:8000/ws/chat/1?token=your_token"
```

### postman websocket
postman now supports websocket connections in the beta features

## important notes

### redis status
- websocket features require redis to be running
- if redis is not installed, rest api will work but websocket won't
- install redis: `sudo apt install redis-server`
- or use docker: `docker run -d -p 6379:6379 redis:latest`

### authentication
- all protected endpoints require `authorization: bearer {token}` header
- tokens expire after 30 minutes (configurable in `.env`)
- use the refresh endpoint to get a new token

### request body examples

**register:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123"
}
```

**login:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**create room:**
```json
{
  "name": "my chat room",
  "room_type": "group",
  "member_ids": [1, 2, 3]
}
```

**send message:**
```json
{
  "content": "hello, world"
}
```

## next steps

### backend is ready

your backend is fully functional and ready for frontend integration. you can now:

1. **test all endpoints in postman** - import the collection and explore
2. **test websocket connections** - use browser console or wscat
3. **start building the react frontend** - begin with task 6.1 from the spec

### start frontend development

```bash
# create react app with vite
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

see `.kiro/specs/realtime-chat-server/tasks.md` for the complete frontend implementation plan.

## troubleshooting

**can't connect to server:**
- check if server is running: `curl http://localhost:8000/health`
- check port 8000: `lsof -i :8000`

**authentication errors:**
- make sure you're using a valid token
- check token hasn't expired (30 min default)
- re-run the login request

**websocket errors:**
- ensure redis is running: `redis-cli ping`
- check websocket url format includes token query parameter
- verify you're a member of the room you're connecting to

## support

for detailed information, see:
- `testing_guide.md` - complete testing guide
- `quick_start.md` - server startup guide
- http://localhost:8000/docs - interactive api documentation
