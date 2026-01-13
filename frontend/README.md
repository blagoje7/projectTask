# Project Tracker

Project management application with role-based access control and team collaboration.

## Setup

### Database

Create a MySQL database named `project_tracker`. Update `backend/config.py` with your credentials.

### Backend

1. Navigate to `backend` directory.
2. Create and activate a virtual environment.
3. Install dependencies:
   `ash
   pip install -r requirements.txt
   ` 
4. Run the server:
   `ash
   python run.py
   ` 

Server running at http://localhost:5001.
Default admin credentials: `admin@example.com` / `admin`.

### Frontend

1. Navigate to `frontend` directory.
2. Install dependencies:
   `ash
   npm install
   ` 
3. Run the development server:
   `ash
   npm run dev
   ` 

App running at http://localhost:5173.

## Features

- Role-based Access Control (Admin, Manager, User).
- Project, Epic, and Task management.
- Real-time collaborative Whiteboard with sticky notes and history.
- Team and user management.
- Task views: List, Grid, Calendar.
- JIRA integration.
- Time tracking and activity logging.
