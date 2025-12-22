from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from ..models import db, Task, Project, Epic, User, TaskActivity
from ..utils import (
    get_current_user_id, get_current_user_role,
    success_response, error_response,
    validate_user_id, check_role
)
from ..constants import ADMIN_MANAGER, ALL_PRIORITIES, ALL_STATUSES

tasks_bp = Blueprint('tasks', __name__)

"""Get all tasks for a project"""
@tasks_bp.route('/projects/<project_id>/tasks', methods=['GET'])
@jwt_required()
def get_tasks(project_id):
    project = Project.query.get(project_id)
    if not project:
        return error_response("Project not found", 404)
    
    tasks = Task.query.filter_by(project_id=project_id).all()
    return success_response([t.to_dict() for t in tasks])

"""Get tasks assigned to current user"""
@tasks_bp.route('/tasks/my-tasks', methods=['GET'])
@jwt_required()
def get_my_tasks():
    user_id = get_current_user_id()
    error = validate_user_id(user_id)
    if error:
        return error
    
    user = User.query.get(user_id)
    if not user:
        return error_response("User not found", 404)
    
    tasks = user.assigned_tasks
    return success_response([t.to_dict() for t in tasks])

"""Create a new task (Admin/Manager only)"""
@tasks_bp.route('/projects/<project_id>/tasks', methods=['POST'])
@jwt_required()
def create_task(project_id):
    user_id = get_current_user_id()
    role = get_current_user_role()
    
    error = validate_user_id(user_id)
    if error:
        return error
    
    error = check_role(role, ADMIN_MANAGER)
    if error:
        return error
    
    project = Project.query.get(project_id)
    if not project:
        return error_response("Project not found", 404)
    
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')
    epic_id = data.get('epicId')
    priority = data.get('priority', 'medium')
    deadline = data.get('deadline')
    assignee_ids = data.get('assigneeIds', [])
    
    if not name:
        return error_response("Task name is required")
    
    if priority not in ALL_PRIORITIES:
        return error_response(f"Priority must be one of: {', '.join(ALL_PRIORITIES)}")
    
    # Validate epic if provided
    if epic_id:
        epic = Epic.query.get(epic_id)
        if not epic or epic.project_id != project_id:
            return error_response("Invalid epic for this project")
    
    task = Task(
        name=name,
        description=description,
        project_id=project_id,
        epic_id=epic_id,
        priority=priority,
        deadline=deadline,
        created_by=user_id
    )
    
    # Assign users to task
    for assignee_id in assignee_ids:
        user = User.query.get(assignee_id)
        if user:
            task.assignees.append(user)
    
    db.session.add(task)
    db.session.commit()
    
    # Log task creation activity
    creation_activity = TaskActivity(
        task_id=task.task_id,
        user_id=user_id,
        action_type='created',
        old_status=None,
        new_status='to_do'
    )
    db.session.add(creation_activity)
    db.session.commit()
    
    # TODO: Create Jira issue (will implement in jira_integration)
    
    return success_response(task.to_dict(), 201)

"""Update task details (Admin/Manager only for priority/deadline, all users for other fields)"""
@tasks_bp.route('/tasks/<task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    role = get_current_user_role()
    
    task = Task.query.get(task_id)
    if not task:
        return error_response("Task not found", 404)
    
    data = request.get_json()
    
    # Check if user is trying to update priority or deadline
    if ('priority' in data or 'deadline' in data) and role not in ['admin', 'manager']:
        return error_response("Only managers and admins can change task priority or deadline", 403)
    
    # Only admin/manager can update name, description, epicId
    error = check_role(role, ADMIN_MANAGER)
    if error:
        return error
    
    if 'name' in data:
        task.name = data['name']
    if 'description' in data:
        task.description = data['description']
    if 'epicId' in data:
        task.epic_id = data['epicId']
    if 'priority' in data:
        if data['priority'] in ALL_PRIORITIES:
            task.priority = data['priority']
    if 'deadline' in data:
        task.deadline = data['deadline']
    if 'assigneeIds' in data:
        # Update assignees
        task.assignees = []
        for assignee_id in data['assigneeIds']:
            user = User.query.get(assignee_id)
            if user:
                task.assignees.append(user)
    
    db.session.commit()
    return success_response(task.to_dict())

"""Update task status (All authenticated users)"""
@tasks_bp.route('/tasks/<task_id>/status', methods=['PUT'])
@jwt_required()
def update_task_status(task_id):
    from datetime import datetime
    
    user_id = get_current_user_id()
    role = get_current_user_role()
    
    task = Task.query.get(task_id)
    if not task:
        return error_response("Task not found", 404)
    
    data = request.get_json()
    status = data.get('status')
    
    if status not in ALL_STATUSES:
        return error_response(f"Invalid status. Must be one of: {', '.join(ALL_STATUSES)}")
    
    # Only managers/admins can mark task as done
    if status == 'done' and role not in ['admin', 'manager']:
        return error_response("Only managers and admins can mark tasks as done", 403)
    
    old_status = task.status
    task.status = status
    
    current_timestamp = int(datetime.utcnow().timestamp())
    
    # Log activity to task_activity table
    activity = TaskActivity(
        task_id=task_id,
        user_id=user_id,
        action_type='status_change',
        old_status=old_status,
        new_status=status
    )
    db.session.add(activity)
    
    # Track when work started (to_do -> in_progress)
    if status == 'in_progress':
        if old_status == 'to_do' and not task.started_at:
            task.started_at = current_timestamp
            task.started_by = user_id
        # Track the start of this work session
        task.last_progress_start = current_timestamp
    
    # Track when sent for review or done (accumulate work time)
    if old_status == 'in_progress' and status in ['for_review', 'done', 'to_do']:
        # Calculate and accumulate the work time for this session
        if task.last_progress_start:
            session_time = current_timestamp - task.last_progress_start
            task.accumulated_work_time = (task.accumulated_work_time or 0) + session_time
            task.last_progress_start = None
    
    # Track when sent for review
    if status == 'for_review' and old_status == 'in_progress' and not task.reviewed_at:
        task.reviewed_at = current_timestamp
        task.reviewed_by = user_id
    
    # Track completion time when task is marked as done (only managers)
    if status == 'done' and old_status != 'done':
        task.completed_at = current_timestamp
        task.completed_by = user_id
    
    # Clear timestamps and users if task is moved backwards in workflow
    if status == 'to_do':
        task.started_at = None
        task.started_by = None
        task.reviewed_at = None
        task.reviewed_by = None
        task.completed_at = None
        task.completed_by = None
        # Keep accumulated work time, just reset the session
        task.last_progress_start = None
    elif status == 'in_progress' and old_status in ['for_review', 'done']:
        # If moving back to in_progress from review/done, clear review/completion timestamps
        task.reviewed_at = None
        task.reviewed_by = None
        task.completed_at = None
        task.completed_by = None
    elif status == 'for_review':
        task.completed_at = None
        task.completed_by = None
    
    db.session.commit()
    
    # TODO: Send notification if status changed to for_review or done
    # This would integrate with Communication Service
    if status in ['for_review', 'done'] and old_status != status:
        # Placeholder for notification logic
        print(f"Task {task.name} moved to {status} - notification should be sent")
    
    return success_response(task.to_dict())

"""Get activity history for a task"""
@tasks_bp.route('/tasks/<task_id>/activities', methods=['GET'])
@jwt_required()
def get_task_activities(task_id):
    task = Task.query.get(task_id)
    if not task:
        return error_response("Task not found", 404)
    
    # Get all activities for this task, ordered by timestamp
    activities = TaskActivity.query.filter_by(task_id=task_id).order_by(TaskActivity.timestamp.asc()).all()
    
    return success_response([activity.to_dict() for activity in activities])

"""Delete a task (Admin/Manager only)"""
@tasks_bp.route('/tasks/<task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    role = get_current_user_role()
    error = check_role(role, ADMIN_MANAGER)
    if error:
        return error
    
    task = Task.query.get(task_id)
    if not task:
        return error_response("Task not found", 404)
    
    db.session.delete(task)
    db.session.commit()
    
    return success_response({"msg": "Task deleted"})

"""Get task assignees"""
@tasks_bp.route('/tasks/<task_id>/assignees', methods=['GET'])
@jwt_required()
def get_task_assignees(task_id):
    task = Task.query.get(task_id)
    if not task:
        return error_response("Task not found", 404)
    
    assignees = [{
        'userId': user.user_id,
        'firstName': user.first_name,
        'lastName': user.last_name,
        'email': user.email,
        'role': user.role.name if user.role else None
    } for user in task.assignees]
    
    return success_response(assignees)
