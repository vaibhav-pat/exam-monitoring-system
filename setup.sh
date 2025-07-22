#!/bin/bash
# setup.sh - Automated setup script for Exam Monitoring System on macOS M2

echo "🚀 Setting up Exam Monitoring System..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check for Homebrew
if ! command_exists brew; then
    print_warning "Homebrew not found. Installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    print_status "Homebrew found"
fi

# Update Homebrew
print_status "Updating Homebrew..."
brew update

# Install system dependencies
print_status "Installing system dependencies..."
brew install python@3.11 postgresql@15 redis cmake pkg-config opencv ffmpeg portaudio node

# Start services
print_status "Starting PostgreSQL and Redis services..."
brew services start postgresql@15
brew services start redis

# Create virtual environment
# print_status "Creating Python virtual environment..."
# python3.11 -m venv venv
# source venv/bin/activate

# Create project structure
# print_status "Creating project structure..."
# mkdir -p app/{static/{css,js,uploads/evidence},templates/{admin,student},models,routes,utils}
# mkdir -p ml_models/{cheating_detection,nlp_grading,weights,yolov5}
# mkdir -p tests
# mkdir -p data/{datasets,logs}
# mkdir -p .vscode

# Create requirements.txt with exact versions
cat > requirements.txt << 'EOF'
# Core dependencies
alembic==1.16.4
amqp==5.3.1
annotated-types==0.7.0
bidict==0.23.1
billiard==4.2.1
blinker==1.9.0
blis==1.3.0
catalogue==2.0.10
celery==5.5.3
certifi==2025.7.14
charset-normalizer==3.4.2
click==8.2.1
click-didyoumean==0.3.1
click-plugins==1.1.1.2
click-repl==0.3.0
cloudpathlib==0.21.1
confection==0.1.5
contourpy==1.3.2
cycler==0.12.1
cymem==2.0.11

# Flask and extensions
Flask==3.0.0
flask-cors==6.0.1
Flask-Login==0.6.3
Flask-Migrate==4.1.0
Flask-SocketIO==5.5.1
Flask-SQLAlchemy==3.1.1
Flask-WTF==1.2.1

# Machine Learning and Data Processing
filelock==3.18.0
fonttools==4.59.0
fsspec==2025.7.0
gitdb==4.0.12
GitPython==3.1.44
h11==0.16.0
idna==3.10
itsdangerous==2.2.0
Jinja2==3.1.6
joblib==1.5.1
kiwisolver==1.4.8
kombu==5.5.4
langcodes==3.5.0
language_data==1.3.0
Mako==1.3.10
marisa-trie==1.2.1
markdown-it-py==3.0.0
MarkupSafe==3.0.2
matplotlib==3.10.3
mdurl==0.1.2
mpmath==1.3.0
murmurhash==1.0.13
networkx==3.5
nltk==3.9.1
numpy==2.2.6
opencv-python==4.12.0.88
packaging==25.0
pandas==2.3.1
pillow==11.3.0
preshed==3.0.10
prompt_toolkit==3.0.51
psutil==7.0.0
psycopg2==2.9.10
py-cpuinfo==9.0.0
pydantic==2.11.7
pydantic_core==2.33.2
Pygments==2.19.2
pyparsing==3.2.3
python-dateutil==2.9.0.post0
python-dotenv==1.1.1
python-engineio==4.12.2
python-socketio==5.13.0
pytz==2025.2
PyYAML==6.0.2
redis==6.2.0
regex==2024.11.6
requests==2.32.4
rich==14.0.0
scipy==1.16.0
seaborn==0.13.2
shellingham==1.5.4
simple-websocket==1.1.0
six==1.17.0
smart_open==7.3.0.post1
smmap==5.0.2
spacy==3.8.7
spacy-legacy==3.0.12
spacy-loggers==1.0.5
SQLAlchemy==2.0.41
srsly==2.5.1
sympy==1.14.0
thinc==8.3.6
thop==0.1.1.post2209072238
torch==2.7.1
torchvision==0.22.1
tqdm==4.67.1
typer==0.16.0
typing_extensions==4.14.1
typing-inspection==0.4.1
tzdata==2025.2
ultralytics==8.3.168
ultralytics-thop==2.0.14
urllib3==2.5.0
vine==5.1.0
wasabi==1.1.3
wcwidth==0.2.13
weasel==0.4.1
Werkzeug==3.1.3
wrapt==1.17.2
wsproto==1.2.0

# Additional ML packages
transformers==4.36.2
sentence-transformers==2.2.2
scikit-learn==1.3.2
librosa==0.10.1
soundfile==0.12.1
PyAudio==0.2.14
mtcnn==0.1.1
dlib==19.24.2

# Testing
pytest==7.4.3
eventlet==0.33.3
EOF

# Install Python packages
print_status "Installing Python packages (this may take a while)..."
pip install --upgrade pip

# Install packages in groups to handle dependencies better
print_status "Installing core packages..."
pip install numpy==2.2.6 scipy==1.16.0 pandas==2.3.1

print_status "Installing Flask and web packages..."
pip install Flask==3.0.0 Flask-SQLAlchemy==3.1.1 Flask-Login==0.6.3 Flask-Migrate==4.1.0 flask-cors==6.0.1 Flask-SocketIO==5.5.1

print_status "Installing ML packages..."
pip install opencv-python==4.12.0.88 torch==2.7.1 torchvision==0.22.1 ultralytics==8.3.168

print_status "Installing NLP packages..."
pip install spacy==3.8.7 nltk==3.9.1 transformers==4.36.2 sentence-transformers==2.2.2

print_status "Installing remaining packages..."
pip install -r requirements.txt

# Download NLTK data
print_status "Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"

# Download spaCy model
print_status "Downloading spaCy language model..."
python -m spacy download en_core_web_sm

# Create PostgreSQL database
print_status "Creating PostgreSQL database..."
createdb exam_monitoring || print_warning "Database may already exist"

# Download pre-trained models
print_status "Downloading pre-trained models..."

# Download dlib face predictor
if [ ! -f "ml_models/weights/shape_predictor_68_face_landmarks.dat" ]; then
    print_status "Downloading dlib face predictor..."
    curl -L -o shape_predictor.bz2 http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
    bunzip2 shape_predictor.bz2
    mv shape_predictor_68_face_landmarks.dat ml_models/weights/
fi

# Clone YOLOv5 (now using ultralytics)
print_status "Setting up YOLO model..."
if [ ! -d "ml_models/yolov5" ]; then
    git clone https://github.com/ultralytics/yolov5.git ml_models/yolov5
fi

# Create .env file
print_status "Creating environment file..."
cat > .env << 'EOF'
SECRET_KEY=your-secret-key-here-$(openssl rand -hex 32)
DATABASE_URL=postgresql://localhost/exam_monitoring
REDIS_URL=redis://localhost:6379
FLASK_ENV=development
FLASK_DEBUG=True
EOF

# Create VS Code settings
print_status "Creating VS Code configuration..."
cat > .vscode/settings.json << 'EOF'
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.terminal.activateEnvironment": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    },
    "editor.formatOnSave": true,
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests"
    ]
}
EOF

cat > .vscode/launch.json << 'EOF'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Flask",
            "type": "python",
            "request": "launch",
            "module": "flask",
            "env": {
                "FLASK_APP": "run.py",
                "FLASK_ENV": "development",
                "FLASK_DEBUG": "1"
            },
            "args": [
                "run",
                "--no-debugger",
                "--no-reload"
            ],
            "jinja": true,
            "justMyCode": true
        }
    ]
}
EOF

# Create empty __init__.py files
# touch app/__init__.py
# touch app/models/__init__.py
# touch app/routes/__init__.py
# touch app/utils/__init__.py
# touch ml_models/__init__.py
# touch ml_models/cheating_detection/__init__.py
# touch ml_models/nlp_grading/__init__.py

# Create static CSS file
cat > app/static/css/style.css << 'EOF'
/* Custom styles for exam monitoring system */
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
}

.monitoring-active {
    border: 3px solid #28a745;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { border-color: #28a745; }
    50% { border-color: #20c997; }
    100% { border-color: #28a745; }
}

.exam-timer {
    font-variant-numeric: tabular-nums;
}

.suspicion-indicator {
    transition: all 0.3s ease;
}

.video-preview {
    transform: scaleX(-1); /* Mirror video */
}
EOF

# Create a sample config.py if not exists
if [ ! -f "config.py" ]; then
    cat > config.py << 'EOF'
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///exam_monitoring.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload folders
    UPLOAD_FOLDER = 'app/static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # ML Model paths
    FACE_DETECTION_MODEL = 'ml_models/weights/face_detection.pkl'
    OBJECT_DETECTION_MODEL = 'ml_models/weights/yolov5s.pt'
    NLP_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
    
    # Monitoring thresholds
    CHEATING_CONFIDENCE_THRESHOLD = 0.7
    ABSENCE_DURATION_THRESHOLD = 10  # seconds
    MULTIPLE_FACES_THRESHOLD = 2
    
    # Redis configuration
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379'
EOF
fi

print_status "Setup complete! 🎉"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Copy the example code files from the artifacts to their respective locations"
echo "3. Initialize the database: flask db init && flask db migrate && flask db upgrade"
echo "4. Run the application: python run.py"
echo ""
print_warning "Important: Remember to update the SECRET_KEY in .env file before deploying to production!"
print_warning "Note: Some packages like dlib might take time to compile on M2. Be patient!"

# Final check
echo ""
echo "Checking installation..."
python -c "import cv2; print('✓ OpenCV installed')" 2>/dev/null || print_error "OpenCV installation failed"
python -c "import torch; print('✓ PyTorch installed')" 2>/dev/null || print_error "PyTorch installation failed"
python -c "import spacy; print('✓ spaCy installed')" 2>/dev/null || print_error "spaCy installation failed"
python -c "import flask; print('✓ Flask installed')" 2>/dev/null || print_error "Flask installation failed"

echo ""
echo "Setup script completed!"