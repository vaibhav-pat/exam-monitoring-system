from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.exam import ExamSession, Exam
from app.models.monitoring import MonitoringLog
from app.models.user import User
from datetime import datetime, timedelta
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_instructor():
            return jsonify({'error': 'Unauthorized'}), 403
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""
    # Get statistics
    stats = {
        'active_exams': Exam.query.filter_by(is_active=True).count(),
        'students_online': ExamSession.query.filter_by(status='in_progress').count(),
        'warnings_today': MonitoringLog.query.filter(
            MonitoringLog.timestamp >= datetime.utcnow().date()
        ).count(),
        'average_score': db.session.query(db.func.avg(ExamSession.total_score)).scalar() or 0
    }
    
    # Get recent sessions
    recent_sessions = ExamSession.query.order_by(
        ExamSession.start_time.desc()
    ).limit(20).all()
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         recent_sessions=recent_sessions)

@admin_bp.route('/session/<int:session_id>')
@login_required
@admin_required
def review_session(session_id):
    """Review specific exam session"""
    session = ExamSession.query.get_or_404(session_id)
    monitoring_logs = MonitoringLog.query.filter_by(
        session_id=session_id
    ).order_by(MonitoringLog.timestamp).all()
    
    return render_template('admin/review_session.html',
                         session=session,
                         monitoring_logs=monitoring_logs)
