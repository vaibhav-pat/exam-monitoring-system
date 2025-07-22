# run_simple.py - Fixed version
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
from flask_socketio import SocketIO

# Initialize extensions directly
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
socketio = SocketIO()

def create_simple_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'dev-secret-key-change-this'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exam_monitoring.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    CORS(app)
    socketio.init_app(app, cors_allowed_origins="*")
    
    return app

# Create app
app = create_simple_app()

# Import models after app creation to avoid circular imports
with app.app_context():
    from app.models.user import User
    from app.models.exam import Exam, Question, ExamSession, Answer
    from app.models.monitoring import MonitoringLog, SystemLog

@app.route('/')
def index():
    """Simple index page"""
    return '''
    <html>
        <head>
            <title>Exam Monitoring System</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <h1>Exam Monitoring System</h1>
                <p>Welcome to the Automated Exam Monitoring System</p>
                <div class="mt-4">
                    <a href="/login" class="btn btn-primary">Login</a>
                    <a href="/register" class="btn btn-secondary">Register</a>
                </div>
                <div class="mt-3">
                    <small>Default admin credentials: admin/admin123</small>
                </div>
            </div>
        </body>
    </html>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Simple login page"""
    from flask import request, redirect, url_for
    from flask_login import login_user
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
    
    return '''
    <html>
        <head>
            <title>Login - Exam Monitoring System</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <div class="row justify-content-center">
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-header">
                                <h4>Login</h4>
                            </div>
                            <div class="card-body">
                                <form method="POST">
                                    <div class="mb-3">
                                        <label for="username" class="form-label">Username</label>
                                        <input type="text" class="form-control" id="username" name="username" required>
                                    </div>
                                    <div class="mb-3">
                                        <label for="password" class="form-label">Password</label>
                                        <input type="password" class="form-control" id="password" name="password" required>
                                    </div>
                                    <button type="submit" class="btn btn-primary">Login</button>
                                    <a href="/" class="btn btn-link">Back</a>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
    </html>
    '''

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Simple registration page"""
    from flask import request, redirect, url_for, flash
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'student')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            return '<h3>Username already exists. <a href="/register">Try again</a></h3>'
        
        # Create new user
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return '<h3>Registration successful! <a href="/login">Login now</a></h3>'
    
    return '''
    <html>
        <head>
            <title>Register - Exam Monitoring System</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <div class="row justify-content-center">
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-header">
                                <h4>Register</h4>
                            </div>
                            <div class="card-body">
                                <form method="POST">
                                    <div class="mb-3">
                                        <label for="username" class="form-label">Username</label>
                                        <input type="text" class="form-control" id="username" name="username" required>
                                    </div>
                                    <div class="mb-3">
                                        <label for="email" class="form-label">Email</label>
                                        <input type="email" class="form-control" id="email" name="email" required>
                                    </div>
                                    <div class="mb-3">
                                        <label for="password" class="form-label">Password</label>
                                        <input type="password" class="form-control" id="password" name="password" required>
                                    </div>
                                    <div class="mb-3">
                                        <label for="role" class="form-label">Role</label>
                                        <select class="form-control" id="role" name="role">
                                            <option value="student">Student</option>
                                            <option value="instructor">Instructor</option>
                                        </select>
                                    </div>
                                    <button type="submit" class="btn btn-primary">Register</button>
                                    <a href="/" class="btn btn-link">Back</a>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
    </html>
    '''

@app.route('/dashboard')
def dashboard():
    """Simple dashboard"""
    from flask_login import current_user, login_required
    
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    return f'''
    <html>
        <head>
            <title>Dashboard - Exam Monitoring System</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <h1>Dashboard</h1>
                <p>Welcome, {current_user.username}!</p>
                <p>Role: {current_user.role}</p>
                <div class="mt-4">
                    <a href="/logout" class="btn btn-danger">Logout</a>
                </div>
            </div>
        </body>
    </html>
    '''

@app.route('/logout')
def logout():
    """Logout"""
    from flask_login import logout_user
    from flask import redirect, url_for
    
    logout_user()
    return redirect(url_for('index'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database and admin user
def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create admin user if doesn't exist
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Created default admin user: admin/admin123")

if __name__ == '__main__':
    print("Starting Exam Monitoring System (Simple Mode)...")
    print("Access the application at: http://localhost:5001")
    print("Default admin credentials: admin/admin123")
    
    # Initialize database
    init_db()
    
    # Run app
    app.run(debug=True, host='0.0.0.0', port=5001)