from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db, socketio
from app.models.exam import ExamSession, Question, Answer
from app.models.monitoring import MonitoringLog
from app.models.user import User
from ml_models.cheating_detection.activity_monitor import ActivityMonitor
from ml_models.nlp_grading.scoring_engine import ScoringEngine
import base64
import cv2
import numpy as np
from datetime import datetime
import json
import os

api_bp = Blueprint('api', __name__)

# Store active monitoring sessions
active_monitors = {}

@api_bp.route('/start_session', methods=['POST'])
@login_required
def start_session():
    """Start a new exam session"""
    data = request.get_json()
    exam_id = data.get('exam_id')
    
    # Create new session
    session = ExamSession(
        exam_id=exam_id,
        student_id=current_user.id,
        start_time=datetime.utcnow(),
        status='in_progress'
    )
    db.session.add(session)
    db.session.commit()
    
    # Initialize activity monitor
    config = current_app.config
    monitor = ActivityMonitor(config)
    active_monitors[session.id] = monitor
    
    return jsonify({
        'session_id': session.id,
        'status': 'started'
    })

@api_bp.route('/submit_frame', methods=['POST'])
@login_required
def submit_frame():
    """Process video frame for monitoring"""
    data = request.get_json()
    session_id = data.get('session_id')
    frame_data = data.get('frame')
    
    if session_id not in active_monitors:
        return jsonify({'error': 'Invalid session'}), 400
    
    try:
        # Decode frame
        frame_bytes = base64.b64decode(frame_data.split(',')[1])
        nparr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Analyze frame
        monitor = active_monitors[session_id]
        activities = monitor.analyze_frame(frame)
        
        # Log suspicious activities
        for activity in activities:
            if activity['confidence'] > current_app.config['CHEATING_CONFIDENCE_THRESHOLD']:
                log = MonitoringLog(
                    session_id=session_id,
                    activity_type=activity['type'],
                    confidence_score=activity['confidence'],
                    details=json.dumps(activity['details']),
                    timestamp=activity['timestamp']
                )
                
                # Save evidence frame
                if activity['confidence'] > 0.8:
                    filename = monitor.save_evidence(session_id, activity)
                    if filename:
                        log.video_frame_path = filename
                
                db.session.add(log)
                db.session.commit()
                
                # Emit warning to student
                socketio.emit('warning', {
                    'type': activity['type'],
                    'message': f"Warning: {activity['details']}"
                }, room=f'student_{current_user.id}')
                
                # Notify admin
                socketio.emit('monitoring_alert', {
                    'session_id': session_id,
                    'student_name': current_user.username,
                    'activity_type': activity['type'],
                    'details': activity['details'],
                    'confidence': activity['confidence'],
                    'timestamp': activity['timestamp'].isoformat()
                }, room='admins')
        
        return jsonify({'status': 'processed', 'activities': len(activities)})
    
    except Exception as e:
        current_app.logger.error(f"Frame processing error: {str(e)}")
        return jsonify({'error': 'Processing failed'}), 500

@api_bp.route('/submit_audio', methods=['POST'])
@login_required
def submit_audio():
    """Process audio data for monitoring"""
    data = request.get_json()
    session_id = data.get('session_id')
    audio_level = data.get('audio_level')
    
    # Simple voice detection based on audio level
    if audio_level > 50:  # Threshold for voice activity
        log = MonitoringLog(
            session_id=session_id,
            activity_type='voice_detected',
            confidence_score=0.7,
            details=json.dumps({'audio_level': audio_level}),
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
    
    return jsonify({'status': 'processed'})

@api_bp.route('/grade_exam', methods=['POST'])
@login_required
def grade_exam():
    """Automatically grade an exam"""
    if not current_user.is_instructor():
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    session_id = data.get('session_id')
    
    # Get exam session
    session = ExamSession.query.get_or_404(session_id)
    
    # Get questions and answers
    questions = Question.query.filter_by(exam_id=session.exam_id).all()
    answers = Answer.query.filter_by(session_id=session_id).all()
    
    # Grade the exam
    scoring_engine = ScoringEngine()
    results = scoring_engine.grade_exam(session, questions, answers)
    
    # Update session with score
    session.total_score = results['percentage']
    db.session.commit()
    
    # Save grading details
    for q_result in results['questions']:
        answer = Answer.query.filter_by(
            session_id=session_id,
            question_id=q_result['question_id']
        ).first()
        
        if answer:
            answer.auto_score = q_result['score']
            answer.feedback = q_result['feedback']
    
    db.session.commit()
    
    return jsonify(results)

@api_bp.route('/session/<int:session_id>/report', methods=['GET'])
@login_required
def get_session_report(session_id):
    """Get detailed report for an exam session"""
    if not current_user.is_instructor():
        return jsonify({'error': 'Unauthorized'}), 403
    
    session = ExamSession.query.get_or_404(session_id)
    
    # Get monitoring summary
    if session_id in active_monitors:
        monitor_summary = active_monitors[session_id].get_summary()
    else:
        # Recreate summary from logs
        logs = MonitoringLog.query.filter_by(session_id=session_id).all()
        monitor_summary = {
            'activity_counts': {},
            'suspicion_score': 0,
            'high_confidence_alerts': []
        }
        
        for log in logs:
            activity_type = log.activity_type
            if activity_type not in monitor_summary['activity_counts']:
                monitor_summary['activity_counts'][activity_type] = 0
            monitor_summary['activity_counts'][activity_type] += 1
            
            if log.confidence_score > 0.7:
                monitor_summary['high_confidence_alerts'].append({
                    'type': log.activity_type,
                    'confidence': log.confidence_score,
                    'timestamp': log.timestamp.isoformat(),
                    'details': log.details
                })
    
    # Get grading results
    questions = Question.query.filter_by(exam_id=session.exam_id).all()
    answers = Answer.query.filter_by(session_id=session_id).all()
    
    grading_summary = {
        'total_score': session.total_score or 0,
        'question_scores': []
    }
    
    for question in questions:
        answer = next((a for a in answers if a.question_id == question.id), None)
        if answer:
            grading_summary['question_scores'].append({
                'question_id': question.id,
                'score': answer.auto_score or 0,
                'max_score': question.max_score,
                'feedback': answer.feedback
            })
    
    report = {
        'session_info': {
            'id': session.id,
            'student': session.student.username,
            'exam': session.exam.title,
            'start_time': session.start_time.isoformat(),
            'end_time': session.end_time.isoformat() if session.end_time else None,
            'status': session.status
        },
        'monitoring_summary': monitor_summary,
        'grading_summary': grading_summary
    }
    
    return jsonify(report)


# WebSocket handlers
from flask_socketio import emit, join_room, leave_room

@socketio.on('join_exam')
def handle_join_exam(data):
    """Student joins exam room"""
    session_id = data.get('session_id')
    join_room(f'exam_{session_id}')
    join_room(f'student_{current_user.id}')
    emit('joined', {'status': 'connected'})

@socketio.on('join_admin')
def handle_join_admin():
    """Admin joins monitoring room"""
    if current_user.is_instructor():
        join_room('admins')
        emit('joined', {'status': 'connected'})

@socketio.on('video_frame')
def handle_video_frame(data):
    """Process video frame from student"""
    # Forward to API endpoint for processing
    # This is handled by the REST API to avoid blocking the WebSocket
    pass

@socketio.on('audio_data')
def handle_audio_data(data):
    """Process audio data from student"""
    # Forward to API endpoint for processing
    pass

@socketio.on('tab_switch')
def handle_tab_switch(data):
    """Handle tab switching event"""
    session_id = data.get('session_id')
    
    log = MonitoringLog(
        session_id=session_id,
        activity_type='tab_switch',
        confidence_score=1.0,
        details=json.dumps({'action': 'Student switched browser tab'}),
        timestamp=datetime.utcnow()
    )
    db.session.add(log)
    db.session.commit()
    
    # Emit warning
    emit('warning', {
        'type': 'tab_switch',
        'message': 'Please stay on the exam tab'
    }, room=f'student_{current_user.id}')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnect"""
    # Clean up any resources
    pass