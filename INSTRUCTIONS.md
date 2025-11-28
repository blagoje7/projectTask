# Development Testing Instructions

This guide walks you through setting up and running the Project Tracker application for development and testing.

## Prerequisites Check

Before starting, ensure you have:
- **Python 3.x** installed (`python --version`)
- **Node.js 16+** installed (`node --version`)
- **MySQL Server 8.0+** running
- **Git** (optional, for version control)

## Initial Setup (First Time Only)

### 1. Database Setup

Open MySQL command line or MySQL Workbench and create the database:

```sql
CREATE DATABASE project_tracker;
```

Verify the database was created:
```sql
SHOW DATABASES;
```

### 2. Configure Database Connection

Edit `backend/config.py` with your MySQL credentials:

```python
MYSQL_HOST = 'localhost'
MYSQL_USER = 'your_mysql_username'  # Usually 'root'
MYSQL_PASSWORD = 'your_mysql_password'
MYSQL_DB = 'project_tracker'
```

### 3. Backend Setup

#### Create Virtual Environment

Navigate to the backend directory:
```bash
cd backend
```

Create a virtual environment (recommended):
```bash
python -m venv venv
```

#### Activate Virtual Environment

**On Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
.\venv\Scripts\activate.bat
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

#### Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Flask (web framework)
- SQLAlchemy (database ORM)
- Flask-JWT-Extended (authentication)
- Flask-CORS (cross-origin support)
- MySQL Connector (database driver)
- **Flask-SocketIO** (WebSocket support for real-time collaboration)
- **Python-SocketIO** (WebSocket engine)

#### Initialize Database Tables

Run the main application to create tables:
```bash
python run.py
```

The first run will:
- Create all necessary database tables
- Create default admin user (username: `admin`, password: `admin`)

Stop the server (Ctrl+C) after you see the tables created.

#### Add Whiteboard Table (if needed)

If the whiteboard table doesn't exist:
```bash
python add_whiteboard_table.py
```

You can verify tables in MySQL:
```sql
USE project_tracker;
SHOW TABLES;
```

### 4. Frontend Setup

Open a **new terminal window** (keep backend terminal open).

Navigate to the frontend directory:
```bash
cd frontend
```

Install Node.js dependencies:
```bash
npm install
```

This installs:
- Vue.js 3 (UI framework)
- Vue Router (routing)
- Axios (HTTP client)
- Vite (build tool)
- **Socket.IO Client** (WebSocket client for real-time collaboration)

## Running the Application for Development

You need **two terminal windows** running simultaneously.

### Terminal 1: Backend Server

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Activate virtual environment:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

3. Start Flask server:
   ```bash
   python run.py
   ```

You should see:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

**Keep this terminal running!** The backend server must stay active.

### Terminal 2: Frontend Dev Server

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Start Vite dev server:
   ```bash
   npm run dev
   ```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

**Keep this terminal running!** The frontend server must stay active.

### Access the Application

Open your browser and go to:
```
http://localhost:5173
```

## Testing the Application

### 1. Login as Admin

Use default credentials:
- **Username**: `admin`
- **Password**: `admin`

### 2. Create Test Users

As admin, create test users with different roles:

1. Go to **Users** (sidebar)
2. Click **+ New User**
3. Create users:
   - **Manager**: username `manager1`, role: Manager
   - **User**: username `user1`, role: User

### 3. Create Teams

1. Go to **Teams**
2. Click **+ New Team**
3. Create a test team (e.g., "Development Team")
4. Add members to the team

### 4. Create Projects

1. Go to **Projects**
2. Click **+ New Project**
3. Create a test project
4. Assign teams to the project

### 5. Create Epics and Tasks

1. Open the project
2. Click **Epics** tab
3. Create an epic
4. Click **Tasks** tab
5. Create tasks with different priorities and deadlines

### 6. Test Whiteboard

1. **As Manager**: 
   - Go to Manager Dashboard
   - Select a project from left sidebar
   - Click **"🎨 Open Whiteboard"** button (below progress bar)
   - Draw on the whiteboard
   - **Open another browser window** and login as a different user
   - Both users should see drawings in real-time
   - Save manually or it auto-saves after each stroke
   - Click **History** to view changes and restore previous versions

2. **Real-time Features**:
   - Open whiteboard in multiple browser tabs
   - Draw in one tab - see it instantly in others
   - Cursor positions are shared (you can see where others are drawing)
   - Auto-saves to MySQL after each stroke
   - All team members can collaborate simultaneously

### 7. Test Manager Dashboard

1. Login as `manager1`
2. You'll be automatically redirected to Manager Dashboard
3. Test:
   - Project selection from left sidebar
   - Team selection
   - Task views (List, Grid, Calendar)
   - Task actions (view, edit, delete)
   - Right sidebar progress indicator

## Common Testing Scenarios

### Test User Roles

| Feature | Admin | Manager | User |
|---------|-------|---------|------|
| Create Users | ✅ | ❌ | ❌ |
| Create Teams | ✅ | ✅ | ❌ |
| Create Projects | ✅ | ✅ | ❌ |
| Create Tasks | ✅ | ✅ | ❌ |
| View Tasks | ✅ | ✅ | ✅ |
| Update Task Status | ✅ | ✅ | ✅ |
| Use Whiteboard | ✅ | ✅ | ✅ |
| View History | ✅ | ✅ | ❌ |
| Revert Whiteboard | ✅ | ✅ | ❌ |

### Test Whiteboard Persistence

1. Draw something on the whiteboard
2. Navigate to another page
3. Come back to Home tab
4. Select the same project
5. Verify drawing is still there

### Test Task Calendar View

1. Create tasks with different deadlines
2. Go to Manager Dashboard
3. Switch to Calendar view
4. Verify tasks appear on correct dates

## Stopping the Application

### Stop Frontend Server
In the frontend terminal:
- Press `Ctrl + C`

### Stop Backend Server
In the backend terminal:
- Press `Ctrl + C`

### Deactivate Virtual Environment
In the backend terminal:
```bash
deactivate
```

## Troubleshooting

### Backend Won't Start

**Error: "Module not found"**
```bash
# Activate venv and reinstall dependencies
pip install -r requirements.txt
```

**Error: "Access denied for user"**
- Check MySQL credentials in `config.py`
- Verify MySQL server is running

**Error: "Database doesn't exist"**
```sql
CREATE DATABASE project_tracker;
```

### Frontend Won't Start

**Error: "Cannot find module"**
```bash
# Delete node_modules and reinstall
rm -rf node_modules
npm install
```

**Error: "Port 5173 already in use"**
```bash
# Kill process on port 5173 (Windows)
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

### Database Connection Issues

**Check MySQL is running:**
```bash
# Windows (PowerShell)
Get-Service MySQL*

# Start MySQL if stopped
Start-Service MySQL80
```

**Test connection:**
```bash
mysql -u root -p
```

### CORS Errors in Browser

- Verify backend is running on `http://localhost:5000`
- Verify frontend is running on `http://localhost:5173`
- Check Flask-CORS is installed: `pip list | grep -i cors`

### Whiteboard Not Saving

**Check whiteboard table exists:**
```sql
USE project_tracker;
DESCRIBE whiteboards;
```

**If table doesn't exist:**
```bash
python add_whiteboard_table.py
```

## Database Reset (For Testing)

If you need to start fresh:

```sql
-- Drop all tables
DROP DATABASE project_tracker;
CREATE DATABASE project_tracker;
```

Then restart the backend server to recreate tables:
```bash
python run.py
```

## Quick Start Commands

Copy-paste these commands for quick setup:

### Backend
```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python add_whiteboard_table.py
python run.py
```

### Frontend (New Terminal)
```bash
cd frontend
npm install
npm run dev
```

### Access
Open browser: `http://localhost:5173`
Login: `admin` / `admin`

## Development Workflow

1. **Start servers** (backend + frontend)
2. **Make code changes**
3. **Test changes** in browser (auto-reloads)
4. **Check terminal** for errors
5. **Verify database** if needed
6. **Stop servers** when done

## API Testing (Optional)

Test API endpoints directly using tools like:
- **Postman**
- **cURL**
- **Thunder Client** (VS Code extension)

Example cURL command:
```bash
# Login
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# Get projects (use token from login)
curl -X GET http://localhost:5000/projects \
  -H "Authorization: Bearer <your_token>"
```

## Next Steps

- Change default admin password
- Create realistic test data
- Test all user roles
- Verify whiteboard functionality
- Test task assignment and tracking
- Explore manager dashboard features

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review `README.md` for feature documentation
3. Check terminal output for error messages
4. Verify database connection and tables
