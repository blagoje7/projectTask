# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

A Flask + Vue.js project management application with role-based access control (Admin/Manager/User), team collaboration, and real-time collaborative whiteboard functionality. The application uses MySQL for persistence and WebSockets (Socket.IO) for real-time features.

## Development Commands

### Database Setup (First Time Only)
```bash
# In MySQL CLI
CREATE DATABASE project_tracker;
```

Update `backend/config.py` with your MySQL credentials before running.

### Backend (Flask + SocketIO)

**Navigate to backend:**
```bash
cd backend
```

**Create and activate virtual environment (macOS/Linux):**
```bash
python -m venv venv
source venv/bin/activate
```

**Create and activate virtual environment (Windows PowerShell):**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Run migration for whiteboard table (if needed):**
```bash
python add_whiteboard_table.py
```

**Start backend server:**
```bash
python run.py
```
Backend runs on `http://localhost:5000` with SocketIO WebSocket support.

**Verify database tables:**
```bash
python check_db.py
```

### Frontend (Vue 3 + Vite)

**Navigate to frontend (in new terminal):**
```bash
cd frontend
```

**Install dependencies:**
```bash
npm install
```

**Start dev server:**
```bash
npm run dev
```
Frontend runs on `http://localhost:5173` with hot-reload.

**Build for production:**
```bash
npm run build
```

### Testing Credentials
- Username: `admin@example.com`
- Password: `admin`
- Role: Super Administrator

## Architecture Overview

### Backend Architecture

**Framework:** Flask 3.1.2 with Blueprint-based modular structure

**Core Components:**
- `app/__init__.py` - Application factory, initializes Flask, CORS, JWT, SQLAlchemy, SocketIO
- `app/models.py` - SQLAlchemy ORM models (User, Role, Team, Project, Epic, Task, Whiteboard)
- `app/routes/` - Blueprint modules for different resources (auth, users, teams, projects, epics, tasks, whiteboards)
- `app/whiteboard_events.py` - SocketIO event handlers for real-time whiteboard collaboration
- `config.py` - Configuration (database URI, JWT secret, optional Jira integration)

**Authentication:** JWT-based with Flask-JWT-Extended. Tokens include user ID, role, and email in claims.

**Database Models & Relationships:**
- Many-to-many: Users ↔ Teams, Projects ↔ Teams, Tasks ↔ Users (assignees)
- One-to-many: Projects → Epics → Tasks
- Whiteboards linked to Projects with version history
- All IDs are UUIDs (varchar 36)

**Real-Time Features:**
- SocketIO for whiteboard collaboration
- Events: `join_whiteboard`, `draw`, `cursor_move`, `save_canvas`, `clear_canvas`
- In-memory tracking of active sessions and cursor positions
- Auto-save on every stroke, manual save option

**Utilities:**
- `app/utils.py` - JWT helpers (`get_current_user_id`, `get_current_user_role`), response helpers
- `app/jira_integration.py` - Optional Jira Cloud API integration

### Frontend Architecture

**Framework:** Vue 3 (Composition API) with Vue Router

**Core Structure:**
- `src/main.js` - App entry point, Vue Router setup
- `src/router/index.js` - Route definitions with authentication guards (checks JWT + role)
- `src/utils/api.js` - Axios wrapper with auto-injected JWT headers
- `src/utils/auth.js` - Authentication helpers
- `src/utils/constants.js` - App-wide constants (status, priority values)
- `src/views/` - Route components (one per page)

**Key Views:**
- `Home.vue` - Redirects managers to dashboard, shows whiteboard for users
- `ManagerDashboard.vue` - Three-panel layout (projects/teams, task views, progress)
- `ProjectDetails.vue` - Tabbed interface (Overview, Epics, Tasks, Whiteboard)
- `MyTasks.vue` - User's assigned tasks
- `Login.vue`, `ResetPassword.vue` - Authentication

**Whiteboard Implementation:**
- HTML5 Canvas API for drawing
- Socket.IO client for real-time collaboration
- Base64 PNG encoding for persistence
- Stroke-by-stroke broadcasting to other users
- Cursor position sharing

**Authentication Flow:**
1. Login stores JWT token + role + userId in localStorage
2. `router/index.js` beforeEach guard checks token/role
3. `api.js` injects `Authorization: Bearer <token>` header
4. Backend validates JWT on protected routes

**State Management:** LocalStorage for authentication state, no Vuex/Pinia (uses props/events)

## Code Style & Patterns

### Backend Patterns

**Route Structure:**
- Each resource has its own Blueprint (users_bp, teams_bp, etc.)
- Routes decorated with `@jwt_required()` for protected endpoints
- Use `get_current_user_id()` from utils to extract user from JWT
- Standard response: `jsonify({...})` with HTTP status code

**Model Methods:**
- Every model has `to_dict()` method for JSON serialization
- Password hashing via `set_password()` and `check_password()` on User model
- Relationships use `backref` for bi-directional navigation

**Database Sessions:**
- Always `db.session.commit()` after modifications
- Use `db.session.rollback()` in exception handlers
- Cascade deletes configured on relationships

### Frontend Patterns

**API Calls:**
- Use helpers from `utils/api.js`: `apiGet()`, `apiPost()`, `apiPut()`, `apiDelete()`
- These automatically handle JWT headers and error responses
- Always destructure: `const { data, error } = await apiGet('/endpoint')`

**Routing Guards:**
- Use `meta: { requiresAuth: true, role: 'admin' }` on routes
- Admin can access all routes, managers can access manager routes, users see limited routes

**Component Communication:**
- Props down, events up
- No global state management (consider adding Vuex/Pinia if complexity grows)

## Important Implementation Details

### Role-Based Access Control
- **Admin:** Full system access, create users, view all projects/teams
- **Manager:** Create projects/teams/tasks, access manager dashboard, view whiteboard history
- **User:** View assigned tasks, update task status, collaborate on whiteboards

Roles are checked both frontend (route guards) and backend (JWT claims + endpoint validation).

### Whiteboard Collaboration
- One whiteboard per project, shared by all team members
- Real-time: Multiple users can draw simultaneously with visible cursors
- Persistence: Auto-saves to MySQL on every stroke as base64 PNG
- History: Last 20 versions stored, managers can view/restore previous versions
- Access: User must be in a team assigned to the project

**WebSocket Events:**
- `join_whiteboard` - User joins room, receives current state
- `draw` - Broadcasts stroke to all users in room
- `cursor_move` - Shares cursor position
- `save_canvas` - Persists to database, broadcasts save confirmation
- `clear_canvas` - Clears for all users

### Database Configuration
Update `backend/config.py` with your MySQL credentials:
```python
SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://USER:PASSWORD@localhost/project_tracker'
```

### Jira Integration (Optional)
Uncomment and configure in `config.py`:
```python
JIRA_SERVER = 'https://your-domain.atlassian.net'
JIRA_EMAIL = 'your-email@example.com'
JIRA_API_TOKEN = 'your-jira-api-token'
```

Projects, epics, and tasks have optional `jira_key` and `jira_url` fields for linking.

## Common Development Scenarios

### Adding a New Route

**Backend:**
1. Create route function in appropriate `app/routes/<resource>.py`
2. Add `@jwt_required()` decorator if protected
3. Extract user with `get_current_user_id()` from utils
4. Register Blueprint in `app/__init__.py` if new file

**Frontend:**
1. Add route to `src/router/index.js` with `meta: { requiresAuth: true }`
2. Create view component in `src/views/`
3. Use `apiGet/Post/Put/Delete` from `utils/api.js` for backend calls

### Adding a Database Model

1. Define model class in `app/models.py` (inherit from `db.Model`)
2. Add `to_dict()` method for JSON serialization
3. Define relationships using `db.relationship()` and association tables if many-to-many
4. Run `python run.py` to create table (or write migration script)

### Adding a WebSocket Event

1. Add event handler in `app/whiteboard_events.py` using `@socketio.on('event_name')`
2. Use `emit()` to send to clients, `join_room()`/`leave_room()` for room management
3. Add corresponding event listener in Vue component using `socket.on('event_name', callback)`

## Debugging & Troubleshooting

### Backend Issues
- Check MySQL is running: `mysql -u root -p`
- Verify tables exist: `python check_db.py` or SQL `SHOW TABLES;`
- Backend logs print to console, check for stack traces
- Test endpoints with curl or Postman (get token from `/login` first)

### Frontend Issues
- Check backend is running on `http://localhost:5000`
- Open browser DevTools → Network tab to see API calls
- Check Console for JavaScript errors
- Verify JWT token exists: `localStorage.getItem('token')`

### Database Reset (Development Only)
```sql
DROP DATABASE project_tracker;
CREATE DATABASE project_tracker;
```
Then restart backend with `python run.py` to recreate tables.

### CORS Errors
Ensure Flask-CORS is enabled in `app/__init__.py` (already configured with `CORS(app)`).

## Project Structure

```
projectTask/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # App factory, SocketIO init
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── utils.py             # JWT helpers
│   │   ├── whiteboard_events.py # SocketIO handlers
│   │   ├── jira_integration.py  # Jira API client
│   │   └── routes/              # Blueprint routes
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── teams.py
│   │       ├── projects.py
│   │       ├── epics.py
│   │       ├── tasks.py
│   │       └── whiteboards.py
│   ├── config.py                # Database & config
│   ├── run.py                   # Entry point
│   ├── requirements.txt
│   └── add_whiteboard_table.py  # Migration script
├── frontend/
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── router/
│   │   │   └── index.js         # Routes + guards
│   │   ├── views/               # Page components
│   │   └── utils/               # API helpers, constants
│   ├── package.json
│   └── vite.config.js
└── README.md
```
