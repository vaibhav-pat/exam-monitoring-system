import os
from flask import Flask
from .config import config  # Import the config dictionary
from .extensions import db, migrate, login_manager, socketio, celery # Import from a dedicated extensions file

def create_app(config_name=os.getenv('FLASK_CONFIG') or 'default'):
    """
    Creates and configures an instance of the Flask application.
    """
    app = Flask(__name__, instance_relative_config=True)

    # --- Load Configuration ---
    app.config.from_object(config[config_name])

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # --- Initialize Extensions ---
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    socketio.init_app(app)

    # The login manager needs to know the endpoint for the login route.
    # 'auth.login' means the 'login' function inside the 'auth' blueprint.
    login_manager.login_view = 'auth.login'
    
    # --- Configure and Update Celery ---
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask

    # --- Register Blueprints ---
    from .routes.main import main_bp
    from .routes.auth import auth_bp
    from .routes.admin import admin_bp
    from .routes.exam import exam_bp
    from .routes.api import api_bp
    
    app.register_blueprint(main_bp, url_prefix='/')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(exam_bp, url_prefix='/exam')
    app.register_blueprint(api_bp, url_prefix='/api')

    # --- CRITICAL: Add the User Loader ---
    from .models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # --- Add Shell Context Processor for easy debugging ---
    @app.shell_context_processor
    def make_shell_context():
        from .models.exam import Exam, Question, ExamSession, Answer
        from .models.monitoring import MonitoringLog, SystemLog
        return {
            'db': db, 'User': User, 'Exam': Exam, 'Question': Question, 
            'ExamSession': ExamSession, 'Answer': Answer, 
            'MonitoringLog': MonitoringLog, 'SystemLog': SystemLog
        }
    
    # Create upload directories if they don't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'evidence'), exist_ok=True)
    
    return app