from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Profile, MacroEntry, ExercisePlan, Exercise
from .extensions import db
from .forms import ProfileForm, MacroTrackingForm
from .macro_service import GoalSettingService
from datetime import datetime, date

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
    if user_profile and user_profile.goal_type:
        exercises = Exercise.query.filter_by(goal_type=user_profile.goal_type).all()
        print("Exercises fetched:", exercises)  # Debug print
    else:
        exercises = []
        print("No goal_type found, fetching all exercises as fallback.")
    return render_template('ExercisePlan.html', exercises=exercises)

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