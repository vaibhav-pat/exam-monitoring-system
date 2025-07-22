from celery import Celery
from app import create_app

def make_celery(app=None):
    app = app or create_app()
    
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

# Create standalone Celery app for worker
def create_celery_app():
    """Create Celery app for standalone worker"""
    from app import create_app
    
    flask_app = create_app()
    celery = make_celery(flask_app)
    
    return celery