# Project Tracker

Project management application with role-based access control and team collaboration.

## Setup

### Database

Create a MySQL database named `project_tracker`. Update `backend/config.py` with your credentials.

### Backend

1. Navigate to `backend` directory.
2. Create and activate a virtual environment.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the server:
   ```bash
   python run.py
   ```

Server running at http://localhost:5001.
Default admin credentials: `admin@example.com` / `admin`.

### Frontend

1. Navigate to `frontend` directory.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

App running at http://localhost:5173.
