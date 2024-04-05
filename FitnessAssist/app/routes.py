from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Profile
from .extensions import db

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def home():
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    return render_template('home.html', profile=profile)

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if profile:
        if request.method == 'POST':
            # Update profile with form data
            profile.name = request.form['name']
            profile.gender = request.form['gender']
            profile.age = int(request.form['age'])
            profile.height = float(request.form['height'])
            profile.weight = float(request.form['weight'])
            profile.activity_level = request.form['activity_level']
            profile.goal_type = request.form['goal_type']
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('main.profile'))
    else:
        if request.method == 'POST':
            # Create new profile with form data
            name = request.form['name']
            gender = request.form['gender']
            age = int(request.form['age'])
            height = float(request.form['height'])
            weight = float(request.form['weight'])
            activity_level = request.form['activity_level']
            goal_type = request.form['goal_type']
            new_profile = Profile(
                user_id=current_user.id,
                name=name,
                gender=gender,
                age=age,
                height=height,
                weight=weight,
                activity_level=activity_level,
                goal_type=goal_type
            )
            db.session.add(new_profile)
            db.session.commit()
            flash('Profile created successfully!', 'success')
            return redirect(url_for('main.profile'))
    return render_template('profile.html', profile=profile)
