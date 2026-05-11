"""Run the Flask application."""
import os
import sys
from app import create_app, db

app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    # Check if 'reset_db' was passed as a command-line argument
    if "reset_db" in sys.argv:
        with app.app_context():
            print("Dropping existing database tables...")
            db.drop_all()
            print("Creating new database tables...")
            db.create_all()
            print("Database reset successfully!")
    else:
        app.run(host='0.0.0.0', port=5000, debug=True)
