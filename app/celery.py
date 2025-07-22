from celery import Celery
from flask import Flask
import os

def make_celery(app_name=__name__):
    """Create a Celery instance"""
    
    # Get Redis URL from environment or use default
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
    
    celery = Celery(
        app_name,
        broker=redis_url + '/0',
        backend=redis_url + '/1',
        include=['app.tasks']  # Include tasks module
    )
    
    # Update configuration
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        broker_connection_retry_on_startup=True,
    )
    
    return celery

# Create the celery instance
celery = make_celery('app')
