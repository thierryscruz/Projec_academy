from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Campos do perfil
    name = db.Column(db.String(100), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    height = db.Column(db.Float, nullable=True)  # em cm
    weight = db.Column(db.Float, nullable=True)  # em kg
    experience = db.Column(db.String(100), nullable=True)
    frequency = db.Column(db.String(50), nullable=True)
    duration = db.Column(db.String(50), nullable=True)
    goal = db.Column(db.String(100), nullable=True)
    
    # Relacionamento com histórico de treinos
    workout_history = db.relationship('WorkoutHistory', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'height': self.height,
            'weight': self.weight,
            'experience': self.experience,
            'frequency': self.frequency,
            'duration': self.duration,
            'goal': self.goal,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class WorkoutHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    workout_id = db.Column(db.String(10), nullable=False)  # A, B, C
    workout_name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(10), nullable=False)
    exercises_data = db.Column(db.Text, nullable=False)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_exercises_data(self, exercises_list):
        self.exercises_data = json.dumps(exercises_list)

    def get_exercises_data(self):
        return json.loads(self.exercises_data) if self.exercises_data else []

    def to_dict(self):
        return {
            'id': self.id,
            'workout_id': self.workout_id,
            'workout_name': self.workout_name,
            'date': self.date.isoformat(),
            'time': self.time,
            'exercises': self.get_exercises_data(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

