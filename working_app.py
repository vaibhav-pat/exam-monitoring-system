# working_app.py - Fixed version with inline templates
from flask import Flask, render_template_string, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Exam, Question, ExamSession, Answer, MonitoringLog

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exam_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Combined template function
def render_page(content, title="Exam Monitoring System"):
    template = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container">
                <a class="navbar-brand" href="/">Exam Monitor</a>
                <div class="navbar-nav ms-auto">
                    {'<span class="navbar-text me-3">' + current_user.username + '</span><a class="nav-link" href="/logout">Logout</a>' if current_user.is_authenticated else '<a class="nav-link" href="/login">Login</a>'}
                </div>
            </div>
        </nav>
        <div class="container mt-4">
            {content}
        </div>
    </body>
    </html>
    '''
    return template

@app.route('/')
def index():
    if current_user.is_authenticated:
        content = f'''
        <h1>Welcome to Exam Monitoring System</h1>
        <h3>Hello, {current_user.username}!</h3>
        <p>Role: {current_user.role}</p>
        <a href="/dashboard" class="btn btn-primary">Go to Dashboard</a>
        '''
    else:
        content = '''
        <h1>Welcome to Exam Monitoring System</h1>
        <p>An AI-powered automated exam proctoring and grading system.</p>
        <a href="/login" class="btn btn-primary">Login</a>
        <a href="/register" class="btn btn-secondary">Register</a>
        '''
    return render_page(content)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            error = '<div class="alert alert-danger">Invalid username or password</div>'
    else:
        error = ''
    
    content = f'''
    <div class="row justify-content-center">
        <div class="col-md-4">
            <h2>Login</h2>
            {error}
            <form method="POST">
                <div class="mb-3">
                    <label>Username</label>
                    <input type="text" name="username" class="form-control" required>
                </div>
                <div class="mb-3">
                    <label>Password</label>
                    <input type="password" name="password" class="form-control" required>
                </div>
                <button type="submit" class="btn btn-primary">Login</button>
                <a href="/register" class="btn btn-link">Register</a>
            </form>
            <p class="mt-3 text-muted">Default admin: admin/admin123</p>
        </div>
    </div>
    '''
    return render_page(content, "Login - Exam Monitoring System")

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = ''
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'student')
        
        if User.query.filter_by(username=username).first():
            error = '<div class="alert alert-danger">Username already exists!</div>'
        else:
            user = User(username=username, email=email, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
    
    content = f'''
    <div class="row justify-content-center">
        <div class="col-md-4">
            <h2>Register</h2>
            {error}
            <form method="POST">
                <div class="mb-3">
                    <label>Username</label>
                    <input type="text" name="username" class="form-control" required>
                </div>
                <div class="mb-3">
                    <label>Email</label>
                    <input type="email" name="email" class="form-control" required>
                </div>
                <div class="mb-3">
                    <label>Password</label>
                    <input type="password" name="password" class="form-control" required>
                </div>
                <div class="mb-3">
                    <label>Role</label>
                    <select name="role" class="form-control">
                        <option value="student">Student</option>
                        <option value="instructor">Instructor</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-primary">Register</button>
                <a href="/login" class="btn btn-link">Back to Login</a>
            </form>
        </div>
    </div>
    '''
    return render_page(content, "Register - Exam Monitoring System")

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_instructor():
        # Get instructor's exams
        exams = Exam.query.filter_by(created_by=current_user.id).all()
        exam_list = ''.join([f'<li>{exam.title} - {exam.duration_minutes} minutes</li>' for exam in exams]) if exams else '<li>No exams created yet</li>'
        
        content = f'''
        <h1>Instructor Dashboard</h1>
        <p>Welcome, {current_user.username}!</p>
        
        <div class="row mt-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Quick Actions</h5>
                    </div>
                    <div class="card-body">
                        <a href="/create-exam" class="btn btn-primary mb-2 d-block">Create New Exam</a>
                        <a href="/view-results" class="btn btn-info mb-2 d-block">View Results</a>
                        <a href="/monitoring" class="btn btn-warning d-block">Live Monitoring</a>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Your Exams</h5>
                    </div>
                    <div class="card-body">
                        <ul>{exam_list}</ul>
                    </div>
                </div>
            </div>
        </div>
        '''
    else:
        # Get available exams for students
        exams = Exam.query.filter_by(is_active=True).all()
        exam_list = ''.join([f'<li><a href="/take-exam/{exam.id}">{exam.title}</a> - {exam.duration_minutes} minutes</li>' for exam in exams]) if exams else '<li>No exams available</li>'
        
        content = f'''
        <h1>Student Dashboard</h1>
        <p>Welcome, {current_user.username}!</p>
        
        <div class="row mt-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Available Exams</h5>
                    </div>
                    <div class="card-body">
                        <ul>{exam_list}</ul>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Your Results</h5>
                    </div>
                    <div class="card-body">
                        <a href="/my-scores" class="btn btn-info">View My Scores</a>
                    </div>
                </div>
            </div>
        </div>
        '''
    
    return render_page(content, "Dashboard - Exam Monitoring System")

@app.route('/create-exam', methods=['GET', 'POST'])
@login_required
def create_exam():
    if not current_user.is_instructor():
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        duration = int(request.form.get('duration', 60))
        
        exam = Exam(
            title=title,
            description=description,
            duration_minutes=duration,
            created_by=current_user.id
        )
        db.session.add(exam)
        db.session.commit()
        
        return redirect(url_for('add_questions', exam_id=exam.id))
    
    content = '''
    <h2>Create New Exam</h2>
    <form method="POST">
        <div class="mb-3">
            <label>Exam Title</label>
            <input type="text" name="title" class="form-control" required>
        </div>
        <div class="mb-3">
            <label>Description</label>
            <textarea name="description" class="form-control" rows="3"></textarea>
        </div>
        <div class="mb-3">
            <label>Duration (minutes)</label>
            <input type="number" name="duration" class="form-control" value="60" required>
        </div>
        <button type="submit" class="btn btn-primary">Create Exam</button>
        <a href="/dashboard" class="btn btn-secondary">Cancel</a>
    </form>
    '''
    return render_page(content, "Create Exam")

@app.route('/add-questions/<int:exam_id>', methods=['GET', 'POST'])
@login_required
def add_questions(exam_id):
    if not current_user.is_instructor():
        return redirect(url_for('dashboard'))
    
    exam = Exam.query.get_or_404(exam_id)
    
    if request.method == 'POST':
        question_text = request.form.get('question_text')
        question_type = request.form.get('question_type')
        answer_key = request.form.get('answer_key')
        max_score = float(request.form.get('max_score', 10))
        
        question = Question(
            exam_id=exam_id,
            question_text=question_text,
            question_type=question_type,
            answer_key=answer_key,
            max_score=max_score
        )
        db.session.add(question)
        db.session.commit()
        
        if request.form.get('add_more'):
            return redirect(url_for('add_questions', exam_id=exam_id))
        else:
            return redirect(url_for('dashboard'))
    
    # Get existing questions
    questions = Question.query.filter_by(exam_id=exam_id).all()
    question_list = ''.join([f'<li>{q.question_text} ({q.max_score} points)</li>' for q in questions]) if questions else '<li>No questions added yet</li>'
    
    content = f'''
    <h2>Add Questions to: {exam.title}</h2>
    
    <div class="card mb-4">
        <div class="card-header">Existing Questions</div>
        <div class="card-body">
            <ul>{question_list}</ul>
        </div>
    </div>
    
    <form method="POST">
        <div class="mb-3">
            <label>Question Text</label>
            <textarea name="question_text" class="form-control" rows="3" required></textarea>
        </div>
        <div class="mb-3">
            <label>Question Type</label>
            <select name="question_type" class="form-control">
                <option value="subjective">Subjective (Essay)</option>
                <option value="objective">Objective (Short Answer)</option>
            </select>
        </div>
        <div class="mb-3">
            <label>Model Answer / Answer Key</label>
            <textarea name="answer_key" class="form-control" rows="3" required></textarea>
        </div>
        <div class="mb-3">
            <label>Max Score</label>
            <input type="number" name="max_score" class="form-control" value="10" step="0.1" required>
        </div>
        <button type="submit" name="add_more" value="1" class="btn btn-primary">Add & Continue</button>
        <button type="submit" class="btn btn-success">Add & Finish</button>
        <a href="/dashboard" class="btn btn-secondary">Cancel</a>
    </form>
    '''
    return render_page(content, "Add Questions")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Add these routes to your working_app.py

@app.route('/take-exam/<int:exam_id>')
@login_required
def take_exam(exam_id):
    if current_user.is_instructor():
        return redirect(url_for('dashboard'))
    
    exam = Exam.query.get_or_404(exam_id)
    
    # Check if student already has an active session
    existing_session = ExamSession.query.filter_by(
        exam_id=exam_id,
        student_id=current_user.id,
        status='in_progress'
    ).first()
    
    if existing_session:
        return redirect(url_for('exam_page', session_id=existing_session.id))
    
    # Create new session
    session = ExamSession(
        exam_id=exam_id,
        student_id=current_user.id
    )
    db.session.add(session)
    db.session.commit()
    
    return redirect(url_for('exam_page', session_id=session.id))

@app.route('/exam/<int:session_id>')
@login_required
def exam_page(session_id):
    session = ExamSession.query.get_or_404(session_id)
    
    # Verify this is the student's session
    if session.student_id != current_user.id:
        return redirect(url_for('dashboard'))
    
    exam = Exam.query.get(session.exam_id)
    questions = Question.query.filter_by(exam_id=exam.id).order_by(Question.order).all()
    
    # Generate question HTML
    questions_html = ''
    for i, q in enumerate(questions, 1):
        if q.question_type == 'objective':
            input_field = f'<input type="text" class="form-control" name="answer_{q.id}" placeholder="Your answer" required>'
        else:
            input_field = f'<textarea class="form-control" name="answer_{q.id}" rows="5" placeholder="Your answer" required></textarea>'
        
        questions_html += f'''
        <div class="question-container mb-4 p-3 bg-light rounded">
            <h5>Question {i} ({q.max_score} points)</h5>
            <p>{q.question_text}</p>
            {input_field}
        </div>
        '''
    
    content = f'''
    <style>
        #video-container {{
            position: fixed;
            top: 80px;
            right: 20px;
            width: 200px;
            height: 150px;
            border: 2px solid #333;
            border-radius: 8px;
            overflow: hidden;
            background: #000;
            z-index: 1000;
        }}
        
        #localVideo {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            transform: scaleX(-1);
        }}
        
        .monitoring-status {{
            position: fixed;
            top: 240px;
            right: 20px;
            width: 200px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
            font-size: 0.9em;
        }}
        
        .timer {{
            position: fixed;
            top: 80px;
            left: 20px;
            font-size: 1.5em;
            font-weight: bold;
            padding: 10px 20px;
            background: #007bff;
            color: white;
            border-radius: 8px;
        }}
    </style>
    
    <div class="row">
        <div class="col-md-9">
            <h2>{exam.title}</h2>
            <p>{exam.description}</p>
            
            <form id="examForm" method="POST" action="/submit-exam/{session.id}">
                {questions_html}
                <button type="submit" class="btn btn-primary btn-lg">Submit Exam</button>
            </form>
        </div>
    </div>
    
    <!-- Video Monitoring Container -->
    <div id="video-container">
        <video id="localVideo" autoplay muted></video>
    </div>
    
    <!-- Monitoring Status -->
    <div class="monitoring-status">
        <h6>Monitoring Status</h6>
        <div>📷 Camera: <span id="cameraStatus">Initializing...</span></div>
        <div>🎤 Audio: <span id="audioStatus">Initializing...</span></div>
        <div class="mt-2">
            <small>⚠️ Warnings: <span id="warningCount">0</span></small>
        </div>
    </div>
    
    <!-- Timer -->
    <div class="timer">
        Time Left: <span id="timeRemaining">{exam.duration_minutes}:00</span>
    </div>
    
    <script>
    let localStream;
    let examDuration = {exam.duration_minutes} * 60;
    let timeLeft = examDuration;
    let warningCount = 0;
    
    // Initialize timer
    function startTimer() {{
        const timerInterval = setInterval(() => {{
            timeLeft--;
            
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            document.getElementById('timeRemaining').textContent = 
                `${{minutes.toString().padStart(2, '0')}}:${{seconds.toString().padStart(2, '0')}}`;
            
            if (timeLeft <= 0) {{
                clearInterval(timerInterval);
                document.getElementById('examForm').submit();
            }}
        }}, 1000);
    }}
    
    // Initialize webcam
    async function initializeMedia() {{
        try {{
            localStream = await navigator.mediaDevices.getUserMedia({{
                video: true,
                audio: true
            }});
            
            document.getElementById('localVideo').srcObject = localStream;
            document.getElementById('cameraStatus').textContent = 'Active';
            document.getElementById('audioStatus').textContent = 'Active';
            
            // Start monitoring
            startMonitoring();
            
        }} catch (error) {{
            console.error('Error accessing media devices:', error);
            alert('Camera and microphone access is required for the exam. Please enable permissions and refresh.');
        }}
    }}
    
    // Simple monitoring (placeholder for real monitoring)
    function startMonitoring() {{
        // In a real implementation, this would send frames to the server
        console.log('Monitoring started');
        
        // Detect tab switching
        document.addEventListener('visibilitychange', () => {{
            if (document.hidden) {{
                warningCount++;
                document.getElementById('warningCount').textContent = warningCount;
                alert('Warning: Please do not switch tabs during the exam!');
            }}
        }});
    }}
    
    // Prevent right-click
    document.addEventListener('contextmenu', (e) => e.preventDefault());
    
    // Prevent copy/paste
    document.addEventListener('copy', (e) => e.preventDefault());
    document.addEventListener('paste', (e) => e.preventDefault());
    
    // Initialize everything when page loads
    document.addEventListener('DOMContentLoaded', () => {{
        initializeMedia();
        startTimer();
    }});
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', (e) => {{
        if (localStream) {{
            localStream.getTracks().forEach(track => track.stop());
        }}
    }});
    </script>
    '''
    
    return render_page(content, f"Exam: {exam.title}")

@app.route('/submit-exam/<int:session_id>', methods=['POST'])
@login_required
def submit_exam(session_id):
    session = ExamSession.query.get_or_404(session_id)
    
    # Verify this is the student's session
    if session.student_id != current_user.id:
        return redirect(url_for('dashboard'))
    
    # Get questions
    exam = Exam.query.get(session.exam_id)
    questions = Question.query.filter_by(exam_id=exam.id).all()
    
    # Save answers
    for question in questions:
        answer_text = request.form.get(f'answer_{question.id}')
        if answer_text:
            answer = Answer(
                session_id=session.id,
                question_id=question.id,
                answer_text=answer_text
            )
            db.session.add(answer)
    
    # Update session status
    session.status = 'completed'
    session.end_time = db.func.now()
    
    db.session.commit()
    
    # Simple auto-grading for objective questions
    total_score = 0
    max_score = 0
    
    for question in questions:
        answer = Answer.query.filter_by(
            session_id=session.id,
            question_id=question.id
        ).first()
        
        if answer and question.question_type == 'objective':
            if answer.answer_text.strip().lower() == question.answer_key.strip().lower():
                answer.auto_score = question.max_score
                total_score += question.max_score
            else:
                answer.auto_score = 0
        
        max_score += question.max_score
    
    # Calculate percentage
    if max_score > 0:
        session.total_score = (total_score / max_score) * 100
    
    db.session.commit()
    
    content = f'''
    <div class="text-center">
        <h2>Exam Submitted Successfully!</h2>
        <p class="lead">Your answers have been recorded.</p>
        
        <div class="card mt-4" style="max-width: 400px; margin: 0 auto;">
            <div class="card-body">
                <h5>Preliminary Score (Objective Questions Only)</h5>
                <h3>{total_score:.1f} / {max_score}</h3>
                <p class="text-muted">Subjective questions will be graded by your instructor.</p>
            </div>
        </div>
        
        <a href="/dashboard" class="btn btn-primary mt-4">Back to Dashboard</a>
    </div>
    '''
    
    return render_page(content, "Exam Submitted")

@app.route('/view-results')
@login_required
def view_results():
    if not current_user.is_instructor():
        return redirect(url_for('dashboard'))
    
    # Get all sessions for exams created by this instructor
    sessions = db.session.query(ExamSession).join(Exam).filter(
        Exam.created_by == current_user.id
    ).order_by(ExamSession.start_time.desc()).all()
    
    rows = ''
    for session in sessions:
        exam = Exam.query.get(session.exam_id)
        student = User.query.get(session.student_id)
        
        status_badge = {
            'in_progress': '<span class="badge bg-primary">In Progress</span>',
            'completed': '<span class="badge bg-success">Completed</span>',
            'terminated': '<span class="badge bg-danger">Terminated</span>'
        }.get(session.status, session.status)
        
        score = f'{session.total_score:.1f}%' if session.total_score else 'Not graded'
        
        rows += f'''
        <tr>
            <td>{student.username}</td>
            <td>{exam.title}</td>
            <td>{session.start_time.strftime('%Y-%m-%d %H:%M')}</td>
            <td>{status_badge}</td>
            <td>{score}</td>
            <td>
                <a href="/grade-session/{session.id}" class="btn btn-sm btn-primary">Grade</a>
            </td>
        </tr>
        '''
    
    content = f'''
    <h2>Exam Results</h2>
    
    <table class="table table-hover">
        <thead>
            <tr>
                <th>Student</th>
                <th>Exam</th>
                <th>Start Time</th>
                <th>Status</th>
                <th>Score</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {rows if rows else '<tr><td colspan="6">No exam sessions found</td></tr>'}
        </tbody>
    </table>
    
    <a href="/dashboard" class="btn btn-secondary">Back to Dashboard</a>
    '''
    
    return render_page(content, "View Results")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create admin user if doesn't exist
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@example.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Created admin user: admin/admin123")
    
    print("Starting application at http://localhost:5001")
    app.run(debug=True, port=5001)
    
    