from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO

db = SQLAlchemy()
bcrypt = Bcrypt()
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'ifri_mentorlink_secret_2026'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Frit9074%40@127.0.0.1:5432/ifri_mentorlink'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialisation des extensions
    db.init_app(app)
    bcrypt.init_app(app)
    socketio.init_app(app)
    
    # Enregistrement des routes
    from app.routes import main
    app.register_blueprint(main)
    
    return app