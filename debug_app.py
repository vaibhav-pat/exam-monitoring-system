import os
from flask import Flask, request, redirect, url_for, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# --- App Initialization ---
app = Flask(__name__)

# --- Configuration: Use an ABSOLUTE path to your home directory ---
# This is the key change to bypass the "unable to open" error.
home_directory = os.path.expanduser('~')
database_path = os.path.join(home_directory, 'my_exam_app_database.db')

app.config['SECRET_KEY'] = 'a-secret-key-for-debugging'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Database and Login Manager Setup ---
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- MODELS (Defined directly inside this file to be self-contained) ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), nullable=False, default='student')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_instructor(self):
        return self.role in ['instructor', 'admin']

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- TEMPLATE HELPER ---
def render_page(content, title="Exam Monitoring System"):
    # ... (This part is the same as before, no need to change)
    if current_user.is_authenticated:
        navbar_links = f'<span class="navbar-text me-3">{current_user.username}</span><a class="nav-link" href="/logout">Logout</a>'
    else:
        navbar_links = '<a class="nav-link" href="/login">Login</a>'
    return render_template_string(f'''<!DOCTYPE html><html lang="en"><head><title>{title}</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet"></head><body><nav class="navbar navbar-expand-lg navbar-dark bg-dark"><div class="container"><a class="navbar-brand" href="/">Exam Monitor</a><div class="navbar-nav ms-auto">{navbar_links}</div></div></nav><div class="container mt-4">{content}</div></body></html>''')

# --- ROUTES (Same as before) ---
@app.route('/')
def index():
    if current_user.is_authenticated: content = f'<h1>Welcome Back, {current_user.username}!</h1><a href="/dashboard" class="btn btn-primary">Go to Dashboard</a>'
    else: content = '<h1>Welcome!</h1><a href="/login" class="btn btn-primary">Login</a> <a href="/register" class="btn btn-secondary">Register</a>'
    return render_page(content)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    error = ''
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and user.check_password(request.form.get('password')):
            login_user(user); return redirect(url_for('dashboard'))
        error = '<div class="alert alert-danger mt-3">Invalid credentials.</div>'
    content = f'''<div class="row justify-content-center"><div class="col-md-5"><h2>Login</h2>{error}<form method="POST"><div class="mb-3"><label>Username</label><input type="text" name="username" class="form-control" required></div><div class="mb-3"><label>Password</label><input type="password" name="password" class="form-control" required></div><button type="submit" class="btn btn-primary w-100">Login</button></form><p class="text-center mt-3">Need an account? <a href="/register">Register</a></p><div class="alert alert-info mt-3">Default admin: admin / admin123</div></div></div>'''
    return render_page(content, title="Login")

@app.route('/register', methods=['GET', 'POST'])
def register():
    # ... (This route is the same as before, no need to change)
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    error = ''
    if request.method == 'POST':
        username, email = request.form.get('username'), request.form.get('email')
        if User.query.filter_by(username=username).first(): error = '<div class="alert alert-danger">Username taken.</div>'
        elif User.query.filter_by(email=email).first(): error = '<div class="alert alert-danger">Email already registered.</div>'
        else:
            user = User(username=username, email=email, role=request.form.get('role', 'student')); user.set_password(request.form.get('password'))
            db.session.add(user); db.session.commit(); return redirect(url_for('login'))
    content = f'''<div class="row justify-content-center"><div class="col-md-5"><h2>Register</h2>{error}<form method="POST"><div class="mb-3"><label>Username</label><input type="text" name="username" class="form-control" required></div><div class="mb-3"><label>Email</label><input type="email" name="email" class="form-control" required></div><div class="mb-3"><label>Password</label><input type="password" name="password" class="form-control" required></div><div class="mb-3"><label>Role</label><select name="role" class="form-select"><option value="student">Student</option><option value="instructor">Instructor</option></select></div><button type="submit" class="btn btn-primary w-100">Register</button></form><p class="text-center mt-3">Have an account? <a href="/login">Login</a></p></div></div>'''
    return render_page(content, title="Register")

@app.route('/dashboard')
@login_required
def dashboard():
    content = f'<h1>{current_user.role.title()} Dashboard</h1>'
    if current_user.is_instructor(): content += '<div class="mt-4"><a href="#" class="btn btn-primary">Create Exam</a> <a href="#" class="btn btn-info">View Results</a></div>'
    else: content += '<div class="mt-4"><a href="#" class="btn btn-primary">Browse Exams</a> <a href="#" class="btn btn-info">My Scores</a></div>'
    return render_page(content, title="Dashboard")

@app.route('/logout')
@login_required
def logout():
    logout_user(); return redirect(url_for('index'))

# --- Application Runner ---
if __name__ == '__main__':
    with app.app_context():
        print(f"--- Attempting to create database at: {database_path} ---")
        db.create_all()
        print("--- Database tables created successfully (or already exist). ---")

        if not User.query.filter_by(username='admin').first():
            print("--- Creating default admin user... ---")
            admin = User(username='admin', email='admin@example.com', role='admin'); admin.set_password('admin123')
            db.session.add(admin); db.session.commit()
            print("--- Admin user created. ---")
    
    print("\nStarting application at http://localhost:5001")
    app.run(debug=True, port=5001)