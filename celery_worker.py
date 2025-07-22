import os
import sys
from app import create_app, celery

app = create_app()
app.app_context().push()

# Import tasks to register them
from app.tasks import *