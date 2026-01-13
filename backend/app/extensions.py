from flask_socketio import SocketIO
from arango import ArangoClient

socketio = SocketIO(cors_allowed_origins="*")

arango_client = None
arango_db = None

def init_arango(app):
    global arango_client, arango_db
    
    url = app.config['ARANGO_URL']
    db_name = app.config['ARANGO_DB_NAME']
    username = app.config['ARANGO_USERNAME']
    password = app.config['ARANGO_PASSWORD']
    
    # Initialize client
    arango_client = ArangoClient(hosts=url)
    
    # Create system connection
    sys_db = arango_client.db('_system', username=username, password=password)
    
    # Create database if not exists
    if not sys_db.has_database(db_name):
        sys_db.create_database(db_name)
    
    # Connect to database
    arango_db = arango_client.db(db_name, username=username, password=password)
    
    # Create collections if not exist
    if not arango_db.has_collection('whiteboard_elements'):
        arango_db.create_collection('whiteboard_elements')
        
    if not arango_db.has_collection('whiteboard_actions'):
        arango_db.create_collection('whiteboard_actions')

