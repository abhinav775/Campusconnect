from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"  # for session management


# ----------------------------
# DATABASE HELPER FUNCTION
# ----------------------------
def get_db_connection():
    conn = sqlite3.connect('campusconnect.db')
    conn.row_factory = sqlite3.Row
    return conn


# ----------------------------
# HOME PAGE
# ----------------------------
@app.route('/')
def index():
    return render_template('index.html')


# ----------------------------
# STUDENT LOGIN
# ----------------------------
@app.route('/student-login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        student = conn.execute(
            'SELECT * FROM students WHERE username = ? AND password = ?',
            (username, password)
        ).fetchone()
        conn.close()

        if student:
            session['student_id'] = student['id']
            return redirect(url_for('student_dashboard'))
        else:
            return "Invalid Credentials"
    return render_template('student-login.html')


# ----------------------------
# STUDENT REGISTER
# ----------------------------
@app.route('/student-register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        name = request.form['studentName']
        cls = request.form['class']
        admissionNo = request.form['admissionNo']
        username = request.form['username']
        password = request.form['password']
        phone = request.form['phone']

        try:
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO students (name, class, admissionNo, username, password, phone) VALUES (?, ?, ?, ?, ?, ?)',
                (name, cls, admissionNo, username, password, phone)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            return "Admission Number or Username already exists!"
        finally:
            conn.close()

        return redirect(url_for('student_login'))

    return render_template('student-register.html')


# ----------------------------
# STUDENT DASHBOARD
# ----------------------------
@app.route('/student-dashboard')
def student_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('student_login'))

    conn = get_db_connection()
    events = conn.execute('SELECT * FROM events').fetchall()
    conn.close()
    return render_template('student-dash.html', events=events)


# ----------------------------
# BROWSE EVENTS
# ----------------------------
@app.route('/events')
def browse_events():
    if 'student_id' not in session:
        return redirect(url_for('student_login'))

    conn = get_db_connection()
    events = conn.execute('SELECT * FROM events').fetchall()
    conn.close()
    return render_template('event.html', events=events)


# ----------------------------
# REGISTER FOR EVENT
# ----------------------------
@app.route('/register-event/<int:event_id>', methods=['POST'])
def register_event(event_id):
    if 'student_id' not in session:
        return redirect(url_for('student_login'))

    student_id = session['student_id']

    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO event_registrations (student_id, event_id) VALUES (?, ?)',
            (student_id, event_id)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Already registered
    finally:
        conn.close()

    return redirect(url_for('browse_events'))


# ----------------------------
# BROWSE CLUBS
# ----------------------------
@app.route('/clubs')
def browse_clubs():
    if 'student_id' not in session:
        return redirect(url_for('student_login'))

    conn = get_db_connection()
    clubs = conn.execute('SELECT * FROM clubs').fetchall()
    conn.close()
    return render_template('club.html', clubs=clubs)


# ----------------------------
# JOIN CLUB
# ----------------------------
@app.route('/join-club/<int:club_id>', methods=['POST'])
def join_club(club_id):
    if 'student_id' not in session:
        return redirect(url_for('student_login'))

    student_id = session['student_id']

    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO club_memberships (student_id, club_id) VALUES (?, ?)',
            (student_id, club_id)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()

    return redirect(url_for('browse_clubs'))


# ----------------------------
# ADMIN LOGIN
# ----------------------------
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        admin = conn.execute(
            'SELECT * FROM admins WHERE username = ? AND password = ?',
            (username, password)
        ).fetchone()
        conn.close()

        if admin:
            session['admin_id'] = admin['id']
            return redirect(url_for('admin_dashboard'))
        else:
            return "Invalid Credentials"
    return render_template('admin-login.html')


# ----------------------------
# ADMIN REGISTER
# ----------------------------
@app.route('/admin-register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conn = get_db_connection()
            conn.execute('INSERT INTO admins (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
        except sqlite3.IntegrityError:
            return "Username already exists!"
        finally:
            conn.close()

        return redirect(url_for('admin_login'))
    return render_template('admin-register.html')


# ----------------------------
# ✅ FIXED ADMIN DASHBOARD
# ----------------------------
@app.route('/admin-dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    conn = get_db_connection()

    students = conn.execute('SELECT * FROM students').fetchall()
    events = conn.execute('SELECT * FROM events').fetchall()
    clubs = conn.execute('SELECT * FROM clubs').fetchall()

    # ✅ Create tables if not exist
    conn.execute('''
        CREATE TABLE IF NOT EXISTS event_registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            event_id INTEGER,
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (event_id) REFERENCES events(id)
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS club_registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            club_id INTEGER,
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (club_id) REFERENCES clubs(id)
        )
    ''')

    # Event registrations
    event_registrations = {}
    for event in events:
        registered_students = conn.execute('''
            SELECT s.name FROM students s
            JOIN event_registrations er ON s.id = er.student_id
            WHERE er.event_id = ?
        ''', (event['id'],)).fetchall()
        event_registrations[event['id']] = registered_students

    # Club registrations
    club_registrations = {}
    for club in clubs:
        registered_students = conn.execute('''
            SELECT s.name FROM students s
            JOIN club_registrations cr ON s.id = cr.student_id
            WHERE cr.club_id = ?
        ''', (club['id'],)).fetchall()
        club_registrations[club['id']] = registered_students

    conn.close()

    return render_template(
        'admin-dash.html',
        students=students,
        events=events,
        clubs=clubs,
        event_registrations=event_registrations,
        club_registrations=club_registrations
    )


# ----------------------------
# CREATE EVENT (ADMIN)
# ----------------------------
@app.route('/create-event', methods=['GET', 'POST'])
def create_event():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        host = request.form['host']
        description = request.form['description']

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO events (name, date, host, description) VALUES (?, ?, ?, ?)',
            (name, date, host, description)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('admin_dashboard'))

    return render_template('create-event.html')


# ----------------------------
# CREATE CLUB (ADMIN)
# ----------------------------
@app.route('/create-club', methods=['GET', 'POST'])
def create_club():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        name = request.form['name']
        banner = request.form['banner']

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO clubs (name, banner) VALUES (?, ?)',
            (name, banner)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('admin_dashboard'))

    return render_template('create-club.html')


# ----------------------------
# CLEAR ALL DATA (ADMIN)
# ----------------------------
@app.route('/clear-data', methods=['POST'])
def clear_data():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM students')
    conn.execute('DELETE FROM events')
    conn.execute('DELETE FROM clubs')
    conn.execute('DELETE FROM event_registrations')
    conn.execute('DELETE FROM club_registrations')
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))


if __name__ == '__main__':
    app.run(debug=True)
