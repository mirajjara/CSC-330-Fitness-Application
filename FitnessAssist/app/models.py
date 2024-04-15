from .extensions import db
from flask_login import UserMixin
from datetime import datetime, date
import enum

class User(UserMixin, db.Model):
    """
    Represents an authenticated user with login capabilities.
    Stores basic user authentication and goal preferences.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    goal_type = db.Column(db.String(50), nullable=True)
 
class Profile(db.Model):
    """
    User profile information linked to a User.
    Stores personal details like name, gender, physical attributes, and activity level.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100))
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    height_feet = db.Column(db.Integer)
    height_inches = db.Column(db.Integer)
    weight_pounds = db.Column(db.Float)
    activity_level = db.Column(db.String(20))
    goal_type = db.Column(db.String(20))

    user = db.relationship('User', backref=db.backref('profile', uselist=False))

class Macros(db.Model):
    """
    Stores macronutrient for a user.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    protein = db.Column(db.Float)
    carbohydrates = db.Column(db.Float)
    fats = db.Column(db.Float)
    calories = db.Column(db.Integer)

class MacroEntry(db.Model):
    """
    Records specific macro entries per user on given dates.
    Ensures tracking of nutritional intake over time.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.Date, nullable=False, default=date.today)
    protein = db.Column(db.Float, nullable=False)
    carbohydrates = db.Column(db.Float, nullable=False)
    fats = db.Column(db.Float, nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    user = db.relationship('User', backref='macro_entries')

class ExercisePlan(db.Model):
    """
    Manages exercise plans for users.
    Each plan includes the type of exercise, duration, and the date planned.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    exercise = db.Column(db.String(255), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in minutes
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('ExercisePlan', lazy=True))


    def __repr__(self):
        return f'<ExercisePlan {self.exercise}>'
    
class Exercise(db.Model):
    """
    Stores predefined exercises associated with specific fitness goals.
    Allows users to select exercises based on their current fitness objectives.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    goal_type = db.Column(db.String(50))  # Relates to UserProfile.goal_type

    @staticmethod
    def get_exercises_by_goal(goal_type):
        return Exercise.query.filter_by(goal_type=goal_type).all()