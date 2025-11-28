# Jira Cloud Integration for Project/Task Management

"""
To enable Jira integration:

1. Install the jira library:
   pip install jira

2. Set up Jira Cloud credentials:
   - Go to https://id.atlassian.com/manage-profile/security/api-tokens
   - Create an API token
   - Add to config.py:
     JIRA_SERVER = 'https://your-domain.atlassian.net'
     JIRA_EMAIL = 'your-email@example.com'
     JIRA_API_TOKEN = 'your-api-token'

3. Uncomment the code below and use in routes/projects.py and routes/tasks.py
"""

# from jira import JIRA
# from flask import current_app

# def get_jira_client():
#     """Get authenticated Jira client"""
#     try:
#         jira = JIRA(
#             server=current_app.config.get('JIRA_SERVER'),
#             basic_auth=(
#                 current_app.config.get('JIRA_EMAIL'),
#                 current_app.config.get('JIRA_API_TOKEN')
#             )
#         )
#         return jira
#     except Exception as e:
#         print(f"Jira connection error: {e}")
#         return None

# def create_jira_project(name, key, description='', lead_email=None):
#     """
#     Create a project in Jira Cloud
    
#     Args:
#         name: Project name
#         key: Project key (e.g., 'PROJ' - must be uppercase, 2-10 chars)
#         description: Project description
#         lead_email: Email of project lead
    
#     Returns:
#         dict with jira_key and jira_url, or None if failed
#     """
#     jira = get_jira_client()
#     if not jira:
#         return None
    
#     try:
#         # Create project in Jira
#         project = jira.create_project(
#             key=key.upper(),
#             name=name,
#             description=description,
#             template_name='Kanban software development',
#             lead={'emailAddress': lead_email} if lead_email else None
#         )
        
#         return {
#             'jira_key': project.key,
#             'jira_url': f"{current_app.config.get('JIRA_SERVER')}/projects/{project.key}"
#         }
#     except Exception as e:
#         print(f"Error creating Jira project: {e}")
#         return None

# def create_jira_issue(project_key, summary, description='', issue_type='Task', priority='Medium', assignee_email=None):
#     """
#     Create an issue (task) in Jira
    
#     Args:
#         project_key: Jira project key
#         summary: Task summary/name
#         description: Task description
#         issue_type: 'Task', 'Epic', 'Story', 'Bug', etc.
#         priority: 'Low', 'Medium', 'High'
#         assignee_email: Email of assignee
    
#     Returns:
#         dict with jira_key and jira_url, or None if failed
#     """
#     jira = get_jira_client()
#     if not jira:
#         return None
    
#     try:
#         issue_dict = {
#             'project': {'key': project_key},
#             'summary': summary,
#             'description': description,
#             'issuetype': {'name': issue_type},
#         }
        
#         if priority:
#             issue_dict['priority'] = {'name': priority}
        
#         if assignee_email:
#             issue_dict['assignee'] = {'emailAddress': assignee_email}
        
#         issue = jira.create_issue(fields=issue_dict)
        
#         return {
#             'jira_key': issue.key,
#             'jira_url': f"{current_app.config.get('JIRA_SERVER')}/browse/{issue.key}"
#         }
#     except Exception as e:
#         print(f"Error creating Jira issue: {e}")
#         return None

# def generate_jira_key(project_name):
#     """
#     Generate a valid Jira project key from project name
    
#     Args:
#         project_name: Name of the project
    
#     Returns:
#         Valid Jira key (uppercase, 2-10 chars, letters only)
#     """
#     # Take first letters of each word, up to 10 characters
#     words = project_name.upper().split()
#     key = ''.join(word[0] for word in words if word)
    
#     # Remove non-letter characters
#     key = ''.join(c for c in key if c.isalpha())
    
#     # Ensure it's at least 2 characters
#     if len(key) < 2:
#         key = project_name.upper().replace(' ', '')[:10]
#         key = ''.join(c for c in key if c.isalpha())
    
#     # Limit to 10 characters
#     key = key[:10]
    
#     return key if len(key) >= 2 else 'PROJ'

# Example usage in routes/projects.py:
# 
# from ..jira_integration import create_jira_project, generate_jira_key
# 
# @projects_bp.route('/projects', methods=['POST'])
# @jwt_required()
# def create_project():
#     # ... existing code ...
#     
#     # Create project in database
#     project = Project(name=name, description=description, created_by=user_id)
#     
#     # Create in Jira
#     jira_key = generate_jira_key(name)
#     jira_data = create_jira_project(
#         name=name,
#         key=jira_key,
#         description=description,
#         lead_email=user.email
#     )
#     
#     if jira_data:
#         project.jira_key = jira_data['jira_key']
#         project.jira_url = jira_data['jira_url']
#     
#     # ... rest of code ...
