import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Load configuration based on the FLASK_ENV environment variable
    env = os.getenv('FLASK_ENV', 'default')
    app.config.from_object(config[env])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes.main import main_bp
    app.register_blueprint(main_bp)
    from app.routes.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    from app.routes.saved import saved_bp
    app.register_blueprint(saved_bp, url_prefix='/saved')
    from app.routes.suggest import suggest_bp
    app.register_blueprint(suggest_bp, url_prefix='/suggest')
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    
    return app
    