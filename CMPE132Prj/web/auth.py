from flask import Blueprint, render_template, request, flash, redirect, url_for, session
import json, os, random, string
from .hashing import hashFun, verify

auth = Blueprint('auth', __name__)
accFile = os.path.join(os.path.dirname(__file__), 'data', 'accounts.json')
waitFile = os.path.join(os.path.dirname(__file__), 'data', 'waitlist.json')

def ranCodeGen(length = 6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k= length))
def loadAcc():
    if not os.path.exists(accFile):
        with open(accFile, 'w') as f:
            json.dump([], f)
    with open(accFile, 'r') as f:
        return json.load(f)

def saveAcc(accounts):
    with open(accFile, 'w') as f:
        json.dump(accounts, f, indent = 4)

def loadWait():
    if not os.path.exists(waitFile):
        with open(waitFile, 'w') as f:
            json.dump([], f)
    with open(waitFile, 'r') as f:
        return json.load(f)

def saveWait(info):
    with open(waitFile, 'w') as f:
        json.dump(info, f, indent = 4)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')
        id = request.form.get('id')
        email = request.form.get('email')
        password = request.form.get('password')
        code = request.form.get('code')
       
        if role == 'role0':
            flash('Select a role!', category = 'error')
        elif len(email) < 1:
            flash('No email input detected!', category = 'error')
        elif len(password) < 1:
            flash('No passowrd input detected!', category = 'error')
        else:
            accounts = loadAcc()
            role_map = {
                'role1': 'Student',
                'role2': 'Instructor',
                'role3': 'Librarian',
                'role4': 'Head Librarian',
                'role5': 'IT Support'
            }
            role_str = role_map.get(role, 'Unknown')
            for acc in accounts:
                if acc['email'] == email and acc['role'] == role_str and acc['id'] == id and acc['code'] == code:
                        if(verify(acc['salt'], acc['password'], password)):
                            session['email'] = acc['email']
                            session['role'] = acc['role']
                            session['id'] = acc['id']
                            session['firstName'] = acc['firstName']
                            session['lastName'] = acc['lastName']
                            flash(f'Login Successful! Welcome back, {acc["firstName"]}!', category = 'success')
                            return redirect(url_for("views.loginHome"))
                        else:
                            flash('Inccorect password!', category = 'error')
                            break
            flash('No account was found!', category = 'error')
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
        id = request.form.get('id')
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
            account = loadAcc()
            list = loadWait()
            if any(acc['email'] == email and acc['role'] == role for acc in account):
                flash('Account already registered with email', category='error')
            elif  any(acc['email'] == email and acc['role'] == role for acc in list):
                flash('Account waiting to be approved!', category = 'success')
            else:   
                role_map = {
                    'role1': 'Student',
                    'role2': 'Instructor',
                    'role3': 'Librarian',
                    'role4': 'Head Librarian',
                    'role5': 'IT Support'
                }

                hash, salt = hashFun(password1)

                code = ranCodeGen()
                newAccount = {
                    'role': role_map.get(role, 'Unknown'),
                    'email': email,
                    'firstName': firstName,
                    'lastName': lastName,
                    'id': id,
                    'salt': salt,
                    'password': hash,
                    'code': code
                }

                list.append(newAccount)
                saveWait(list)

                flash('Account is now being processed!', category='success')
                return redirect(url_for('auth.login'))
      return render_template("signup.html")

@auth.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('role', None)
    session.pop('id', None)
    flash('User logged out! ', category = 'success')
    return redirect(url_for("views.home"))