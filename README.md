# Project Tracker App

A comprehensive project management application with role-based access control, team collaboration, and integrated whiteboard functionality.

## Prerequisites
- Python 3.x
- Node.js 16+
- MySQL Server 8.0+

## Setup

### Database
1. Create a MySQL database named `project_tracker`:
   ```sql
   CREATE DATABASE project_tracker;
   ```
2. Update `backend/config.py` with your MySQL credentials.

### Backend (Flask)
1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the whiteboard table migration (if not already created):
   ```bash
   python add_whiteboard_table.py
   ```
5. Run the application:
   ```bash
   python run.py
   ```
   The server will start on `http://localhost:5001`. (fixing macOS problems, already using 5000 port)
   The database tables will be created automatically, and a super admin user (`admin`/`admin`) will be created.

### Frontend (Vue.js)
1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   The application will be available at `http://localhost:5173`.

## Features

### User Management
- **Role-based Access Control**: Admin, Manager, and User roles
- **User Creation**: Admin can create new users with assigned roles
- **Team Management**: Create and manage teams with multiple members
- **Password Reset**: Users can reset their passwords

### Project Management
- **Projects**: Create and manage projects with descriptions
- **Epics**: Organize work into epics within projects
- **Tasks**: Create detailed tasks with priorities, deadlines, and assignees
- **Team Assignment**: Assign teams to projects for collaboration

### Task Features
- **Priority Levels**: Low, Medium, High
- **Status Tracking**: To Do, In Progress, For Review, Done
- **Multiple Views**: List, Grid, and Calendar views for tasks
- **Assignee Management**: Assign multiple users to tasks
- **Deadline Tracking**: Set and monitor task deadlines

### Manager Dashboard
- **Three-Panel Layout**:
  - Left: Projects, Teams, and Team Members navigation
  - Center: Task management with list/grid/calendar views
  - Right: Project progress visualization
- **Task Actions**: View, edit, change priority/status, delete
- **Search & Filter**: Find tasks quickly

### Collaborative Whiteboard
- **Project-Based**: One whiteboard per project
- **Persistent Storage**: Whiteboards saved to MySQL database
- **Drawing Tools**: Pen and eraser with color selection
- **Auto-Save**: Automatically saves after each stroke
- **Manual Save**: Option to save manually
- **Version History** (Manager/Admin only):
  - View last 20 changes with timestamps and user attribution
  - Revert to previous versions
  - Full audit trail of changes
- **Access Control**: All team members can draw, only managers can view/revert history
- **Home Tab Integration**: Accessible from Home tab, switches when project changes

### Jira Integration (Optional)
- Connect projects to Jira for external tracking
- Sync tasks with Jira issues

## Application Routes

### Public Routes
- `/login` - User login page
- `/reset-password` - Password reset

### User Routes
- `/` - Home page (redirects managers to dashboard, shows whiteboard for users)
- `/my-tasks` - View assigned tasks

### Manager/Admin Routes
- `/manager-dashboard` - Comprehensive manager dashboard
- `/users` - User list and management
- `/users/new` - Create new user
- `/teams` - Team list
- `/teams/:id` - Team details
- `/projects` - Project list
- `/projects/new` - Create new project
- `/projects/:id` - Project details with epics and tasks
- `/projects/:id/tasks/new` - Create new task

## User Roles

### Admin
- Full system access
- Create and manage users
- Access all projects and teams
- View all whiteboards and history

### Manager
- Access assigned projects and teams
- Create and manage tasks
- View manager dashboard with analytics
- Access whiteboard history and version control
- Assign teams to projects

### User
- View assigned tasks
- Update task status
- Collaborate on project whiteboards
- Access projects through team membership

## API Endpoints

### Authentication
- `POST /login` - User authentication
- `POST /reset-password` - Password reset

### Users
- `GET /users` - List all users
- `GET /users/:id` - Get user details
- `POST /users` - Create new user
- `PUT /users/:id` - Update user
- `DELETE /users/:id` - Delete user

### Teams
- `GET /teams` - List all teams
- `GET /teams/:id` - Get team details
- `POST /teams` - Create new team
- `PUT /teams/:id` - Update team
- `DELETE /teams/:id` - Delete team

### Projects
- `GET /projects` - List user's projects
- `GET /projects/:id` - Get project details with tasks and epics
- `POST /projects` - Create new project
- `PUT /projects/:id` - Update project
- `DELETE /projects/:id` - Delete project
- `POST /projects/:id/teams` - Assign teams to project

### Epics
- `POST /projects/:id/epics` - Create epic
- `DELETE /epics/:id` - Delete epic

### Tasks
- `GET /tasks/my` - Get current user's tasks
- `GET /tasks/:id` - Get task details
- `POST /tasks` - Create new task
- `PUT /tasks/:id` - Update task
- `PUT /tasks/:id/status` - Update task status
- `DELETE /tasks/:id` - Delete task

### Whiteboards
- `GET /projects/:id/whiteboard` - Get current whiteboard and history
- `POST /projects/:id/whiteboard` - Save whiteboard state
- `GET /projects/:id/whiteboard/history` - Get whiteboard history
- `DELETE /whiteboards/:id` - Delete whiteboard entry (Manager/Admin only)

## Database Schema

### Core Tables
- `users` - User accounts and credentials
- `roles` - User roles (admin, manager, user)
- `teams` - Team definitions
- `user_teams` - Many-to-many relationship between users and teams
- `projects` - Project information
- `project_teams` - Many-to-many relationship between projects and teams
- `epics` - Epic definitions within projects
- `tasks` - Task details with assignments and tracking
- `task_assignees` - Many-to-many relationship between tasks and users
- `whiteboards` - Whiteboard canvas states with version history

## Technology Stack

### Backend
- **Flask** 3.1.2 - Web framework
- **SQLAlchemy** 2.0.44 - ORM
- **Flask-JWT-Extended** 4.7.1 - Authentication
- **Flask-CORS** 6.0.1 - Cross-origin support
- **MySQL Connector** 9.5.0 - Database driver

### Frontend
- **Vue.js** 3.5.24 - UI framework
- **Vue Router** 4.6.3 - Routing
- **Axios** 1.13.2 - HTTP client
- **Vite** - Build tool

## Default Credentials
-**Email**:`admin@example.com`
- **Username**: `admin`
- **Password**: `admin`

⚠️ **Important**: Change the default admin password after first login in a production environment.
