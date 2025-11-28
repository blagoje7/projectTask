import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key'
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://blagoje:takovo123@localhost/project_tracker'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Jira Cloud Integration (Optional - uncomment and configure to enable)
    # JIRA_SERVER = 'https://your-domain.atlassian.net'
    # JIRA_EMAIL = 'your-email@example.com'
    # JIRA_API_TOKEN = 'your-jira-api-token'
