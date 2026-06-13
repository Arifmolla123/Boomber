import os
import requests
import concurrent.futures
from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)

APIS = [
    {"name": "Test API (dummy)", "url": "https://httpbin.org/post", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"phone":"{p}"}}'},
]

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>UNLIMITED OTP BOMBER</title>
    <style>
        body { background: #0a0f1e; color: #0f0; font-family: monospace; text-align: center; padding: 50px; }
        .card { background: #111; border: 2px solid red; border-radius: 30px; padding: 30px; max-width: 500px; margin: auto; }
        input, button { padding: 12px; margin: 10px; font-size: 1rem; border-radius: 30px; }
        button { background: red; color: white; cursor: pointer; }
        pre { text-align: left; background: #000; padding: 10px; overflow: auto; max-height: 400px; }
    </style>
</head>
<body>
<div class="card">
    <h1>OTP BOMBER</h1>
    <p>Developer: Arif</p>
    <input type="text" id="phone" placeholder="10 digit number" maxlength="10">
    <br>
    <button id="startBtn">START UNLIMITED</button>
    <button id="stopBtn">STOP</button>
    <pre id="output">Ready.</pre>
</div>
<script>
    let running = false;
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const phoneInput = document.getElementById('phone');
    const output = document.getElementById('output');

    async function sendRound(phone) {
        const res = await fetch('/bomb', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({phone: phone})
        });
        const data = await res.json();
        return data.log;
    }

    startBtn.onclick = async () => {
        if (running) return;
        let phone = phoneInput.value.trim();
        if (!phone || phone.length !== 10) {
            output.innerText = "Invalid number";
            return;
        }
        running = true;
        startBtn.disabled = true;
        stopBtn.disabled = false;
        output.innerText = "Bombing started...\\n";
        let round = 0;
        while (running) {
            round++;
            output.innerText += `Round ${round}\\n`;
            let log = await sendRound(phone);
            output.innerText += log + "\\n";
            await new Promise(r => setTimeout(r, 500));
        }
        startBtn.disabled = false;
        stopBtn.disabled = true;
        output.innerText += "Stopped.";
    };
    stopBtn.onclick = () => { running = false; };
    stopBtn.disabled = true;
</script>
</body>
</html>
"""

def send_request(api, phone):
    try:
        if callable(api['url']):
            url = api['url'](phone)
        else:
            url = api['url']
        headers = api['headers'].copy() if api['headers'] else {}
        headers["User-Agent"] = "Mozilla/5.0"
        data = None
        if api.get('data') and api['data']:
            data = api['data'](phone) if callable(api['data']) else api['data']
        if api['method'] == 'POST':
            r = requests.post(url, headers=headers, data=data, timeout=5)
        else:
            r = requests.get(url, headers=headers, timeout=5)
        return f"[+] {api['name']} → {r.status_code}"
    except Exception as e:
        return f"[-] {api['name']} → {str(e)[:40]}"

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/bomb', methods=['POST'])
def bomb():
    phone = request.json.get('phone')
    if not phone or len(phone) != 10:
        return jsonify({"log": "Invalid phone"}), 400
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(send_request, api, phone) for api in APIS]
        logs = [f.result() for f in concurrent.futures.as_completed(futures)]
    return jsonify({"log": "\n".join(logs)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
