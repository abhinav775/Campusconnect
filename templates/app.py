from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

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

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO students (name, class, admissionNo, username, password, phone) VALUES (?, ?, ?, ?, ?, ?)',
            (name, cls, admissionNo, username, password, phone)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('student_login'))

    return render_template('student-register.html')

# ----------------------------
# STUDENT DASHBOARD
# ----------------------------
@app.route('/student-dashboard')
def student_dashboard():
    conn = get_db_connection()
    events = conn.execute('SELECT * FROM events').fetchall()
    conn.close()
    return render_template('student-dash.html', events=events)

# ----------------------------
# BROWSE EVENTS
# ----------------------------
@app.route('/events')
def browse_events():
    conn = get_db_connection()
    events = conn.execute('SELECT * FROM events').fetchall()
    conn.close()
    return render_template('event.html', events=events)

# ----------------------------
# BROWSE CLUBS
# ----------------------------
@app.route('/clubs')
def browse_clubs():
    conn = get_db_connection()
    clubs = conn.execute('SELECT * FROM clubs').fetchall()
    conn.close()
    return render_template('club.html', clubs=clubs)

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

        conn = get_db_connection()
        conn.execute('INSERT INTO admins (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_login'))
    return render_template('admin-register.html')

# ----------------------------
# ADMIN DASHBOARD
# ----------------------------
@app.route('/admin-dashboard')
def admin_dashboard():
    return render_template('admin-dash.html')

# ----------------------------
# CREATE EVENT (ADMIN)
# ----------------------------
@app.route('/create-event', methods=['GET', 'POST'])
def create_event():
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
        return redirect(url_for('browse_events'))

    return render_template('create-event.html')


if __name__ == '__main__':
    app.run(debug=True)