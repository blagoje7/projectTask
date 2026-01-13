import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'mysql+mysqlconnector://blagoje:takovo123@localhost/project_tracker'
    
    # ArangoDB Config
    ARANGO_URL = os.environ.get('ARANGO_URL') or 'http://localhost:8529'
    ARANGO_DB_NAME = os.environ.get('ARANGO_DB_NAME') or 'project_tracker_whiteboard'
    ARANGO_USERNAME = os.environ.get('ARANGO_USERNAME') or 'root'
    ARANGO_PASSWORD = os.environ.get('ARANGO_PASSWORD') or ''

    SQLALCHEMY_TRACK_MODIFICATIONS = False
