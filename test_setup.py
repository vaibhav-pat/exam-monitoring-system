import os
import sys

print("Testing Exam Monitoring System Setup...")
print("=" * 50)

# Test 1: Python version
print(f"Python version: {sys.version}")

# Test 2: Check directory structure
print("\nChecking directory structure:")
dirs_to_check = [
    'app',
    'app/models',
    'app/routes',
    'app/static',
    'app/templates',
    'ml_models',
    'ml_models/cheating_detection',
    'ml_models/nlp_grading'
]

for dir_path in dirs_to_check:
    exists = os.path.exists(dir_path)
    print(f"  {'✓' if exists else '✗'} {dir_path}")

# Test 3: Try basic imports
print("\nTesting basic imports:")
try:
    import flask
    print("  ✓ Flask")
except ImportError as e:
    print(f"  ✗ Flask: {e}")

try:
    import flask_sqlalchemy
    print("  ✓ Flask-SQLAlchemy")
except ImportError as e:
    print(f"  ✗ Flask-SQLAlchemy: {e}")

try:
    import flask_login
    print("  ✓ Flask-Login")
except ImportError as e:
    print(f"  ✗ Flask-Login: {e}")

# Test 4: Create minimal Flask app
print("\nTesting minimal Flask app:")
try:
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'test-key'
    
    db = SQLAlchemy(app)
    
    # Define a simple model
    class TestModel(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50))
    
    with app.app_context():
        db.create_all()
        print("  ✓ Database creation successful")
        
        # Test insert
        test_record = TestModel(name='test')
        db.session.add(test_record)
        db.session.commit()
        print("  ✓ Database insert successful")
        
        # Clean up
        os.remove('test.db')
        
except Exception as e:
    print(f"  ✗ Flask app test failed: {e}")

print("\n" + "=" * 50)
print("Setup test complete!")