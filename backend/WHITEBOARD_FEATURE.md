# Whiteboard Feature Implementation

## What's New
- **Collaborative whiteboard shared by all team members** on a project
- Persistent whiteboard storage in MySQL database
- Auto-save on every drawing action
- Manual save button for explicit saves
- Whiteboard history with user attribution
- Automatic loading when project is selected
- Accessible from both Manager Dashboard and Project Details page

## Access Control
- **All users** in teams assigned to a project can view and edit the whiteboard
- Not limited to managers - promotes team collaboration
- Each project has its own whiteboard shared among all team members
- Admins have access to all whiteboards

## Database Changes

### New Table: `whiteboard`
```sql
CREATE TABLE whiteboard (
    whiteboard_id VARCHAR(36) PRIMARY KEY,
    project_id VARCHAR(36) NOT NULL,
    image_data TEXT NOT NULL,
    created_by VARCHAR(36) NOT NULL,
    created_at INTEGER NOT NULL,
    FOREIGN KEY (project_id) REFERENCES project(project_id),
    FOREIGN KEY (created_by) REFERENCES user(user_id)
);
```

## Setup Instructions

### 1. Run Migration
From the `backend` directory:
```bash
python add_whiteboard_table.py
```

### 2. Restart Backend
```bash
python run.py
```

### 3. Test the Feature

**As a Manager:**
1. Login as a manager
2. Go to Manager Dashboard
3. Select a project
4. Click "Whiteboard" tab
5. Draw something and it auto-saves

**As a Regular User:**
1. Login as a user assigned to a team
2. Go to Projects → Select a project
3. Click "Whiteboard" tab
4. See and contribute to the same whiteboard as managers
5. Draw, save, view history

### 4. Verify Collaboration
1. Open two browser windows
2. Login as different users in the same project teams
3. Both can draw on the same whiteboard
4. Refresh to see each other's changes

## API Endpoints

### GET /projects/<project_id>/whiteboard
- Returns current whiteboard state and history
- Response: `{ imageData: string, history: array }`

### POST /projects/<project_id>/whiteboard
- Saves whiteboard state
- Body: `{ imageData: string }` (base64 encoded canvas)
- Response: `{ message: string, whiteboard: object }`

### GET /projects/<project_id>/whiteboard/history
- Returns whiteboard history (last 20 entries)
- Response: `[{ whiteboardId, imageData, userName, createdAt }]`

### DELETE /whiteboards/<whiteboard_id>
- Deletes a specific whiteboard entry (manager/admin only)

## How It Works

1. **Auto-Load**: When you select a project and switch to whiteboard tab, it automatically loads the most recent whiteboard from the database

2. **Auto-Save**: Every time you finish a drawing stroke (mouseup), it automatically saves to the database

3. **Manual Save**: Click the "💾 Save" button to explicitly save the current state

4. **History**: Click "History" to see all previous versions with timestamps and user names. Click "Restore" to load any previous version

5. **Persistence**: All drawings are stored in MySQL as base64-encoded PNG images, so they persist across:
   - Page refreshes
   - Browser sessions
   - Different devices (shared with all team members)

6. **Collaboration**: All users in teams assigned to a project can view and edit the same whiteboard
   - Regular users access via: Projects → Project Details → Whiteboard tab
   - Managers access via: Manager Dashboard → Select Project → Whiteboard tab
   - Changes are visible after refresh (not real-time, but persistent)

## Technical Details

- **Storage**: Base64-encoded PNG in MySQL TEXT column
- **Max Size**: ~16MB per whiteboard (MySQL TEXT limit)
- **History Limit**: Last 20 versions kept in memory, all versions in database
- **Compression**: Canvas toDataURL() provides automatic PNG compression

## Notes

- Whiteboards are **project-specific** (each project has its own whiteboard)
- **All team members** assigned to a project can see and edit the whiteboard
- Drawing history shows who created each version
- The whiteboard canvas is cleared when you clear it, and the cleared state is saved
- Access control verifies user is in at least one team assigned to the project
- Perfect for brainstorming, sketching ideas, and visual collaboration
