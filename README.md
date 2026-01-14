# Project Tracker

Project management application with role-based access control and team collaboration.

### Database

1. **MySQL**: Create a database named `project_tracker`. Update `backend/config.py` with your credentials.

2. **ArangoDB**:
   - Download and install ArangoDB Community Edition from [arangodb.com](https://www.arangodb.com/download/).
   - version 3.11.8
   - Start the ArangoDB server (default port `8529`).
   - Default user `root` with no password (or update `backend/config.py`).
   - The application will automatically create the `project_tracker_whiteboard` database and collections.

### Backend

1. Navigate to `backend` directory.

2. Create and activate a virtual environment.

3. Install dependencies:
   pip install -r requirements.txt

4. Run the server:
   python run.py

Server running at http://localhost:5001.
Default admin credentials: `admin@example.com` / `admin`.

### Frontend

1. Navigate to `frontend` directory.

2. Install dependencies:
   npm install

3. Run the development server:
   npm run dev

App running at http://localhost:5173.
