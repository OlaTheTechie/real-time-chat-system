# architecture overview

## system architecture

```

                         CLIENT LAYER                             

  React Frontend (TypeScript)                                     
  - Authentication UI                                             
  - Chat Interface                                                
  - Real-time Messaging                                           
  - Room Management                                               

                              
                               HTTP/WebSocket
                              

                      FASTAPI APPLICATION                         

                                                                   
     
                      ADMIN PANEL                              
    SQLAdmin Web Interface (/admin)                           
    - User Management                                          
    - ChatRoom Management                                      
    - Message Management                                       
    - Token Management                                         
     
                                                                   
     
                      API ROUTES                               
    /api/v1/auth/*    - Authentication endpoints              
    /api/v1/chat/*    - Chat endpoints                        
    /api/v1/admin/*   - Admin API endpoints                   
    /ws/chat/*        - WebSocket endpoints                   
     
                                                                  
                                                                  
     
                    CLASS-BASED VIEWS                          
                                                                
             
      AuthViews      ChatRoomViews   MessageViews      
                                                       
     - register()    - list()        - get()           
     - login()       - create()      - send()          
     - logout()      - get()                           
     - refresh()                                       
             
                                                                
                                               
      AdminViews                                             
                                                             
     - list_*()                                              
     - get_*()                                               
     - delete_*()                                            
                                               
     
                                                                  
                                                                  
     
                    PYDANTIC SCHEMAS                           
    - UserCreate, UserResponse                                 
    - ChatRoomCreate, ChatRoomResponse                         
    - MessageCreate, MessageResponse                           
    - Token, TokenRefresh                                      
     
                                                                  
                                                                  
     
                    SQLALCHEMY MODELS                          
    - User                                                      
    - ChatRoom                                                 
    - Message                                                  
    - PasswordResetToken                                       
     
                                                                   

                              
                              

                      DATABASE LAYER                              

  SQLite (Development) / PostgreSQL (Production)                  
  - users                                                         
  - chat_rooms                                                    
  - messages                                                      
  - password_reset_tokens                                         
  - room_memberships (association table)                          



                      REDIS LAYER (Optional)                      

  Redis Cache                                                     
  - WebSocket message broadcasting                                
  - Password reset tokens                                         
  - Session management                                            

```

## request flow

### rest api request flow

```
Client Request
    
    
FastAPI Router (/api/v1/auth/register)
    
    
Route Handler (register_user)
    
    
View Class Method (AuthViews.register)
    
     Validate Input (Pydantic Schema)
    
     Business Logic
        Check existing user
        Hash password
        Create user
    
     Database Operation (SQLAlchemy)
    
     Return Response (Pydantic Schema)
        
        
    JSON Response to Client
```

### websocket request flow

```
Client WebSocket Connection
    
    
WebSocket Endpoint (/ws/chat/{room_id})
    
     Authenticate (JWT Token)
    
     Verify Room Membership
    
     Connect to Room
    
     Message Loop
        
         Receive Message
        
         Save to Database
        
         Broadcast to Room Members
           (via Redis or in-memory)
        
         Continue Loop
```

### admin panel flow

```
Admin Panel Request (/admin/user)
    
    
SQLAdmin Interface
    
     Render List View
        Query Database
        Apply Filters/Search
        Paginate Results
        Render HTML
    
     Handle CRUD Operations
        Create: Form → Validate → Insert
        Read: Query → Display
        Update: Form → Validate → Update
        Delete: Confirm → Delete
    
     Return HTML Response
```

## class-based view architecture

### view class structure

```python
class AuthViews:
    """
    Class-based views for authentication operations
    All methods are static for stateless operation
    """
    
    @staticmethod
    def register(user_data: UserCreate, db: Session):
        """
        Register a new user
        
        Time Complexity: O(1) - Single database operation
        Space Complexity: O(1) - Single user object
        
        Args:
            user_data: User registration data
            db: Database session
            
        Returns:
            UserResponse: Created user data
            
        Raises:
            HTTPException: If user already exists
        """
        # implementation
        pass
```

### route delegation pattern

```python
# routes.py
@router.post("/register", response_model=UserResponse)
def register_user(*args, **kwargs):
    """Register a new user"""
    return AuthViews.register(*args, **kwargs)
```

## data flow

### authentication flow

```
1. User Registration
   Client → POST /api/v1/auth/register
   → AuthViews.register()
   → Hash password
   → Save to database
   → Return user data

2. User Login
   Client → POST /api/v1/auth/login
   → AuthViews.login()
   → Verify credentials
   → Generate JWT tokens
   → Update online status
   → Return tokens

3. Session Check
   Client → GET /api/v1/auth/me (with JWT)
   → Verify JWT token
   → AuthViews.get_current_user_profile()
   → Return user data

4. Token Refresh
   Client → POST /api/v1/auth/refresh (with refresh token)
   → AuthViews.refresh_token()
   → Verify refresh token
   → Generate new tokens
   → Return new tokens
```

### chat flow

```
1. Create Room
   Client → POST /api/v1/chat/rooms
   → ChatRoomViews.create_chat_room()
   → Validate room type
   → Check for duplicates (one-to-one)
   → Create room
   → Add members
   → Return room data

2. Send Message (REST)
   Client → POST /api/v1/chat/rooms/{id}/messages
   → MessageViews.send_message()
   → Verify membership
   → Save message
   → Return message data

3. Send Message (WebSocket)
   Client → WebSocket message
   → Verify connection
   → Save to database
   → Broadcast to room members
   → Confirm delivery

4. Get Messages
   Client → GET /api/v1/chat/rooms/{id}/messages
   → MessageViews.get_room_messages()
   → Verify membership
   → Query with pagination
   → Return messages
```

## database schema

```

     users       

 id (PK)         
 username        
 email           
 hashed_password 
 is_online       
 created_at      
 last_seen       

        
         1:N
        
         
  chat_rooms     N:N room_memberships 
         
 id (PK)                   room_id (FK)     
 name                      user_id (FK)     
 room_type                
 created_by (FK) 
 created_at      

        
         1:N
        

    messages     

 id (PK)         
 room_id (FK)    
 sender_id (FK)  
 content         
 timestamp       
 message_type    
 is_edited       



 password_reset_tokens

 id (PK)              
 user_id (FK)         
 token                
 expires_at           
 created_at           
 used                 

```

## component responsibilities

### admin panel (`app/admin/`)
- Web-based interface for data management
- CRUD operations for all models
- Search, filter, and sort capabilities
- Built with SQLAdmin

### api routes (`app/api/v1/`)
- Route definitions
- Request/response handling
- Delegation to view classes
- API documentation

### views (`app/*/views.py`)
- Business logic implementation
- Database operations
- Validation and error handling
- Complexity-optimized algorithms

### models (`app/models/`)
- Database schema definitions
- Relationships between entities
- Model methods and properties
- SQLAlchemy ORM

### schemas (`app/*/schemas.py`)
- Request/response validation
- Data serialization
- Type definitions
- Pydantic models

### core (`app/core/`)
- Configuration management
- Security utilities (JWT, hashing)
- Application settings
- Constants

### database (`app/database/`)
- Database connection
- Session management
- Redis connection
- Connection pooling

## security architecture

```

                    SECURITY LAYERS                           

                                                               
  1. Authentication Layer                                     
     - JWT token validation                                   
     - Password hashing (bcrypt)                              
     - Token expiration                                       
                                                               
  2. Authorization Layer                                      
     - Room membership verification                           
     - User ownership checks                                  
     - Admin access control                                   
                                                               
  3. Input Validation Layer                                   
     - Pydantic schema validation                             
     - Type checking                                          
     - Data sanitization                                      
                                                               
  4. Database Layer                                           
     - SQL injection prevention (ORM)                         
     - Parameterized queries                                  
     - Transaction management                                 
                                                               
  5. Transport Layer                                          
     - HTTPS (production)                                     
     - CORS configuration                                     
     - WebSocket security                                     
                                                               

```

## scalability considerations

### horizontal scaling
- Stateless API design
- JWT tokens (no server-side sessions)
- Redis for shared state
- Load balancer ready

### vertical scaling
- Optimized database queries
- Connection pooling
- Efficient algorithms (documented complexity)
- Pagination for large datasets

### caching strategy
- Redis for WebSocket messages
- Password reset tokens in Redis
- Database query optimization
- Static asset caching

## monitoring points

```

                    MONITORING POINTS                         

                                                               
  1. API Endpoints                                            
     - Request count                                          
     - Response time                                          
     - Error rate                                             
                                                               
  2. Database                                                 
     - Query performance                                      
     - Connection pool usage                                  
     - Slow queries                                           
                                                               
  3. WebSocket                                                
     - Active connections                                     
     - Message throughput                                     
     - Connection errors                                      
                                                               
  4. Admin Panel                                              
     - Access logs                                            
     - CRUD operations                                        
     - User activity                                          
                                                               

```

## deployment architecture

```

                    PRODUCTION SETUP                          

                                                               
                                              
   Load Balancer                                            
                                              
                                                              
                                                   
                                                            
                                                 
  App1   App2  FastAPI Instances                         
                                                 
                                                            
                                                    
                                                              
                                                   
    PostgreSQL  Database                                    
                                                   
                                                              
                                                   
      Redis    Cache & WebSocket                           
                                                   
                                                               

```

This architecture provides a scalable, maintainable, and well-documented foundation for the realtime chat server.
