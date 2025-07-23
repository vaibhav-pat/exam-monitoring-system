from app import create_app, socketio, db
from app.models.user import User

# Create the application instance using the factory from app/__init__.py
app = create_app()

def setup_database(current_app):
    """
    Function to create database tables and a default admin user.
    This should be done via `flask db upgrade` in production,
    but is useful for quick development starts.
    """
    with current_app.app_context():
        # The recommended way is to use Flask-Migrate from the command line.
        # However, for a simple run script, we can call db.create_all().
        # Make sure your database is deleted if you change models.
        db.create_all()
        
        # Check for and create admin user
        if not User.query.filter_by(username='admin').first():
            print("Creating default admin user...")
            admin = User(username='admin', email='admin@example.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created (admin/admin123).")

if __name__ == '__main__':
    # Setup the database within the application context
    setup_database(app)

    # Run the app with SocketIO support
    print("Starting Exam Monitoring System...")
    print("Access at: http://localhost:5001")
    socketio.run(app, debug=True, port=5001)