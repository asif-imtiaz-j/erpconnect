from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from app.models import User
from app.forms import LoginForm
from app import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash(f"Welcome {user.username}!", 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

from werkzeug.security import generate_password_hash

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = LoginForm()  # Or use a separate RegisterForm if you later add fields
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash("Username already exists", "danger")
            return redirect(url_for('auth.register'))

        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password, role='viewer')
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! You can now log in.", "success")
        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)

