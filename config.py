import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-this'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///exam_monitoring.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload folders
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app/static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # ML Model paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FACE_DETECTION_MODEL = os.path.join(BASE_DIR, 'ml_models/weights/face_detection.pkl')
    OBJECT_DETECTION_MODEL = os.path.join(BASE_DIR, 'ml_models/weights/yolov5s.pt')
    NLP_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
    
    # Monitoring thresholds
    CHEATING_CONFIDENCE_THRESHOLD = 0.7
    ABSENCE_DURATION_THRESHOLD = 10  # seconds
    MULTIPLE_FACES_THRESHOLD = 2
    
    # Redis configuration
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379'
    
    # Celery configuration
    CELERY_BROKER_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379'
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL') or 'redis://localhost:6379'

