from .. import db # Correct relative import
from datetime import datetime

class Exam(db.Model):
    __tablename__ = 'exams'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text) # Added description back
    duration_minutes = db.Column(db.Integer, default=60)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # --- THIS IS THE FIX ---
    # Add the missing is_active column
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # --- RELATIONSHIPS ---
    creator = db.relationship("app.models.user.User", back_populates="exams_created")
    questions = db.relationship("app.models.exam.Question", back_populates="exam", cascade="all, delete-orphan")
    sessions = db.relationship("app.models.exam.ExamSession", back_populates="exam", cascade="all, delete-orphan")

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'))
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), default='subjective') # Added back
    correct_answer = db.Column(db.Text) # Added back
    answer_key = db.Column(db.Text) # Added back
    max_score = db.Column(db.Float, default=10.0) # Added back
    order = db.Column(db.Integer, default=0) # Added back
    
    # --- RELATIONSHIPS ---
    exam = db.relationship("app.models.exam.Exam", back_populates="questions")
    answers = db.relationship("app.models.exam.Answer", back_populates="question", cascade="all, delete-orphan")

class ExamSession(db.Model):
    __tablename__ = 'exam_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='in_progress')
    total_score = db.Column(db.Float) # Added back
    
    # --- RELATIONSHIPS ---
    exam = db.relationship("app.models.exam.Exam", back_populates="sessions")
    student = db.relationship("app.models.user.User", back_populates="exam_sessions")
    answers = db.relationship("app.models.exam.Answer", back_populates="session", cascade="all, delete-orphan")
    monitoring_logs = db.relationship("app.models.monitoring.MonitoringLog", back_populates="session", cascade="all, delete-orphan")

class Answer(db.Model):
    __tablename__ = 'answers'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('exam_sessions.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    answer_text = db.Column(db.Text)
    auto_score = db.Column(db.Float) # Added back
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow) # Added back
    
    # --- RELATIONSHGIPS ---
    session = db.relationship("app.models.exam.ExamSession", back_populates="answers")
    question = db.relationship("app.models.exam.Question", back_populates="answers")