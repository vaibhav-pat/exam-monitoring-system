
from flask import Flask, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///minimal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Simple User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return '<h1>Exam System</h1><a href="/login">Login</a>'

@app.route('/login')
def login():
    # Auto-create and login test user
    with app.app_context():
        user = User.query.first()
        if not user:
            user = User(username='test')
            db.session.add(user)
            db.session.commit()
        login_user(user)
    return '<h1>Logged in!</h1><a href="/protected">Go to protected page</a>'

@app.route('/protected')
@login_required
def protected():
    return f'<h1>Hello {current_user.username}!</h1>'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
