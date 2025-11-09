# admin panel documentation

## overview

The project now includes a comprehensive admin panel built with SQLAdmin, providing a web-based interface to manage all database models. This fulfills the requirement: "The admin panel should contain all the models."

## access

**URL**: `http://localhost:8000/admin`

The admin panel is automatically available when the server is running in DEBUG mode.

## features

### 1. user management

**Model**: User

**Capabilities**:
- View all users with pagination
- Search users by username or email
- Sort by ID, username, email, or creation date
- View detailed user information
- Edit user details (username, email, online status)
- View user relationships (chat rooms, messages)

**Columns Displayed**:
- ID
- Username
- Email
- Online Status
- Created At
- Last Seen

**Note**: Password hashes are excluded from display for security.

### 2. chat room management

**Model**: ChatRoom

**Capabilities**:
- View all chat rooms with pagination
- Search rooms by name
- Sort by ID, name, or creation date
- View room details including members and messages
- Edit room properties
- Delete rooms
- View member count and message count

**Columns Displayed**:
- ID
- Name
- Room Type (one_to_one / group)
- Created By (User ID)
- Created At
- Member Count
- Message Count

### 3. message management

**Model**: Message

**Capabilities**:
- View all messages with pagination
- Search messages by content
- Sort by ID, timestamp, room, or sender
- View message details including sender and room
- Edit message content and properties
- Delete messages
- View message metadata (edited status, type)

**Columns Displayed**:
- ID
- Room ID
- Sender ID
- Content
- Timestamp
- Message Type
- Is Edited

### 4. password reset token management

**Model**: PasswordResetToken

**Capabilities**:
- View all password reset tokens
- Sort by creation date or expiration
- View token details
- Delete expired tokens
- Monitor token usage

**Columns Displayed**:
- ID
- User ID
- Token
- Created At
- Expires At
- Used Status

**Note**: This is a read-only view (cannot create or edit tokens).

## interface features

### navigation
- Sidebar with all model categories
- Icon-based navigation for easy identification
- Breadcrumb navigation

### list views
- Pagination controls
- Configurable page size
- Column sorting (click column headers)
- Search functionality
- Bulk actions

### detail views
- Complete model information
- Related object links
- Edit capabilities
- Delete confirmation

### forms
- Validation
- Required field indicators
- Relationship selectors
- Date/time pickers

## technical implementation

### technology stack
- **SQLAdmin**: Admin interface framework
- **SQLAlchemy**: ORM integration
- **FastAPI**: Web framework integration

### code structure

```python
backend/app/admin/
 __init__.py
 admin_panel.py      # Admin views and setup
```

### admin views

Each model has a dedicated admin view class:

1. **UserAdmin**: Manages User model
2. **ChatRoomAdmin**: Manages ChatRoom model
3. **MessageAdmin**: Manages Message model
4. **PasswordResetTokenAdmin**: Manages PasswordResetToken model

### setup

The admin panel is initialized in `app/main.py`:

```python
from app.admin import setup_admin

# setup admin panel (accessible at /admin)
admin = setup_admin(app, engine)
```

## security considerations

### current implementation
- Admin panel is accessible without authentication in DEBUG mode
- Suitable for development and testing

### production recommendations
1. Add authentication middleware
2. Implement role-based access control (RBAC)
3. Restrict access to admin users only
4. Enable audit logging
5. Use HTTPS only

### example authentication (future enhancement)

```python
from sqladmin.authentication import AuthenticationBackend

class AdminAuth(AuthenticationBackend):
    async def login(self, request):
        # implement admin login
        pass
    
    async def logout(self, request):
        # implement admin logout
        pass
    
    async def authenticate(self, request):
        # verify admin credentials
        pass

admin = Admin(app, engine, authentication_backend=AdminAuth())
```

## usage examples

### viewing users
1. Navigate to `http://localhost:8000/admin`
2. Click "Users" in the sidebar
3. Browse, search, or sort users
4. Click any user to view details

### creating a chat room
1. Go to "Chat Rooms"
2. Click "Create"
3. Fill in room details
4. Select room type
5. Save

### searching messages
1. Go to "Messages"
2. Use the search box to find content
3. Filter by room if needed
4. Click message to view full details

### managing password reset tokens
1. Go to "Password Reset Tokens"
2. View active tokens
3. Delete expired tokens
4. Monitor token usage

## api endpoints vs admin panel

### admin panel (web ui)
- **URL**: `/admin`
- **Purpose**: Human-friendly interface
- **Use Case**: Manual data management, debugging, monitoring

### admin api endpoints
- **URL**: `/api/v1/admin/*`
- **Purpose**: Programmatic access
- **Use Case**: Automated scripts, integrations, testing

Both provide similar functionality but serve different use cases.

## customization

### adding new models

To add a new model to the admin panel:

1. Create the model admin view:
```python
class NewModelAdmin(ModelView, model=NewModel):
    column_list = [NewModel.id, NewModel.name]
    name = "New Model"
    icon = "fa-solid fa-icon"
```

2. Register in `setup_admin()`:
```python
admin.add_view(NewModelAdmin)
```

### customizing views

Customize admin views by overriding properties:

- `column_list`: Columns to display in list view
- `column_searchable_list`: Searchable columns
- `column_sortable_list`: Sortable columns
- `column_details_list`: Fields in detail view
- `form_columns`: Editable fields
- `can_create`: Enable/disable creation
- `can_edit`: Enable/disable editing
- `can_delete`: Enable/disable deletion

## troubleshooting

### admin panel not loading
- Ensure server is running: `python run_server.py`
- Check URL: `http://localhost:8000/admin`
- Verify SQLAdmin is installed: `poetry show sqladmin`

### models not appearing
- Ensure models are imported in `app/models/__init__.py`
- Check admin views are registered in `setup_admin()`
- Restart the server

### cannot edit records
- Check `can_edit` property in admin view
- Verify `form_columns` includes the fields
- Check database permissions

## benefits

### for development
- Quick data inspection
- Easy testing data creation
- Debug database state
- Monitor relationships

### for testing
- Verify data integrity
- Check cascade deletes
- Inspect timestamps
- Validate constraints

### for debugging
- View raw data
- Check foreign keys
- Inspect relationships
- Monitor token expiration

## comparison with django admin

| Feature | Django Admin | SQLAdmin (FastAPI) |
|---------|-------------|-------------------|
| Model Registration |  |  |
| List Views |  |  |
| Detail Views |  |  |
| Search |  |  |
| Filtering |  |  |
| Sorting |  |  |
| CRUD Operations |  |  |
| Relationships |  |  |
| Custom Actions |  |  Limited |
| Authentication |  Built-in |  Manual |

SQLAdmin provides similar functionality to Django Admin while working seamlessly with FastAPI.

## next steps

### recommended enhancements
1. Add authentication and authorization
2. Implement audit logging
3. Add custom actions (bulk operations)
4. Create dashboard with statistics
5. Add export functionality (CSV, JSON)
6. Implement advanced filtering
7. Add inline editing for relationships

## conclusion

The admin panel provides a complete web-based interface for managing all models in the chat server, meeting the project requirement for an admin panel that contains all models. It's accessible in DEBUG mode and provides full CRUD operations with a user-friendly interface.
