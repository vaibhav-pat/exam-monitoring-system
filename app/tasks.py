from app import celery, db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@celery.task(name='app.tasks.test_task')
def test_task():
    """Test task to verify Celery is working"""
    return "Celery is working!"

@celery.task(name='app.tasks.grade_exam_async')
def grade_exam_async(session_id):
    """Asynchronously grade an exam"""
    from app.models.exam import ExamSession, Question, Answer
    from ml_models.nlp_grading.scoring_engine import ScoringEngine
    
    try:
        session = ExamSession.query.get(session_id)
        if not session:
            return {'error': 'Session not found'}
        
        # Get questions and answers
        questions = Question.query.filter_by(exam_id=session.exam_id).all()
        answers = Answer.query.filter_by(session_id=session_id).all()
        
        # Grade the exam
        scoring_engine = ScoringEngine()
        results = scoring_engine.grade_exam(session, questions, answers)
        
        # Update session with score
        session.total_score = results['percentage']
        db.session.commit()
        
        return results
    except Exception as e:
        logger.error(f"Error grading exam: {str(e)}")
        return {'error': str(e)}

@celery.task(name='app.tasks.process_monitoring_data')
def process_monitoring_data(session_id, frame_data):
    """Process monitoring data asynchronously"""
    from app.models.monitoring import MonitoringLog
    
    try:
        # Heavy ML processing here
        # This is a placeholder - implement actual processing
        
        log = MonitoringLog(
            session_id=session_id,
            activity_type='processed',
            confidence_score=0.5,
            details='Frame processed',
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
        
        return {'status': 'processed'}
    except Exception as e:
        logger.error(f"Error processing monitoring data: {str(e)}")
        return {'error': str(e)}

@celery.task(name='app.tasks.cleanup_old_sessions')
def cleanup_old_sessions():
    """Clean up old exam sessions and their data"""
    from app.models.exam import ExamSession
    from datetime import timedelta
    
    try:
        # Delete sessions older than 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        old_sessions = ExamSession.query.filter(
            ExamSession.end_time < cutoff_date
        ).all()
        
        count = len(old_sessions)
        for session in old_sessions:
            db.session.delete(session)
        
        db.session.commit()
        return {'deleted': count}
    except Exception as e:
        logger.error(f"Error cleaning up sessions: {str(e)}")
        return {'error': str(e)}