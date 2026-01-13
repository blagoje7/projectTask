from flask_socketio import emit, join_room, leave_room
from .extensions import socketio, arango_db
from .models import User
import json
import uuid
import time

@socketio.on('join_project')
def on_join(data):
    project_id = data.get('projectId')
    print(f"User joining project room (ArangoDB): {project_id}")
    room = project_id
    join_room(room)
    
    # Get elements for this project from ArangoDB
    # AQL Query
    cursor = arango_db.aql.execute(
        'FOR doc IN whiteboard_elements FILTER doc.projectId == @pid RETURN doc',
        bind_vars={'pid': project_id}
    )
    
    elements = []
    
    for doc in cursor:
        elements.append({
            'elementId': doc['elementId'],
            'projectId': doc['projectId'],
            'type': doc['type'],
            'content': doc['content'], 
            'createdBy': doc['createdBy'],
            'createdByName': doc['createdByName'],
            'createdAt': doc['createdAt']
        })

    emit('init_whiteboard', elements)

@socketio.on('draw')
def on_draw(data):
    project_id = data.get('projectId')
    emit('drawing', data, room=project_id, include_self=False)

@socketio.on('save_element')
def on_save_element(data):
    project_id = data.get('projectId')
    user_id = data.get('userId')
    element_type = data.get('type') 
    content_data = data.get('content') 
    
    element_id = str(uuid.uuid4())
    user = User.query.get(user_id)
    user_name = f"{user.first_name} {user.last_name}" if user else "Unknown"
    
    doc = {
        "elementId": element_id,
        "projectId": project_id,
        "type": element_type,
        "content": content_data,
        "createdBy": user_id,
        "createdByName": user_name,
        "createdAt": int(time.time()),
        "_key": element_id # Use elementId as Arango key
    }
    
    arango_db.collection('whiteboard_elements').insert(doc)
    
    action_doc = {
        "actionId": str(uuid.uuid4()),
        "projectId": project_id, 
        "userId": user_id,
        "userName": user_name,
        "actionType": "add",
        "elementId": element_id,
        "elementType": element_type,
        "data": content_data,
        "timestamp": int(time.time())
    }
    arango_db.collection('whiteboard_actions').insert(action_doc)
    
    emit('element_saved', doc, room=project_id)

@socketio.on('update_element')
def on_update_element(data):
    element_id = data.get('elementId')
    project_id = data.get('projectId')
    user_id = data.get('userId')
    new_content = data.get('content')
    
    # Check existence
    collection = arango_db.collection('whiteboard_elements')
    if collection.has(element_id):
        existing = collection.get(element_id)
        old_content = existing.get('content')
        
        # Update
        existing['content'] = new_content
        collection.update(existing)
        
        emit('element_updated', existing, room=project_id, include_self=False)
        
        user = User.query.get(user_id)
        user_name = f"{user.first_name} {user.last_name}" if user else "Unknown"
        
        action_doc = {
            "actionId": str(uuid.uuid4()),
            "projectId": project_id,
            "userId": user_id,
            "userName": user_name,
            "actionType": "modify",
            "elementId": element_id,
            "elementType": existing.get('type'),
            "data": {"before": old_content, "after": new_content},
            "timestamp": int(time.time())
        }
        arango_db.collection('whiteboard_actions').insert(action_doc)

@socketio.on('delete_element')
def on_delete_element(data):
    element_id = data.get('elementId')
    project_id = data.get('projectId')
    user_id = data.get('userId')
    
    collection = arango_db.collection('whiteboard_elements')
    if collection.has(element_id):
        existing = collection.get(element_id)
        content_snapshot = existing.get('content')
        
        collection.delete(existing)
        
        user = User.query.get(user_id)
        user_name = f"{user.first_name} {user.last_name}" if user else "Unknown"
        
        action_doc = {
            "actionId": str(uuid.uuid4()),
            "projectId": project_id,
            "userId": user_id,
            "userName": user_name,
            "actionType": "delete",
            "elementId": element_id,
            "elementType": existing.get('type'),
            "data": content_snapshot,
            "timestamp": int(time.time())
        }
        arango_db.collection('whiteboard_actions').insert(action_doc)
        
        emit('element_deleted', {'elementId': element_id}, room=project_id)

@socketio.on('get_history')
def on_get_history(data):
    project_id = data.get('projectId')
    
    # AQL for History
    cursor = arango_db.aql.execute(
        '''
        FOR doc IN whiteboard_actions 
        FILTER doc.projectId == @pid 
        SORT doc.timestamp DESC 
        LIMIT 50 
        RETURN doc
        ''',
        bind_vars={'pid': project_id}
    )
    
    history = []
    for doc in cursor:
        history.append({
            "actionId": doc.get('actionId'),
            "userName": doc.get('userName', 'Unknown'),
            "actionType": doc.get('actionType'),
            "elementId": doc.get('elementId'),
            "elementType": doc.get('elementType'),
            "data": doc.get('data'),
            "timestamp": doc.get('timestamp')
        })
    emit('history_data', history)