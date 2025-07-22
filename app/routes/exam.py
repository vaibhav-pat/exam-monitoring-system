from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models.exam import Exam, Question, ExamSession, Answer
from app.models.user import User
from datetime import datetime

exam_bp = Blueprint('exam', __name__)

@exam_bp.route('/')
@login_required
def index():
    """Main exam page - list available exams"""
    if current_user.is_instructor():
        # Show exams created by instructor
        exams = Exam.query.filter_by(created_by=current_user.id).all()
        return render_template('instructor/exam_list.html', exams=exams)
    else:
        # Show available exams for students
        exams = Exam.query.filter_by(is_active=True).all()
        return render_template('student/exam_list.html', exams=exams)

@exam_bp.route('/take/<int:exam_id>')
@login_required
def take_exam(exam_id):
    """Take an exam"""
    exam = Exam.query.get_or_404(exam_id)
    
    # Check if student already has a session
    existing_session = ExamSession.query.filter_by(
        exam_id=exam_id,
        student_id=current_user.id,
        status='in_progress'
    ).first()
    
    if existing_session:
        session = existing_session
    else:
        # Create new session
        session = ExamSession(
            exam_id=exam_id,
            student_id=current_user.id,
            start_time=datetime.utcnow()
        )
        db.session.add(session)
        db.session.commit()
    
    questions = Question.query.filter_by(exam_id=exam_id).order_by(Question.order).all()
    
    return render_template('exam.html', exam=exam, questions=questions, session=session)

@exam_bp.route('/submit/<int:exam_id>', methods=['POST'])
@login_required
def submit_exam(exam_id):
    """Submit exam answers"""
    exam = Exam.query.get_or_404(exam_id)
    session = ExamSession.query.filter_by(
        exam_id=exam_id,
        student_id=current_user.id,
        status='in_progress'
    ).first()
    
    if not session:
        flash('No active exam session found', 'error')
        return redirect(url_for('exam.index'))
    
    # Save answers
    questions = Question.query.filter_by(exam_id=exam_id).all()
    for question in questions:
        answer_text = request.form.get(f'answer_{question.id}')
        if answer_text:
            answer = Answer(
                session_id=session.id,
                question_id=question.id,
                answer_text=answer_text,
                submitted_at=datetime.utcnow()
            )
            db.session.add(answer)
    
    # Update session status
    session.status = 'completed'
    session.end_time = datetime.utcnow()
    
    db.session.commit()
    
    flash('Exam submitted successfully!', 'success')
    return redirect(url_for('exam.index'))

@exam_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_exam():
    if not current_user.is_instructor():
        flash('Only instructors can create exams', 'error')
        return redirect(url_for('exam.index'))
    
    if request.method == 'POST':
        exam = Exam(
            title=request.form.get('title'),
            description=request.form.get('description'),
            duration_minutes=int(request.form.get('duration', 60)),
            created_by=current_user.id,
            is_active=True
        )
        db.session.add(exam)
        db.session.commit()
        
        flash('Exam created successfully!', 'success')
        return redirect(url_for('exam.index'))
    
    return render_template('instructor/create_exam.html')

@exam_bp.route('/edit/<int:exam_id>')
@login_required
def edit_exam(exam_id):
    # Stub for edit functionality
    return "Edit exam page"

@exam_bp.route('/results/<int:exam_id>')
@login_required
def view_results(exam_id):
    # Stub for results functionality
    return "View results page"