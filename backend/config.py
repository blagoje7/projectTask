import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'mysql+mysqlconnector://blagoje:takovo123@localhost/project_tracker'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
