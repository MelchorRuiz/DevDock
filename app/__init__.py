import os
from flask import Flask
from config import config

def create_app():
    app = Flask(__name__)
    
    # Load configuration based on the FLASK_ENV environment variable
    env = os.getenv('FLASK_ENV', 'default')
    app.config.from_object(config[env])
    
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)
    
    @app.errorhandler(404)
    def page_not_found(e):
        return "Page not found", 404
    
    return app
    