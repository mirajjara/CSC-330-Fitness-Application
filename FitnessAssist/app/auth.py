from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from .models import User
from . import db

# Create a Blueprint named 'auth'
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Handle the login process
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False  # Remember user session

        user = User.query.filter_by(username=username).first()  # Query database for user

        # Check if user exists and password is correct
        if user and check_password_hash(user.password, password):
            login_user(user, remember=remember)  # Log in the user and set session
            return redirect(url_for('main.home'))  # Redirect to the home page after login
        else:
            # Flash error message if login fails
            flash('Login unsuccessful. Please check username and password and try again.')
    
    # Render the login template if GET request or login fails
    return render_template('login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    # Handle the signup process
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        user = User.query.filter_by(username=username).first()  # Check if username already exists

        if user:
            # Flash error if username is taken
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('auth.signup'))

        if password != confirm_password:
            # Flash error if passwords do not match
            flash('Passwords do not match. Please try again.')
            return redirect(url_for('auth.signup'))

        # Create new user with hashed password
        new_user = User(username=username, password=generate_password_hash(password))
        db.session.add(new_user)  # Add new user to database
        db.session.commit()  # Commit changes to database

        # Flash success message and redirect to login page
        flash('Registration successful. You can now login.')
        return redirect(url_for('auth.login'))

    # Render the registration template if GET request or registration fails
    return render_template('register.html')

@auth.route('/logout')
@login_required
def logout():
    # Log out the current user
    logout_user()
    # Redirect to the login page after logging out
    return redirect(url_for('auth.login'))
