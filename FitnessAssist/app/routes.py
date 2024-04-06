from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Profile, MacroEntry
from .extensions import db
from .forms import ProfileForm, MacroTrackingForm
from .macro_service import GoalSettingService
from datetime import datetime, date


main = Blueprint('main', __name__)

@main.route('/')
@login_required
def home():
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    return render_template('home.html', profile=profile)

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # Retrieve the current user's profile or initialize a new one
    user_profile = Profile.query.filter_by(user_id=current_user.id).first() or Profile(user_id=current_user.id)
    form = ProfileForm(obj=user_profile)  # Populate form with user_profile data

    if form.validate_on_submit():
        form.populate_obj(user_profile)  # Populate user_profile with form data
        db.session.add(user_profile)  # Add new or update existing profile
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.profile'))

    return render_template('profile.html', form=form)

@main.route('/macros', methods=['GET', 'POST'])
@login_required
def macros():
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
        'calories': sum(entry.calories for entry in today_entries),
        'protein': sum(entry.protein for entry in today_entries),
        'carbohydrates': sum(entry.carbohydrates for entry in today_entries),
        'fats': sum(entry.fats for entry in today_entries),
    }

    return render_template('macros.html', form=form, daily_totals=daily_totals, recommended_calories=recommended_calories, recommended_macros=recommended_macros)

@main.route('/reset_macros')
@login_required
def reset_macros():
    MacroEntry.query.filter_by(user_id=current_user.id, date=date.today()).delete()
    db.session.commit()
    flash('Today\'s intake has been reset.', 'success')
    return redirect(url_for('main.macros'))