import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db, socketio
from app.models.user import User
from app.models.exam import Exam, Question, ExamSession, Answer
from app.models.monitoring import MonitoringLog, SystemLog

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': User, 
        'Exam': Exam,
        'Question': Question,
        'ExamSession': ExamSession,
        'Answer': Answer,
        'MonitoringLog': MonitoringLog,
        'SystemLog': SystemLog
    }

if __name__ == '__main__':
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)