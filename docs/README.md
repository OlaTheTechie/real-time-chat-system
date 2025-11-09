# engineering python test -  complete

## project status: all requirements implemented 

This is a Realtime Chat Server built with **FastAPI** (approved alternative to Django Rest Framework).

---

##  requirements completed

### 1. class-based views 
- **Requirement**: "The code should be class based"
- **Status**:  COMPLETE
- All endpoints refactored to use class-based architecture
- View classes: `AuthViews`, `ChatRoomViews`, `MessageViews`, `AdminViews`
- See: [`backend/docs/CLASS_BASED_VIEWS.md`](backend/docs/CLASS_BASED_VIEWS.md)

### 2. admin panel 
- **Requirement**: "The admin panel should contain all the models"
- **Status**:  COMPLETE
- Web-based admin interface at `/admin`
- All models included: User, ChatRoom, Message, PasswordResetToken
- Full CRUD operations with search, sort, and filter
- See: [`backend/docs/ADMIN_PANEL.md`](backend/docs/ADMIN_PANEL.md)

### 3. authentication 
- **Requirement**: Login, Sign-up, Register, Forgot Password, Check session, Refresh session
- **Status**:  COMPLETE
- All authentication endpoints implemented
- JWT token-based authentication
- Password reset functionality

### 4. chat features 
- **Requirement**: One-to-one chat, Group chat, Real-time, Stored in DB
- **Status**:  COMPLETE
- One-to-one chat with duplicate prevention
- Group chat with multiple members
- Real-time messaging via WebSocket
- All messages stored in database

### 5. frontend 
- **Requirement**: Minimal frontend to test the app
- **Status**:  COMPLETE
- React application with TypeScript
- Full authentication flow
- Real-time chat interface

### 6. code quality 
- **Requirement**: Refined code, minimal complexity, proper structure
- **Status**:  COMPLETE
- Time and space complexity documented for all methods
- Multiple apps with clear separation
- Properly structured and readable

### 7. api interface 
- **Requirement**: "APIs should be interface-able via direct path in DEBUG mode"
- **Status**:  COMPLETE
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Admin Panel: http://localhost:8000/admin

---

##  quick start

### 1. install dependencies
```bash
cd backend
poetry lock
poetry install --no-root
```

### 2. start server
```bash
cd backend
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. access application
- **API Documentation**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:8000/admin 
- **Health Check**: http://localhost:8000/health

### 4. run frontend
```bash
cd frontend
npm install
npm start
```

---

##  api endpoints

### authentication (`/api/v1/auth`)
-  POST `/register` - Sign-up/Register
-  POST `/login` - Login
-  POST `/logout` - Logout
-  GET `/me` - Check session
-  POST `/refresh` - Refresh session
-  POST `/password-reset` - Forgot password (request)
-  POST `/password-reset-confirm` - Forgot password (confirm)

### chat (`/api/v1/chat`)
-  GET `/rooms` - List user's rooms
-  POST `/rooms` - Create room (one-to-one or group)
-  GET `/rooms/{id}` - Get room details
-  GET `/rooms/{id}/messages` - Get messages (paginated)
-  POST `/rooms/{id}/messages` - Send message

### admin (`/api/v1/admin`)
-  GET `/users` - List all users
-  GET `/chat-rooms` - List all rooms
-  GET `/messages` - List all messages
-  GET `/stats` - Database statistics

### websocket
-  `/ws/chat/{room_id}?token={jwt}` - Real-time chat
-  `/ws/notifications?token={jwt}` - Typing indicators

### admin panel (web ui)
-  `/admin` - Admin dashboard with all models

---

##  project structure

```
punch-trial-project/
 backend/
    app/
       admin/              #  Admin panel
       api/v1/             # API routes
       auth/               # Authentication (views + routes)
       chat/               # Chat (views + routes)
       core/               # Configuration
       database/           # Database connections
       models/             # SQLAlchemy models
       main.py             # FastAPI app
    docs/
       CLASS_BASED_VIEWS.md        #  Architecture guide
       ADMIN_PANEL.md              #  Admin panel guide
       IMPLEMENTATION_COMPLETE.md  #  Requirements checklist
       ARCHITECTURE.md             #  System architecture
       API_TESTING_SUMMARY.md
    pyproject.toml
 frontend/                   # React application
 QUICK_START_UPDATED.md      #  Quick start guide
 IMPLEMENTATION_SUMMARY.md   #  Project summary
 FINAL_CHECKLIST.md          #  Verification checklist
 CHANGES_MADE.md             #  All changes documented
 README.md                   # This file
```

---

##  key features

### class-based architecture
All endpoints use class-based views for better organization:
```python
class AuthViews:
    @staticmethod
    def register(user_data: UserCreate, db: Session):
        """
        Register a new user
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        # implementation
```

### admin panel
Web-based interface for managing all models:
- User management
- Chat room management
- Message management
- Password reset token management
- Search, sort, filter capabilities

### time & space complexity
All methods include complexity documentation:
- Easy performance analysis
- Identify bottlenecks
- Optimization guidance

---

##  documentation

| Document | Description |
|----------|-------------|
| [`CLASS_BASED_VIEWS.md`](backend/docs/CLASS_BASED_VIEWS.md) | Class-based architecture guide |
| [`ADMIN_PANEL.md`](backend/docs/ADMIN_PANEL.md) | Admin panel usage guide |
| [`IMPLEMENTATION_COMPLETE.md`](backend/docs/IMPLEMENTATION_COMPLETE.md) | Detailed requirements checklist |
| [`ARCHITECTURE.md`](backend/docs/ARCHITECTURE.md) | System architecture diagrams |
| [`QUICK_START_UPDATED.md`](QUICK_START_UPDATED.md) | Quick start guide |
| [`IMPLEMENTATION_SUMMARY.md`](IMPLEMENTATION_SUMMARY.md) | Project summary |
| [`FINAL_CHECKLIST.md`](FINAL_CHECKLIST.md) | Verification checklist |
| [`CHANGES_MADE.md`](CHANGES_MADE.md) | All changes documented |

---

##  testing

### manual testing
1. **API**: http://localhost:8000/docs
2. **Admin Panel**: http://localhost:8000/admin
3. **Frontend**: http://localhost:3000

### automated testing
```bash
cd backend
./test_api.sh
```

### postman collection
Import `backend/postman_collection.json` for complete API testing.

---

##  performance

All operations are optimized with documented complexity:

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| Register | O(1) | O(1) |
| Login | O(1) | O(1) |
| List Rooms | O(n) | O(n) |
| Create Room | O(m) | O(m) |
| Send Message | O(1) | O(1) |
| Get Messages | O(log n + k) | O(k) |

---

##  security

- JWT token authentication
- Password hashing with bcrypt
- Input validation with Pydantic
- SQL injection prevention (ORM)
- CORS configuration
- WebSocket security

---

##  technologies

- **Backend**: FastAPI, SQLAlchemy, SQLAdmin
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Cache**: Redis (optional)
- **Frontend**: React, TypeScript
- **Authentication**: JWT, bcrypt
- **WebSocket**: FastAPI WebSocket support

---

##  requirements verification

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Class-based views |  | `app/*/views.py` |
| Admin panel |  | `/admin` URL |
| Authentication |  | 7 auth endpoints |
| One-to-one chat |  | Implemented |
| Group chat |  | Implemented |
| Real-time |  | WebSocket |
| Stored in DB |  | All messages |
| Frontend |  | React app |
| Multiple apps |  | admin, auth, chat |
| Models |  | 4 models |
| Serializers |  | Pydantic schemas |
| Complexity docs |  | All methods |
| API interface |  | `/docs`, `/admin` |
| Code quality |  | Structured, documented |

---

##  conclusion

**All project requirements have been successfully implemented and verified.**

The project includes:
-  Class-based views throughout
-  Admin panel with all models
-  Complete authentication system
-  One-to-one and group chat
-  Real-time messaging
-  Message persistence
-  Minimal functional frontend
-  Time/space complexity documented
-  API interface in DEBUG mode
-  Clean, readable, well-structured code

---

##  support

For questions or issues:
1. Check documentation in `backend/docs/`
2. Review API docs at http://localhost:8000/docs
3. Test admin panel at http://localhost:8000/admin
4. See `QUICK_START_UPDATED.md` for setup help

---

## original requirements

You're supposed to build a Realtime Chat Server using Django Rest Framework (FastAPI approved as alternative), so it can be utilised on the front-end. Some specifications for the project are as follow:

There should be Authentication, which consists of Login, Sign-up, Register, Forgot Password, Check session, Refresh session and so on. You can build it custom or use any library for achieving the goal.

The options for chat can be multiple:
- One-to-one Chat
- Group Chat

The chat should be realtime.
The chat should be accessible at a later time/stored in db as well.

The front-end should be minimal to test the app. There would be No points for the UI but for functionality. You can use any front-end technology or plain HTML/JS. Simple text boxes would work.

Code requirements:
- The code should be class based.
- You are free to create as many apps, models, serialisers, and views required but More points would be given to the refined code.
- The time and space complexity for each function/view/serialised should be minimal.
- The admin panel should contain all the models. And the APIs should be interface-able via direct path in DEBUG mode.
- The code should be properly structured and readable.

---

**Project Status**:  COMPLETE - All requirements met and verified
**Date**: November 8, 2025