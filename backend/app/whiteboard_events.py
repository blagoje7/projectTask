from flask_socketio import emit, join_room, leave_room
from flask import request

# Store active whiteboard sessions in memory
# Format: {project_id: {user_id: {username, cursor_pos}}}
active_sessions = {}

# Store whiteboard state in memory (temporary until saved to DB)
# Format: {project_id: canvas_data}
whiteboard_state = {}

def register_whiteboard_events(socketio):
    @socketio.on('join_whiteboard')
    def handle_join(data):
        """User joins a whiteboard room"""
        from .models import Whiteboard
        
        project_id = data.get('projectId')
        user_id = data.get('userId')
        username = data.get('username')
        
        if not project_id:
            return
        
        # Join the room for this project
        join_room(project_id)
        
        # Track user in active session
        if project_id not in active_sessions:
            active_sessions[project_id] = {}
        
        active_sessions[project_id][user_id] = {
            'username': username,
            'cursor': None,
            'sid': request.sid
        }
        
        # Send current whiteboard state from database OR in-memory
        canvas_data = None
        
        # Always check database first for most recent state
        from .models import Whiteboard
        latest_whiteboard = Whiteboard.query.filter_by(project_id=project_id)\
            .order_by(Whiteboard.created_at.desc())\
            .first()
        
        if latest_whiteboard:
            canvas_data = latest_whiteboard.image_data
            # Update in-memory state with database version
            whiteboard_state[project_id] = canvas_data
        elif project_id in whiteboard_state:
            # Fallback to in-memory if no database entry
            canvas_data = whiteboard_state[project_id]
        
        if canvas_data:
            emit('whiteboard_state', {
                'canvasData': canvas_data
            }, room=request.sid)
        
        # Notify others that a user joined
        emit('user_joined', {
            'userId': user_id,
            'username': username,
            'activeUsers': list(active_sessions[project_id].keys())
        }, room=project_id, skip_sid=request.sid)
        
        # Send list of active users to the new user
        emit('active_users', {
            'users': [
                {'userId': uid, 'username': udata['username']}
                for uid, udata in active_sessions[project_id].items()
            ]
        }, room=request.sid)
    
    @socketio.on('leave_whiteboard')
    def handle_leave(data):
        """User leaves a whiteboard room"""
        project_id = data.get('projectId')
        user_id = data.get('userId')
        
        if not project_id:
            return
        
        leave_room(project_id)
        
        # Remove user from active session
        if project_id in active_sessions and user_id in active_sessions[project_id]:
            del active_sessions[project_id][user_id]
            
            # Clean up empty sessions
            if not active_sessions[project_id]:
                del active_sessions[project_id]
        
        # Notify others that user left
        emit('user_left', {
            'userId': user_id
        }, room=project_id)
    
    @socketio.on('draw')
    def handle_draw(data):
        """Broadcast drawing strokes to other users in real-time"""
        project_id = data.get('projectId')
        
        if not project_id:
            return
        
        # Broadcast to all users in the room except sender
        emit('draw', {
            'userId': data.get('userId'),
            'tool': data.get('tool'),
            'color': data.get('color'),
            'points': data.get('points'),
            'username': data.get('username')
        }, room=project_id, skip_sid=request.sid)
    
    @socketio.on('cursor_move')
    def handle_cursor_move(data):
        """Broadcast cursor position to other users"""
        project_id = data.get('projectId')
        user_id = data.get('userId')
        cursor_pos = data.get('position')
        
        if not project_id or not user_id:
            return
        
        # Update cursor position in active session
        if project_id in active_sessions and user_id in active_sessions[project_id]:
            active_sessions[project_id][user_id]['cursor'] = cursor_pos
        
        # Broadcast cursor position to others
        emit('cursor_update', {
            'userId': user_id,
            'username': data.get('username'),
            'position': cursor_pos
        }, room=project_id, skip_sid=request.sid)
    
    @socketio.on('save_canvas')
    def handle_save_canvas(data):
        """Save canvas state to database and memory"""
        from .models import Whiteboard, db
        from datetime import datetime
        
        project_id = data.get('projectId')
        canvas_data = data.get('canvasData')
        user_id = data.get('userId')  # This comes from frontend
        
        if not project_id or not canvas_data or not user_id:
            return
        
        # Store in memory
        whiteboard_state[project_id] = canvas_data
        
        # Persist to database
        try:
            current_timestamp = int(datetime.utcnow().timestamp())
            
            new_whiteboard = Whiteboard(
                project_id=project_id,
                image_data=canvas_data,
                created_by=user_id,
                created_at=current_timestamp
            )
            db.session.add(new_whiteboard)
            db.session.commit()
            
            # Broadcast to all users that canvas was saved
            emit('canvas_saved', {
                'userId': user_id,
                'username': data.get('username'),
                'timestamp': datetime.utcnow().isoformat()
            }, room=project_id, include_self=True)
        except Exception as e:
            print(f"Error saving canvas to database: {str(e)}")
            db.session.rollback()
    
    @socketio.on('clear_canvas')
    def handle_clear_canvas(data):
        """Clear canvas for all users"""
        project_id = data.get('projectId')
        
        if not project_id:
            return
        
        # Clear in-memory state
        if project_id in whiteboard_state:
            del whiteboard_state[project_id]
        
        # Broadcast clear to all users
        emit('canvas_cleared', {
            'userId': data.get('userId'),
            'username': data.get('username')
        }, room=project_id)
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle user disconnect"""
        # Find and remove user from all active sessions
        for project_id, users in list(active_sessions.items()):
            for user_id, user_data in list(users.items()):
                if user_data.get('sid') == request.sid:
                    del active_sessions[project_id][user_id]
                    
                    # Clean up empty sessions
                    if not active_sessions[project_id]:
                        del active_sessions[project_id]
                    else:
                        # Notify others
                        emit('user_left', {
                            'userId': user_id
                        }, room=project_id)
                    break
