from .. import db # Correct relative import
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), default='student')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # --- RELATIONSHIPS USING FULLY QUALIFIED STRINGS ---
    # A user can create many exams
    exams_created = db.relationship("app.models.exam.Exam", back_populates="creator")
    # A user can have many exam sessions
    exam_sessions = db.relationship("app.models.exam.ExamSession", back_populates="student")
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        if not self.password_hash: return False
        return check_password_hash(self.password_hash, password)
    
    def is_instructor(self):
        return self.role in ['instructor', 'admin']