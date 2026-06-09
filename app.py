import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Database Configuration: Use Postgres on Vercel, SQLite on local PC
database_url = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL', 'sqlite:///database.db')
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Ensure database tables are created automatically (crucial for Vercel)
with app.app_context():
    db.create_all()

# Database Schema Model for Lead/User Entries
class UserSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.email}>'

# Main Route to Render Your Massive Luxury Homepage
@app.route('/')
def home():
    return render_template('index.html')

# Backend API Endpoint to Receive and Store JavaScript Form Submissions
@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request payload"}), 400
            
        email = data.get('email', '').strip()

        if not email:
            return jsonify({"error": "Email address is required."}), 400

        # Check if the email already exists in your SQLite database
        existing_user = UserSubmission.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"message": "You have already joined our exclusive list!"}), 200

        # Save the new user record entry
        new_submission = UserSubmission(email=email)
        db.session.add(new_submission)
        db.session.commit()

        return jsonify({"message": "Welcome to the inner circle. Registration successful."}), 201

    except Exception as e:
        print(f"Server Error: {str(e)}")
        return jsonify({"error": "Internal server issue. Please try again later."}), 500

if __name__ == '__main__':
    app.run(debug=True)