# class-based views implementation

## overview

All API endpoints have been refactored to use class-based views as required by the project specifications. This improves code organization, reusability, and maintainability.

## architecture

### structure

```
backend/app/
 auth/
    views.py          # AuthViews class with all auth logic
    routes.py         # Route definitions delegating to AuthViews
 chat/
    views.py          # ChatRoomViews and MessageViews classes
    routes.py         # Route definitions delegating to views
 api/v1/
     admin_views.py    # AdminViews class for admin operations
     admin.py          # Admin route definitions
```

## class-based views

### 1. authviews (app/auth/views.py)

Handles all authentication operations:

- `register()` - User registration
- `login()` - User authentication and token generation
- `logout()` - User logout and status update
- `refresh_token()` - JWT token refresh
- `get_current_user_profile()` - Session check / get current user
- `request_password_reset()` - Password reset request
- `confirm_password_reset()` - Password reset confirmation

**Time & Space Complexity**: All methods are O(1) for database operations with proper indexing.

### 2. chatroomviews (app/chat/views.py)

Handles chat room operations:

- `list_user_chat_rooms()` - List all rooms for current user
  - Time: O(n) where n is number of rooms
  - Space: O(n)
  
- `create_chat_room()` - Create new chat room
  - Time: O(n) where n is number of members
  - Space: O(n)
  
- `get_chat_room_details()` - Get room with messages
  - Time: O(m log m) where m is number of messages
  - Space: O(m)

### 3. messageviews (app/chat/views.py)

Handles message operations:

- `get_room_messages()` - Paginated message history
  - Time: O(log n + k) where n is total messages, k is page size
  - Space: O(k)
  
- `send_message()` - Send message to room
  - Time: O(1)
  - Space: O(1)

### 4. adminviews (app/api/v1/admin_views.py)

Handles admin operations for all models:

**User Management:**
- `list_users()` - List all users with pagination
- `get_user()` - Get specific user
- `delete_user()` - Delete user

**ChatRoom Management:**
- `list_chat_rooms()` - List all rooms with pagination
- `get_chat_room()` - Get specific room
- `delete_chat_room()` - Delete room

**Message Management:**
- `list_messages()` - List all messages with optional filtering
- `get_message()` - Get specific message
- `delete_message()` - Delete message

**Statistics:**
- `get_database_stats()` - Get database statistics

All admin methods include time and space complexity documentation.

## benefits

### 1. code organization
- Clear separation of concerns
- Business logic in view classes
- Route definitions remain clean and simple

### 2. reusability
- View methods can be called from multiple routes
- Easy to create alternative endpoints (e.g., GraphQL)

### 3. testability
- View classes can be tested independently
- No need to mock FastAPI routing

### 4. maintainability
- Changes to business logic only affect view classes
- Route changes don't affect business logic

### 5. performance documentation
- Each method includes time and space complexity
- Easy to identify performance bottlenecks

## usage example

### route definition (routes.py)
```python
@router.post("/register", response_model=UserResponse)
def register_user(*args, **kwargs):
    """Register a new user"""
    return AuthViews.register(*args, **kwargs)
```

### view implementation (views.py)
```python
class AuthViews:
    @staticmethod
    def register(user_data: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
        """
        Register a new user
        
        Time Complexity: O(1) - database query with index lookup
        Space Complexity: O(1) - single user object
        """
        # implementation here
        pass
```

## testing

All endpoints remain accessible at the same URLs:

- Authentication: `/api/v1/auth/*`
- Chat: `/api/v1/chat/*`
- Admin: `/api/v1/admin/*`

The refactoring is transparent to API consumers - all existing tests and integrations continue to work without modification.

## complexity analysis

All view methods include inline documentation of their time and space complexity:

- **O(1)**: Single database operations with indexes
- **O(n)**: Operations that iterate over n items
- **O(log n)**: Database queries with sorting/pagination
- **O(n log n)**: Operations that sort n items

This makes it easy to identify and optimize performance bottlenecks.
