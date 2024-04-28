from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, NumberRange, Length

class MacroTrackingForm(FlaskForm):
    # Form for tracking daily macronutrients intake
    calories = FloatField('Calories', validators=[
        DataRequired(message="Calories are required."),  # Ensures input is provided
        NumberRange(min=0, message="Calories must be greater than or equal to 0.")  # Validates that values are not negative
    ])
    protein = FloatField('Protein (g)', validators=[
        DataRequired(message="Protein is required."),
        NumberRange(min=0, message="Protein must be greater than or equal to 0.")
    ])
    carbohydrates = FloatField('Carbohydrates (g)', validators=[
        DataRequired(message="Carbohydrates are required."),
        NumberRange(min=0, message="Carbohydrates must be greater than or equal to 0.")
    ])
    fats = FloatField('Fats (g)', validators=[
        DataRequired(message="Fats are required."),
        NumberRange(min=0, message="Fats must be greater than or equal to 0.")
    ])
    submit = SubmitField('Track')  # Button to submit form data

class ProfileForm(FlaskForm):
    # Form for user profile setup and updates
    name = StringField('Name', validators=[DataRequired(message="Name is required.")])
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female')], validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired(message="Age is required."), NumberRange(min=0, message="Age must be a positive number.")])
    height_feet = IntegerField('Height (Feet)', validators=[DataRequired(message="Height in feet is required."), NumberRange(min=0, message="Height in feet must be a positive number.")])
    height_inches = IntegerField('Height (Inches)', validators=[DataRequired(message="Height in inches is required."), NumberRange(min=0, max=11, message="Height in inches must be between 0 and 11.")])
    weight_pounds = FloatField('Weight (Pounds)', validators=[DataRequired(message="Weight in pounds is required."), NumberRange(min=0, message="Weight must be a positive number.")])
    activity_level = SelectField('Activity Level', choices=[('sedentary', 'Sedentary'), ('lightly_active', 'Lightly Active'), ('moderately_active', 'Moderately Active'), ('very_active', 'Very Active'), ('extra_active', 'Extra Active')], validators=[DataRequired()])
    goal_type = SelectField('Goal Type', choices=[('lose_weight', 'Lose Weight'), ('maintain_weight', 'Maintain Weight'), ('gain_muscle', 'Gain Muscle')], validators=[DataRequired()])
    goal_time_frame = SelectField('Goal Time Frame', choices=[('1_week', '1 Week'), ('1_month', '1 Month'), ('1_year', '1 Year')], validators=[DataRequired(message="Goal Time Frame is required.")])  # New field
    submit = SubmitField('Save Profile')  # Button to submit form data

def get_exercises_for_goal(goal_type):
    # Retrieve exercise suggestions based on user's goal type
    exercises = {
        'Lose Weight': ['Running', 'Cycling', 'Swimming'],
        'Maintain Weight': ['Yoga', 'Pilates', 'Light Jogging'],
        'Gain Muscle': ['Weightlifting', 'Bodybuilding', 'Resistance Training']
    }
    return exercises.get(goal_type, [])  # Returns a list of exercises or empty if goal_type is not defined
