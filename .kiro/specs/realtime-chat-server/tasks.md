# Implementation Plan

## Backend Tasks (Already Completed)

The FastAPI backend has been fully implemented with the following features:
- ✅ User authentication (register, login, logout, refresh token)
- ✅ Password reset functionality
- ✅ Chat room creation (one-to-one and group)
- ✅ Message sending via REST API
- ✅ WebSocket real-time messaging
- ✅ Redis pub/sub for message broadcasting
- ✅ Database models and relationships
- ✅ API documentation (Swagger/ReDoc)
- ✅ Admin endpoints

## Frontend Tasks (To Be Implemented)

- [x] 1. Set up React project with TypeScript and Vite
  - Initialize Vite project with React and TypeScript template
  - Install and configure TailwindCSS for styling
  - Set up project structure (components, pages, services, hooks, context, types, utils)
  - Configure environment variables for API base URL
  - _Requirements: 11.1, 11.2_

- [x] 2. Implement authentication context and API service
  - [x] 2.1 Create TypeScript type definitions for User, Token, and auth-related types
    - Define User interface with id, email, username, is_online, last_seen, created_at
    - Define Token interface with access_token, refresh_token, token_type
    - Define RegisterData and LoginData interfaces
    - _Requirements: 1.1, 2.1_

  - [x] 2.2 Create API client service with Axios
    - Set up Axios instance with base URL and interceptors
    - Implement request interceptor to inject JWT token
    - Implement response interceptor for automatic token refresh on 401
    - Add error handling and response transformation
    - _Requirements: 2.1, 3.1, 3.2_

  - [x] 2.3 Implement authentication API functions
    - Create register(email, username, password) function
    - Create login(email, password) function
    - Create logout() function
    - Create refreshToken(refreshToken) function
    - Create getCurrentUser() function
    - _Requirements: 1.1, 1.5, 2.1, 2.5, 3.3_

  - [x] 2.4 Create AuthContext with React Context API
    - Implement AuthProvider component with user state management
    - Add login, logout, and register functions to context
    - Implement token storage in localStorage
    - Add automatic token refresh logic
    - Provide isAuthenticated and currentUser state
    - _Requirements: 2.1, 3.1, 3.3_

  - [x] 2.5 Create useAuth custom hook
    - Export hook to access AuthContext
    - Provide convenient access to auth state and functions
    - _Requirements: 2.1, 3.1_

- [x] 3. Build authentication pages and components
  - [x] 3.1 Create Login page component
    - Build form with email and password inputs
    - Add form validation (required fields, email format)
    - Implement login submission with error handling
    - Add "Forgot Password" link
    - Add "Register" link for new users
    - Redirect to chat list on successful login
    - _Requirements: 2.1, 2.2, 11.1_

  - [x] 3.2 Create Register page component
    - Build form with email, username, and password inputs
    - Add password confirmation field
    - Implement form validation (matching passwords, email format, username length)
    - Implement registration submission with error handling
    - Add "Login" link for existing users
    - Redirect to login page on successful registration
    - _Requirements: 1.1, 1.2, 1.3, 1.5, 11.1_

  - [x] 3.3 Create PasswordReset page component
    - Build form for requesting password reset with email input
    - Build form for confirming reset with token and new password
    - Implement submission with error handling
    - Add success messages and redirect to login
    - _Requirements: 4.1, 4.3, 4.4_

  - [x] 3.4 Create ProtectedRoute component
    - Implement route wrapper that checks authentication
    - Redirect to login if not authenticated
    - Allow access if authenticated
    - _Requirements: 3.1, 9.2_

- [x] 4. Implement chat room list functionality
  - [x] 4.1 Create TypeScript type definitions for chat-related types
    - Define ChatRoom interface with id, name, room_type, created_by, created_at, members, last_message
    - Define Message interface with id, room_id, sender_id, content, timestamp, message_type, is_edited, sender_username
    - Define CreateRoomData interface
    - _Requirements: 5.4, 6.4, 8.5_

  - [x] 4.2 Implement chat API functions
    - Create getChatRooms() function to fetch user's rooms
    - Create createChatRoom(roomData) function
    - Create getRoomDetails(roomId) function
    - Create getMessages(roomId, page, pageSize) function
    - Create sendMessage(roomId, content) function
    - _Requirements: 5.4, 6.4, 8.3, 9.1_

  - [x] 4.3 Create ChatContext for chat state management
    - Implement ChatProvider with rooms and current room state
    - Add functions to load rooms, select room, create room
    - Manage messages state for current room
    - Provide loading and error states
    - _Requirements: 9.1, 11.2_

  - [x] 4.4 Create ChatRoomList page component
    - Display list of user's chat rooms
    - Show room name (or member names for one-to-one)
    - Display last message preview and timestamp
    - Show online status indicators for members
    - Add "Create Chat" button
    - Implement room selection to navigate to chat view
    - Add loading and empty states
    - _Requirements: 9.1, 9.5, 10.4, 11.2_

  - [x] 4.5 Create CreateChatModal component
    - Build modal with room type selection (one-to-one or group)
    - Add user search/selection interface
    - Add room name input for group chats
    - Implement member selection with checkboxes
    - Add create button with validation
    - Handle creation success and error states
    - Close modal and navigate to new room on success
    - _Requirements: 5.1, 5.4, 6.1, 6.4, 11.3_

- [x] 5. Build chat room view with message display
  - [x] 5.1 Create ChatRoomView page component
    - Display chat room header with name and members
    - Show message history in scrollable container
    - Add message composition input at bottom
    - Implement auto-scroll to latest message
    - Add loading state while fetching messages
    - Handle empty room state
    - _Requirements: 8.3, 11.4, 12.2_

  - [x] 5.2 Create MessageBubble component
    - Display message content, sender username, and timestamp
    - Apply different styling for own messages vs. others
    - Position own messages on right, others on left
    - Add message metadata (time, edited indicator)
    - _Requirements: 8.5, 12.3, 12.4_

  - [x] 5.3 Create MessageInput component
    - Build text input field for composing messages
    - Add send button
    - Implement Enter key to send (Shift+Enter for new line)
    - Prevent sending empty messages
    - Clear input after sending
    - Add character limit indicator
    - _Requirements: 13.1, 13.2, 13.3, 13.4_

  - [x] 5.4 Implement message pagination
    - Add "Load More" button at top of message list
    - Fetch older messages when clicked
    - Maintain scroll position when loading more
    - Disable button when no more messages
    - _Requirements: 8.3, 8.4_

- [x] 6. Implement WebSocket real-time messaging
  - [x] 6.1 Create WebSocket service class
    - Implement connect(roomId, token) method
    - Implement disconnect() method
    - Implement sendMessage(content) method
    - Add event listeners: onMessage, onConnect, onDisconnect, onError
    - Implement automatic reconnection logic
    - Add message queuing during reconnection
    - _Requirements: 7.1, 7.2, 7.4, 12.5_

  - [x] 6.2 Create useWebSocket custom hook
    - Accept roomId and token as parameters
    - Manage WebSocket connection lifecycle
    - Provide sendMessage function
    - Provide connection status state
    - Handle incoming messages and update state
    - Clean up connection on unmount
    - _Requirements: 7.1, 7.5, 12.1_

  - [x] 6.3 Integrate WebSocket into ChatRoomView
    - Initialize WebSocket connection when room is selected
    - Send messages through WebSocket instead of REST API
    - Listen for incoming messages and update UI immediately
    - Display connection status indicator
    - Handle connection errors gracefully
    - Fall back to REST API if WebSocket unavailable
    - _Requirements: 7.2, 7.3, 12.1, 12.2, 12.5, 13.2_

  - [x] 6.4 Add real-time message updates to ChatRoomList
    - Update last message preview when new message arrives
    - Update room order based on latest activity
    - Show unread message indicators
    - _Requirements: 12.1_

- [x] 7. Add user presence and status features
  - [x] 7.1 Display online status indicators
    - Show green dot for online users in room member list
    - Show gray dot for offline users
    - Display last seen time for offline users
    - _Requirements: 10.1, 10.2, 10.4_

  - [x] 7.2 Create Navbar component
    - Display current user's username
    - Show user's online status
    - Add logout button
    - Include navigation to chat list
    - _Requirements: 10.5_

  - [x] 7.3 Create Sidebar component
    - Display chat room list
    - Add search/filter functionality
    - Include "Create Chat" button
    - Show online member count for each room
    - _Requirements: 11.2_

- [x] 8. Implement routing and navigation
  - [x] 8.1 Set up React Router
    - Install react-router-dom
    - Configure routes for login, register, password reset, chat list, and chat room
    - Implement protected routes for authenticated pages
    - Add 404 page for invalid routes
    - _Requirements: 11.1_

  - [x] 8.2 Create App component with routing
    - Wrap app with AuthProvider and ChatProvider
    - Define route structure
    - Add navigation between pages
    - Implement route guards for authentication
    - _Requirements: 11.1_

- [x] 9. Add styling and responsive design
  - [x] 9.1 Style authentication pages
    - Create centered card layout for forms
    - Add consistent button and input styling
    - Implement error message styling
    - Make forms responsive for mobile
    - _Requirements: 11.1_

  - [x] 9.2 Style chat interface
    - Create two-column layout (sidebar + chat view)
    - Style message bubbles with colors and spacing
    - Add hover effects and transitions
    - Implement responsive design for mobile (collapsible sidebar)
    - Style scrollbars and loading indicators
    - _Requirements: 11.2, 11.4, 12.3, 12.4_

  - [x] 9.3 Add loading and error states
    - Create loading spinner component
    - Create error message component
    - Add skeleton loaders for chat rooms and messages
    - Implement toast notifications for errors
    - _Requirements: 13.5_

- [ ] 10. Optimize performance and user experience
  - [ ] 10.1 Implement message virtualization
    - Use react-window or react-virtual for long message lists
    - Improve scrolling performance
    - Reduce memory usage for large chat histories
    - _Requirements: 12.2_

  - [ ] 10.2 Add optimistic UI updates
    - Show sent messages immediately before server confirmation
    - Add sending indicator
    - Handle send failures gracefully
    - _Requirements: 13.2, 13.5_

  - [ ] 10.3 Implement debouncing and throttling
    - Debounce search input in user selection
    - Throttle scroll events for pagination
    - Optimize re-renders with React.memo
    - _Requirements: 11.2_

  - [ ] 10.4 Add error boundaries
    - Create error boundary component
    - Wrap main sections with error boundaries
    - Display user-friendly error messages
    - Add error reporting
    - _Requirements: 11.1_

- [ ] 11. Testing and quality assurance
  - [ ] 11.1 Write unit tests for components
    - Test authentication forms
    - Test message components
    - Test custom hooks
    - Test utility functions
    - _Requirements: All_

  - [ ] 11.2 Write integration tests
    - Test authentication flow
    - Test chat room creation
    - Test message sending
    - Test WebSocket connection
    - _Requirements: All_

  - [ ] 11.3 Perform manual testing
    - Test all user flows in different browsers
    - Test responsive design on mobile devices
    - Test WebSocket reconnection scenarios
    - Test error handling
    - _Requirements: All_

- [ ] 12. Documentation and deployment preparation
  - [ ] 12.1 Create frontend README
    - Document setup instructions
    - List available scripts
    - Explain environment variables
    - Add development guidelines
    - _Requirements: 15.1_

  - [ ] 12.2 Build production bundle
    - Configure Vite for production build
    - Optimize bundle size
    - Test production build locally
    - _Requirements: 11.1_

  - [ ] 12.3 Set up deployment configuration
    - Create Dockerfile for frontend
    - Configure nginx for serving React app
    - Set up environment-specific configs
    - Document deployment process
    - _Requirements: 11.1_
