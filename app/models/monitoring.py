from .. import db # Correct relative import
from datetime import datetime

class MonitoringLog(db.Model):
    __tablename__ = 'monitoring_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('exam_sessions.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    activity_type = db.Column(db.String(50))
    
    # --- RELATIONSHIP ---
    session = db.relationship("app.models.exam.ExamSession", back_populates="monitoring_logs")

# Your SystemLog model would go here if needed