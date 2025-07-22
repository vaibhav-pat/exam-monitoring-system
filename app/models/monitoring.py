from app import db
from datetime import datetime

class MonitoringLog(db.Model):
    __tablename__ = 'monitoring_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('exam_sessions.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    activity_type = db.Column(db.String(50))  # multiple_faces, no_face, phone_detected, audio_anomaly, etc.
    confidence_score = db.Column(db.Float)
    details = db.Column(db.Text)  # JSON string with additional details
    video_frame_path = db.Column(db.String(255))  # Path to saved frame
    reviewed = db.Column(db.Boolean, default=False)
    reviewer_notes = db.Column(db.Text)

class SystemLog(db.Model):
    __tablename__ = 'system_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    level = db.Column(db.String(20))  # INFO, WARNING, ERROR
    module = db.Column(db.String(50))
    message = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

