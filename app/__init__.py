import os
from flask import Flask, render_template
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
    import os
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:Frit9074%40@127.0.0.1:5432/ifri_mentorlink')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
   # Initialisation des extensions
    db.init_app(app)
    bcrypt.init_app(app)
    socketio.init_app(app)

    # Créer les tables automatiquement
    with app.app_context():
        db.create_all()
    
    # Enregistrement des routes
    from app.routes import main
    app.register_blueprint(main)

    @app.errorhandler(404)
    def page_non_trouvee(e):
        return render_template('404.html'), 404
    
    return app