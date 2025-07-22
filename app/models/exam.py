from app import db
from datetime import datetime
import json

class Exam(db.Model):
    __tablename__ = 'exams'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    duration_minutes = db.Column(db.Integer, default=60)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    questions = db.relationship('Question', backref='exam', lazy='dynamic', cascade='all, delete-orphan')
    sessions = db.relationship('ExamSession', backref='exam', lazy='dynamic')

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'))
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20))  # 'subjective', 'objective'
    correct_answer = db.Column(db.Text)  # For objective questions
    answer_key = db.Column(db.Text)  # Model answer for subjective questions
    rubric = db.Column(db.Text)  # JSON string containing grading rubric
    max_score = db.Column(db.Float, default=10.0)
    order = db.Column(db.Integer, default=0)

class ExamSession(db.Model):
    __tablename__ = 'exam_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='in_progress')  # in_progress, completed, terminated
    total_score = db.Column(db.Float)
    
    # Relationships
    answers = db.relationship('Answer', backref='session', lazy='dynamic', cascade='all, delete-orphan')
    monitoring_logs = db.relationship('MonitoringLog', backref='session', lazy='dynamic', cascade='all, delete-orphan')

class Answer(db.Model):
    __tablename__ = 'answers'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('exam_sessions.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    answer_text = db.Column(db.Text)
    auto_score = db.Column(db.Float)
    manual_score = db.Column(db.Float)
    feedback = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    question = db.relationship('Question', backref='answers')
