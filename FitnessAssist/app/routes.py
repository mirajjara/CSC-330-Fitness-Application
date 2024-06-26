from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import Profile, MacroEntry, ExercisePlan, Exercise, Challenge
from .extensions import db
from .forms import ProfileForm, MacroTrackingForm
from .macro_service import GoalSettingService
from datetime import datetime, date, timedelta
import random

# Create a Blueprint for the main section of the application.
main = Blueprint('main', __name__)

@main.route('/')
@login_required
def home():
    """Home page route showing user's profile and planned exercises."""
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    exercise_plans = ExercisePlan.query.filter_by(user_id=current_user.id).all()

    # Translate exercise plan IDs to descriptive names, if available.
    for plan in exercise_plans:
        descriptive_exercise = Exercise.query.filter_by(id=plan.exercise).first()
        if descriptive_exercise:
            plan.exercise = descriptive_exercise.name
        else:
            plan.exercise = "Unknown Exercise"  # Fallback if no matching exercise found

    return render_template('home.html', profile=profile, exercise_plans=exercise_plans)

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management route to view and update personal information."""
    user_profile = Profile.query.filter_by(user_id=current_user.id).first() or Profile(user_id=current_user.id)
    form = ProfileForm(obj=user_profile)  # Populate form with user_profile data

    if form.validate_on_submit():
        form.populate_obj(user_profile)  # Populate user_profile with form data
        db.session.add(user_profile)  # Add new or update existing profile
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.profile'))

    return render_template('profile.html', form=form)

@main.route('/ExercisePlan', methods=['GET', 'POST'])
@login_required
def exercise_plan():
    """Manage and view exercise plans based on user's fitness goal."""
    user_profile = Profile.query.filter_by(user_id=current_user.id).first()
    exercises, goal_type, goal_time_frame = [], None, None
    
    if user_profile:
        exercises = Exercise.query.filter_by(goal_type=user_profile.goal_type).all()
        goal_type = user_profile.goal_type
        goal_time_frame = user_profile.goal_time_frame  # Ensure that goal_time_frame is part of your Profile model
        print("Exercises fetched:", exercises)  # Debug print
    else:
        print("No goal_type found, fetching all exercises as fallback.")

    return render_template('ExercisePlan.html', exercises=exercises, goal_type=goal_type, goal_time_frame=goal_time_frame)


@main.route('/save_exercise_plan', methods=['POST'])
@login_required
def save_exercise_plan():
    """Save a new or updated exercise plan for the user."""
    # Extract form data
    exercise = request.form.get('exercise')
    duration = request.form.get('duration')
    date_str = request.form.get('date')

    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

    # Create and save the exercise plan
    new_exercise_plan = ExercisePlan(
        user_id=current_user.id,
        exercise=exercise,
        duration=int(duration),
        date=date_obj
    )
    db.session.add(new_exercise_plan)
    try:
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        flash('Error saving exercise plan: ' + str(e))

    return redirect(url_for('main.exercise_plan'))

@main.route('/macros', methods=['GET', 'POST'])
@login_required
def macros():
    """Track and manage user's daily macronutrient intake."""
    form = MacroTrackingForm()
    if form.validate_on_submit():
        # Create a new MacroEntry from form data
        new_entry = MacroEntry(
            user_id=current_user.id,
            date=date.today(),
            calories=form.calories.data,
            protein=form.protein.data,
            carbohydrates=form.carbohydrates.data,
            fats=form.fats.data,
        )
        db.session.add(new_entry)
        db.session.commit()
        flash('Your macro and calorie intake have been recorded!', 'success')
        return redirect(url_for('main.macros'))
        
    # Retrieve the user's profile to calculate recommended intake
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if profile:
        recommended_intake = GoalSettingService.suggest_macro_nutrient_targets(profile)
        recommended_calories = recommended_intake.get('calories', 0)
        recommended_macros = {
            'protein': recommended_intake.get('protein', 0),
            'carbohydrates': recommended_intake.get('carbohydrates', 0),
            'fats': recommended_intake.get('fats', 0)
        }
    else:
        recommended_calories = 0
        recommended_macros = {'protein': 0, 'carbohydrates': 0, 'fats': 0}

    # Aggregate daily totals from MacroEntry records
    today_entries = MacroEntry.query.filter_by(user_id=current_user.id, date=date.today()).all()
    daily_totals = {
        'calories': sum(entry.calories for entry in today_entries if entry.calories is not None),
        'protein': sum(entry.protein for entry in today_entries if entry.protein is not None),
        'carbohydrates': sum(entry.carbohydrates for entry in today_entries if entry.carbohydrates is not None),
        'fats': sum(entry.fats for entry in today_entries if entry.fats is not None),
    }
    return render_template('macros.html', form=form, daily_totals=daily_totals, recommended_calories=recommended_calories, recommended_macros=recommended_macros)

@main.route('/reset_macros')
@login_required
def reset_macros():
    """Reset user's daily macro intake records."""
    MacroEntry.query.filter_by(user_id=current_user.id, date=date.today()).delete()
    db.session.commit()
    flash('Today\'s intake has been reset.', 'success')
    return redirect(url_for('main.macros'))

@main.route('/generate-schedule', methods=['POST'])
@login_required
def generate_schedule():
    try:
        if not request.is_json:
            return jsonify({'success': False, 'message': 'Request must be in JSON format'}), 400

        data = request.get_json()
        exercise = data.get('exercise')
        goal_time_frame = data.get('goalTimeFrame')
        default_duration = 30  # Assuming a default duration of 30 minutes for all exercises

        if not exercise or not goal_time_frame:
            return jsonify({'success': False, 'message': 'Exercise and goal time frame are required'}), 400

        def schedule_dates(start_date, time_frame):
            if time_frame == '1_week':
                return [start_date + timedelta(days=i) for i in range(7)]
            elif time_frame == '1_month':
                return [start_date + timedelta(days=i*7) for i in range(4)]
            elif time_frame == '1_year':
                return [start_date + timedelta(days=i*30) for i in range(12)]
            else:
                return [start_date]

        start_date = date.today()
        dates = schedule_dates(start_date, goal_time_frame)

        for schedule_date in dates:
            new_plan = ExercisePlan(
                user_id=current_user.id, 
                exercise=exercise, 
                duration=default_duration,  # Apply the default duration here
                date=schedule_date
            )
            db.session.add(new_plan)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Schedule created successfully!'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500



@main.route('/save_scheduled_exercise_plan', methods=['POST'])
@login_required
def save_scheduled_exercise_plan():
    """Save multiple exercise plans based on user's goal time frame."""
    exercise_id = request.form.get('scheduled_exercise')
    duration = int(request.form.get('scheduled_duration'))
    start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()

    # Fetch user's goal time frame from the profile
    user_profile = Profile.query.filter_by(user_id=current_user.id).first()
    if user_profile:
        time_frame = user_profile.goal_time_frame
        dates = schedule_dates(start_date, time_frame)
        for date in dates:
            try:
                new_exercise_plan = ExercisePlan(
                    user_id=current_user.id,
                    exercise=exercise_id,
                    duration=duration,
                    date=date
                )
                db.session.add(new_exercise_plan)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                flash('Error saving scheduled exercise plans: ' + str(e), 'error')
                print('Rollback due to:', e)  # Debug print
    else:
        flash('No user profile found, cannot schedule exercises.', 'error')

    return redirect(url_for('main.exercise_plan'))

def schedule_dates(start_date, time_frame):
    """Generate a list of dates for the scheduled exercises based on the time frame."""
    if time_frame == '1_week':
        return [start_date + timedelta(days=i) for i in range(7)]
    elif time_frame == '1_month':
        return [start_date + timedelta(days=i*7) for i in range(4)]
    elif time_frame == '1_year':
        return [start_date + timedelta(days=i*30) for i in range(12)]
    else:
        return [start_date]  # Fallback to single date if no time frame matches

# Define the list of challenges
challenges = [
            {'name': 'Push Ups I', 'description': 'Get those arms ready for a superhero pose! Complete 10 push ups in one set', 'difficulty': 'Easy'},
            {'name': 'Push Ups II', 'description': 'Time to level up! Complete 20 push ups in two sets of 10 and show off those guns', 'difficulty': 'Medium'},
            {'name': 'Push Ups III', 'description': 'The ultimate push up challenge! Complete 30 push ups in three sets of 10 and earn your superhero cape', 'difficulty': 'Hard'},
            {'name': 'One Mile Run', 'description': 'Ready, set, go! Run one mile without stopping and feel the rush of endorphins', 'difficulty': 'Easy'},
            {'name': 'Two Mile Run', 'description': 'You\'ve got this! Run two miles without stopping and show off your endurance skills', 'difficulty': 'Medium'},
            {'name': 'Three Mile Run', 'description': 'The ultimate test of endurance! Run three miles without stopping and earn your marathon badge', 'difficulty': 'Hard'},
            {'name': 'Sit Ups I', 'description': 'Get ready to crunch! Complete 15 sit ups in one set and strengthen that core', 'difficulty': 'Easy'},
            {'name': 'Sit Ups II', 'description': 'Time to step it up! Complete 30 sit ups in two sets of 15 and show off your six pack', 'difficulty': 'Medium'},
            {'name': 'Sit Ups III', 'description': 'The ultimate core challenge! Complete 45 sit ups in three sets of 15 and earn your superhero abs', 'difficulty': 'Hard'},
            {'name': 'Cycling I', 'description': 'Pedal to the metal! Cycle for 10 minutes without stopping and feel the wind in your hair', 'difficulty': 'Easy'},
            {'name': 'Cycling II', 'description': 'You\'re on a roll! Cycle for 20 minutes without stopping and show off your cycling skills', 'difficulty': 'Medium'},
            {'name': 'Cycling III', 'description': 'The ultimate cycling challenge! Cycle for 30 minutes without stopping and earn your cycling badge', 'difficulty': 'Hard'},
        ]

daily_challenge_cache = {}

def generate_challenge():
    # Select a random challenge from the list
    random_challenge = random.choice(challenges)
    return random_challenge

@main.route('/daily_fitness_challenge')
def daily_fitness_challenge():
    # Get the current date and time
    now = datetime.now()
    today = now.date()

    # Check if the challenge for today is already cached and hasn't expired
    if today not in daily_challenge_cache or daily_challenge_cache[today]['expires'] < now:
        # If not, generate a new challenge and cache it
        challenge = generate_challenge()
        expires = now.replace(hour=23, minute=59, second=59)  # set expires time to 11:59:59 PM
        daily_challenge_cache[today] = {'challenge': challenge, 'expires': expires, 'completed': False}
    else:
        # If it is, retrieve it from the cache
        challenge = daily_challenge_cache[today]['challenge']
        if daily_challenge_cache[today]['completed']:
            return render_template('already_completed.html')  # Render a template indicating that the challenge has already been completed

    # Render the template with the challenge
    return render_template('daily_fitness_challenge.html', challenge=challenge)

@main.route('/complete_challenge', methods=['POST'])
def complete_challenge():
    today = datetime.today()
    if daily_challenge_cache[today]['completed']:
        return "Challenge already completed!"
    else:
        daily_challenge_cache[today]['completed'] = True
        return "Challenge completed successfully!"