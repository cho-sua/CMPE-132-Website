from flask import Blueprint, render_template, request, flash, redirect, url_for, session
import json, os
from datetime import datetime
    
views = Blueprint('views', __name__)

bFile = os.path.join(os.path.dirname(__file__), 'data', 'books.json')
borrowedFile = os.path.join(os.path.dirname(__file__), 'data', 'borrowed.json')
restrictedFile = os.path.join(os.path.dirname(__file__), 'data', 'restricted.json')
accFile = os.path.join(os.path.dirname(__file__), 'data', 'accounts.json')
log = os.path.join(os.path.dirname(__file__), 'data', 'log.json')
waitFile = os.path.join(os.path.dirname(__file__), 'data', 'waitlist.json')

def loadWait():
    if not os.path.exists(waitFile):
        with open(waitFile, 'w') as f:
            json.dump([], f)
    with open(waitFile, 'r') as f:
        return json.load(f)

def saveWait(info):
    with open(waitFile, 'w') as f:
        json.dump(info, f, indent = 4)

def loadLog():
    if not os.path.exists(log):
        with open(log, "w") as f:
            json.dump([], f)

    with open(log, "r") as f:
        try:
            data = json.load(f)
            if not isinstance(data, list):
                data = []
        except json.JSONDecodeError:
            data = []
    return data

def addLog(info):
    data = loadLog()
    data.append(info)
    with open(log, 'w') as f:
        json.dump(data, f, indent = 4)

def loadBooks():
    if not os.path.exists(bFile):
        with open(bFile, 'w') as f:
            json.dump([], f)
    with open(bFile, 'r') as f:
        return json.load(f)

def saveBooks(info):
    with open(bFile, 'w') as f:
        json.dump(info, f, indent = 4)

def loadBorrowed():
    if not os.path.exists(borrowedFile):
        with open(borrowedFile, 'w') as f:
            json.dump([], f)
    with open(borrowedFile, 'r') as f:
        return json.load(f)

def saveBorrowed(info):
    with open(borrowedFile, 'w') as f:
        json.dump(info, f, indent = 4)

def loadRestrictions():
    if not os.path.exists(restrictedFile):
        with open(restrictedFile, 'w') as f:
            json.dump([], f)
    with open(restrictedFile, 'r') as f:
        return json.load(f)

def saveRestrictions(info):
    with open(restrictedFile, 'w') as f:
        json.dump(info, f, indent = 4 )


def loadAcc():
    if not os.path.exists(accFile):
        with open(accFile, 'w') as f:
            json.dump([], f)
    with open(accFile, 'r') as f:
        return json.load(f)

def saveAcc(accounts):
    with open(accFile, 'w') as f:
        json.dump(accounts, f, indent = 4)

@views.route('/')
def home():
    return render_template("home.html")

@views.route('/loginHome')
def loginHome():
    role = session.get('role')
    if not role:
        return redirect(url_for('auth.login'))
    
    role_pages = {'Student': 'student.html', 'Instructor': 'instructor.html', 'Librarian': 'librarian.html', 'Head Librarian': 'headLibrarian.html', 'IT Support': 'it.html'}
    if role == 'Librarian':
        books = loadBooks()
        return redirect(url_for('views.librarianHome', role = session.get('role'), books = books))
    
    if role == 'Head Librarian':
        books = loadBooks()
        waitlist = loadWait()
        return render_template('headLibrarian.html', role=session.get('role'), books = books, waitlist = waitlist)
    
    if role == 'Student':
        return redirect(url_for('views.studentHome'))
    
    if role == 'IT Support':
        return redirect(url_for('views.itHome'))
    
    if role == 'Instructor':
        return redirect(url_for('views.instructorHome'))
    
    template = role_pages.get(role, 'home.html')
    return render_template(template, role=role)

@views.route('/student')
def studentHome():
    if session.get('role') != 'Student':
        flash('Access denied.', category = 'error')
        return redirect(url_for('views.loginHome'))

    userID = session.get('id')
    books = loadBooks()
    borrowed = loadBorrowed()

    availableBooks = [b for b in books if b['copies'] > 0]
    myBooks = [b for b in borrowed if b['userID'] == userID]

    return render_template('student.html', availableBooks=availableBooks, myBooks=myBooks)

@views.route('/librarian')
def librarianHome():
    if session.get('role') != 'Librarian':
        flash('Access denied.', category = 'error')
        return redirect(url_for('views.loginHome'))

    books = loadBooks()
    return render_template('librarian.html', role=session.get('role'), books=books)

@views.route('/head_librarian')
def hLibrarianHome():
    if session.get('role') != 'Head Librarian':
        flash('Access denied.', category = 'error')
        return redirect(url_for('views.loginHome'))

    books = loadBooks()
    return render_template('headLibrarian.html', role=session.get('role'), books=books)

@views.route('/it')
def itHome():
    if session.get('role') != 'IT Support':
        flash('Access denied.', category = 'error')
        return redirect(url_for('views.loginHome'))

    books = loadBooks()
    waitlist = loadWait()
    return render_template('it.html', role=session.get('role'), books = books, waitlist = waitlist)

@views.route('/instructor')
def instructorHome():
    if session.get('role') != 'Instructor':
        flash('Access denied.', category = 'error')
        return redirect(url_for('views.loginHome'))

    userID = session.get('id')
    books = loadBooks()
    borrowed = loadBorrowed()

    availableBooks = [b for b in books if b['copies'] > 0]
    myBooks = [b for b in borrowed if b['userID'] == userID]
    return render_template('instructor.html', role=session.get('role'), availableBooks = availableBooks, myBooks = myBooks)

@views.route('/borrow/<isbn>')
def borrowBook(isbn):
    if session.get('role') != 'Student' and session.get('role' != 'Instructor'):
        flash('Access denied.', category = 'error')
        return redirect(url_for('views.loginHome'))

    userID = session.get('id')
    books = loadBooks()
    borrowed = loadBorrowed()

    book = next((b for b in books if b['isbn'] == isbn), None)
    if not book or book['copies'] <= 0:
        flash('Book unavailable.', category = 'error')
        return redirect(url_for('views.loginHome'))

    info = {
        "time": datetime.now().strftime("%H:%M:%S"), "date": datetime.now().strftime("%Y-%m-%d"),
        "userID": session.get('id'),
        "firstName": session.get('firstName'),
        "lastName": session.get('lastName'),
        "email": session.get('email'),
        "role": session.get('role'),
        "message": f"User borrowed book with isbn: {isbn}"
    }
    addLog(info)
    book['copies'] -= 1
    borrowed.append({'userID': userID, 'isbn': isbn, 'title': book['title']})

    saveBooks(books)
    saveBorrowed(borrowed)

    flash(f'You borrowed "{book["title"]}".', category = 'success')
    return redirect(url_for('views.loginHome'))

@views.route('/return/<isbn>')
def returnBook(isbn):
    if session.get('role') != 'Student' and session.get('role' != 'Instructor'):
        flash('Access denied.', category = 'error')
        return redirect(url_for('views.loginHome'))

    userID = session.get('id')
    books = loadBooks()
    borrowed = loadBorrowed()

    for i, b in enumerate(borrowed):
        if b['isbn'] == isbn and b['userID'] == userID:
            borrowedEntry = borrowed.pop(i)
            break
    else:
        flash('This book is not in your borrowed list.', category = 'error')
        return redirect(url_for('views.loginHome'))

    book = next((b for b in books if b['isbn'] == isbn), None)
    if book:
        book['copies'] += 1

    info = {
        "time": datetime.now().strftime("%H:%M:%S"), "date": datetime.now().strftime("%Y-%m-%d"),
        "userID": session.get('id'),
        "firstName": session.get('firstName'),
        "lastName": session.get('lastName'),
        "email": session.get('email'),
        "role": session.get('role'),
        "message": f"User returned book with isbn: {isbn}"
    }
    addLog(info)
    saveBooks(books)
    saveBorrowed(borrowed)

    flash(f'You returned "{borrowedEntry["title"]}".', category = 'success')
    return redirect(url_for('views.loginHome'))

@views.route('/add_book', methods=['GET', 'POST'])
def addBook():
    if session.get('role') != 'Librarian' and session.get('role') != 'Head Librarian':
        flash('Access denied: Librarians only.', category = 'error')
        return redirect(url_for('views.loginHome'))

    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        isbn = request.form.get('isbn')
        restricted = request.form.get('restricted')

        if not title or not author or not isbn:
            flash('All fields are required!', category = 'error')
        else:
            books = loadBooks()
            existingBook = next((b for b in books if b['isbn'] == isbn), None)

            if existingBook:
                existingBook['copies'] = existingBook.get('copies', 1) + 1
                flash(f'Book "{title}" added successfully!', category = 'success')
            else:
                books.append({'title': title, 'author': author, 'isbn': isbn, 'restricted': restricted, 'copies': 1
                })
                flash(f'Book "{title}" added successfully!', category = 'success')

                info = {
                    "time": datetime.now().strftime("%H:%M:%S"), "date": datetime.now().strftime("%Y-%m-%d"),
                    "userID": session.get('id'),
                    "firstName": session.get('firstName'),
                    "lastName": session.get('lastName'),
                    "email": session.get('email'),
                    "role": session.get('role'),
                    "message": f"User added book with isbn: {isbn}"
                }
                addLog(info)

            saveBooks(books)
            return redirect(url_for('views.loginnHome'))

    return render_template('addBook.html')

@views.route('/remove_book', methods=['GET', 'POST'])
def removeBook():
    if session.get('role') != 'Librarian' and session.get('role') != 'Head Librarian':
        flash('Access denied: Librarians only.', category = 'error')
        return redirect(url_for('views.loginHome'))

    books = loadBooks()

    if request.method == 'POST':
        isbn = request.form.get('isbn')
        books = [b for b in books if b['isbn'] != isbn]
        saveBooks(books)
        info = {
            "time": datetime.now().strftime("%H:%M:%S"), "date": datetime.now().strftime("%Y-%m-%d"),
            "userID": session.get('id'),
            "firstName": session.get('firstName'),
            "lastName": session.get('lastName'),
            "email": session.get('email'),
            "role": session.get('role'),
            "message": f"User removed book with isbn: {isbn}"
        }
        addLog(info)
        flash(f'Book with ISBN {isbn} removed.', category = 'success')
        return redirect(url_for('views.loginHome'))

    return render_template('removeBook.html', books=books)

@views.route('/edit_book/<isbn>', methods=['GET', 'POST'])
def editBook(isbn):
    if session.get('role') != 'Librarian' and session.get('role') != 'Head Librarian':
        flash('Access denied: Librarians only.', category = 'error')
        return redirect(url_for('views.loginHome'))

    books = loadBooks()
    book = next((b for b in books if b['isbn'] == isbn), None)
    if not book:
        flash('Book not found.', category = 'error')
        return redirect(url_for('views.loginHome'))

    if request.method == 'POST':
        book['title'] = request.form.get('title')
        book['author'] = request.form.get('author')
        book['restricted'] = request.form.get('restricted')
        book['copies'] = int(request.form.get('copies'))
        saveBooks(books)
        info = {
            "time": datetime.now().strftime("%H:%M:%S"), "date": datetime.now().strftime("%Y-%m-%d"),
            "userID": session.get('id'),
            "firstName": session.get('firstName'),
            "lastName": session.get('lastName'),
            "email": session.get('email'),
            "role": session.get('role'),
            "message": f"User edited book with isbn: {isbn}"
        }
        addLog(info)
        flash('Book updated successfully!', category = 'success')
        return redirect(url_for('views.loginHome'))

    return render_template('editBook.html', book=book)

@views.route('/add_restrictions/<isbn>', methods=['GET', 'POST'])
def addRestrictions(isbn):
    if session.get('role') != 'Librarian' and session.get('role') != 'Head Librarian':
        flash('Access denied: Librarians only.', category = 'error')
        return redirect(url_for('views.loginHome'))

    userID = request.form.get('userID')
    if not userID:
        flash('Invalid ID', category = 'error')
        return redirect(url_for('views.loginHome'))

    user = loadAcc()
    validUser = next((a for a in user if a.get('id') == userID and a.get('role') == 'Student'), None)
    if not validUser:
        flash('Invalid user ID!', category = 'error')
        return redirect(url_for('views.loginHome'))
    
    restrictions = loadRestrictions()
    if any(a['userID'] == userID and a['isbn'] == isbn for a in restrictions):
        flash('This student already has access.', category = 'error')
    else:
        restrictions.append({'userID': userID, 'isbn': isbn})
        saveRestrictions(restrictions)
        info = {
            "time": datetime.now().strftime("%H:%M:%S"), "date": datetime.now().strftime("%Y-%m-%d"),
            "userID": session.get('id'),
            "firstName": session.get('firstName'),
            "lastName": session.get('lastName'),
            "email": session.get('email'),
            "role": session.get('role'),
            "message": f"User granted access to book with isbn: {isbn}, to user with ID: {userID}"
        }
        addLog(info)
        flash('Access granted!', category = 'success')
    return redirect(url_for('views.loginHome'))

@views.route('/remove_restrictions/<isbn>', methods=['GET', 'POST'])
def removeRestrictions(isbn):
    if session.get('role') != 'Librarian' and session.get('role') != 'Head Librarian':
        flash('Access denied: Librarians only.', category = 'error')
        return redirect(url_for('views.loginHome'))

    userID = request.form.get('userID')
    if not userID:
        flash('Invalid ID', category = 'error')
        return redirect(url_for('views.loginHome'))

    user = loadAcc()
    validUser = next((a for a in user if a.get('id') == userID and a.get('role') == 'Student'), None)
    if not validUser:
        flash('Invalid user ID!', category = 'error')
        return redirect(url_for('views.loginHome'))
    
    restrictions = loadRestrictions()
    existingUser = next((x for x in restrictions if x['userID'] == userID and x['isbn'] == isbn), None)
    if(existingUser):
        restrictions.remove(existingUser)
        saveRestrictions(restrictions)
        flash('Successfully removed!', category = 'success')
        info = {
            "time": datetime.now().strftime("%H:%M:%S"), "date": datetime.now().strftime("%Y-%m-%d"),
            "userID": session.get('id'),
            "firstName": session.get('firstName'),
            "lastName": session.get('lastName'),
            "email": session.get('email'),
            "role": session.get('role'),
            "message": f"User removed access to book with isbn: {isbn}, to user with ID: {userID}"
        }
        addLog(info)
    else:
        flash('No user found!', category = 'error')
    return redirect(url_for('views.loginHome'))

@views.route('/assign_to_user/<isbn>', methods=['GET', 'POST'])
def assignToUser(isbn):
    if session.get('role') != 'Librarian' and session.get('role') != 'Head Librarian' and session.get('role') != 'Instructor':
        flash('Access denied!', category = 'error')
        return redirect(url_for('views.loginHome'))

    userID = request.form.get('userID')
    if not userID:
        flash('Invalid ID', category = 'error')
        return redirect(url_for('views.loginHome'))

    user = loadAcc()
    validUser = next((a for a in user if a.get('id') == userID and a.get('role') == 'Student'), None)
    if not validUser:
        flash('Invalid user ID!', category = 'error')
        return redirect(url_for('views.loginHome'))
    
    books = loadBooks()
    book = next((b for b in books if b['isbn'] == isbn), None)
    borrowed = loadBorrowed()
    restrictions = loadRestrictions()

    if book['copies'] != 0:
        if book['restricted'] == 'Yes':
            existingUser = next((x for x in restrictions if x['userID'] == userID and x['isbn'] == isbn), None)
            if(existingUser):
                borrowed.append({'userID': userID, 'isbn': isbn, 'title':book['title']})
                book['copies'] -= 1
                saveBooks(books)
                saveBorrowed(borrowed)
                flash('User assigned to book!', category = 'success')
                return redirect(url_for('views.loginHome'))
        else:
            borrowed.append({'userID': userID, 'isbn': isbn, 'title':book['title']})
            book['copies'] -= 1
            saveBooks(books)
            saveBorrowed(borrowed)
            info = {
                "time": datetime.now().strftime("%H:%M:%S"), "date": datetime.now().strftime("%Y-%m-%d"),
                "userID": session.get('id'),
                "firstName": session.get('firstName'),
                "lastName": session.get('lastName'),
                "email": session.get('email'),
                "role": session.get('role'),
                "message": f"User assigned book with isbn: {isbn}, to user with ID: {userID}"
            }
            addLog(info)
            flash('User assigned to book!', category = 'success')
            return redirect(url_for('views.loginHome'))
    flash('No user found!/Out of copies!', category = 'error')
    return redirect(url_for('views.loginHome'))

@views.route('/approve', methods=['GET', 'POST'])
def approve():
    if session.get('role') != 'Head Librarian' and session.get('role') != 'IT Support':
        flash('Access denied!', category='error')
        return redirect(url_for('views.loginHome'))
    
    waitlist = loadWait()
    accounts = loadAcc()
    if request.method == 'POST':
        action = request.form.get('input')
        email = request.form.get('email')

        user = next((u for u in waitlist if u['email'] == email), None)
        if not user:
            flash('User not found.', category = 'error')
        elif action == 'approve':
            accounts.append(user)
            saveAcc(accounts)
            waitlist.remove(user)
            saveWait(waitlist)
            info = {
                "time": datetime.now().strftime("%H:%M:%S"), "date": datetime.now().strftime("%Y-%m-%d"),
                "userID": session.get('id'),
                "firstName": session.get('firstName'),
                "lastName": session.get('lastName'),
                "email": session.get('email'),
                "role": session.get('role'),
                "message": f"User approved user with ID: {user['id']}"
            }
            addLog(info)
            flash(f"Approved {user['firstName']} {user['lastName']}!", category='success')
        elif action == 'reject':
            waitlist.remove(user)
            saveWait(waitlist)
            info = {
                "time": datetime.now().strftime("%H:%M:%S"), "date": datetime.now().strftime("%Y-%m-%d"),
                "userID": session.get('id'),
                "firstName": session.get('firstName'),
                "lastName": session.get('lastName'),
                "email": session.get('email'),
                "role": session.get('role'),
                "message": f"User disapproved user with ID: {user['id']}"
            }
            addLog(info)
            flash(f"Rejected {user['firstName']} {user['lastName']}.", category='error')
        waitlist = loadWait()
    books = loadBooks()
    return redirect(url_for('views.loginHome'))

@views.route('/readLog', methods = ['GET', 'POST'])
def readLog():
    if session.get('role') != 'IT Support':
        flash('Access denied!', category='error')
        return redirect(url_for('views.loginHome'))
    info = {
        "time": datetime.now().strftime("%H:%M:%S"), "date": datetime.now().strftime("%Y-%m-%d"),
        "userID": session.get('id'),
        "firstName": session.get('firstName'),
        "lastName": session.get('lastName'),
        "email": session.get('email'),
        "role": session.get('role'),
        "message": f"User with ID: {session.get('id')}, accessed logs"
    }
    addLog(info)
    logs = loadLog()
    return render_template('readLog.html', logs = logs)

@views.route('/saveBackup', methods = ['GET', 'POST'])
def saveBackup():
    if session.get('role') != 'IT Support':
        flash('Access denied!', category='error')
        return redirect(url_for('views.loginHome'))
    
    files_to_backup = {
        'books.json': bFile,
        'borrowed.json': borrowedFile,
        'restricted.json': restrictedFile,
        'accounts.json': accFile,
        'log.json': log,
        'waitlist.json': waitFile
    }
    
    backup_folder = os.path.join(os.path.dirname(__file__), 'data', 'backup')
    os.makedirs(backup_folder, exist_ok=True)

    for name, path in files_to_backup.items():
        if os.path.exists(path):
            backup_path = os.path.join(backup_folder, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{name}")
            with open(path, 'r') as f_src, open(backup_path, 'w') as f_dst:
                f_dst.write(f_src.read())
    info = {
        "time": datetime.now().strftime("%H:%M:%S"), "date": datetime.now().strftime("%Y-%m-%d"),
        "userID": session.get('id'),
        "firstName": session.get('firstName'),
        "lastName": session.get('lastName'),
        "email": session.get('email'),
        "role": session.get('role'),
        "message": f"User with ID: {session.get('id')}, saved a backup"
    }
    addLog(info)
    flash('Backup saved!', category='success')
    return redirect(url_for('views.itHome'))