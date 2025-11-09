# quick start guide - updated project

## what's new

 **Class-Based Views** - All endpoints now use class-based architecture
 **Admin Panel** - Web interface at `/admin` for managing all models
 **Complete Requirements** - All project specifications met

## quick start

### 1. install dependencies

```bash
cd backend
poetry lock
poetry install --no-root
```

### 2. start the server

```bash
cd backend
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or use the startup script:
```bash
cd backend
./start.sh
```

### 3. access the application

Once the server is running:

- **API Documentation**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:8000/admin  NEW
- **Health Check**: http://localhost:8000/health

### 4. test the admin panel

1. Open http://localhost:8000/admin
2. Browse through:
   - **Users** - View and manage all users
   - **Chat Rooms** - View and manage chat rooms
   - **Messages** - View and manage messages
   - **Password Reset Tokens** - View reset tokens

### 5. test the api

#### using swagger ui (recommended)
1. Go to http://localhost:8000/docs
2. Try the endpoints in order:
   - POST `/api/v1/auth/register` - Create a user
   - POST `/api/v1/auth/login` - Get access token
   - Click "Authorize" button, enter: `Bearer YOUR_TOKEN`
   - GET `/api/v1/auth/me` - Check session
   - POST `/api/v1/chat/rooms` - Create a chat room
   - POST `/api/v1/chat/rooms/{id}/messages` - Send a message

#### using postman
```bash
# import the collection
cd backend
# open postman and import: postman_collection.json
```

#### using curl
```bash
# register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"password123"}'

# login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# check session (replace token with your access token)
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer TOKEN"
```

### 6. run the frontend

```bash
cd frontend
npm install
npm start
```

Frontend will be available at http://localhost:3000

## project structure

```
punch-trial-project/
 backend/
    app/
       admin/          #  NEW: Admin panel
       api/v1/         # API routes
       auth/           # Authentication (views + routes)
       chat/           # Chat (views + routes)
       core/           # Configuration
       database/       # Database connections
       models/         # SQLAlchemy models
       main.py         # FastAPI app
    docs/
       CLASS_BASED_VIEWS.md        #  NEW
       ADMIN_PANEL.md              #  NEW
       IMPLEMENTATION_COMPLETE.md  #  NEW
       API_TESTING_SUMMARY.md
    pyproject.toml
 frontend/
     src/
```

## key changes

### 1. class-based views

**Before:**
```python
@router.post("/register")
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # logic here
    pass
```

**After:**
```python
# views.py
class AuthViews:
    @staticmethod
    def register(user_data: UserCreate, db: Session = Depends(get_db)):
        """Time Complexity: O(1), Space Complexity: O(1)"""
        # logic here
        pass

# routes.py
@router.post("/register")
def register_user(*args, **kwargs):
    return AuthViews.register(*args, **kwargs)
```

### 2. admin panel

New web interface at `/admin` with:
- User management
- Chat room management
- Message management
- Password reset token management
- Search, sort, filter capabilities

### 3. complexity documentation

All view methods now include:
```python
"""
Method description

Time Complexity: O(n)
Space Complexity: O(n)
"""
```

## testing checklist

###  authentication
- [ ] Register a new user
- [ ] Login with credentials
- [ ] Get current user (session check)
- [ ] Refresh token
- [ ] Request password reset
- [ ] Confirm password reset
- [ ] Logout

###  chat
- [ ] Create one-to-one chat
- [ ] Create group chat
- [ ] List user's chat rooms
- [ ] Get room details
- [ ] Send message via REST
- [ ] Get message history
- [ ] Connect via WebSocket
- [ ] Send real-time message

###  admin panel
- [ ] Access admin panel at `/admin`
- [ ] View users list
- [ ] View chat rooms list
- [ ] View messages list
- [ ] Search for a user
- [ ] Sort messages by timestamp
- [ ] View room details
- [ ] Delete a message

###  admin api
- [ ] GET `/api/v1/admin/users`
- [ ] GET `/api/v1/admin/chat-rooms`
- [ ] GET `/api/v1/admin/messages`
- [ ] GET `/api/v1/admin/stats`

## troubleshooting

### server won't start
```bash
# check if port 8000 is in use
lsof -i :8000

# kill the process if needed
kill -9 <PID>

# reinstall dependencies
cd backend
poetry install --no-root
```

### admin panel not loading
```bash
# verify sqladmin is installed
poetry show sqladmin

# check server logs for errors
poetry run uvicorn app.main:app --reload
```

### import errors
```bash
# ensure you're in the backend directory
cd backend

# run with poetry
poetry run uvicorn app.main:app --reload
```

### database errors
```bash
# delete and recreate database
rm chat.db

# restart server (tables will be created automatically)
poetry run uvicorn app.main:app --reload
```

## documentation

For detailed information, see:

1. **CLASS_BASED_VIEWS.md** - Architecture and implementation details
2. **ADMIN_PANEL.md** - Admin panel usage guide
3. **IMPLEMENTATION_COMPLETE.md** - Complete requirements checklist
4. **API_TESTING_SUMMARY.md** - API testing guide

## support

If you encounter any issues:

1. Check the documentation in `backend/docs/`
2. Review the API documentation at http://localhost:8000/docs
3. Check server logs for error messages
4. Verify all dependencies are installed: `poetry show`

## next steps

1.  Start the server
2.  Test the admin panel
3.  Test the API endpoints
4.  Run the frontend
5.  Test real-time chat via WebSocket
6.  Review the documentation

## summary

All project requirements have been implemented:

 Class-based views
 Admin panel with all models
 Complete authentication
 One-to-one and group chat
 Real-time messaging
 Message persistence
 Minimal frontend
 Time/space complexity documented
 API interface in DEBUG mode

The project is ready for testing and deployment!
