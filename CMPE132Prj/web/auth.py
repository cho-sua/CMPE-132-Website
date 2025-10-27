from flask import Blueprint, render_template, request, flash

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("login.html")
"""
@auth.route('/logout')
def logout():
        return "<p>logout</p>"
"""
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
      if request.method == 'POST':
        role = request.form.get('role')
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if role == 'role0':
            flash('Select a role!', category = 'error')
        elif len(email) < 1:
            flash('No email input detected!', category = 'error')
        elif len(firstName) < 1:
            flash('No first name input detected!', category = 'error')
        elif len(lastName) < 1:
            flash('No last name input detected!', category = 'error')
        elif len(password1) < 1:
            flash('No password input detected!', category = 'error')
        elif len(password2) < 1:
            flash('No password confirmation input detected!', category = 'error')
        elif password1 != password2:
            flash('Passwords do not match!', category = 'error')
        else:
            flash('Account created!', category='success')
      return render_template("signup.html")